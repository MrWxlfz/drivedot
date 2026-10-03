# Firmware notes

## Setup

Install PlatformIO through its VS Code extension or `python3 -m pip install platformio==6.1.18`. Open the `firmware` folder. The pinned PlatformIO environment targets the standard Seeed Studio XIAO ESP32S3 and uses its USB-C port for power, upload and native USB serial. The selected board manifest enables USB CDC at boot. Use a data-capable cable.

Other S3 variants, flash sizes or native-USB arrangements need matching board settings. Check the vendor documentation; don't copy a generic pin map onto a different board. Update `include/config.h` for different pins and I²C addresses. This selection uses D4/GPIO5 for SDA, D5/GPIO6 for SCL and D3/GPIO4 for the button. If upload cannot find the board, hold BOOT while connecting USB, release it, then retry; see the [manufacturer's guide](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/).

## Controls

| Input | Behavior |
| --- | --- |
| Hold button for 1.5 seconds, then release | When idle: calibrate after a short settling pause; keep the unit flat and stationary for about 2 seconds |
| Short button press and release | Start or end a session after calibration |
| Long hold during a session | Ignored; release does not end the session |
| Serial `c` | Same calibration while idle; ignored during a session |
| Serial `n` | Start a new session after calibration; ignored during an existing session |
| Serial `e` | End session and retain summary |

At power-up, the OLED prompts `PARK + MOUNT FLAT` / `Hold button 1.5s`. Hold until `RELEASE BUTTON`, release, and keep still. A successful calibration opens the ready screen. Tap to start, then tap to end and view the summary. No computer or serial command is required after uploading firmware.

Calibration is explicit, since power might be connected while the car is moving. Recalibrate while parked whenever you change the mount. A retry clears the previous calibration, so failure cannot silently reuse offsets from a different mounting position. Results are in RAM and disappear on restart.

The 100-sample calibration rejects nonfinite values, obvious motion on any acceleration axis, angular motion, zeroed data, an upside-down sensor and a substantially tilted mount. Defaults require acceleration magnitude 0.8–1.2 g, positive Z at least 0.8 g, horizontal magnitude no more than 0.35 g, gyro magnitude no more than 0.1 rad/s, and variance no more than 0.04 (m/s²)² on each axis. These are provisional bench thresholds, not proof that a vehicle is stationary. The check cannot reliably distinguish steady acceleration from tilt: calibrate only while parked.

The button uses 35 ms debouncing. A long hold consumes the release, preventing calibration from immediately starting a session. A short press acts on release.

## Measurement model

Subtract stationary X/Y offsets, convert m/s² to g using 9.80665, then apply a 120 ms low-pass filter. The baseline remains fixed during a drive so sustained acceleration isn't silently learned away. This is a first prototype: no gyroscope-based attitude compensation, GPS, speed measurement, automatic trip detection or cloud service.

This approach works best with a fixed, flat mounting orientation. Road grade and vehicle pitch/roll alter the gravity projection; changing tilt by hand can look like acceleration. The gyro is used only to help reject motion during calibration.

Events use provisional 0.30 g forward/braking and 0.35 g lateral thresholds, a 300 ms dwell and a 70% reset level. One held excursion produces one event. Smoothness is `100 × (1 − harsh_time / sampled_session_time)`, rounded to an integer. A score exists only after sampling; it isn't validated against driving skill or safety.

The sampling target is 50 Hz and display target 10 Hz, with I²C at 400 kHz. OLED/I²C transfers can lower the effective sampling rate; CSV timestamps are the evidence. Time deltas are taken after completed reads. Loop gaps over 200 ms are excluded from sampled session time and reset pending event dwell. A calibration sample gap over 100 ms rejects that attempt.

## Sensor errors

The pinned [Adafruit MPU6050 2.2.6 source](https://github.com/adafruit/Adafruit_MPU6050/blob/2.2.6/Adafruit_MPU6050.cpp) returns `true` from `getEvent()` even though its underlying burst read does not propagate an I²C error. DriveDot uses Adafruit initialization but reads the 14 sensor bytes directly through `Wire`, checking the address transaction and exact byte count. Conversion uses the selected ±4 g / ±500°/s scales. The range/filter configuration is read back at boot and before calibration.

A failed transaction stops an active session, prints its partial summary to serial, and leaves `SENSOR ERROR` on the OLED; check the connections and restart. This handles observable bus failures, not every sensor failure: a stuck sensor returning plausible bytes, changed configuration mid-session, or a disconnected display may not be detected. Hardware unplug/reconnect behavior has not yet been bench-tested.

CSV columns: `ms,forward_g,lateral_g,score,active`. A score of `-1` means no session samples have been recorded yet. Lines beginning with `#` are messages. When inactive the displayed score belongs to the last session, not current motion. No trip files are stored on-device.
