## WN-DineHub-Printer

### Ý nghĩa

Đây là công cụ do White Neuron phát triển để **kết nối hệ thống quản lý nhà hàng WN-DineHub chạy trên máy chủ ngoài (cloud/server)** với **máy in cục bộ (local printer)** ngay tại nhà hàng. Nhờ đó, khi nhân viên tạo order, hóa đơn hoặc phiếu bếp trên DineHub, dữ liệu sẽ được gửi tức thì từ server về máy in tại chỗ, bảo đảm tốc độ **real-time** và sự liền mạch trong vận hành.

### Cách hoạt động

1. **Máy chủ ngoài (Server WN-DineHub)**
   Lưu trữ dữ liệu, đồng bộ order, hóa đơn, báo cáo.
2. **WN-DineHub-Printer (Trung gian kết nối)**
   Được cài đặt trên máy tính hoặc thiết bị trong LAN tại nhà hàng, nhận tín hiệu từ server.
3. **Máy in cục bộ**
   In hóa đơn/bill/phiếu order ngay lập tức mà không cần phụ thuộc trực tiếp vào internet toàn cầu.

### Lợi ích

* **Tốc độ**: In tức thì trong mạng LAN → không bị chậm trễ như khi in qua cloud thuần túy.
* **An toàn**: Nếu internet ngoài gián đoạn, hệ thống vẫn có thể in trong mạng nội bộ.
* **Linh hoạt**: Có thể tùy biến kết nối nhiều máy in (quầy thu ngân, bếp, bar…).
* **Kết nối 2 thế giới**: Dữ liệu quản lý tập trung trên server, nhưng in vẫn gắn liền với không gian thực tại.
