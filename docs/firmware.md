# Firmware notes

## Setup

Install PlatformIO through its VS Code extension or `python3 -m pip install platformio==6.1.18`. Open the `firmware` folder. The pinned PlatformIO environment targets the standard Seeed Studio XIAO ESP32S3 and uses its USB-C port for power, upload and native USB serial. The selected board manifest enables USB CDC at boot. Use a data-capable cable.

Other S3 variants, flash sizes or native-USB arrangements need matching board settings. Check the vendor documentation; don't copy a generic pin map onto a different board. Update `include/config.h` for different pins and I²C addresses. This selection uses D4/GPIO5 for SDA, D5/GPIO6 for SCL and D3/GPIO4 for the button. If upload cannot find the board, hold BOOT while connecting USB, release it, then retry; see the [manufacturer's guide](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/).

## Controls

| Input | Behavior |
| --- | --- |
| Serial `c` | Collect 100 samples over about 2 seconds while stationary; reject obvious motion |
| Serial `n` | Start a new session after calibration; ignored during an existing session |
| Serial `e` | End session and retain summary |
| Short button press | Start or end a session after calibration |

Calibration is explicit, since power might be connected while the car is moving. Recalibrate while parked whenever you change the mount. The stillness check cannot detect steady acceleration; only calibrate at rest. Results are in RAM and disappear on restart.

## Measurement model

Subtract stationary X/Y offsets, convert m/s² to g using 9.80665, then apply a 120 ms low-pass filter. The baseline remains fixed during a drive so sustained acceleration isn't silently learned away. This is a first prototype: no gyroscope-based attitude compensation, GPS, speed measurement, automatic trip detection or cloud service.

This approach works best with a fixed, flat mounting orientation. Road grade and vehicle pitch/roll alter the gravity projection; changing tilt by hand can look like acceleration. The gyro is used only to help reject motion during calibration.

Events use provisional 0.30 g forward/braking and 0.35 g lateral thresholds, a 300 ms dwell and a 70% reset level. One held excursion produces one event. Smoothness is `100 × (1 − harsh_time / sampled_session_time)`, rounded to an integer. A score exists only after sampling; it isn't validated against driving skill or safety.

The sampling target is 50 Hz and display target 10 Hz. OLED/I²C transfers can lower the effective sampling rate; CSV timestamps are the evidence. Loop gaps over 200 ms are excluded from sampled session time.

CSV columns: `ms,forward_g,lateral_g,score,active`. Lines beginning with `#` are messages. When inactive the displayed score belongs to the last session, not current motion. No trip files are stored on-device.
