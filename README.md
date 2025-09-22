# WN-PrinterHub

*"Một nhịp cầu mảnh giữa ứng dụng và máy in—
chung LAN là chạm, gọi là in."*

**WN-PrinterHub** là dịch vụ **Python + FastAPI** chạy **local trong LAN**, đóng vai trò **connector in ấn** cho *mọi ứng dụng nội bộ của White Neuron* (web/desktop/backend). Ứng dụng của bạn chỉ cần gọi HTTP tới **host local** của PrinterHub để:

* **Ping & Scan**: kiểm tra và tìm kiếm máy in trong LAN
* **Print Text**: in văn bản với formatting ESC/POS  
* **Print Raw**: gửi lệnh ESC/POS tùy chỉnh

> Không cùng LAN → không thể kết nối máy in → trả lỗi rõ ràng để UI thông báo.
> Cùng LAN → xác nhận kết nối, in bất cứ lúc nào người dùng thao tác.

## 🚀 **Đã Triển Khai & Sẵn Sàng Sử Dụng**

✅ **Core Features**: Tất cả tính năng cơ bản theo spec  
✅ **Enhanced APIs**: Network scanning, ESC/POS printing, network info  
✅ **Production Ready**: Logging, error handling, validation  
✅ **Easy Setup**: Startup scripts và documentation đầy đủ

📖 **[Xem Hướng Dẫn Cài Đặt Chi Tiết](INSTALLATION.md)**Hub

*“Một nhịp cầu mảnh giữa ứng dụng và máy in—
chung LAN là chạm, gọi là in.”*

**WN-PrinterHub** là dịch vụ **Python + FastAPI** chạy **local trong LAN**, đóng vai trò **connector in ấn** cho *mọi ứng dụng nội bộ của White Neuron* (web/desktop/backend). Ứng dụng của bạn chỉ cần gọi HTTP tới **host local** của PrinterHub để:

* **/printers/ping**: kiểm tra khả dụng máy in trong LAN.
* **/print**: gửi lệnh in ngay lập tức.

> Không cùng LAN → không thể kết nối máy in → trả lỗi rõ ràng để UI thông báo.
> Cùng LAN → xác nhận kết nối, in bất cứ lúc nào người dùng thao tác.

---

## Features

- 🖨️ **Printer Management**: Ping printers, test connectivity, and check status
- 📄 **Text & Raw Printing**: Print text with formatting or send custom ESC/POS commands  
- 📊 **Test Patterns**: Print test pages to verify printer functionality
- 🌐 **Network Discovery**: Scan LAN for available printers
- 🔍 **Health Monitoring**: Real-time printer status and diagnostics
- 🔒 **Optional Authentication**: Bearer token security for production, can be disabled for development
- 🚀 **CORS Support**: Cross-origin requests with Private Network Access headers
- 📖 **Interactive API**: Swagger UI documentation at `/docs`

---

## 🧩 Mô hình mạng (tổng quát)

```
Ứng dụng WN (Web/Desktop/Backend)
            │  HTTP fetch (CORS + Private Network Access)
            ▼
WN-PrinterHub (FastAPI, chạy trong LAN)
  ├─ /health                      # kiểm tra service
  ├─ /api/v1/network/info         # thông tin mạng local
  ├─ /api/v1/printers/ping      # kiểm tra kết nối máy in
  ├─ /api/v1/printers/scan      # quét mạng tìm máy in
  └─ /api/v1/print              # in ESC/POS (text/raw_base64)
            ▼
Máy in LAN (JetDirect/RAW 9100)
```

* PrinterHub **dùng cổng máy in mặc định 9100** (RAW/JetDirect). Có thể đổi bằng biến môi trường; payload **không cần** cổng.

---

## ⚙️ Cài đặt & chạy với `uv`

### 🚀 Quick Start (Khuyến nghị)

```bash
# 1. Clone repository
git clone <repository-url>
cd WN-PrinterHub

# 2. Chạy script setup tự động  
./start.sh          # macOS/Linux
start.bat           # Windows

# Script sẽ tự động:
# - Cài dependencies với uv
# - Tạo .env file từ template
# - Khởi động server với hot-reload
```

### 📚 Manual Setup (Chi tiết)

### 0) Cài `uv`

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

### 1) Cài dependencies

```bash
uv sync
```

### 2) Biến môi trường

```bash
# Tạo từ template
cp .env.example .env

# Chỉnh sửa .env file - QUAN TRỌNG: Đổi API token!
nano .env
```

