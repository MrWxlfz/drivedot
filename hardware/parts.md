# Selected parts

Supplier listings checked October 2, 2026. No orders have been placed.

| Part | Exact selection | Buy quantity | Listed USD price | Supplier |
| --- | --- | --- | --- | --- |
| Controller | Seeed Studio XIAO ESP32S3, SKU 113991114, standard unsoldered 1pcs | 1 | $7.49 | [Seeed](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html) |
| Motion sensor | GY-521 MPU6050, SEN-03-004 | 1 | $1.96 | [ElectroPeak](https://electropeak.com/gyro-accelerometer-gy521-mpu6050) |
| Screen | 0.96-inch SSD1306 I2C OLED, LCD-01-125; white option preferred | 1 | $1.29 base listing | [ElectroPeak](https://electropeak.com/0-96-inch-i2c-oled-display-module-ssd1306) |
| Button | 6mm through-hole tactile switch, Adafruit product 367 | 1 pack of 20 | $2.50 for the whole pack | [Adafruit](https://www.adafruit.com/product/367) |

These four listings total **$13.24 before shipping, tax or import charges**. Screen option pricing must be confirmed. The full button pack is counted, not a fictional one-button checkout price. If a suitable button is already available or can be bought from another selected supplier, replace that line with the real source and price to avoid a third shipment.

## Budget check

Unquoted allowances from the draft: headers/wire $1.50, PCB fabrication $5.00, enclosure/fasteners $2.00 and a USB-C data cable $2.00. These bring the provisional subtotal to **$23.74**, leaving **$6.26** for all delivery costs, taxes and overruns within $30.

That is a tight budget across multiple suppliers and a PCB manufacturer. **The complete Tier 1 budget is not verified.** Do not enter the allowances as real vendor quotes or treat an empty shipping cell as zero. Confirm checkout totals and fabrication pricing; reduce shipping through available supplies or consolidated sourcing, or revise scope/funding tier under the event rules.

## Why this controller

The XIAO has a compact form factor and a documented pinout and KiCad resources. The firmware now selects `seeed_xiao_esp32s3` and uses D4/GPIO5 for SDA, D5/GPIO6 for SCL and D3/GPIO4 for the button. It replaces the generic DevKitC configuration in the starter.

- [Seeed pinout, power details and CAD resources](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- [PlatformIO XIAO ESP32S3 board](https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32s3.html)

Version 1 remains USB powered. It does not need a battery, Grove base, camera expansion board or RGB strip.

## Before committing footprints

Use the module schematics and received board markings. Keep I2C at 3.3V, inspect the GY-521 regulator and pull-ups, check OLED address and pin order, and measure headers and mounting holes. Cheap generic breakouts can differ between batches. Supplier dimensional claims are starting points, not a completed mechanical fit check.

## Half-Life parts entry

Add actual selected purchases to the project's parts form with their vendor URLs and full purchase quantities. Enter shipping/tax separately from checkout quotes. `hardware/bom.csv` is a planning sheet; the event's synced root `BOM.md` should remain managed by the event.
