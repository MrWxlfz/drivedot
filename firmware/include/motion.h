#pragma once
#include <algorithm>
#include <cmath>
#include <stdint.h>

namespace drivedot {
constexpr float GRAVITY = 9.80665f;

// A sustained excursion counts once until it drops below a lower reset level.
class EventGate {
 public:
  void reset() { elapsed_ = 0; latched_ = false; }
  bool update(float value, float threshold, float dt) {
    if (value < threshold * 0.7f) { reset(); return false; }
    if (value < threshold) { elapsed_ = 0; return false; }
    elapsed_ += dt;
    if (!latched_ && elapsed_ >= 0.3f) { latched_ = true; return true; }
    return false;
  }
 private:
  float elapsed_ = 0;
  bool latched_ = false;
};

struct Summary {
  float seconds = 0;
  float harshSeconds = 0;
  float peakG = 0;
  uint32_t accelerationEvents = 0;
  uint32_t brakingEvents = 0;
  uint32_t turningEvents = 0;
  int score() const {
    if (seconds <= 0) return 100;
    return static_cast<int>(std::lround(100.0f *
        (1.0f - std::min(1.0f, harshSeconds / seconds))));
  }
};

class Motion {
 public:
  void calibrate(float x, float y) {
    baselineX_ = x; baselineY_ = y;
    forwardG = lateralG = 0;
    calibrated_ = true;
  }
  bool calibrated() const { return calibrated_; }
  bool active() const { return active_; }
  void start() {
    if (!calibrated_) return;
    summary = Summary{};
    accel_.reset(); brake_.reset(); turn_.reset();
    active_ = true;
  }
  void stop() { active_ = false; }
  bool update(float x, float y, float dt, float forwardSign = 1,
              float lateralSign = 1) {
    if (!calibrated_ || !std::isfinite(x) || !std::isfinite(y) ||
        !std::isfinite(dt) || dt <= 0 || dt > 0.2f) return false;
    // Time-based low-pass filter; the baseline stays fixed throughout a drive.
    const float alpha = 1.0f - std::exp(-dt / 0.12f);
    forwardG += alpha * ((x - baselineX_) / GRAVITY * forwardSign - forwardG);
    lateralG += alpha * ((y - baselineY_) / GRAVITY * lateralSign - lateralG);
    if (!active_) return true;
    const float magnitude = std::sqrt(forwardG * forwardG + lateralG * lateralG);
    summary.seconds += dt;
    summary.peakG = std::max(summary.peakG, magnitude);
    // Experimental defaults to tune with recorded bench data.
    if (std::fabs(forwardG) >= 0.30f || std::fabs(lateralG) >= 0.35f)
      summary.harshSeconds += dt;
    if (accel_.update(forwardG, 0.30f, dt)) ++summary.accelerationEvents;
    if (brake_.update(-forwardG, 0.30f, dt)) ++summary.brakingEvents;
    if (turn_.update(std::fabs(lateralG), 0.35f, dt)) ++summary.turningEvents;
    return true;
  }
  float forwardG = 0;
  float lateralG = 0;
  Summary summary;
 private:
  float baselineX_ = 0, baselineY_ = 0;
  bool calibrated_ = false, active_ = false;
  EventGate accel_, brake_, turn_;
};
}
