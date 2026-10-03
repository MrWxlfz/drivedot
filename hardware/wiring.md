# Prototype wiring

Unplug USB before wiring. These pins target an ESP32-S3 development board, not a bare module. Confirm the exact board and module schematics before powering up. ESP32 GPIO is 3.3 V logic.

| ESP32-S3 connection | Destination |
| --- | --- |
| 3V3 | MPU6050 and OLED supply inputs, only if each selected breakout supports 3.3 V power |
| GND | MPU6050 GND, OLED GND, one side of button |
| GPIO8 | MPU6050 SDA and OLED SDA |
| GPIO9 | MPU6050 SCL and OLED SCL |
| GPIO4 | Other side of button; firmware enables internal pull-up |
| USB-to-UART connector | USB power and serial programming |

Expected addresses: MPU6050 `0x68` (AD0 low), OLED `0x3C`. Adjust `firmware/include/config.h` to match the actual modules. Leave unused IMU interrupt and auxiliary pins unconnected unless the selected breakout documentation says otherwise.

I²C pull-ups must go to 3.3 V. Inspect breakout schematics for existing pull-ups; add a suitable pair (start with 4.7 kΩ) only if needed. A regulator on a breakout does not establish that its I²C pins are safe at every supply voltage.

Mount the IMU horizontally and rigidly: sensor X toward the front of the vehicle, sensor Y to the left, Z up. The display and enclosure may be angled independently. Check the manufacturer's axis diagram, then verify signs with bench motion. An IMU attached directly to an angled face would need coordinate rotation that this starter does not implement.

Version 1 uses a dev board's existing power circuit. Do not add a second USB supply in parallel or connect to car wiring. The optional RGB indicator is not wired or supported by this starter firmware yet.
