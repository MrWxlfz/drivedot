#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_SSD1306.h>
#include "config.h"
#include "motion.h"
#include "button.h"
#include "calibration.h"

Adafruit_MPU6050 imu;
Adafruit_SSD1306 display(128, 64, &Wire, -1, 400000, 400000);
drivedot::Motion motion;
drivedot::Button button;
bool displayReady = false, imuReady = false, hasSession = false;
bool calibrationPending = false;
uint32_t lastSample = 0, lastDisplay = 0;

void message(const char* first, const char* second) {
  Serial.printf("# %s: %s\n", first, second);
  if (!displayReady) return;
  display.clearDisplay(); display.setTextSize(1); display.setCursor(0, 8);
  display.println(first); display.println(); display.println(second);
  display.display();
}

// MPU6050 getEvent() in the pinned Adafruit release always returns true.
// Check the actual I2C transaction and byte count instead of trusting it.
bool readRegisters(uint8_t reg, uint8_t* bytes, size_t length) {
  Wire.beginTransmission(config::IMU_ADDRESS);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  const size_t received = Wire.requestFrom(config::IMU_ADDRESS, length, true);
  if (received != length) {
    while (Wire.available()) Wire.read();
    return false;
  }
  for (size_t i = 0; i < length; ++i) {
    const int value = Wire.read();
    if (value < 0) return false;
    bytes[i] = static_cast<uint8_t>(value);
  }
  return true;
}

bool configurationMatches() {
  uint8_t ranges[3], power;
  // CONFIG=21 Hz, GYRO_CONFIG=500 deg/s, ACCEL_CONFIG=4 g.
  return readRegisters(0x1A, ranges, sizeof(ranges)) &&
      readRegisters(0x6B, &power, 1) && (ranges[0] & 7) == 4 &&
      (ranges[1] & 0xF8) == 8 && (ranges[2] & 0xF8) == 8 &&
      (power & 0xC0) == 0;
}

bool readSample(drivedot::Sample& sample) {
  uint8_t bytes[14];
  if (!readRegisters(0x3B, bytes, sizeof(bytes))) return false;
  const auto axis = [&bytes](size_t index) -> float {
    const uint16_t raw = (static_cast<uint16_t>(bytes[index]) << 8) |
                         bytes[index + 1];
    const int32_t signedRaw = raw >= 0x8000 ? static_cast<int32_t>(raw) - 65536 : raw;
    return static_cast<float>(signedRaw);
  };
  // Fixed scales match the configuration read back at boot and calibration.
  constexpr float accelScale = drivedot::GRAVITY / 8192.0f;
  constexpr float gyroScale = 0.01745329252f / 65.5f;
  sample = {axis(0) * accelScale, axis(2) * accelScale, axis(4) * accelScale,
            axis(8) * gyroScale, axis(10) * gyroScale, axis(12) * gyroScale};
  return true;
}

void endSession() {
  if (!motion.active()) return;
  motion.stop();
  const auto& s = motion.summary;
  Serial.printf("# Summary: %.1fs, score=%d, peak=%.2fg, accel=%lu, brake=%lu, turn=%lu\n",
      s.seconds, s.seconds > 0 ? s.score() : -1, s.peakG, static_cast<unsigned long>(s.accelerationEvents),
      static_cast<unsigned long>(s.brakingEvents), static_cast<unsigned long>(s.turningEvents));
}

void sensorFault() {
  endSession();
  imuReady = false;
  calibrationPending = false;
  message("SENSOR ERROR", "Check wiring; reboot");
}

bool calibrate() {
  if (!imuReady || motion.active()) return false;
  motion.clearCalibration();  // A failed retry must not retain an old mount offset.
  hasSession = false;
  button.suppressRelease();
  message("CALIBRATING", "Keep flat/still 2s");
  delay(300);  // Allow the released button and mount to settle.
  if (!configurationMatches()) { sensorFault(); return false; }
  drivedot::Calibration calibration;
  uint32_t previous = millis();
  for (int i = 0; i < 100; ++i) {
    while (millis() - previous < config::SAMPLE_MS) delay(1);
    drivedot::Sample sample;
    if (!readSample(sample)) { sensorFault(); return false; }
    const uint32_t sampledAt = millis();
    // Do not accept a calibration that was substantially stalled.
    if (sampledAt - previous > 100 || !calibration.add(sample)) {
      message("CALIBRATION FAILED", "Hold 1.5s to retry"); return false;
    }
    previous = sampledAt;
  }
  if (!calibration.valid()) {
    message("KEEP FLAT AND STILL", "Hold 1.5s to retry"); return false;
  }
  motion.calibrate(calibration.x(), calibration.y());
  lastSample = millis();
  message("READY", "Tap button to start");
  return true;
}

