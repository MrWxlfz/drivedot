# Footprint evidence and authorship

Checked October 2, 2026. The schematic symbols, footprint graphics, routing generator and carrier design in this directory were created for DriveDot with AI assistance. They use the repository's MIT license. No supplier CAD artwork, logo, footprint file or 3D model is redistributed in this directory. Numerical dimensions and electrical connections are taken from the sources below; the vendor names identify compatible purchased parts.

| Source | Used to verify |
| --- | --- |
| [Seeed XIAO ESP32S3 documentation](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/) | D3/GPIO4, D4/GPIO5/SDA, D5/GPIO6/SCL; 3V3 regulated output; standard board envelope 21 × 17.8 mm; external antenna connector; header assembly |
| [Seeed official XIAO footprint archive](https://files.seeedstudio.com/wiki/XIAO-KiCad-Library/New_XIAO_Series_Footprints.zip), `XIAO-ESP32-S3-DIP.kicad_mod` | Fourteen through-hole centres at ±7.62 mm across rows, 2.54 mm along rows; physical numbering; USB orientation and approximate overhang |
| [ElectroPeak LCD-01-125 OLED](https://electropeak.com/0-96-inch-i2c-oled-display-module-ssd1306) | GND, VCC, SCL, SDA connector mapping; 3.3 V supply option. Module is wired off-board; no assumed module footprint is used |
| [ElectroPeak SEN-03-004 GY-521](https://electropeak.com/gyro-accelerometer-gy521-mpu6050) | VCC/GND/SCL/SDA roles, 3.3 V supply listing, default `0x68` address with AD0 low; listing itself flags generic-board revision variation |
| [Adafruit 367](https://www.adafruit.com/product/367), linked example 6 mm switch datasheet | Nominal 6 mm tactile body; 6.5 × 4.5 mm standard lead arrangement. Received-switch contact pairing and actuator height remain physical checks |
| [KiCad switch footprint source](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Button_Switch_THT.pretty/SW_PUSH_6mm.kicad_mod) | Independent cross-check of the 6.5 × 4.5 mm pattern and horizontally paired duplicate switch terminals; footprint was redrawn, not copied |

The original Seeed footprint uses a 0.889 mm through-hole drill. DriveDot's independent socket carrier footprint deliberately uses 1.0 mm drills with 1.8 mm pads for standard 0.64 mm square socket leads. Header fit still requires a physical check. Generic off-board modules are connected by their printed labels because variant layouts and header orders differ.

DNP resistor and header footprints use standard 2.54/7.62 mm connector and axial lead pitches, not claims about an unselected vendor part. Matching sockets, wire and any optional resistors need final sourcing. The shared project budget remains unquoted for those items and for PCB delivery.
