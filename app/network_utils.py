"""
Network utilities for WN-PrinterHub
Enhanced network operations and printer discovery
"""
import asyncio
import socket
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


async def scan_network_for_printers(network_base: str = "192.168.1", 
                                   port: int = 9100,
                                   timeout_ms: int = 1000) -> List[Dict[str, Any]]:
    """
    Scan a network range for printers on the specified port.
    
    Args:
        network_base: Network base (e.g., "192.168.1" for 192.168.1.x)
        port: Port to scan (default 9100 for JetDirect)
        timeout_ms: Timeout per host in milliseconds
    
    Returns:
        List of dictionaries with printer information
    """
    logger.info(f"Scanning network {network_base}.1-254 on port {port}")
    
    # Create IP range
    hosts = [f"{network_base}.{i}" for i in range(1, 255)]
    
    # Create semaphore to limit concurrent connections
    semaphore = asyncio.Semaphore(50)
    
    async def check_host(host: str) -> Optional[Dict[str, Any]]:
        async with semaphore:
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Try to connect
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=timeout_ms / 1000
                )
                
                writer.close()
                await writer.wait_closed()
                
                latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
                
                return {
                    "host": host,
                    "port": port,
                    "status": "online",
                    "latency_ms": latency
                }
                
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                return None
    
    # Run scan concurrently
    tasks = [check_host(host) for host in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter successful connections
    printers = [result for result in results if result is not None and not isinstance(result, Exception)]
    
    logger.info(f"Found {len(printers)} potential printers")
    return printers


def get_local_network_info() -> Dict[str, Any]:
    """Get information about the local network interfaces."""
    try:
        # Get hostname
        hostname = socket.gethostname()
        
        # Get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # Calculate network base
        ip_parts = local_ip.split(".")
        network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        return {
            "hostname": hostname,
            "local_ip": local_ip,
            "network_base": network_base,
            "suggested_scan_range": f"{network_base}.1-254"
        }
    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        return {
            "hostname": "unknown",
            "local_ip": "unknown",
            "network_base": "192.168.1",
            "suggested_scan_range": "192.168.1.1-254"
        }


async def enhanced_ping(host: str, port: int = 9100, timeout_ms: int = 1500) -> Dict[str, Any]:
    """
    Enhanced ping with additional information about the printer.
    
    Args:
        host: Target host IP
        port: Target port
        timeout_ms: Connection timeout in milliseconds
    
    Returns:
        Dictionary with ping results and additional info
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Basic connectivity test
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout_ms / 1000
        )
        
        # Try to get some printer information (if available)
        printer_info = {}
        try:
            # Send a simple query (ESC/POS status request)
            writer.write(b"\x1b\x76")  # ESC v (return firmware version - if supported)
            await writer.drain()
            
            # Try to read response with short timeout
            try:
                response = await asyncio.wait_for(reader.read(1024), timeout=0.5)
                if response:
                    printer_info["raw_response"] = response.hex()
                    printer_info["response_length"] = len(response)
            except asyncio.TimeoutError:
                # No response is normal for many printers
                pass
            
        except Exception as e:
            logger.debug(f"Could not query printer info: {e}")
        
        writer.close()
        await writer.wait_closed()
        
        latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        return {
            "ok": True,
            "latency_ms": latency,
            "message": f"Connected {host}:{port}",
            "printer_info": printer_info,
            "connection_time": asyncio.get_event_loop().time()
        }
        
    except asyncio.TimeoutError:
        latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
        return {
            "ok": False,
            "latency_ms": latency,
            "message": f"Timeout connecting {host}:{port}",
            "error_type": "timeout"
        }
        
    except ConnectionRefusedError:
        latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
        return {
            "ok": False,
            "latency_ms": latency,
            "message": f"Connection refused {host}:{port}",
            "error_type": "refused"
        }
        
    except Exception as e:
        latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
        return {
            "ok": False,
            "latency_ms": latency,
            "message": f"Error: {str(e)}",
            "error_type": "unknown",
            "error_details": str(e)
        }


def validate_ip_address(ip: str) -> bool:
    """Validate if a string is a valid IP address."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_private_ip(ip: str) -> bool:
    """Check if an IP address is in a private range."""
    try:
        octets = list(map(int, ip.split('.')))
        
        # Private ranges:
        # 10.0.0.0/8
        # 172.16.0.0/12  
        # 192.168.0.0/16
        return (
            octets[0] == 10 or
            (octets[0] == 172 and 16 <= octets[1] <= 31) or
            (octets[0] == 192 and octets[1] == 168)
        )
    except (ValueError, IndexError):
        return False