# WN-PrinterHub

*“Một nhịp cầu mảnh giữa ứng dụng và máy in—
chung LAN là chạm, gọi là in.”*

**WN-PrinterHub** là dịch vụ **Python + FastAPI** chạy **local trong LAN**, đóng vai trò **connector in ấn** cho *mọi ứng dụng nội bộ của White Neuron* (web/desktop/backend). Ứng dụng của bạn chỉ cần gọi HTTP tới **host local** của PrinterHub để:

* **/printers/ping**: kiểm tra khả dụng máy in trong LAN.
* **/print**: gửi lệnh in ngay lập tức.

> Không cùng LAN → không thể kết nối máy in → trả lỗi rõ ràng để UI thông báo.
> Cùng LAN → xác nhận kết nối, in bất cứ lúc nào người dùng thao tác.

---

## ✨ Tính năng

* **Local-first**: chạy tại quầy/PC trong LAN, không phụ thuộc cloud để chạm máy in.
* **API tối giản**: chỉ cần **IP máy in** (không cần cổng).
* **Hai chế độ in**:

  * `text`: chuyển chuỗi → bytes ESC/POS cơ bản (init, newline, cắt giấy).
  * `raw_base64`: gửi **bytes ESC/POS** (đã base64) do ứng dụng tạo sẵn.
* **Bảo mật**: Bearer Token; giới hạn CORS theo domain ứng dụng.
* **Quản lý môi trường**: dùng **`uv` (Astral)**—nhanh, tái lập, gọn gàng.
* **Healthcheck**: `/health` để giám sát sống/chết.

---

## 🧩 Mô hình mạng (tổng quát)

```
Ứng dụng WN (Web/Desktop/Backend)
            │  HTTP fetch (CORS + Private Network Access)
            ▼
WN-PrinterHub (FastAPI, chạy trong LAN)
  ├─ /api/v1/printers/ping   # kiểm tra IP máy in (JetDirect mặc định)
  └─ /api/v1/print           # in ESC/POS (text/raw_base64)
            ▼
Máy in LAN (JetDirect/RAW 9100)
```

* PrinterHub **dùng cổng máy in mặc định 9100** (RAW/JetDirect). Có thể đổi bằng biến môi trường; payload **không cần** cổng.

---

## ⚙️ Cài đặt & chạy với `uv` (không Docker)

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
uv add fastapi "uvicorn[standard]" pydantic
```

### 2) Biến môi trường

```bash
# Token API
export WN_API_TOKEN="ĐỔI_THÀNH_CHUỖI_BẢO_MẬT_DÀI"

# Cho phép CORS từ domain ứng dụng (nhiều domain ngăn cách bằng dấu phẩy)
export WN_ALLOWED_ORIGINS="https://app.whiteneuron.com,https://another-app.whiteneuron.com"

# Cổng JetDirect mặc định (máy in) – mặc định 9100
export WN_PRINTER_DEFAULT_PORT=9100
```

### 3) Chạy server

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
```

> Khuyến nghị: nếu ứng dụng web chạy HTTPS, ưu tiên gọi **`http://localhost:8088`** (cùng máy trình duyệt) để giảm va chạm Mixed Content/PNA.

---

## 🔌 API Reference (tối giản – chỉ cần IP)

> Các API ghi yêu cầu header `Authorization: Bearer <WN_API_TOKEN>`.

### Health

**GET** `/health`

```json
{ "status": "ok" }
```

### Kiểm tra kết nối máy in

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
`401/403` (token), `504` (timeout/khác LAN), `502` (lỗi gửi), `422` (schema).

---

## 🌐 CORS & Private Network Access (PNA)

Khi **web app (HTTPS)** gọi tới **dịch vụ local (HTTP, IP private)**, trình duyệt cần:

* **CORS** hợp lệ (`Access-Control-Allow-Origin` đúng domain app).
* **PNA header**: `Access-Control-Allow-Private-Network: true`.

Trong FastAPI, thêm:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("WN_ALLOWED_ORIGINS","*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_pna_header(request, call_next):
    resp = await call_next(request)
    resp.headers["Access-Control-Allow-Private-Network"] = "true"
    return resp
```

---

## 🧪 Tích hợp mẫu

### Từ ứng dụng Web (JS)

```js
const HUB = "http://localhost:8088"; // hoặc http://192.168.1.20:8088
const TOKEN = "ĐỔI_THÀNH_CHUỖI_BẢO_MẬT_DÀI";

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
```

### Từ ứng dụng Python (desktop/backend)

```python
import requests
HUB = "http://localhost:8088"
TOKEN = "ĐỔI_THÀNH_CHUỖI_BẢO_MẬT_DÀI"
HEAD = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def ping(ip):
  return requests.post(f"{HUB}/api/v1/printers/ping", json={"host": ip, "timeout_ms": 1500}, headers=HEAD).json()

def print_text(ip, content):
  payload = {
    "printer": {"host": ip, "timeout_ms": 2000},
    "mode": "text",
    "text": content,
    "text_opts": {"encoding": "utf-8", "append_cut": True, "append_newlines": 2}
  }
  return requests.post(f"{HUB}/api/v1/print", json=payload, headers=HEAD).json()
```

---

## 🔒 Gợi ý bảo mật

* Dùng **token dài**; chỉ expose service trong **LAN nội bộ**.
* Giới hạn `WN_ALLOWED_ORIGINS` đúng domain ứng dụng.
* OS firewall: cho phép outbound TCP tới **IP máy in:9100**.

---

## 🧱 FastAPI skeleton (rút gọn)

```python
# app/main.py
import asyncio, base64, contextlib, os, time
from typing import Literal, Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

API_TOKEN = os.getenv("WN_API_TOKEN", "CHANGE_ME")
DEFAULT_PORT = int(os.getenv("WN_PRINTER_DEFAULT_PORT", "9100"))
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("WN_ALLOWED_ORIGINS","*").split(",") if o.strip()]