**Cấu hình quan trọng trong `.env`:**
```bash
# Authentication - Set to false for development, true for production  
USE_AUTH=true

# Token API - ĐỔI THÀNH CHUỖI BẢO MẬT DÀI! (chỉ cần khi USE_AUTH=true)
WN_API_TOKEN=your_secure_token_here_at_least_32_characters_long

# Cho phép CORS từ domain ứng dụng (nhiều domain ngăn cách bằng dấu phẩy)
WN_ALLOWED_ORIGINS=https://app.whiteneuron.com,https://another-app.whiteneuron.com

# Cấu hình server (thường không cần đổi)
WN_HOST=0.0.0.0
WN_PORT=8088
WN_PRINTER_DEFAULT_PORT=9100
WN_LOG_LEVEL=INFO
```

### 3) Chạy server

**Development (với hot-reload):**
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
```

**Production:**
```bash
uv run python production.py
```

> **Truy cập service:**
> - API: http://localhost:8088  
> - Interactive Docs: http://localhost:8088/docs
> - ReDoc: http://localhost:8088/redoc

> Khuyến nghị: nếu ứng dụng web chạy HTTPS, ưu tiên gọi **`http://localhost:8088`** (cùng máy trình duyệt) để giảm va chạm Mixed Content/PNA.

---

## 🔌 API Reference (Enhanced)

> **Authentication**: APIs require header `Authorization: Bearer <WN_API_TOKEN>` when `USE_AUTH=true` (default). Set `USE_AUTH=false` in environment to disable authentication for development.

### Health Check

**GET** `/health`

```json
{ 
  "status": "ok", 
  "service": "WN-PrinterHub", 
  "version": "1.0.0",
  "timestamp": 1695130800.123
}
```

### Thông tin mạng local

**GET** `/api/v1/network/info`

```json
{
  "ok": true,
  "network_info": {
    "hostname": "MacBook-Pro",
    "local_ip": "192.168.1.100",
    "network_base": "192.168.1",
    "suggested_scan_range": "192.168.1.1-254"
  }
}
```

### Tìm máy in trong LAN

**POST** `/api/v1/printers/scan`
**Request**

```json
{
  "network_base": "192.168.1",
  "port": 9100,
  "timeout_ms": 1000
}
```

**Response**

```json
{
  "ok": true,
  "network_base": "192.168.1",
  "port": 9100,
  "printers_found": 2,
  "printers": [
    {
      "host": "192.168.1.50",
      "port": 9100,
      "status": "online",
      "latency_ms": 45
    },
    {
      "host": "192.168.1.51", 
      "port": 9100,
      "status": "online",
      "latency_ms": 67
    }
  ],
  "scan_info": {
    "hostname": "MacBook-Pro",
    "local_ip": "192.168.1.100"
  }
}
```

### Kiểm tra kết nối máy in

**POST** `/api/v1/printers/ping`
**Request**

```json
{ "host": "192.168.1.50", "timeout_ms": 1500 }
```

**POST** `/api/v1/printers/ping`
**Request**

```json
{ "host": "192.168.1.50", "timeout_ms": 1500 }
```

**Response (ok)**

```json
{ 
  "ok": true, 
  "latency_ms": 23, 
  "message": "Connected 192.168.1.50:9100",
  "printer_info": {
    "response_length": 0
  },
  "connection_time": 1695130800.456
}
```

**Response (fail | khác LAN/offline)**

```json
{ 
  "ok": false, 
  "latency_ms": 1500, 
  "message": "Timeout connecting 192.168.1.50:9100",
  "error_type": "timeout"
}
```

### In văn bản (text mode)

**POST** `/api/v1/print`

**Chế độ `text`** – với formatting nâng cao:

```json
{
  "printer": { "host": "192.168.1.50", "timeout_ms": 2000 },
  "mode": "text",
  "text": "QUẦY BẾP\nBÀN T5\nPhở bò x2\nTrà đá x1\n",
  "text_opts": { 
    "encoding": "utf-8", 
    "append_cut": true, 
    "append_newlines": 2 
  }
}
```

**Chế độ `raw_base64`** – ESC/POS tùy chỉnh:

```json
{
  "printer": { "host": "192.168.1.50" },
  "mode": "raw_base64",
  "raw_base64": "G0A...==" 
}
```

### Response (tất cả print endpoints)

```json
{ 
  "ok": true, 
  "bytes_sent": 164, 
  "message": "Printed"
}
```

**POST** `/api/v1/printers/ping`
**Request**

```json
{ "host": "192.168.1.50", "timeout_ms": 1500 }
```

**Response (ok)**

```json
{ "ok": true, "latency_ms": 23, "message": "Connected 192.168.1.50:9100" }
```

**Response (fail | khác LAN/offline)**

```json
{ "ok": false, "latency_ms": 1500, "message": "Timeout connecting 192.168.1.50:9100" }
```

### In

**POST** `/api/v1/print`

**Chế độ `text`** – nhanh cho hoá đơn cơ bản:

