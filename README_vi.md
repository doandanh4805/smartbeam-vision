# 📌 Giới thiệu tổng quan 

Dự án này là nguyên mẫu hệ thống đèn pha thông minh hoạt động dựa trên sự kết hợp giữa **Thị giác máy tính (Computer Vision/AI)** và **Hệ thống nhúng (Embedded System)**. 

Hệ thống theo dõi luồng video trực tiếp từ camera, sử dụng mạng nơ-ron **YOLOv8** để nhận diện phương tiện và người đi bộ theo thời gian thực. Tọa độ của vật thể sẽ được nội suy và truyền qua cổng Serial UART xuống vi điều khiển **ESP32**. Tại đây, ESP32 sẽ điều khiển các bóng LED Matrix tạo ra "vùng tối tự động" che khuất mắt người đối diện, đồng thời điều khiển cơ cấu Servo liếc góc chiếu để bám đường cong.

## ✨ Các tính năng nổi bật:
- **Matrix Dark Zone:** Tự động tính toán và tắt/giảm sáng cục bộ các mắt LED chiếu trực tiếp vào phương tiện đối diện (Chống chói/Anti-glare).
- **Auto City/Highway Mode:** Tự động phân tích cường độ sáng môi trường để điều chỉnh góc cụp/xòe và công suất LED.
- **Curve Tracking (AFS):** Ứng dụng biến đổi Hough (Hough Transform) để nhận diện vạch kẻ đường, tự động liếc Servo soi sáng góc khuất khi vào cua.
- **Real-time Processing:** Kiến trúc đa luồng (Multi-threading) và xử lý bất đồng bộ (Non-blocking) đảm bảo độ trễ thấp nhất.

---

### 🛠 Kiến trúc Phần cứng (Hardware Architecture)

Hệ thống được thiết kế chia làm 2 phân hệ Master (PC) và Slave (ESP32):

| STT | Thành phần | Chi tiết |
| :--- | :--- | :--- |
| 1 | **Vi điều khiển** | ESP32 (ESP-WROOM-32) - *Đóng vai trò Slave* |
| 2 | **Cơ cấu liếc (Pan-Tilt)**| 4x Servo MG90S (Bánh răng kim loại) |
| 3 | **Ma trận ánh sáng** | 8x LED High Power 3W (Kèm chóa 30° và ống PVC thu sáng) |
| 4 | **Mạch công suất LED** | 8x MOSFET FR120N (Logic-level) |
| 5 | **Mạch quản lý nguồn** | XL4015 DC-DC 5A (CC/CV) |
| 6 | **Nguồn cấp** | Khối Pin Lithium 8.4V |
<img width="742" height="415" alt="Screenshot 2026-05-07 151841" src="https://github.com/user-attachments/assets/689e5491-91c2-4282-a8e3-85b840a118f9" />

