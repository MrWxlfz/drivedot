#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>
#include "motion.h"

void samples(drivedot::Motion& m, float forward, float lateral, int count) {
  for (int i = 0; i < count; ++i)
    assert(m.update(forward * drivedot::GRAVITY, lateral * drivedot::GRAVITY, 0.02f));
}

int main() {
  drivedot::Motion m;
  m.start(); assert(!m.active());
  assert(!m.update(0, 0, 0.02f));
  assert(!m.calibrate(std::numeric_limits<float>::quiet_NaN(), 0));
  assert(!m.calibrated());
  m.calibrate(0, 0); m.start();
  assert(!m.calibrate(1, 2)); // Baseline cannot change during a session.
  samples(m, 0, 0, 100);
  assert(m.summary.score() == 100 && m.summary.peakG == 0);
  samples(m, 0.5f, 0, 100);
  assert(m.summary.accelerationEvents == 1);
  assert(m.summary.brakingEvents == 0);
  assert(m.summary.score() < 100);
  samples(m, 0.5f, 0, 100);
  assert(m.summary.accelerationEvents == 1); // A held event doesn't repeat.
  samples(m, 0, 0, 100);
  samples(m, 0.5f, 0, 100);
  assert(m.summary.accelerationEvents == 2);
  samples(m, -0.5f, 0, 100);
  assert(m.summary.brakingEvents == 1);
  samples(m, 0, 0.6f, 100);
  samples(m, 0, -0.6f, 100);
  assert(m.summary.turningEvents == 2);
  m.stop(); const float recordedSeconds = m.summary.seconds;
  samples(m, 0, 0, 100);
  assert(m.summary.seconds == recordedSeconds);
  m.start(); assert(m.summary.seconds == 0 && m.summary.accelerationEvents == 0);
  const auto before = m.summary;
  assert(!m.update(std::numeric_limits<float>::quiet_NaN(), 0, 0.02f));
  assert(!m.update(0, 0, -1));
  assert(!m.update(0, 0, 1)); // Don't count a long blocked loop as motion.
  assert(m.summary.seconds == before.seconds);
  m.stop(); m.calibrate(1.2f, -0.7f); m.start();
  for (int i = 0; i < 100; ++i) assert(m.update(1.2f, -0.7f, 0.02f));
  assert(std::fabs(m.forwardG) < 0.001f && std::fabs(m.lateralG) < 0.001f);
  drivedot::EventGate gate;
  assert(!gate.update(0.5f, 0.3f, 0.1f));
  assert(!gate.update(0, 0.3f, 0.1f)); // A brief spike doesn't count.
  drivedot::Motion shortDrive, longDrive;
  shortDrive.calibrate(0, 0); longDrive.calibrate(0, 0);
  shortDrive.start(); longDrive.start();
  samples(shortDrive, 0.5f, 0, 500); samples(shortDrive, 0, 0, 500);
  samples(longDrive, 0.5f, 0, 1000); samples(longDrive, 0, 0, 1000);
  assert(std::abs(shortDrive.summary.score() - longDrive.summary.score()) <= 1);
  longDrive.stop(); longDrive.clearCalibration(); longDrive.start();
  assert(!longDrive.calibrated() && !longDrive.active());
  drivedot::Motion gap;
  gap.calibrate(0, 0); gap.start();
  assert(gap.update(0.5f * drivedot::GRAVITY, 0, 0.2f));
  assert(!gap.update(0.5f * drivedot::GRAVITY, 0, 1.0f));
  samples(gap, 0.5f, 0, 6);
  assert(gap.summary.accelerationEvents == 0); // Dwell restarts after lost time.
  std::cout << "Motion tests passed: calibration, filtering, event counts, session reset, score, invalid samples\n";
}