void startSession() {
  if (motion.active() || calibrationPending) return;
  if (!motion.calibrated()) {
    message("CALIBRATE FIRST", "Park; hold 1.5s"); return;
  }
  motion.start(); hasSession = true;
  lastSample = millis();
  Serial.println("# Session started");
}

void render() {
  if (!displayReady || !motion.calibrated() || calibrationPending) return;
  display.clearDisplay(); display.setTextSize(1); display.setCursor(0, 0);
  if (!motion.active()) {
    display.println(hasSession ? "DRIVE SUMMARY" : "DRIVEDOT / READY");
    if (hasSession) {
      const auto& s = motion.summary;
      if (s.seconds > 0) {
        display.printf("%.0fs  Smoothness %d\nPeak %.2fg\nAccel %lu / Brake %lu\nTurns %lu\n",
            s.seconds, s.score(), s.peakG, static_cast<unsigned long>(s.accelerationEvents),
            static_cast<unsigned long>(s.brakingEvents), static_cast<unsigned long>(s.turningEvents));
      } else display.println("No samples recorded");
    } else {
      display.println("Mounted flat + still");
      display.println("Tap to start");
    }
    display.setCursor(0, 48); display.print("Hold 1.5s: calibrate");
    display.setCursor(0, 56); display.print("Tap: new session");
  } else {
    display.print("DRIVEDOT");
    display.setCursor(0, 18); display.printf("F %+.2fg\nL %+.2fg", motion.forwardG, motion.lateralG);
    display.setCursor(0, 44);
    if (motion.summary.seconds > 0) display.printf("Score %d", motion.summary.score());
    else display.print("Score --");
    display.setCursor(0, 56); display.print("Tap: end");
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
  Wire.setClock(400000);
  Wire.setTimeOut(50);
  Wire.beginTransmission(config::OLED_ADDRESS);
  const bool oledAck = Wire.endTransmission() == 0;
  displayReady = oledAck && display.begin(SSD1306_SWITCHCAPVCC, config::OLED_ADDRESS);
  if (displayReady) { display.setTextColor(SSD1306_WHITE); display.setTextWrap(false); }
  else Serial.println("# OLED not found; check wiring / 0x3C");
  imuReady = imu.begin(config::IMU_ADDRESS, &Wire);
  if (!imuReady) { message("IMU NOT FOUND", "Check wiring / 0x68"); return; }
  imu.setAccelerometerRange(MPU6050_RANGE_4_G);
  imu.setGyroRange(MPU6050_RANGE_500_DEG);
  imu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  if (!configurationMatches()) { sensorFault(); return; }
  Serial.println("# Hold button 1.5s and release to calibrate while parked; tap to start/end");
  Serial.println("# Commands: c calibrate, n new session, e end");
  Serial.println("ms,forward_g,lateral_g,score,active");
  message("PARK + MOUNT FLAT", "Hold button 1.5s");
  lastSample = millis();
}

void loop() {
  if (!imuReady) { delay(20); return; }
  if (Serial.available()) {
    const char command = Serial.read();
    if (command == 'c' && !motion.active()) {
      calibrationPending = false;
      calibrate(); lastSample = millis();
    } else if (command == 'n') startSession();
    else if (command == 'e') endSession();
    if (!imuReady) return;
  }
  const auto event = button.update(digitalRead(config::BUTTON_PIN) == LOW, millis());
  if (event == drivedot::ButtonEvent::LongPress && !motion.active()) {
    calibrationPending = true;
    message("RELEASE BUTTON", "Then keep flat/still");
  } else if (event == drivedot::ButtonEvent::ShortPress && !calibrationPending) {
    if (motion.active()) endSession(); else startSession();
  }
  if (calibrationPending && !button.pressed()) {
    calibrationPending = false;
    calibrate(); lastSample = millis();
    if (!imuReady) return;
  }
  // Refresh now after any blocking calibration, avoiding unsigned time underflow.
  if (millis() - lastSample >= config::SAMPLE_MS && !calibrationPending) {
    drivedot::Sample sample;
    if (!readSample(sample)) { sensorFault(); return; }
    const uint32_t sampledAt = millis();
    const float dt = (sampledAt - lastSample) / 1000.0f;
    lastSample = sampledAt;
    if (motion.update(sample.x, sample.y, dt, config::FORWARD_SIGN, config::LATERAL_SIGN)) {
      Serial.printf("%lu,%.3f,%.3f,%d,%d\n", static_cast<unsigned long>(sampledAt),
          motion.forwardG, motion.lateralG,
          motion.summary.seconds > 0 ? motion.summary.score() : -1, motion.active());
    }
  }
  const uint32_t now = millis();
  if (now - lastDisplay >= config::DISPLAY_MS) { lastDisplay = now; render(); }
  delay(1);
}
