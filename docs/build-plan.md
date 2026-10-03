# Build plan

Revision A includes a carrier PCB, enclosure and standalone firmware. Start with [the assembly guide](assembly.md), [PCB files](../hardware/pcb/README.md) and [enclosure files](../hardware/enclosure/README.md).

## Before ordering or printing

1. Review the schematic and check the selected module pinouts.
2. Confirm supplier checkout totals, fabrication minimum quantities, shipping and tax. The $30 total is still unverified.
3. Measure the received XIAO headers/USB connector, OLED glass and board, GY-521 board, switch and fasteners. Update the CAD parameters where needed.
4. Inspect the fabrication and CAD checks, then review Gerbers in the manufacturer's viewer and STLs in a slicer.

## Bench prototype

1. Test the modules with short wires before committing the assembly to the case.
2. Compile and upload the firmware; check stationary readings over USB serial.
3. Hold the button to calibrate while still, then short-press to start and end a session.
4. Test a straight push and stop, then sideways motion. Verify sensor axes and signs using recorded data.
5. Test button debounce, sensor failure handling and recalibration. Change wiring only with power disconnected.
6. Fit the parts, verify plunger travel and connector clearance, then repeat the stationary test in the closed enclosure.

## Evidence still needed

- [ ] Received module measurements and physical fit check.
- [ ] Exact purchased parts, fabrication and checkout totals.
- [ ] Assembled PCB power and continuity checks.
- [ ] Firmware upload and real sensor/display/button results.
- [ ] Calibration and motion recordings.
- [ ] Photos, demo and journal with actual work time.
- [ ] Event eligibility, AI-assistance rules, deadline timezone and submission requirements checked.

The source and exports were created with AI assistance. Automated checks and rendered views are design evidence, not photographs or proof of a built device. The event's synced `BOM.md` and `JOURNAL.md` remain managed by Half-Life; log only real work and purchases there.