```json
{
  "printer": { "host": "192.168.1.50", "timeout_ms": 2000 },
  "mode": "text",
  "text": "QUẦY BẾP\nBÀN T5\nPhở bò x2\nTrà đá x1\n",
  "text_opts": { "encoding": "utf-8", "append_cut": true, "append_newlines": 2 }
}
```

**Chế độ `raw_base64`** – bạn tự dựng bytes ESC/POS (base64) ở ứng dụng:

```json
{
  "printer": { "host": "192.168.1.50" },
  "mode": "raw_base64",
  "raw_base64": "G0A...==" 
}
```

**Response**

```json
{ "ok": true, "bytes_sent": 64, "message": "Printed" }
```

**Mã lỗi thường gặp**
`401/403` (token), `504` (timeout/khác LAN), `502` (lỗi gửi), `422` (validation schema).

---

## 🧪 Tích hợp mẫu (Updated)

### Từ ứng dụng Web (JS) - Enhanced

```js
const HUB = "http://localhost:8088"; // hoặc http://192.168.1.20:8088
const TOKEN = "your_secure_token_here";

// Tìm máy in trong LAN
async function scanPrinters(networkBase = "192.168.1") {
  const r = await fetch(`${HUB}/api/v1/printers/scan`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ 
      network_base: networkBase, 
      port: 9100, 
      timeout_ms: 1000 
    })
  });
  if (!r.ok) throw new Error(`Scan failed: ${r.status}`);
  return r.json();
}

async function pingPrinter(ip) {
  const r = await fetch(`${HUB}/api/v1/printers/ping`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ host: ip, timeout_ms: 1500 })
  });
  if (!r.ok) throw new Error(`Ping failed: ${r.status}`);
  return r.json();
}

async function printText(ip, text) {
  const payload = {
    printer: { host: ip, timeout_ms: 2000 },
    mode: "text",
    text,
    text_opts: { encoding: "utf-8", append_cut: true, append_newlines: 2 }
  };
  const r = await fetch(`${HUB}/api/v1/print`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error(`Print failed: ${r.status}`);
  return r.json();
}

// const printers = await scanPrinters("192.168.1");
// const result = await printText(printers.printers[0].host, "Hello World!");
```

### Từ ứng dụng Python (desktop/backend) - Enhanced

```python
import requests
HUB = "http://localhost:8088"
TOKEN = "your_secure_token_here"
HEAD = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def scan_printers(network_base="192.168.1"):
    """Tìm máy in trong LAN."""
    return requests.post(f"{HUB}/api/v1/printers/scan", 
        json={"network_base": network_base, "port": 9100, "timeout_ms": 1000}, 
        headers=HEAD).json()

def ping(ip):
    return requests.post(f"{HUB}/api/v1/printers/ping", 
        json={"host": ip, "timeout_ms": 1500}, headers=HEAD).json()

def print_text(ip, content):
    payload = {
        "printer": {"host": ip, "timeout_ms": 2000},
        "mode": "text",
        "text": content,
        "text_opts": {"encoding": "utf-8", "append_cut": True, "append_newlines": 2}
    }
    return requests.post(f"{HUB}/api/v1/print", json=payload, headers=HEAD).json()

# Sử dụng:
# printers = scan_printers("192.168.1")
# if printers["printers_found"] > 0:
#     printer_ip = printers["printers"][0]["host"]
#     result = print_text(printer_ip, "Hello from Python!")
```

---

## 🌐 CORS & Private Network Access

✅ **Đã được cấu hình tự động** trong implementation.

Khi **web app (HTTPS)** gọi tới **dịch vụ local (HTTP)**, PrinterHub tự động thêm:
* **CORS headers** theo `WN_ALLOWED_ORIGINS` 
* **PNA header**: `Access-Control-Allow-Private-Network: true`

---

## 🚀 Production Deployment

### Linux với systemd
```bash
# Copy service file và setup
sudo cp wn-printerhub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wn-printerhub
sudo systemctl start wn-printerhub

# Kiểm tra status
sudo systemctl status wn-printerhub
sudo journalctl -u wn-printerhub -f
```

### Manual Production Run
```bash
uv run python production.py
```

📖 **[Xem hướng dẫn deployment chi tiết](INSTALLATION.md)**

---

## 🧪 Testing & Development

```bash
# Chạy tests
uv run pytest

# Test với coverage
uv run pytest --cov=app

# Format code
uv run black app/ tests/
uv run ruff check app/ tests/
```

---

## 🔒 Bảo mật & Best Practices

* ✅ **Token authentication** đã được implement
* ✅ **Input validation** cho tất cả endpoints  
* ✅ **CORS restrictions** theo domain cấu hình
* ✅ **Request logging** cho audit trail
* 🔧 **Khuyến nghị**:
  * Dùng token dài (>32 characters) trong production
  * Giới hạn `WN_ALLOWED_ORIGINS` đúng domain ứng dụng
  * Chạy trong LAN nội bộ, không expose ra internet
  * Enable firewall cho outbound TCP tới máy in (port 9100)

