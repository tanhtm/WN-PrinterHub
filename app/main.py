"""
WN-PrinterHub Main Application
FastAPI-based local printer connector service
"""
import asyncio
import base64
import contextlib
import time
import logging
from typing import Literal, Optional, List

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from .config import config
from .escpos_utils import create_receipt, create_simple_text, ESCPOSBuilder
from .network_utils import scan_network_for_printers, get_local_network_info, enhanced_ping, validate_ip_address

# Setup logging
logging.basicConfig(
    level=config.get_log_level(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wn-printerhub")

# FastAPI app initialization
app = FastAPI(
    title="WN-PrinterHub",
    description="Local LAN printer connector service for White Neuron applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins if config.allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_pna_header(request: Request, call_next):
    """Add Private Network Access header for HTTPS->HTTP requests."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.perf_counter()
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    process_time = time.perf_counter() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


# Pydantic models
class PrinterTarget(BaseModel):
    """Target printer configuration."""
    host: str = Field(..., description="Printer IP address")
    timeout_ms: int = Field(1500, ge=100, le=30000, description="Connection timeout in milliseconds")

    @field_validator("host")
    @classmethod
    def validate_host(cls, v):
        """Basic IP address validation."""
        if not v or not v.strip():
            raise ValueError("Host cannot be empty")
        return v.strip()


class PrintTextOptions(BaseModel):
    """Options for text printing mode."""
    encoding: str = Field("utf-8", description="Text encoding")
    append_cut: bool = Field(True, description="Append paper cut command")
    append_newlines: int = Field(2, ge=0, le=10, description="Number of newlines to append")


class ReceiptItem(BaseModel):
    """Receipt item model."""
    name: str = Field(..., description="Item name")
    qty: int = Field(..., ge=1, description="Quantity")
    price: float = Field(..., ge=0, description="Price per item")


class PrintReceiptRequest(BaseModel):
    """Print receipt request payload."""
    printer: PrinterTarget
    items: List[ReceiptItem] = Field(..., description="List of items")
    total: float = Field(..., ge=0, description="Total amount")
    header: Optional[str] = Field(None, description="Receipt header")
    footer: Optional[str] = Field(None, description="Receipt footer") 
    datetime: Optional[str] = Field(None, description="Date/time string")
    encoding: str = Field("utf-8", description="Text encoding")


class NetworkScanRequest(BaseModel):
    """Network scan request."""
    network_base: str = Field("192.168.1", description="Network base (e.g., '192.168.1' for 192.168.1.x)")
    port: int = Field(9100, ge=1, le=65535, description="Port to scan")
    timeout_ms: int = Field(1000, ge=100, le=10000, description="Timeout per host in milliseconds")


class PrintRequest(BaseModel):
    """Print request payload."""
    printer: PrinterTarget
    mode: Literal["text", "raw_base64"]
    text: Optional[str] = Field(None, description="Text to print (for text mode)")
    raw_base64: Optional[str] = Field(None, description="Base64-encoded ESC/POS data (for raw mode)")
    text_opts: PrintTextOptions = PrintTextOptions()

    @field_validator("text")
    @classmethod
    def validate_text(cls, v, info):
        """Validate text field based on mode."""
        if info.data.get("mode") == "text" and not v:
            raise ValueError("text is required when mode=text")
        return v

    @field_validator("raw_base64")
    @classmethod
    def validate_raw_base64(cls, v, info):
        """Validate raw_base64 field based on mode."""
        if info.data.get("mode") == "raw_base64" and not v:
            raise ValueError("raw_base64 is required when mode=raw_base64")
        if v and info.data.get("mode") == "raw_base64":
            try:
                base64.b64decode(v, validate=True)
            except Exception:
                raise ValueError("raw_base64 is not valid base64 data")
        return v


# Authentication dependency
async def authenticate(authorization: str = Header(None)):
    """Verify Bearer token authentication."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.split(" ", 1)[1].strip()
    if token != config.api_token:
        raise HTTPException(status_code=403, detail="Invalid token")


# Utility functions
async def tcp_connect(host: str, port: int, timeout_ms: int):
    """Establish TCP connection to printer."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout_ms / 1000
        )
        return reader, writer
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Timeout connecting to {host}:{port}")
    except Exception as e:
        raise Exception(f"Connection error to {host}:{port}: {str(e)}")


async def tcp_send(host: str, port: int, data: bytes, timeout_ms: int) -> int:
    """Send data to printer via TCP."""
    reader, writer = await tcp_connect(host, port, timeout_ms)
    try:
        writer.write(data)
        await writer.drain()
        return len(data)
    finally:
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()


def escpos_from_text(text: str, encoding: str, newlines: int, cut: bool) -> bytes:
    """Convert text to ESC/POS commands."""
    # ESC @ - Initialize printer
    output = bytearray(b"\x1b@")
    
    # Add the text content
    try:
        text_bytes = text.encode(encoding, errors="replace")
        output.extend(text_bytes)
    except (UnicodeError, LookupError):
        # Fallback to UTF-8 if encoding fails
        logger.warning(f"Failed to encode with {encoding}, falling back to utf-8")
        text_bytes = text.encode("utf-8", errors="replace")
        output.extend(text_bytes)
    
    # Add newlines
    if newlines > 0:
        output.extend(b"\n" * newlines)
    
    # Add paper cut command
    if cut:
        output.extend(b"\x1dV\x00")  # GS V 0 - Full cut
    
    return bytes(output)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "WN-PrinterHub",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.post("/api/v1/printers/ping")
async def ping_printer(body: PrinterTarget, _=Depends(authenticate)):
    """Check printer connectivity."""
    if not validate_ip_address(body.host):
        raise HTTPException(status_code=422, detail=f"Invalid IP address: {body.host}")
    
    result = await enhanced_ping(body.host, config.printer_default_port, body.timeout_ms)
    return result


@app.post("/api/v1/printers/scan")
async def scan_printers(body: NetworkScanRequest, _=Depends(authenticate)):
    """Scan network for printers."""
    logger.info(f"Scanning network {body.network_base} on port {body.port}")
    
    try:
        printers = await scan_network_for_printers(
            network_base=body.network_base,
            port=body.port,
            timeout_ms=body.timeout_ms
        )
        
        return {
            "ok": True,
            "network_base": body.network_base,
            "port": body.port,
            "printers_found": len(printers),
            "printers": printers,
            "scan_info": get_local_network_info()
        }
        
    except Exception as e:
        logger.error(f"Network scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/api/v1/network/info")
async def network_info(_=Depends(authenticate)):
    """Get local network information."""
    return {
        "ok": True,
        "network_info": get_local_network_info()
    }


@app.post("/api/v1/print")
async def print_document(request: PrintRequest, _=Depends(authenticate)):
    """Send print job to printer."""
    logger.info(f"Print request: mode={request.mode}, printer={request.printer.host}")
    
    # Prepare print data based on mode
    if request.mode == "text":
        if not request.text:
            raise HTTPException(status_code=422, detail="Text is required for text mode")
        
        # Use enhanced ESC/POS utilities
        data = create_simple_text(
            request.text,
            encoding=request.text_opts.encoding,
            append_newlines=request.text_opts.append_newlines,
            append_cut=request.text_opts.append_cut
        )
        
        logger.info(f"Generated ESC/POS data: {len(data)} bytes")
        
    else:  # raw_base64 mode
        if not request.raw_base64:
            raise HTTPException(status_code=422, detail="raw_base64 is required for raw_base64 mode")
        
        try:
            data = base64.b64decode(request.raw_base64, validate=True)
            logger.info(f"Decoded raw data: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Base64 decode error: {str(e)}")
            raise HTTPException(status_code=422, detail="Invalid base64 data")
    
    # Send to printer
    try:
        bytes_sent = await tcp_send(
            request.printer.host,
            config.printer_default_port,
            data,
            request.printer.timeout_ms
        )
        
        logger.info(f"Successfully sent {bytes_sent} bytes to printer {request.printer.host}")
        
        return {
            "ok": True,
            "bytes_sent": bytes_sent,
            "message": "Printed"
        }
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout sending to printer {request.printer.host}:{config.printer_default_port}")
        raise HTTPException(
            status_code=504,
            detail=f"Timeout sending to {request.printer.host}:{config.printer_default_port}"
        )
        
    except Exception as e:
        logger.error(f"Print error to {request.printer.host}:{config.printer_default_port}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Print error: {str(e)}"
        )


@app.post("/api/v1/print/receipt")
async def print_receipt(request: PrintReceiptRequest, _=Depends(authenticate)):
    """Print a formatted receipt."""
    if not validate_ip_address(request.printer.host):
        raise HTTPException(status_code=422, detail=f"Invalid IP address: {request.printer.host}")
    
    logger.info(f"Receipt print request: {len(request.items)} items, total=${request.total}")
    
    try:
        # Convert request items to dict format
        items = [
            {
                "name": item.name,
                "qty": item.qty,
                "price": item.price
            }
            for item in request.items
        ]
        
        # Create receipt data
        receipt_options = {
            "encoding": request.encoding,
            "cut": True,
            "feed_lines": 3
        }
        
        if request.header:
            receipt_options["header"] = request.header
        if request.footer:
            receipt_options["footer"] = request.footer
        if request.datetime:
            receipt_options["datetime"] = request.datetime
            
        data = create_receipt(items, request.total, **receipt_options)
        
        logger.info(f"Generated receipt data: {len(data)} bytes")
        
        # Send to printer
        bytes_sent = await tcp_send(
            request.printer.host,
            config.printer_default_port,
            data,
            request.printer.timeout_ms
        )
        
        logger.info(f"Successfully sent receipt ({bytes_sent} bytes) to printer {request.printer.host}")
        
        return {
            "ok": True,
            "bytes_sent": bytes_sent,
            "message": "Receipt printed",
            "items_count": len(request.items),
            "total": request.total
        }
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout sending receipt to printer {request.printer.host}:{config.printer_default_port}")
        raise HTTPException(
            status_code=504,
            detail=f"Timeout sending to {request.printer.host}:{config.printer_default_port}"
        )
        
    except Exception as e:
        logger.error(f"Receipt print error to {request.printer.host}:{config.printer_default_port}: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Print error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "WN-PrinterHub",
        "description": "Local LAN printer connector service for White Neuron applications",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "network_info": "GET /api/v1/network/info",
            "ping": "POST /api/v1/printers/ping",
            "scan": "POST /api/v1/printers/scan", 
            "print": "POST /api/v1/print",
            "print_receipt": "POST /api/v1/print/receipt"
        },
        "documentation": "/docs",
        "features": [
            "ESC/POS text printing",
            "Raw ESC/POS command printing",
            "Formatted receipt printing",
            "Network printer scanning",
            "Enhanced printer connectivity testing"
        ]
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("WN-PrinterHub starting up...")
    logger.info(f"Default printer port: {config.printer_default_port}")
    logger.info(f"Allowed CORS origins: {config.allowed_origins}")
    
    if config.api_token == "CHANGE_ME":
        logger.warning("WARNING: Using default API token! Please set WN_API_TOKEN environment variable!")


# Shutdown event  
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("WN-PrinterHub shutting down...")


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=True,
        log_level=config.log_level.lower()
    )


def main():
    """Main entry point for the application."""
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower()
    )