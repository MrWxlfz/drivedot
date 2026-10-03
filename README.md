# DriveDot

**A little dashboard device for smoother drives.**

DriveDot is a standalone ESP32-S3 motion monitor. The plan: read acceleration, braking, and cornering with an IMU, show a live G-force dot on a small OLED, and give a summary after each drive. USB powered, with no connection to the car's electronics.

I'm learning to drive, so I wanted to build hardware connected to something I'd actually use. This is my Hack Club Half-Life warm-up project.

## Current status

**Starter project / design in progress.** This repository was scaffolded with AI assistance. The measurement and event logic has automated host tests; the ESP32 firmware still needs a hardware bench test. No custom PCB, finished enclosure, or road-tested accuracy is claimed. This is not yet a complete design submission.

| Part | Status |
| --- | --- |
| Concept, requirements, wiring plan | Drafted |
| ESP32 firmware and OLED UI | Starter implementation; hardware untested |
| Motion/event logic | Host tests included |
| Parts list | Budget targets; supplier quotes still needed |
| Custom PCB | To design in KiCad |
| Enclosure | To model after measuring the chosen modules |
| Journal and demo evidence | To record during actual work |

## Version 1

- ESP32-S3 development board, MPU6050 breakout, 128×64 SSD1306 I²C OLED.
- Stationary calibration before a session.
- Live forward/lateral acceleration display and G-force dot.
- Start/stop button; session summary with peak G and sustained-event counts.
- CSV output over USB serial for checking measurements.
- Optional LED feedback after the basic prototype works.

The score is an experimental smoothness heuristic, **not a driving safety grade**. Hills, bumps, sensor drift, and changes in mounting angle affect it. Read summaries while parked; live feedback is mainly for a passenger during testing. Mount the device securely outside sightlines and airbag deployment areas.

## Start here

1. Read [the build plan](docs/build-plan.md) and [wiring](hardware/wiring.md).
2. Pick exact parts and fill in real prices in [the BOM](hardware/bom.csv).
3. Open `firmware/` in VS Code with PlatformIO. Choose `esp32-s3-devkitc-1` for the initial N8/no-PSRAM board.
4. Build and upload using the board's USB-to-UART port, then open the serial monitor:

   ```sh
   cd firmware
   pio run
   pio run --target upload
   pio device monitor
   ```

   A different ESP32-S3 variant may require a different board configuration. See [firmware setup](docs/firmware.md).

5. With the device stationary, send `c` to calibrate, then `n` to start. Send `e` to end. After calibration, the button also toggles a session.
6. Record what you actually did in [the journal](journal/README.md), with screenshots and real elapsed time.

Run the measurement tests without a microcontroller:

```sh
python3 scripts/test.py
```

## Repository map

| Path | Contents |
| --- | --- |
| `firmware/` | PlatformIO project, OLED/IMU code, portable motion logic and tests |
| `hardware/` | Wiring, BOM, PCB and enclosure design briefs |
| `docs/` | Build plan, firmware instructions, validation and references |
| `journal/` | Empty work log template; no hours prefilled |
| `.github/workflows/` | Automated host tests and firmware build |

## Half-Life

The supplied warm-up screenshots show a design or finished-build submission and Tier 1 at $30 for parts / 10 hours of design time. They show a deadline of Sunday, October 4 at 11:59 PM, without specifying timezone. Check the event page for timezone, current rules, and how assisted work is counted. The parts budget below is a target, not a supplier quote or funding guarantee.

Before submitting a design, finish the real schematic, PCB and CAD files, confirm your BOM, and attach evidence of your own design work. Repository setup and generated code do not establish ten hours of work.

## License

MIT; see [LICENSE](LICENSE).
