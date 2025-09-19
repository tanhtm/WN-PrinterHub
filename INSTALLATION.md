# 🚀 WN-PrinterHub - Installation & Quick Start Guide

## ✅ What's Been Implemented

This implementation includes all the features specified in the original README plus several enhancements:

### 📋 Core Features (As Specified)
- ✅ **FastAPI-based local printer service**
- ✅ **Bearer token authentication**
- ✅ **CORS + Private Network Access support**
- ✅ **Two printing modes**: `text` and `raw_base64`
- ✅ **JetDirect/RAW printing** (port 9100)
- ✅ **Environment-based configuration**
- ✅ **Health check endpoint**

### 🔥 Enhanced Features (Improvements)
- ✅ **Enhanced ESC/POS utilities** with fluent builder interface
- ✅ **Formatted receipt printing** with table support
- ✅ **Network printer scanning** capability
- ✅ **Enhanced printer connectivity testing**
- ✅ **Comprehensive logging** with request/response tracking
- ✅ **Production-ready configuration**
- ✅ **Startup scripts** for Unix/Windows
- ✅ **Systemd service** configuration
- ✅ **Input validation** and IP address verification
- ✅ **Test suite** with pytest
- ✅ **Developer tools** integration (Black, Ruff)

## 🛠️ Installation

### 1. Prerequisites

Install `uv` (Python package manager):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Clone and Setup

```bash
git clone <repository-url>
cd WN-PrinterHub

# Install dependencies
uv sync

# Create environment file
cp .env.example .env

# Edit .env file - IMPORTANT: Change WN_API_TOKEN!
nano .env
```

### 3. Configure Environment

Edit `.env` file and update these important settings:

```bash
# SECURITY: Change this to a secure token!
WN_API_TOKEN=your_secure_token_here_at_least_32_characters_long

# CORS Configuration (your application domains)
WN_ALLOWED_ORIGINS=https://app.whiteneuron.com,https://another-app.whiteneuron.com

# Server settings (defaults are usually fine)
WN_HOST=0.0.0.0
WN_PORT=8088
WN_PRINTER_DEFAULT_PORT=9100
WN_LOG_LEVEL=INFO
```

## 🚀 Running the Application

### Development Mode
```bash
# Using startup script (recommended)
./start.sh          # Unix/Linux/macOS
start.bat           # Windows

# Or manually
uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
```

### Production Mode
```bash
# Direct production run
uv run python production.py

# Or with systemd (Linux)
sudo cp wn-printerhub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wn-printerhub
sudo systemctl start wn-printerhub
```

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8088/health
```

### Network Information
```bash
curl -H "Authorization: Bearer your_token" http://localhost:8088/api/v1/network/info
```

### Ping Printer
```bash
curl -X POST "http://localhost:8088/api/v1/printers/ping" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{"host": "192.168.1.50", "timeout_ms": 1500}'
```

### Scan Network for Printers
```bash
curl -X POST "http://localhost:8088/api/v1/printers/scan" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "network_base": "192.168.1",
    "port": 9100,
    "timeout_ms": 1000
  }'
```

### Print Text
```bash
curl -X POST "http://localhost:8088/api/v1/print" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "printer": {"host": "192.168.1.50", "timeout_ms": 2000},
    "mode": "text",
    "text": "QUẦY BẾP\\nBÀN T5\\nPhở bò x2\\nTrà đá x1\\n",
    "text_opts": {
      "encoding": "utf-8",
      "append_cut": true,
      "append_newlines": 2
    }
  }'
```

### Print Receipt (Enhanced Feature)
```bash
curl -X POST "http://localhost:8088/api/v1/print/receipt" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "printer": {"host": "192.168.1.50", "timeout_ms": 2000},
    "items": [
      {"name": "Phở Bò", "qty": 2, "price": 8.50},
      {"name": "Trà Đá", "qty": 1, "price": 2.00}
    ],
    "total": 19.00,
    "header": "QUẦY BẾP - BÀN T5",
    "footer": "Cảm ơn quý khách!",
    "datetime": "2025-09-19 14:30:00",
    "encoding": "utf-8"
  }'
```

## 🧪 Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Test imports
uv run python -c "from app.main import app; print('✅ Import successful')"

# Test configuration
uv run python -c "from app.config import config; print(f'Port: {config.port}')"
```

