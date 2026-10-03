#pragma once
#include <stdint.h>

namespace config {
// Seeed Studio XIAO ESP32S3: D4=GPIO5, D5=GPIO6, D3=GPIO4.
constexpr int SDA_PIN = 5;
constexpr int SCL_PIN = 6;
constexpr int BUTTON_PIN = 4;
constexpr uint8_t OLED_ADDRESS = 0x3C;
constexpr uint8_t IMU_ADDRESS = 0x68;
constexpr uint32_t SAMPLE_MS = 20;
constexpr uint32_t DISPLAY_MS = 100;
// Mount the IMU flat: X forward, Y left, Z up. Verify signs on the bench.
constexpr float FORWARD_SIGN = 1.0f;
constexpr float LATERAL_SIGN = 1.0f;
}
