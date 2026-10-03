# Review the schematic

The revision A source and exports are in [hardware/pcb](../hardware/pcb/README.md). Open the supplied schematic in KiCad and follow these nets before assembling it.

| Net | Connections | Purpose |
| --- | --- | --- |
| +3V3 | XIAO 3V3 to both module connectors | Powers the selected 3.3V-compatible modules |
| GND | XIAO GND, both module connectors and button | Common return |
| SDA | XIAO D4 / GPIO5 to OLED and IMU SDA | I2C data |
| SCL | XIAO D5 / GPIO6 to OLED and IMU SCL | I2C clock |
| BUTTON | XIAO D3 / GPIO4 to normally-open button | Pulls low when pressed; firmware enables an internal pull-up |

The display and sensor connect with short wire harnesses. Their generic breakout footprints are not soldered directly to the carrier: received module sizes and pin orders can differ. Follow each connector's numbered pin labels and the actual breakout silkscreen. The OLED and IMU carrier connectors use different power-pin orders.

The GY-521's AD0 must be low for address `0x68`. Check its existing pull-down; wire AD0 to GND on the module if needed. Unused XDA, XCL and INT pins are left unconnected. The OLED is expected at `0x3C`.

Check both breakouts for I2C pull-ups and supply requirements. Pull-ups must reference 3.3V; do not add extra resistors without checking the combined resistance. Verify the GY-521's regulated sensor rail when supplied with 3.3V, since generic boards use different regulators. Do not compensate by feeding 5V to GPIO-connected pull-ups.

With power disconnected, use a meter to check that the switch closes GPIO4 to GND only when pressed. Check that 3V3 and GND are not shorted, and check each harness end-to-end before connecting it.

The CAD and electrical checks describe the design files. They do not verify soldering, received components or a physical prototype. Record what you inspect and change in your own journal, with the actual time spent.
