# Revision A assembly

This is an unbuilt prototype design. Use the [PCB notes](../hardware/pcb/README.md) and [enclosure notes](../hardware/enclosure/README.md) for the exact sources, fabrication settings, fasteners and dimensional assumptions.

## 1. Check the modules

Use the standard XIAO ESP32S3, a GY-521 MPU6050 and a four-pin I2C SSD1306 display. Confirm the actual voltage requirements, pin labels and dimensions. Measure the OLED glass as well as its PCB; the case must not press on the glass. Check the switch's joined leg pairs with a meter.

The carrier is 60 × 40 mm. Its four mounting holes are at `(4,4)`, `(56,4)`, `(56,36)` and `(4,36)` mm from the PCB drawing origin. Keep the XIAO USB connector facing the marked board edge. The screen and IMU are mounted separately and connect with wire harnesses.

## 2. Assemble the carrier

With USB disconnected, solder the sockets, module connectors and switch using the placement drawing. Keep sockets square and check the XIAO orientation before inserting it. Leave the optional R1/R2 pull-up footprints empty until the breakout pull-ups have been checked. Inspect solder joints and measure for a 3V3-to-GND short.

Make the two harnesses by net name. **Do not assume both connectors have the same pin order.** The carrier OLED connector is GND, 3V3, SCL, SDA; the IMU connector is 3V3, GND, SCL, SDA. Check every wire end-to-end against the labels on the received modules. Keep wiring short and clear of screw bosses and the moving button.

## 3. Bring it up on the bench

Use a known USB data cable and follow [firmware setup](firmware.md). First confirm power, then display and IMU communication. Disconnect power immediately if a part becomes hot. If a module is absent or a read fails, fix the wiring before starting a session.

Keep the IMU rigid and flat, with sensor X forward, sensor Y left and sensor Z up. Verify the chip axes against its documentation and motion data; the PCB arrow on a generic module is not sufficient. The firmware uses a fixed mounting frame and does not compensate for arbitrary sensor tilt. Its sign settings can reverse X/Y directions but cannot swap the two axes. The rectangular IMU cradle does not allow a 90-degree module rotation: orient the whole case to suit the sensor, or revise the cradle/firmware axis mapping before fabrication.

Hold the button for 1.5 seconds while idle and still to calibrate. Release it after the hold; that release should not start a session. A short press/release starts or ends a session. Inspect USB CSV readings at rest and during gentle movements before enclosing the device.

## 4. Fit the enclosure

Print the separate parts in the orientations described in the [enclosure guide](../hardware/enclosure/README.md). Dry-fit without electronics first. Clear the screw holes and check lid registration. The plunger assumes a switch actuator 5.0 mm above the carrier; measure yours and adjust the CAD if needed. Insert the plunger from inside the lid, fit its separate cap outside, and secure it with one M2 × 6 screw. Check free movement, release and the cap's travel stop.

Install the carrier and seat the IMU flat in its cradle, with its header toward the USB side (−Y). Trim IMU solder tails to at most 2.2 mm below the PCB, preferably 2.0 mm. Fit the OLED with its header toward the rear (+Y), through the clamp's notch; a tall front-facing header would hit the carrier connectors. Configure display rotation in the firmware if this orientation turns the image upside down. Tighten the clamps only enough to retain the boards, route wires clear of the plunger, and verify USB access and button return before closing the lid.

Use the specified screw lengths. A screw that is too long can hit a PCB or crack a printed boss. Do not substitute lengths blindly. The mounting surface must keep the sensor level; an angled dashboard needs a separate leveling mount, which is not included in this revision.

## 5. Record the result

Repeat calibration and button tests with the case closed, take photos and record the actual findings. Inspect heat and mounting stability before any vehicle test. Calibrate and review the summary while parked; use a passenger for observing live feedback during testing. This prototype's score is a rough motion metric, not a safety grade.