app = FastAPI(title="WN-PrinterHub", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_pna_header(request, call_next):
    resp = await call_next(request)
    resp.headers["Access-Control-Allow-Private-Network"] = "true"
    return resp

class PrinterTarget(BaseModel):
    host: str
    timeout_ms: int = 1500

class PrintTextOptions(BaseModel):
    encoding: str = "utf-8"
    append_cut: bool = True
    append_newlines: int = Field(2, ge=0, le=6)

class PrintRequest(BaseModel):
    printer: PrinterTarget
    mode: Literal["text", "raw_base64"]
    text: Optional[str] = None
    raw_base64: Optional[str] = None
    text_opts: PrintTextOptions = PrintTextOptions()
    @field_validator("text") @classmethod
    def _v_text(cls, v, info):
        if info.data.get("mode") == "text" and not v: raise ValueError("text is required when mode=text")
        return v
    @field_validator("raw_base64") @classmethod
    def _v_raw(cls, v, info):
        if info.data.get("mode") == "raw_base64" and not v: raise ValueError("raw_base64 is required when mode=raw_base64")
        return v

async def auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing Bearer token")
    if authorization.split(" ", 1)[1].strip() != API_TOKEN:
        raise HTTPException(403, "Invalid token")

async def tcp_connect(host: str, timeout_ms: int):
    return await asyncio.wait_for(asyncio.open_connection(host, DEFAULT_PORT), timeout=timeout_ms/1000)

async def tcp_send(host: str, data: bytes, timeout_ms: int) -> int:
    r, w = await tcp_connect(host, timeout_ms)
    try: w.write(data); await w.drain(); return len(data)
    finally:
        w.close(); 
        with contextlib.suppress(Exception): await w.wait_closed()

def escpos_from_text(text: str, enc: str, nl: int, cut: bool) -> bytes:
    out = bytearray(b"\x1b@"); out.extend(text.encode(enc, errors="replace")); out.extend(b"\n"*nl)
    if cut: out.extend(b"\x1dV\x00"); return bytes(out)

@app.get("/health")
async def health(): return {"status":"ok"}

@app.post("/api/v1/printers/ping")
async def ping(body: PrinterTarget, _=Depends(auth)):
    t0 = time.perf_counter()
    try: 
        r,w = await tcp_connect(body.host, body.timeout_ms); w.close()
        with contextlib.suppress(Exception): await w.wait_closed()
        dt = int((time.perf_counter()-t0)*1000)
        return {"ok": True, "latency_ms": dt, "message": f"Connected {body.host}:{DEFAULT_PORT}"}
    except asyncio.TimeoutError:
        dt = int((time.perf_counter()-t0)*1000)
        return {"ok": False, "latency_ms": dt, "message": f"Timeout connecting {body.host}:{DEFAULT_PORT}"}
    except Exception as e:
        dt = int((time.perf_counter()-t0)*1000)
        return {"ok": False, "latency_ms": dt, "message": f"Error: {e}"}

@app.post("/api/v1/print")
async def print_now(req: PrintRequest, _=Depends(auth)):
    if req.mode == "text":
        data = escpos_from_text(req.text or "", req.text_opts.encoding, req.text_opts.append_newlines, req.text_opts.append_cut)
    else:
        try: data = base64.b64decode(req.raw_base64 or "", validate=True)
        except Exception: raise HTTPException(422, "raw_base64 invalid")
    try:
        n = await tcp_send(req.printer.host, data, req.printer.timeout_ms)
        return {"ok": True, "bytes_sent": n, "message": "Printed"}
    except asyncio.TimeoutError:
        raise HTTPException(504, f"Timeout sending to {req.printer.host}:{DEFAULT_PORT}")
    except Exception as e:
        raise HTTPException(502, f"Print error: {e}")
```

---

## 🧭 Vận hành

* **Linux systemd**: chạy nền ổn định (service tự khởi động).
* **Windows Task Scheduler**: chạy script khởi động PrinterHub khi logon/boot.
* **Firewall**: cho phép outbound TCP từ PrinterHub → IP máy in:9100.

---

## 🗺️ Roadmap

* Hỗ trợ **queue + retry + idempotency** (`job_id`).
* Templates Jinja2 (định dạng hoá đơn) & helpers ESC/POS (ảnh/QR/barcode).
* **CUPS/Win32 backends** (tùy chọn) bên cạnh JetDirect.
* `/metrics` (Prometheus) + WebSocket cập nhật trạng thái.

---

## 📜 License

MIT

---

*Dù ứng dụng nào của White Neuron gọi tên, chỉ cần chung mạng—**WN-PrinterHub** sẽ đưa chữ từ màn hình đến giấy, nhanh như một nhịp gật đầu.*
