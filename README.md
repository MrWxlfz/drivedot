# DriveDot

A small dashboard gadget that shows how smooth your driving is.

DriveDot is an ESP32-S3 with an IMU and a tiny OLED. It reads acceleration, braking, and cornering, draws a live G-force dot on the screen, and gives you a summary when the drive ends. It runs off USB and doesn't touch the car's electronics at all.

I'm learning to drive, so I wanted my first hardware project to be something I'd actually use. This is my warm-up project for Hack Club Half-Life.

## Where it's at

Early. I used AI to scaffold this repo, so the structure and starter code came from that, and I'm doing the real design and bench work now. The motion and event logic has host tests that pass. The ESP32 firmware hasn't been tried on real hardware yet. There's no custom PCB, no enclosure, and nothing has been road-tested, so I'm not claiming any accuracy numbers.

- **Done:** concept, requirements, wiring plan
- **Written, not tested on hardware:** ESP32 firmware and OLED UI
- **Tested on my computer:** motion/event logic
- **Rough:** parts list (budget targets, no supplier quotes yet)
- **Still to do:** PCB in KiCad, enclosure (after I measure the actual modules), journal and demo evidence

## Version 1

- ESP32-S3 dev board, MPU6050 breakout, 128×64 SSD1306 OLED over I²C
- Calibrate while parked before each session
- Live forward/lateral acceleration with a G-force dot
- Button to start and stop, then a summary with peak G and sustained-event counts
- CSV over USB serial so I can sanity-check the numbers
- LED feedback if the basics work and I have time

The score is a rough smoothness heuristic, not a safety grade. Hills, bumps, sensor drift, and a shifted mounting angle all throw it off. Check the summary while parked. Live feedback is really meant for a passenger during testing. Mount it solidly, out of your line of sight and away from airbags.

## Running it

1. Read the [build plan](docs/build-plan.md) and [wiring](hardware/wiring.md).
2. Choose exact parts and put real prices in the [BOM](hardware/bom.csv).
3. Open `firmware/` in VS Code with PlatformIO. Use the `esp32-s3-devkitc-1` board for the N8/no-PSRAM version.
4. Build, upload through the board's USB-to-UART port, and open the serial monitor:

```sh
   cd firmware
   pio run
   pio run --target upload
   pio device monitor
```

   Other ESP32-S3 variants may need a different board config. See [firmware setup](docs/firmware.md).

5. Keep the device still, send `c` to calibrate, then `n` to start a session and `e` to end it. Once it's calibrated, the button toggles a session too.
6. Log what you actually did in the [journal](journal/README.md), with screenshots and real time spent.

To run the motion tests without a microcontroller:

```sh
python3 scripts/test.py
```

## What's where

- `firmware/`: PlatformIO project, OLED/IMU code, motion logic and its tests
- `hardware/`: wiring, BOM, PCB and enclosure briefs
- `docs/`: build plan, firmware notes, validation, references
- `journal/`: work log (empty until I actually do the work)
- `.github/workflows/`: automated host tests and firmware build

## Half-Life

This is for the warm-up round: Tier 1, $30 for parts and 10 hours of design time, due Sunday, October 4 at 11:59 PM. The event page doesn't state a timezone, so I'm checking that along with the current rules and how AI-assisted work counts. The budget here is a target, not a quote or a promise of funding.

Before I submit, I need to finish the real schematic, PCB, and CAD files, lock the BOM, and show evidence of my own design work. A scaffolded repo doesn't count as ten hours.

## License

MIT. See [LICENSE](LICENSE).
