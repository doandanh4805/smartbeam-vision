#include <ESP32Servo.h>

// Thứ tự chân LED chuẩn: L1->L4 | R1->R4
const int leds[] = {18, 17, 16, 15, 23, 22, 21, 19};
Servo sLX, sLY, sRX, sRY;

// Lưu trạng thái hiện tại của LED để chống gọi ledcWrite liên tục
int currentLedVals[8] = {-1, -1, -1, -1, -1, -1, -1, -1};

// Biến nội suy làm mượt riêng cho Servo
float curServos[4] = {90, 90, 90, 90};
int tarServos[4] = {90, 90, 90, 90};

String inputBuffer = "";
bool receiving = false;
unsigned long lastUpdate = 0;

void setup() {
  Serial.begin(115200);

  // 1. QUY HOẠCH CHO SERVO (Chiếm kênh 0, 1, 2, 3)
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  // Ép tần số chuẩn 50Hz cho Servo để không bị giật
  sLX.setPeriodHertz(50); 
  sLY.setPeriodHertz(50);
  sRX.setPeriodHertz(50); 
  sRY.setPeriodHertz(50);

  sLX.attach(33); sLY.attach(32);
  sRX.attach(25); sRY.attach(26);

  // 2. QUY HOẠCH CHO LED (Ép sang kênh từ 8 đến 15 để né hoàn toàn Servo)
  for (int i = 0; i < 8; i++) {
    // Thay vì ledcAttach tự do, ta dùng ledcAttachChannel để bắt buộc chỉ định kênh
    // Leds[i] sẽ lần lượt được gán vào kênh: 8, 9, 10, 11, 12, 13, 14, 15
    ledcAttachChannel(leds[i], 1000, 8, i + 8); 
    
    // Tắt đèn lúc khởi động
    ledcWrite(leds[i], 200);      
    currentLedVals[i] = 200;      
  }
}

void loop() {
  // 1. Nhận Serial (Non-blocking)
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '<') { inputBuffer = ""; receiving = true; }
    else if (c == '>' && receiving) { parseFrame(inputBuffer); receiving = false; }
    else if (receiving) { inputBuffer += c; }
  }

  // 2. Chạy thuật toán Easing cho Servo (mỗi 15ms)
  if (millis() - lastUpdate > 15) {
    lastUpdate = millis();
    updateServos();
  }
}

void parseFrame(String data) {
  int vals[12]; int idx = 0;
  char buf[data.length() + 1]; data.toCharArray(buf, sizeof(buf));
  char* token = strtok(buf, ",");
  while (token != NULL && idx < 12) {
    vals[idx++] = atoi(token); token = strtok(NULL, ",");
  }

  if (idx == 12) {
    // --- STATE CACHING CHO LED (CHỐNG NHÁY TUYỆT ĐỐI) ---
    for (int i = 0; i < 8; i++) {
      int newTarget = constrain(vals[i], 0, 200);
      // Chỉ ra lệnh khi cường độ thực sự thay đổi (Ví dụ từ 200 xuống 0)
      if (newTarget != currentLedVals[i]) {
        ledcWrite(leds[i], newTarget);
        currentLedVals[i] = newTarget; 
      }
    }

    // --- CẬP NHẬT MỤC TIÊU CHO SERVO ---
    for (int i = 0; i < 4; i++) {
      tarServos[i] = constrain(vals[8+i], 0, 180);
    }
  }
}

void updateServos() {
  // Chỉ vuốt mượt cơ khí để chống giật gãy Mica
  for (int i = 0; i < 4; i++) {
    if (abs(tarServos[i] - curServos[i]) > 0.5) {
      curServos[i] += (tarServos[i] - curServos[i]) * 0.15;
    }
  }
  sLX.write(curServos[0]); 
  sLY.write(curServos[1]);
  sRX.write(curServos[2]); 
  sRY.write(curServos[3]);
}