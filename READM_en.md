# Smart Adaptive Headlight System

## 📌 Overview

This project is a prototype of an intelligent automotive headlight system developed through the integration of **Computer Vision (AI)** and **Embedded Systems**.

The system monitors a live video stream from a camera and uses the **YOLOv8 neural network** to detect vehicles and pedestrians in real time. The detected object coordinates are interpolated and transmitted via **Serial UART** to an **ESP32 microcontroller**. The ESP32 then controls an **LED Matrix** to generate an automatic **“dark zone”** that blocks direct glare toward oncoming drivers, while also controlling **Servo mechanisms** to dynamically adjust the beam direction for curve tracking.

---

## ✨ Key Features

### 🔹 Matrix Dark Zone
Automatically calculates and turns off/reduces the brightness of specific LED segments that directly illuminate oncoming vehicles (**Anti-glare system**).

### 🔹 Auto City/Highway Mode
Automatically analyzes ambient light intensity to adjust beam angle and LED power output depending on driving conditions.

### 🔹 Curve Tracking (AFS)
Uses **Hough Transform** to detect road lane markings and automatically steers the Servo mechanism to illuminate blind corners while turning.

### 🔹 Real-time Processing
A **multi-threading** and **non-blocking** architecture ensures the lowest possible system latency.

---

# 🛠 Hardware Architecture

The system is designed with two main subsystems:

- **Master:** PC (AI Processing)
- **Slave:** ESP32 (Hardware Control)

| No. | Component | Details |
|---|---|---|
| 1 | Microcontroller | ESP32 (ESP-WROOM-32) – Acts as Slave |
| 2 | Pan-Tilt Mechanism | 4x MG90S Servo Motors (Metal Gear) |
| 3 | Lighting Matrix | 8x High Power 3W LEDs (with 30° reflector and PVC light tube) |
| 4 | LED Driver Circuit | 8x FR120N Logic-level MOSFETs |
| 5 | Power Management Circuit | XL4015 DC-DC 5A (CC/CV) |
| 6 | Power Supply | 8.4V Lithium Battery Pack |

---

# ⚙️ System Workflow

1. Camera captures live road video.
2. YOLOv8 detects vehicles and pedestrians in real time.
3. Object coordinates are processed and interpolated.
4. Data is transmitted to ESP32 via UART.
5. ESP32 controls:
   - LED Matrix dark zones
   - Servo steering mechanism
   - Adaptive brightness modes
6. Headlight beam dynamically adapts to the environment and road conditions.

---

# 🧠 Technologies Used

- Python
- YOLOv8
- OpenCV
- ESP32
- UART Communication
- Computer Vision
- Embedded Systems
- Multi-threading
- Hough Transform

---

# 🚗 Future Improvements

- CAN Bus integration
- GPS-based adaptive lighting
- Rain/Fog detection
- Full automotive-grade PCB design
- TensorRT acceleration for faster AI inference

---

# 📷 Demo

> Add project images, diagrams, or demo GIFs here.

```md
<img width="742" height="415" alt="Screenshot 2026-05-07 151841" src="https://github.com/user-attachments/assets/c9ef4072-dc6f-49c3-8250-6eef8d0f34fd" />

```

https://github.com/user-attachments/assets/f216be23-4dfb-45f5-9575-32a5d9b4850d

---
<img width="2568" height="1444" alt="z7798202596686_1b1c3c276adaa3b4fb6e03bf69cc63ba" src="https://github.com/user-attachments/assets/2760848b-5c4b-4725-87b8-3d9d80b6be7a" /><img width="2568" height="1444" alt="z7798202589724_672cd23e7262deae4e3e858b3f7f95ba" src="https://github.com/user-attachments/assets/5c5434b3-85e3-4a3f-807a-5aba5f5564f6" />


# 📄 License

This project is developed for research and educational purposes.
