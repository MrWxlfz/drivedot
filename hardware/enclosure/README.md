# Enclosure design brief

**No CAD or print-ready enclosure exists yet.**

Target a compact wedge with a readable front display, one recessed button, and access to USB. Keep the IMU horizontal even if the screen is tilted. Final size depends on measured components.

- Start around 85 × 60 × 35 mm as a layout study, not a guaranteed fit.
- Begin with 2 mm walls; tune clearances with a small print coupon.
- Provide rigid PCB standoffs, removable lid screws, and USB cable strain relief.
- Prevent the IMU from flexing or rattling; avoid a soft moving mount inside the case.
- Provide a secure removable base outside windshield sightlines and airbag areas.
- Dashboard heat can deform PLA; evaluate material temperature ratings for the intended use.

Measure the exact OLED active area, mounting holes, PCB, dev-board USB location, header height and button travel. Finish source CAD here plus `body.stl`, `lid.stl`, and an assembled view. Fit-check before calling it ready to print.
