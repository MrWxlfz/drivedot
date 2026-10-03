#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_SSD1306.h>
#include "config.h"
#include "motion.h"

Adafruit_MPU6050 imu;
Adafruit_SSD1306 display(128, 64, &Wire, -1);
drivedot::Motion motion;
bool displayReady = false, imuReady = false, hasSession = false;
uint32_t lastSample = 0, lastDisplay = 0;

void message(const char* first, const char* second) {
  Serial.printf("# %s: %s\n", first, second);
  if (!displayReady) return;
  display.clearDisplay(); display.setTextSize(1); display.setCursor(0, 8);
  display.println(first); display.println(); display.println(second);
  display.display();
}

bool calibrate() {
  if (!imuReady || motion.active()) return false;
  message("CALIBRATING", "Keep still for 2s");
  float sx = 0, sy = 0, sx2 = 0, sy2 = 0, maxGyro = 0;
  for (int i = 0; i < 100; ++i) {
    sensors_event_t a, g, t;
    if (!imu.getEvent(&a, &g, &t) || !std::isfinite(a.acceleration.x) ||
        !std::isfinite(a.acceleration.y) || !std::isfinite(a.acceleration.z) ||
        !std::isfinite(g.gyro.x) || !std::isfinite(g.gyro.y) ||
        !std::isfinite(g.gyro.z)) {
      message("SENSOR ERROR", "Check I2C wiring"); return false;
    }
    sx += a.acceleration.x; sy += a.acceleration.y;
    sx2 += a.acceleration.x * a.acceleration.x;
    sy2 += a.acceleration.y * a.acceleration.y;
    maxGyro = std::max(maxGyro, std::sqrt(g.gyro.x * g.gyro.x +
        g.gyro.y * g.gyro.y + g.gyro.z * g.gyro.z));
    delay(config::SAMPLE_MS);
  }
  const float x = sx / 100, y = sy / 100;
  if (sx2 / 100 - x * x > 0.04f || sy2 / 100 - y * y > 0.04f || maxGyro > 0.1f) {
    message("MOVED DURING CAL", "Keep still; send c"); return false;
  }
  motion.calibrate(x, y);
  hasSession = false;
  message("READY", "Button / n to start");
  return true;
}

void startSession() {
  if (motion.active()) return;
  if (!motion.calibrated()) {
    message("CALIBRATE FIRST", "Stationary: send c"); return;
  }
  motion.start(); hasSession = true;
  lastSample = millis();
  Serial.println("# Session started");
}

void endSession() {
  if (!motion.active()) return;
  motion.stop();
  const auto& s = motion.summary;
  Serial.printf("# Summary: %.1fs, score=%d, peak=%.2fg, accel=%lu, brake=%lu, turn=%lu\n",
      s.seconds, s.score(), s.peakG, static_cast<unsigned long>(s.accelerationEvents),
      static_cast<unsigned long>(s.brakingEvents), static_cast<unsigned long>(s.turningEvents));
}

void render() {
  if (!displayReady || !motion.calibrated()) return;
  display.clearDisplay(); display.setTextSize(1); display.setCursor(0, 0);
  if (!motion.active()) {
    display.println(hasSession ? "DRIVE SUMMARY" : "DRIVEDOT / READY");
    if (hasSession) {
      const auto& s = motion.summary;
      display.printf("%.0fs  Smoothness %d\nPeak %.2fg\nAccel %lu / Brake %lu\nTurns %lu\n",
          s.seconds, s.score(), s.peakG, static_cast<unsigned long>(s.accelerationEvents),
          static_cast<unsigned long>(s.brakingEvents), static_cast<unsigned long>(s.turningEvents));
    }
    display.setCursor(0, 56); display.print("Button: new session");
  } else {
    display.print("DRIVEDOT");
    display.setCursor(0, 18); display.printf("F %+.2fg\nL %+.2fg", motion.forwardG, motion.lateralG);
    display.setCursor(0, 44); display.printf("Score %d", motion.summary.score());
    display.setCursor(0, 56); display.print("Button: end");
    display.drawRect(82, 17, 44, 44, SSD1306_WHITE);
    display.drawLine(104, 19, 104, 58, SSD1306_WHITE);
    display.drawLine(84, 39, 123, 39, SSD1306_WHITE);
    // Leftward acceleration goes left; forward acceleration goes down.
    const int dx = std::max(-19, std::min(19, static_cast<int>(-motion.lateralG * 38)));
    const int dy = std::max(-19, std::min(19, static_cast<int>(motion.forwardG * 38)));
    display.fillCircle(104 + dx, 39 + dy, 2, SSD1306_WHITE);
  }
  display.display();
}

void setup() {
  Serial.begin(115200);
  pinMode(config::BUTTON_PIN, INPUT_PULLUP);
  Wire.begin(config::SDA_PIN, config::SCL_PIN);
  Wire.setTimeOut(50);
  displayReady = display.begin(SSD1306_SWITCHCAPVCC, config::OLED_ADDRESS);
  if (displayReady) { display.setTextColor(SSD1306_WHITE); display.setTextWrap(false); }
  imuReady = imu.begin(config::IMU_ADDRESS, &Wire);
  if (!imuReady) { message("IMU NOT FOUND", "Check wiring / 0x68"); return; }
  imu.setAccelerometerRange(MPU6050_RANGE_4_G);
  imu.setGyroRange(MPU6050_RANGE_500_DEG);
  imu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.println("# Commands: c calibrate, n new session, e end");
  Serial.println("ms,forward_g,lateral_g,score,active");
  message("DRIVEDOT", "Stationary: send c");
  lastSample = millis();
}

void loop() {
  if (!imuReady) { delay(20); return; }
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 'c') {
      calibrate(); lastSample = millis();
    } else if (command == 'n') startSession();
    else if (command == 'e') endSession();
  }
  const uint32_t now = millis();
  static bool rawPrevious = HIGH, stableButton = HIGH;
  static uint32_t changedAt = 0;
  const bool raw = digitalRead(config::BUTTON_PIN);
  if (raw != rawPrevious) { changedAt = now; rawPrevious = raw; }
  if (now - changedAt >= 35 && raw != stableButton) {
    stableButton = raw;
    if (stableButton == LOW) {
      if (motion.active()) endSession(); else startSession();
    }
  }
  if (now - lastSample >= config::SAMPLE_MS) {
    const float dt = (now - lastSample) / 1000.0f;
    lastSample = now;
    sensors_event_t a, g, t;
    if (!imu.getEvent(&a, &g, &t) || !std::isfinite(a.acceleration.x) ||
        !std::isfinite(a.acceleration.y)) {
      endSession(); imuReady = false;
      message("SENSOR ERROR", "Check wiring; reboot"); return;
    }
    if (motion.update(a.acceleration.x, a.acceleration.y, dt,
        config::FORWARD_SIGN, config::LATERAL_SIGN)) {
      Serial.printf("%lu,%.3f,%.3f,%d,%d\n", static_cast<unsigned long>(now),
          motion.forwardG, motion.lateralG, motion.summary.score(), motion.active());
    }
  }
  if (now - lastDisplay >= config::DISPLAY_MS) { lastDisplay = now; render(); }
  delay(1);
}