---

## 📁 Project Structure (Implemented)

```
WN-PrinterHub/
├── app/
│   ├── main.py              # FastAPI application với tất cả endpoints
│   ├── config.py            # Configuration management với validation
│   ├── escpos_utils.py      # ESC/POS utilities & text formatting  
│   └── network_utils.py     # Network scanning & enhanced ping
├── tests/
│   └── test_main.py         # Test suite với pytest
├── .env.example             # Environment template
├── pyproject.toml           # Dependencies với uv
├── start.sh / start.bat     # Cross-platform startup scripts
├── production.py            # Production deployment script
├── wn-printerhub.service    # Systemd service file
├── INSTALLATION.md          # Chi tiết setup & deployment
└── ENHANCEMENTS.md          # Đề xuất nâng cấp tương lai
```

---

## 🏆 Implementation Status

✅ **Core Features**: Hoàn thành 100% theo spec gốc  
✅ **Enhanced APIs**: Network scanning, ESC/POS printing, network info  
✅ **Production Ready**: Logging, systemd, startup scripts  
✅ **Developer Tools**: Tests, documentation, type hints  
✅ **Security**: Authentication, validation, CORS  

**🎯 Sẵn sàng sản xuất** - Có thể deploy ngay cho các ứng dụng White Neuron.

---

## 🧱 FastAPI Implementation (Rút gọn - Tham khảo)

> **Lưu ý**: Code đầy đủ đã được implement trong `app/main.py` với tất cả tính năng nâng cao.

```python
# app/main.py - Core structure (simplified)
from fastapi import FastAPI, Depends, HTTPException
from .config import config
from .escpos_utils import create_simple_text
from .network_utils import scan_network_for_printers, enhanced_ping

app = FastAPI(title="WN-PrinterHub", version="1.0.0")

# Middleware: CORS, PNA, Logging đã được cấu hình

@app.get("/health")
async def health(): 
    return {"status": "ok", "service": "WN-PrinterHub", "version": "1.0.0"}

@app.post("/api/v1/printers/ping") 
async def ping_printer(body: PrinterTarget, _=Depends(authenticate)):
    return await enhanced_ping(body.host, config.printer_default_port, body.timeout_ms)

@app.post("/api/v1/printers/scan")
async def scan_printers(body: NetworkScanRequest, _=Depends(authenticate)):
    printers = await scan_network_for_printers(body.network_base, body.port, body.timeout_ms)
    return {"ok": True, "printers_found": len(printers), "printers": printers}

@app.post("/api/v1/print")
async def print_document(request: PrintRequest, _=Depends(authenticate)):
    # Text/Raw printing với enhanced ESC/POS processing
```

---

## 🧭 Vận hành & Troubleshooting

### Kiểm tra trạng thái service
```bash
# Development
curl http://localhost:8088/health

# Production với systemd  
systemctl status wn-printerhub
journalctl -u wn-printerhub -f
```

### Debug thường gặp
1. **Connection timeout**: Kiểm tra IP máy in và kết nối LAN
2. **Authentication error**: Verify token trong `.env` và client code
3. **CORS error**: Thêm domain vào `WN_ALLOWED_ORIGINS`
4. **Port conflict**: Đổi `WN_PORT` trong `.env`

📖 **[Xem troubleshooting guide đầy đủ](INSTALLATION.md#troubleshooting)**

---

## 🗺️ Roadmap & Enhancements

🎯 **Current Status**: ✅ Production-ready với tất cả core features  
🚀 **Future Plans**: Xem [ENHANCEMENTS.md](ENHANCEMENTS.md) cho roadmap chi tiết

**Tính năng đề xuất**:
- Print job queue với retry logic
- Jinja2 templates cho receipt formatting  
- QR code & barcode printing
- CUPS integration cho system printers
- WebSocket status updates
- Admin dashboard

---

## 📞 Support & Documentation

- 📖 **Setup Guide**: [INSTALLATION.md](INSTALLATION.md)
- 🔮 **Future Features**: [ENHANCEMENTS.md](ENHANCEMENTS.md)  
- 🌐 **Interactive API Docs**: http://localhost:8088/docs (khi service chạy)
- 🧪 **Test Suite**: `uv run pytest` để chạy tests
- 🏗️ **Code Structure**: Well-documented trong từng module

---

## 📜 License

MIT

---

**🎉 WN-PrinterHub đã sẵn sàng production!**

*Dù ứng dụng nào của White Neuron gọi tên, chỉ cần chung mạng—**WN-PrinterHub** sẽ đưa chữ từ màn hình đến giấy, nhanh như một nhịp gật đầu.*

**✅ Fully Implemented** • **🚀 Ready to Deploy** • **📈 Enhanced with Advanced Features**
