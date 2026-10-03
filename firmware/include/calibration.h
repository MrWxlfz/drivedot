#pragma once
#include <algorithm>
#include <cmath>
#include <stdint.h>
#include "motion.h"

namespace drivedot {
struct Sample {
  float x, y, z;       // m/s^2
  float gx, gy, gz;    // rad/s
};

class Calibration {
 public:
  bool add(const Sample& s) {
    if (!std::isfinite(s.x) || !std::isfinite(s.y) || !std::isfinite(s.z) ||
        !std::isfinite(s.gx) || !std::isfinite(s.gy) || !std::isfinite(s.gz)) {
      invalid_ = true;
      return false;
    }
    ++count_;
    const float axes[] = {s.x, s.y, s.z};
    // Welford variance avoids cancellation when gravity is near one axis.
    for (int axis = 0; axis < 3; ++axis) {
      const float delta = axes[axis] - mean_[axis];
      mean_[axis] += delta / count_;
      m2_[axis] += delta * (axes[axis] - mean_[axis]);
    }
    maxGyro_ = std::max(maxGyro_, std::sqrt(s.gx*s.gx + s.gy*s.gy + s.gz*s.gz));
    const float length = std::sqrt(s.x*s.x + s.y*s.y + s.z*s.z);
    // Reject zeroed data, free-fall and implausible gravity. Mount Z upward.
    if (length < 0.8f * GRAVITY || length > 1.2f * GRAVITY ||
        s.z < 0.8f * GRAVITY || std::hypot(s.x, s.y) > 0.35f * GRAVITY)
      invalid_ = true;
    return true;
  }
  bool valid() const {
    if (invalid_ || count_ < 100 || maxGyro_ > 0.1f) return false;
    for (int axis = 0; axis < 3; ++axis)
      if (m2_[axis] / count_ > 0.04f) return false;
    return true;
  }
  float x() const { return mean_[0]; }
  float y() const { return mean_[1]; }
 private:
  uint32_t count_ = 0;
  float mean_[3] = {}, m2_[3] = {}, maxGyro_ = 0;
  bool invalid_ = false;
};
}