## 📚 API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8088/docs
- **ReDoc**: http://localhost:8088/redoc
- **OpenAPI spec**: http://localhost:8088/openapi.json

## 🔐 Security Notes

1. **Change the default API token** in `.env` file
2. **Set specific CORS origins** instead of `*`
3. **Use HTTPS** for production applications
4. **Restrict network access** with firewall rules
5. **Monitor logs** for suspicious activity

## 🌐 Integration Examples

### JavaScript (Frontend)
```javascript
const PRINTERHUB = "http://localhost:8088";
const TOKEN = "your_secure_token";

// Ping printer
async function pingPrinter(ip) {
  const response = await fetch(`${PRINTERHUB}/api/v1/printers/ping`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ host: ip, timeout_ms: 1500 })
  });
  return await response.json();
}

// Print receipt
async function printReceipt(ip, items, total) {
  const payload = {
    printer: { host: ip, timeout_ms: 2000 },
    items: items,
    total: total,
    header: "MY STORE",
    footer: "Thank you for your purchase!",
    datetime: new Date().toLocaleString()
  };
  
  const response = await fetch(`${PRINTERHUB}/api/v1/print/receipt`, {
    method: "POST",
    mode: "cors", 
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  return await response.json();
}
```

### Python (Backend)
```python
import requests

PRINTERHUB = "http://localhost:8088"
TOKEN = "your_secure_token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def scan_printers(network="192.168.1"):
    """Scan network for available printers."""
    response = requests.post(
        f"{PRINTERHUB}/api/v1/printers/scan",
        json={"network_base": network, "port": 9100, "timeout_ms": 1000},
        headers=HEADERS
    )
    return response.json()

def print_receipt(printer_ip, items, total, **options):
    """Print a formatted receipt."""
    payload = {
        "printer": {"host": printer_ip, "timeout_ms": 2000},
        "items": items,
        "total": total,
        **options
    }
    response = requests.post(
        f"{PRINTERHUB}/api/v1/print/receipt",
        json=payload,
        headers=HEADERS
    )
    return response.json()

# Example usage
printers = scan_printers("192.168.1")
print(f"Found {printers['printers_found']} printers")

if printers['printers']:
    printer_ip = printers['printers'][0]['host']
    result = print_receipt(printer_ip, [
        {"name": "Coffee", "qty": 2, "price": 3.50},
        {"name": "Donut", "qty": 1, "price": 2.25}
    ], 9.25, header="Coffee Shop", footer="Have a great day!")
    print(result)
```

## 🔄 Production Deployment

### Linux Systemd Service

1. Copy service file: `sudo cp wn-printerhub.service /etc/systemd/system/`
2. Create user: `sudo useradd -r -s /bin/false printerhub`
3. Setup directory: `sudo mkdir -p /opt/wn-printerhub`
4. Copy files: `sudo cp -r * /opt/wn-printerhub/`
5. Set permissions: `sudo chown -R printerhub:printerhub /opt/wn-printerhub`
6. Enable service: `sudo systemctl enable wn-printerhub`
7. Start service: `sudo systemctl start wn-printerhub`
8. Check status: `sudo systemctl status wn-printerhub`

### Docker (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
COPY app/ ./app/

RUN pip install uv && uv sync
EXPOSE 8088

CMD ["uv", "run", "python", "production.py"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Run `uv sync` to install dependencies
2. **Port Already in Use**: Change `WN_PORT` in `.env` file
3. **Printer Connection Timeout**: Check network connectivity and printer IP
4. **Authentication Failed**: Verify `WN_API_TOKEN` matches in client code
5. **CORS Issues**: Add your domain to `WN_ALLOWED_ORIGINS`

### Logging

Check logs for debugging:
```bash
# Development
tail -f logs/wn-printerhub.log

# Production with systemd
sudo journalctl -u wn-printerhub -f

# Check service status
systemctl status wn-printerhub
```

## 🤝 Support

- Check the interactive API docs at `/docs` when running
- Review the comprehensive test suite in `tests/`
- All configurations are documented in `.env.example`
- Production deployment examples provided

---

**🎉 WN-PrinterHub is ready to bridge your applications to any network printer!**