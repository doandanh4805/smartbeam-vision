import serial
import time

class SerialManager:
    def __init__(self, port='COM12', baud_rate=115200):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)
            print(f"[*] Đã kết nối thành công với ESP32 tại cổng {self.port}!")
            return True
        except Exception as e:
            print(f"[!] Lỗi kết nối Serial: {e}")
            return False

    def send_data(self, L_leds, R_leds, servo_angles):
        if not self.ser or not self.ser.is_open:
            return
            
        # KHÓA CỨNG: Ép giá trị PWM không bao giờ vượt quá 200
        L_leds = [min(int(x), 200) for x in L_leds]
        R_leds = [min(int(x), 200) for x in R_leds]
        
        # Đóng gói chuẩn <L1,...,R4,SX1,...,SY2>
        full_data = L_leds + R_leds + [int(a) for a in servo_angles]
        data_str = "<" + ",".join(map(str, full_data)) + ">\n"
        
        try:
            self.ser.write(data_str.encode('ascii'))
        except Exception as e:
            print(f"[!] Lỗi gửi Serial: {e}")

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[*] Đã đóng cổng Serial.")