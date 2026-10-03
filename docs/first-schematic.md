# First KiCad session

Goal: draw the carrier connections yourself and understand each net before laying out copper. This is a walkthrough, not a completed schematic or a logged session.

1. Create a KiCad project named `drivedot` in `hardware/pcb/`.
2. Open Schematic Editor. Use the XIAO symbol and footprint resources linked from [Seeed's official page](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/). Read their license before redistributing them.
3. Add connector symbols for the actual OLED and GY-521 modules, plus a normally-open push-button symbol. Use the exact module header pin order; don't assign an unverified footprint.
4. Draw these connections:

| Net | Connections |
| --- | --- |
| +3V3 | XIAO 3V3 to IMU VCC and OLED VCC |
| GND | XIAO GND to IMU GND, OLED GND and one switched button contact |
| SDA | XIAO D4/GPIO5 to IMU SDA and OLED SDA |
| SCL | XIAO D5/GPIO6 to IMU SCL and OLED SCL |
| SESSION_BUTTON | XIAO D3/GPIO4 to the other switched button contact |
| IMU_ADDRESS | GY-521 AD0 to GND for address 0x68; verify its existing pull-down |

5. Inspect the selected breakout schematics for I2C pull-ups. Add pull-ups to 3.3V only if needed; don't blindly parallel extra pairs. Leave unused IMU XDA, XCL and INT unconnected.
6. Label the nets, annotate the symbols and run ERC. Resolve genuine errors; investigate power-pin warnings rather than suppressing them with random flags.
7. Save a screenshot and a journal entry explaining the wiring, what you checked, what confused you, and the real time spent.

**Stop before PCB footprints** if you haven't confirmed the exact module pin order, header spacing or physical dimensions. A wiring diagram does not verify a footprint. Check the button with a meter so GPIO4 and GND reach opposite switched contacts, not two permanently joined legs.

[The wiring table](../hardware/wiring.md) and [parts list](../hardware/parts.md) are the references for this session.
