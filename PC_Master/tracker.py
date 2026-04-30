import cv2
import numpy as np

class LightMatrixMapper:
    def __init__(self, frame_width=1280, frame_height=720):
        self.w = frame_width
        self.h = frame_height
        self.MAX_PWM = 200 # Biến này giờ sẽ tự động thay đổi theo môi trường
        
        self.last_l_leds = [200] * 4
        self.last_r_leds = [200] * 4
        self.last_servos = [90, 90, 90, 90]
        self.lost_frames = 0 
        
        # Biến trạng thái để hiển thị lên màn hình
        self.current_mode = "HIGHWAY"
        self.curve_status = "STRAIGHT"

    def update_environment(self, frame):
        """Hàm phân tích độ sáng và vạch kẻ đường (Gọi trước khi chạy YOLO)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # --- TÍNH NĂNG 1: AUTO CITY / HIGHWAY (Dựa vào Histogram) ---
        avg_brightness = np.mean(gray)
        if avg_brightness > 90: # Cảnh nhiều ánh sáng -> Đường thành phố
            self.MAX_PWM = 80   # Giảm công suất tối đa xuống cho đỡ chói
            base_y = 75         # Tự động cụp pha xuống
            self.current_mode = f"CITY (Low Beam - Brightness: {int(avg_brightness)})"
        else:                   # Cảnh tối -> Cao tốc/Đường nông thôn
            self.MAX_PWM = 200  # Mở max 200
            base_y = 90         # Giương pha chiếu xa
            self.current_mode = f"HIGHWAY (High Beam - Brightness: {int(avg_brightness)})"

        # --- TÍNH NĂNG 2: ĐÈN LIẾC THEO ĐƯỜNG CONG (Hough Transform) ---
        h, w = gray.shape
        roi = gray[int(h*0.5):h, :] # Lấy nửa dưới bức ảnh (Mặt đường)
        
        blurred = cv2.GaussianBlur(roi, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=40, maxLineGap=20)
        
        pan_offset = 0
        self.curve_status = "STRAIGHT"
        
        if lines is not None:
            left_lines = []
            right_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x2 == x1: continue
                slope = (y2 - y1) / (x2 - x1)
                if slope < -0.3: left_lines.append(slope)
                elif slope > 0.3: right_lines.append(slope)
            
            # Logic: Nếu phát hiện số lượng vạch kẻ bên nào áp đảo -> Đường cong về bên đó
            if len(left_lines) > len(right_lines) * 2: 
                pan_offset = -15
                self.curve_status = "CURVE LEFT (-15 deg)"
            elif len(right_lines) > len(left_lines) * 2:
                pan_offset = 15
                self.curve_status = "CURVE RIGHT (+15 deg)"
                
        base_x = 90 + pan_offset
        return base_y, base_x

    def calculate(self, boxes, base_y=90, base_x=90):
        # Chống nháy AI
        if len(boxes) == 0:
            self.lost_frames += 1
            if self.lost_frames < 15:
                return self.last_l_leds, self.last_r_leds, self.last_servos
            else:
                self.last_l_leds = [self.MAX_PWM] * 4
                self.last_r_leds = [self.MAX_PWM] * 4
                self.last_servos = [base_x, base_y, base_x, base_y] # Trả về góc liếc tự động
                return self.last_l_leds, self.last_r_leds, self.last_servos
                
        self.lost_frames = 0
        leds = [self.MAX_PWM] * 8 
        
        max_area = 0
        main_target = None
        
        # Tính vùng tối động
        for box in boxes:
            cx, cy, bw, bh = box
            if bw * bh > max_area:
                max_area = bw * bh
                main_target = (cx, cy, bw, bh)
                
            center_idx = int((cx / self.w) * 8)
            center_idx = max(0, min(7, center_idx))
            
            num_off = 1
            if bw > self.w * 0.2: num_off = 3
            elif bw > self.w * 0.08: num_off = 2
                
            start_idx = max(0, center_idx - num_off // 2)
            end_idx = min(8, start_idx + num_off)
            for i in range(start_idx, end_idx):
                leds[i] = 0 
                    
        # Áp dụng góc Servo tự động (ghi đè nếu xe đối diện quá gần)
        lx, ly, rx, ry = base_x, base_y, base_x, base_y
        if main_target:
            tcx, tcy, tw, th = main_target
            if th > self.h * 0.15: # Khẩn cấp: Xe chạy đến quá gần
                ly, ry = 75, 75    # Bắt buộc cụp pha để không rọi vào mắt lái xe

        self.last_l_leds = leds[0:4]
        self.last_r_leds = leds[4:8]
        self.last_servos = [lx, ly, rx, ry]
            
        return self.last_l_leds, self.last_r_leds, self.last_servos