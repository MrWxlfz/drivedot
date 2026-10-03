# Validation

## Automated

`python3 scripts/test.py` builds two portable C++ test programs:

- Motion: stationary offset subtraction, signed braking/acceleration, one event per sustained excursion, left/right turns, rejection of brief gate spikes, session reset, invalid samples, lost-time dwell reset, calibration guards and score behavior across different durations.
- Controls/calibration: contact bounce, short press, 1.5-second hold, one action per hold, release suppression, delayed input polling, `millis()` rollover, calibration sample count, offsets, invalid numbers, zeroed data, upside-down/tilted mounting, angular motion and Z-axis shaking.

Both programs pass on the host compiler with `-Wall -Wextra -Werror` (2026-10-03 UTC).

`python3 -m platformio run -d firmware` also passes locally for `seeed_xiao_esp32s3` using the pinned dependencies (2026-10-03 UTC). The resulting build uses 19,032 bytes RAM and 300,017 bytes flash. This verifies compilation and linking, including the direct `Wire` acquisition and OLED APIs. The firmware has not been flashed to or tested on a physical board.

These are synthetic logic tests and a cross-compile. They do not validate electrical wiring, I²C bus-fault behavior, real sensor noise, the calibration thresholds on hardware, physical orientation, or real driving accuracy. The GitHub workflow repeats the host tests and ESP32 build; its own run status must be checked separately.

## Hardware design checks

KiCad 9.0.9 reports **0 ERC violations, 0 DRC violations, 0 unconnected items and 0 schematic/PCB parity issues**, with no exclusions. See the [ERC report](../hardware/pcb/validation/erc.rpt), [DRC report](../hardware/pcb/validation/drc.rpt) and [validation summary](../hardware/pcb/validation/summary.json). The summary's source hashes match the supplied schematic and PCB.

The [enclosure validation report](../hardware/enclosure/validation.json) records valid CAD solids, **7 closed, manifold STL meshes** with no boundary/nonmanifold edges, and passing results for every modeled nominal intersection check. Checks include printed parts against each other and against the modeled module, connector and header envelopes.

Module dimensions, socket heights and component envelopes remain design assumptions. Purchased parts must be measured, sensor axes verified, and physical fit and printer tolerances checked. The PCB and enclosure have not been manufactured or assembled.

## Bench checklist

- [ ] Record the exact hardware revision, modules and wiring.
- [ ] Compile and flash the actual selected board.
- [ ] Confirm both I²C addresses and operation at 3.3 V.
- [ ] Log at rest before and after calibration.
- [ ] Check X and Y signs using motion in a known direction.
- [ ] Tilt the device to demonstrate the gravity limitation.
- [ ] Verify short noise spikes don't create repeated events.
- [ ] Power from USB without a serial terminal: hold for 1.5 seconds, release, calibrate, tap to start and tap to end.
- [ ] Confirm a hold never triggers a second short-press action on release; verify holds during a drive do not recalibrate.
- [ ] Check failed calibration, repeated start, recalibration and power-cycle behavior.
- [ ] Evaluate sample timing while refreshing the OLED.
- [ ] Power down, disconnect a sensor, restart, and confirm a clear error.
- [ ] With a current-limited bench supply and safe test wiring, interrupt only the IMU signal connection during a session; verify recording stops and the error persists. Restore power only after fixing wiring.
- [ ] Film a bench demo and publish only actual results.

Do vehicle tests only with a secure mount and a passenger managing the device. Review summaries while parked. This prototype gives no basis for judging emergency braking as a bad driving decision.
