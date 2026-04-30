import cv2
import time
import threading
import queue
import numpy as np
from ultralytics import YOLO
from tracker import LightMatrixMapper
from serial_com import SerialManager

running = True 
frame_queue = queue.Queue(maxsize=1) 
cmd_queue = queue.Queue(maxsize=1)   

def camera_thread(camera_index, width, height):
    global running
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print("[*] Luồng Camera đã khởi chạy...")
    while running:
        success, frame = cap.read()
        if success:
            if frame_queue.full():
                try: frame_queue.get_nowait()
                except queue.Empty: pass
            frame_queue.put(frame)
        else:
            time.sleep(0.01) 
    cap.release()
    print("[*] Luồng Camera đã đóng.")

def serial_thread(port, baud_rate):
    global running
    serial_mgr = SerialManager(port=port, baud_rate=baud_rate)
    connected = serial_mgr.connect()
    
    if not connected:
        print("[!] Luồng Serial: Không tìm thấy phần cứng, chạy mô phỏng.")
    else:
        print("[*] Luồng Serial đã sẵn sàng bắn lệnh...")
        
    while running:
        try:
            l_leds, r_leds, servos = cmd_queue.get(timeout=0.05) 
            if connected:
                serial_mgr.send_data(l_leds, r_leds, servos)
                time.sleep(0.05)
        except queue.Empty:
            pass
            
    if connected:
        serial_mgr.send_data([0]*4, [0]*4, [90,90,90,90])
        serial_mgr.close()
    print("[*] Luồng Serial đã đóng.")

def main():
    global running
    print("[*] Đang tải mô hình YOLOv8...")
    model = YOLO("yolov8n.pt")  
    TARGET_CLASSES = [0, 2, 3, 5, 7]
    
    W, H = 1280, 720
    mapper = LightMatrixMapper(frame_width=W, frame_height=H)
    
    # KÍCH HOẠT CÁC LUỒNG
    cam_worker = threading.Thread(target=camera_thread, args=(0, W, H), daemon=True) # Nhớ đổi 1 thành 0 nếu dùng cam thường
    serial_worker = threading.Thread(target=serial_thread, args=("COM12", 115200), daemon=True)
    
    cam_worker.start()
    serial_worker.start()
    print("[*] HỆ THỐNG SẴN SÀNG! Nhấn 'q' để thoát, 'SPACE' để Đá pha.")
    
    while running:
        try:
            frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            continue
            
        # --- 1. TÍNH TOÁN MÔI TRƯỜNG TRƯỚC ---
        env_y, env_x = mapper.update_environment(frame)
            
        # --- 2. CHẠY AI NHẬN DIỆN XE ---
        results = model.predict(source=frame, classes=TARGET_CLASSES, conf=0.3, verbose=False)
        boxes_data = [box.xywh[0].cpu().numpy() for r in results for box in r.boxes] if results else []
        
        for b in boxes_data:
            x_c, y_c, w, h = b
            cv2.rectangle(frame, (int(x_c-w/2), int(y_c-h/2)), (int(x_c+w/2), int(y_c+h/2)), (0,0,255), 2)

        # --- 3. ĐẨY DATA XUỐNG ESP32 ---
        l_leds, r_leds, servos = mapper.calculate(boxes_data, base_y=env_y, base_x=env_x)
        
        if cmd_queue.full():
            try: cmd_queue.get_nowait()
            except queue.Empty: pass
        cmd_queue.put((l_leds, r_leds, servos))

        # --- 4. XỬ LÝ PHÍM BẤM ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): 
            print("\n[!] >>> ĐÁ PHA <<<")
            if cmd_queue.full(): cmd_queue.get_nowait()
            cmd_queue.put(([200]*4, [200]*4, [90,90,90,90]))
            time.sleep(0.1) 
            if cmd_queue.full(): cmd_queue.get_nowait()
            cmd_queue.put(([0]*4, [0]*4, [90,90,90,90]))
        elif key == ord('q'): 
            running = False 
            break

        # --- 5. VẼ GIAO DIỆN (HUD) CHUYÊN NGHIỆP ---
        # Vẽ khung đen mờ để chữ dễ đọc
        cv2.rectangle(frame, (10, 10), (550, 140), (0, 0, 0), -1)
        
        cv2.putText(frame, f"MODE : {mapper.current_mode}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"CURVE: {mapper.curve_status}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, f"L_PWM: {l_leds}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"R_PWM: {r_leds}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow("ADB Matrix System - UTC NCKH", frame)

    print("[*] Đang đợi các luồng đóng an toàn...")
    cam_worker.join(timeout=2)
    serial_worker.join(timeout=2)
    cv2.destroyAllWindows()
    print("[*] Thoát chương trình thành công!")

if __name__ == "__main__":
    main()