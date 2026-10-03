# DriveDot enclosure — revision A

A dimensioned CAD design with seven printable solids, STEP files and generated images. **It has not been printed or physically fitted.** The checks in [validation.json](validation.json) cover the actual CAD/STL geometry against simplified electronic envelopes, not the dimensions of purchased modules.

![Assembled CAD](renders/assembled.png)

![Exploded CAD](renders/exploded.png)

The screw-fastened case holds the carrier on four standoffs. A removable frame clamps the OLED into the lid; separate edge clamps hold the IMU flat in the base. A guided plunger and separately screwed cap operate the PCB switch with a travel stop. OLED and IMU mounting holes are not assumed.

## Files and regeneration

- [Editable CadQuery source](../../scripts/generate_enclosure.py)
- [STEP assembly](step/drivedot-assembly.step); individual parts also in `step/`
- [Dimension drawing](dimensions.svg)
- [Body STL](stl/body.stl), [lid STL](stl/lid.stl), [plunger STL](stl/button-plunger.stl), [cap STL](stl/button-cap.stl), [OLED clamp STL](stl/oled-clamp.stl), [left IMU clamp STL](stl/imu-clamp-left.stl), [right IMU clamp STL](stl/imu-clamp-right.stl)
- [Validation report](validation.json)

STLs are already placed on the print bed. Lid and button cap are inverted; all others rest on their lowest flat face. STEP parts retain assembly coordinates. The generated `exports/` meshes are temporary renderer inputs and are omitted from published files.

With Python packages `cadquery==2.7.0`, `vtk`, `numpy` and `Pillow`, run from the repository root:

```sh
python scripts/generate_enclosure.py
```

The source exports CAD/meshes, checks solid validity, checks printed-part intersections and selected electronic keepouts, checks STL boundary/nonmanifold edges, and renders with a CPU depth buffer. No X server is needed. Case width/depth/height/lid thickness, OLED position/PCB size, and switch height are primary parameters. Other dimensions are recorded in the manifest or beside their CAD features. Changing the carrier layout, stack heights, module thicknesses or sensor orientation requires updating associated features and envelopes together. This is not a universal module adapter. The reference drawing must be revised after dimensional changes.

## Mechanical contract

All dimensions are mm. Origin: outside front-left corner; +Y toward the back, +Z upward. Front is the USB side. Vehicle installation must follow verified IMU axes, rather than assuming case axes equal sensor axes.

| Feature | Revision A geometry |
|---|---|
| Case envelope | 90 × 76 × 34.4; button cap reaches Z = 37.65, excluding screw head |
| Walls and floor | 2.4; outside corner radius 5 |
| Lid location | 2-deep lip, nominal 0.30 side gap |
| Lid screws | (5,5), (85,5), (85,71), (5,71); 3.4 clearance |
| Carrier | 60 × 40 × 1.6; lower-left (15,9), bottom Z = 6.0 |
| Carrier holes | (19,13), (71,13), (71,45), (19,45); 3.2 PCB holes |
| USB opening | X = 22…42, Z = 10…26, through front wall |
| OLED PCB | 27 × 25 × 1.6, centre (60,26), bottom Z = 27.6 |
| OLED glass assumption | 24.7 × 16.5 × 2.4, centred on PCB; top Z = 31.6 |
| Screen window | 23.0 × 13.2, centre (60,26); active area assumed 21.744 × 10.864 |
| OLED rear header | 10.16 × 2.54 × 12 downward keepout, centre (60,37.23), Z = 15.6…27.6 |
| IMU PCB | 20 × 15 × 1.6, centre (55,62), bottom Z = 4.8 |
| IMU header | 20.32 × 2.54 × 12 upward keepout, centre (55,55.77), starts Z = 6.4 |
| IMU solder tails | Trim to at most 2.2 below PCB (prefer 2.0); keepout Z = 2.6…4.8 |
| Switch | Centre (32,39); actuator nominally 5.0 above carrier top |
| Plunger | 5.2 shaft in 5.8 bore; 0.20 initial actuator gap |
| Travel stop | Cap stops after 0.45 downward travel, giving nominal 0.25 switch compression |

The XIAO socket plus male spacer is modelled as an 11.0-high stack, plus 1.2 board and 3.5 USB shell. Its top reaches Z = 23.3. **These are estimates:** allow at least 16 above the carrier and measure the purchased sockets, pins and USB plug. The access opening is deliberately broad. Connector and antenna geometry are not vendor CAD.

The OLED frame bears on a 1 mm PCB perimeter and four nominally clear 1.4 × 1.4 PCB corners. Its central rear notch clears the header and wire harness. Put the OLED header toward +Y; a front-facing tall header would clash with the carrier connectors. If this rotates the displayed image, configure firmware rotation after testing. Measure the actual active-area offset and glass envelope before printing the lid. The glass sits 0.4 below the lid; the PCB is held between stops and frame.

IMU clamps contact only 0.8 mm of each side at its middle, leaving the 8-pin header edge exposed. The four underside support pads are beneath these middle contacts, away from header solder. The header faces −Y in this model. Verify all board margins are free of components and solder before tightening; move the pads in CAD if necessary. Keep the IMU rigid and horizontal.

## Fasteners and printing

| Fastener | Quantity | Purpose |
|---|---:|---|
| M3 × 10 | 4 | Lid |
| M3 × 6 | 4 | Carrier |
| M2 × 6 | 4 | OLED clamp |
| M2 × 6 | 4 | IMU clamps |
| M2 × 6 | 1 | Button cap |

These are required fasteners, not sourced purchases or verified prices. Printed pilots are 2.6 for M3 and 1.7 for M2. Test a coupon and ream/tap to suit the printer and screws; hand-tighten into plastic. No inserts are required. Use pan or button heads; the holes have no countersinks. Screw heads are not included in CAD collision checks: measure their diameter and height, verify clearance to adjacent parts, and avoid heads that contact electronics.

Start a bench fit prototype with a 0.4 nozzle, 0.2 layers and at least three walls. The body prints upright; the lid and cap print outside face down. The USB roof needs a 20 mm bridge or removable support, and the cap has a shallow socket bridge. Inspect the slicer preview. Printer tolerance and material performance are untested. The slicer determines filament use and time.

Two underside 12 × 52 × 0.6 recesses accept suitable non-slip or fastening material. Select and test a secure mount outside sightlines and airbag paths. Select material for measured cabin temperatures; the design has no automotive environmental qualification.

## Assembly

1. Check prints and clear pilots. Confirm the plunger slides freely. Insert it into the lid from inside, fit the cap outside, and attach with one M2 × 6. Confirm its travel stop and release.
2. Seat the OLED display outward, with the header at the rear notch. Attach its clamp with four M2 × 6. Check the PCB corners seat on stops without loading the glass or components.
3. Seat the IMU on the four base supports. Check trimmed solder-tail clearance, header orientation and clamp contact margins. Attach both rails using four M2 × 6; the board must stay flat without rattling.
4. Mount the carrier with four M3 × 6, fit modules and route wires clear of the button guide. Leave enough slack to open the lid. Measure the actual switch height and adjust the plunger if it differs from 5.0.
5. Dry-fit the lid and test USB insertion and button release. Close with four M3 × 10 only after checking cable and component clearance. Verify sensor axis signs and calibrate on a level bench.

CAD checks do not simulate wires, screw heads, mechanical force, print tolerance, thermal performance or exact purchased electronics. Physical measurements and a bench fit remain required before treating this as a fabrication-ready design.
