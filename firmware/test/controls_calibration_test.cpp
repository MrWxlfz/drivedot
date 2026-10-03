#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include "button.h"
#include "calibration.h"

using drivedot::ButtonEvent;

void testButton() {
  drivedot::Button button;
  assert(button.update(true, 10) == ButtonEvent::None);
  assert(button.update(false, 20) == ButtonEvent::None); // Contact bounce.
  assert(button.update(true, 25) == ButtonEvent::None);
  assert(button.update(true, 60) == ButtonEvent::None);
  assert(button.pressed());
  assert(button.update(false, 120) == ButtonEvent::None);
  assert(button.update(true, 130) == ButtonEvent::None); // Release bounce.
  assert(button.update(false, 140) == ButtonEvent::None);
  assert(button.update(false, 175) == ButtonEvent::ShortPress);
  assert(!button.pressed());
  assert(button.update(false, 1000) == ButtonEvent::None);

  assert(button.update(true, 2000) == ButtonEvent::None);
  assert(button.update(true, 2035) == ButtonEvent::None);
  assert(button.update(true, 3534) == ButtonEvent::None);
  assert(button.update(true, 3535) == ButtonEvent::LongPress);
  assert(button.update(true, 5000) == ButtonEvent::None); // Never repeat.
  assert(button.update(false, 5010) == ButtonEvent::None);
  assert(button.update(false, 5045) == ButtonEvent::None); // No accidental start.
  assert(!button.pressed());

  // A delayed loop that first sees release after the threshold still means hold.
  assert(button.update(true, 6000) == ButtonEvent::None);
  assert(button.update(true, 6035) == ButtonEvent::None);
  assert(button.update(false, 8000) == ButtonEvent::None);
  assert(button.update(false, 8035) == ButtonEvent::LongPress);

  // millis() wraps about every 49 days; durations use unsigned subtraction.
  drivedot::Button wrap;
  const uint32_t begin = UINT32_MAX - 100;
  assert(wrap.update(true, begin) == ButtonEvent::None);
  assert(wrap.update(true, begin + 35) == ButtonEvent::None);
  assert(wrap.update(true, begin + 1535) == ButtonEvent::LongPress);
  assert(wrap.update(false, begin + 1600) == ButtonEvent::None);
  assert(wrap.update(false, begin + 1635) == ButtonEvent::None);

  drivedot::Button serial;
  serial.update(true, 1); serial.update(true, 36);
  serial.suppressRelease();
  serial.update(false, 100);
  assert(serial.update(false, 135) == ButtonEvent::None);
}

void testCalibration() {
  const drivedot::Sample atRest = {0.1f, -0.2f, drivedot::GRAVITY, 0.01f, 0, 0};
  drivedot::Calibration good;
  for (int i = 0; i < 99; ++i) assert(good.add(atRest));
  assert(!good.valid());
  assert(good.add(atRest)); assert(good.valid());
  assert(std::fabs(good.x() - 0.1f) < 0.0001f);
  assert(std::fabs(good.y() + 0.2f) < 0.0001f);

  drivedot::Calibration zero, upsideDown, tilt, rotating, shakingZ, nonfinite;
  for (int i = 0; i < 100; ++i) {
    zero.add({0, 0, 0, 0, 0, 0});
    upsideDown.add({0, 0, -drivedot::GRAVITY, 0, 0, 0});
    tilt.add({0.5f * drivedot::GRAVITY, 0, 0.866f * drivedot::GRAVITY, 0, 0, 0});
    rotating.add({0, 0, drivedot::GRAVITY, 0, 0.11f, 0});
    shakingZ.add({0, 0, drivedot::GRAVITY + (i % 2 ? 0.3f : -0.3f), 0, 0, 0});
    nonfinite.add(atRest);
  }
  assert(!zero.valid() && !upsideDown.valid() && !tilt.valid());
  assert(!rotating.valid() && !shakingZ.valid());
  auto broken = atRest;
  broken.gz = std::numeric_limits<float>::quiet_NaN();
  assert(!nonfinite.add(broken) && !nonfinite.valid());
}

int main() {
  testButton(); testCalibration();
  std::cout << "Controls/calibration tests passed: debounce, tap/hold, release suppression, clock wrap, rest/tilt/motion/invalid data\n";
}
