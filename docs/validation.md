# Validation

## Automated

`python3 scripts/test.py` builds the portable motion logic with a host C++ compiler. It checks stationary offset subtraction, signed braking/acceleration, one event per sustained excursion, left/right turns, rejection of brief gate spikes, session reset, invalid sample handling and score behavior across different durations.

These tests do not validate electrical wiring, I²C faults, calibration stillness detection, physical orientation, or real driving accuracy. The GitHub workflow also attempts a PlatformIO ESP32 build; a configured workflow is not evidence that it has passed.

## Bench checklist

- [ ] Record the exact hardware revision, modules and wiring.
- [ ] Compile and flash the actual selected board.
- [ ] Confirm both I²C addresses and operation at 3.3 V.
- [ ] Log at rest before and after calibration.
- [ ] Check X and Y signs using motion in a known direction.
- [ ] Tilt the device to demonstrate the gravity limitation.
- [ ] Verify short noise spikes don't create repeated events.
- [ ] Check start/end, repeated start, recalibration and power-cycle behavior.
- [ ] Evaluate sample timing while refreshing the OLED.
- [ ] Power down, disconnect a sensor, restart, and confirm a clear error.
- [ ] Film a bench demo and publish only actual results.

Do vehicle tests only with a secure mount and a passenger managing the device. Review summaries while parked. This prototype gives no basis for judging emergency braking as a bad driving decision.
