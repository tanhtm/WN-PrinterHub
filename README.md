# WN-DineHub-Printer

*“Một nhịp cầu nhỏ giữa mây và quầy bếp—
đơn in rơi về bếp, nóng hổi như món vừa ra lò.”*

**WN-DineHub-Printer** là một công cụ **Python + FastAPI** nhẹ, kết nối hệ thống **WN-DineHub (cloud/server)** với **máy in cục bộ (LAN)** tại nhà hàng, cho phép in **real-time** order, hóa đơn và phiếu bếp — ngay cả khi internet chập chờn.

---

## ✨ Tính năng nổi bật

* **In tức thì** từ server DineHub → máy in LAN (ESC/POS, CUPS, Windows).
* **Hàng đợi an toàn** với retry, backoff và idempotency theo `job_id`.
* **Tùy biến hóa đơn** bằng Jinja2 template.
* **Bảo mật**: Bearer Token + HMAC signature tùy chọn.
* **Theo dõi dễ dàng**: `/health` kiểm tra sống/chết, `/metrics` xuất số liệu Prometheus.

---

## 🧩 Kiến trúc

```
Server DineHub (Cloud)
        │  HTTPS (Webhook/API)
        ▼
WN-DineHub-Printer (FastAPI)
  ├─ Xác thực / HMAC verify
  ├─ Hàng đợi job (memory/Redis)
  ├─ Template hóa đơn (Jinja2)
  ├─ Backends in:
  │    • ESC/POS (TCP)
  │    • CUPS (Linux/macOS)
  │    • Win32 (Windows)
  └─ WebSocket: cập nhật trạng thái
        ▼
 Máy in nội bộ (LAN)
```

---

## 🚀 Khởi chạy nhanh

### 1) Yêu cầu

* Python 3.10+
* Redis (tùy chọn, nếu muốn hàng đợi bền vững)
* Máy in cục bộ (ESC/POS, CUPS hoặc Windows)

### 2) Cài đặt

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

### 3) Cấu hình

Tạo file `config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8088
  base_path: /api/v1
  api_token: "DOI_THANH_CHUOI_BAO_MAT"
  hmac_secret: "TÙY_CHỌN"   
  allow_origins: ["*"]

queue:
  driver: "memory"     
  redis_url: "redis://localhost:6379/0"
  max_retries: 3
  backoff_seconds: 2   

printing:
  default_backend: "escpos"    
  escpos:
    host: "192.168.1.50"
    port: 9100
  cups:
    printer_name: "Kitchen_Printer"
  win32:
    printer_name: "POS-58"

templates:
  directory: "./templates"
  default: "receipt.j2"
```

### 4) Chạy

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
```

---

## 🧪 Ví dụ gọi API (tạo job in)

```bash
curl -X POST http://localhost:8088/api/v1/print-jobs \
  -H "Authorization: Bearer DOI_THANH_CHUOI_BAO_MAT" \
  -H "Content-Type: application/json" \
  -d '{
        "job_id": "order_20384",
        "type": "kitchen_ticket",
        "template": "kitchen_ticket.j2",
        "data": {
          "order_no": "DH-00123",
          "table": "T5",
          "items": [{"name":"Phở bò", "qty":2}, {"name":"Trà đá", "qty":1}],
          "note": "Không hành"
        },
        "printer": { "backend":"escpos", "host":"192.168.1.50", "port":9100 }
      }'
```

Kết quả:

```json
{
  "job_id": "order_20384",
  "status": "queued",
  "queued_at": "2025-09-19T01:23:45Z"
}
```

---

## 🧠 API chính

* `GET /health` → kiểm tra sống/chết.
* `GET /metrics` → số liệu Prometheus.
* `POST /printers/register` → đăng ký máy in.
* `GET /printers` → liệt kê máy in.
* `POST /print-jobs` → tạo job in.
* `GET /print-jobs/{job_id}` → lấy trạng thái job.
* `POST /print-jobs/{job_id}/cancel` → hủy job đang chờ.
* `POST /webhooks/dinehub` → server DineHub gửi trực tiếp yêu cầu in.
* `GET /ws` (WebSocket) → nhận cập nhật real-time (job đang in, đã in…).

---

## 🔐 Bảo mật

* **Bearer Token**: mọi API quan trọng đều yêu cầu token.
* **HMAC (khuyên dùng)**: kiểm chứng dữ liệu từ server DineHub.
* **Idempotency**: job chỉ in 1 lần, tránh trùng lặp.

---

## 🖨️ Hỗ trợ in

* **ESC/POS (TCP/IP)**
* **CUPS (Linux/macOS)**
* **Win32 (Windows Spooler)**

---

## 📄 Template mẫu (`templates/receipt.j2`)

```jinja2
{{ store.name }}
Order: {{ order_no }}
Time : {{ printed_at }}

{% for it in items -%}
{{ ("%s x%s" % (it.name, it.qty)).ljust(20) }} {{ ("%.0f" % it.price).rjust(8) }}
{%- endfor %}

Total: {{ ("%.0f" % total).rjust(8) }}
Xin cảm ơn!
```

---

## 📦 Triển khai

* **Docker**: build image, mount `config.yaml` + `templates/`.
* **Systemd**: chạy uvicorn như service.
* **Reverse Proxy**: NGINX/Caddy; có thể dùng Cloudflare Tunnel.

---

## 🗺️ Roadmap

* In QR/barcode cho ESC/POS.
* Hàng đợi ưu tiên bằng Redis.
* Quy tắc định tuyến máy in theo chi nhánh.
* API preview template (xuất PDF/PNG).

---

## 📜 License

MIT
