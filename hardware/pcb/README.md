# Carrier PCB design brief

**No KiCad schematic, layout, or manufacturing files exist yet.**

Make a small carrier for the selected dev board, IMU, display connector, and button. Using modules keeps the first revision manageable. The wiring draft is in [../wiring.md](../wiring.md).

1. Select exact modules; measure them and obtain their schematics and mechanical drawings.
2. Draw the real schematic with 3.3 V power, a shared ground, I²C, and the button.
3. Verify symbols and footprints against actual pin ordering and pitch.
4. Place the IMU on a flat section and mark X forward / Y left on silkscreen.
5. Keep the ESP32 antenna end clear of copper and nearby hardware, following its module documentation.
6. Add mounting holes matched to the enclosure and accessible test points.
7. Check connector accessibility, I²C pull-ups, clearances, then run ERC and DRC.
8. Export schematics, board screenshots, BOM and Gerbers only after review.

Save source files here as `drivedot.kicad_pro`, `drivedot.kicad_sch`, and `drivedot.kicad_pcb`. Store fabrication exports in `fabrication/` with the revision identified. Empty briefs are not manufacturing-ready designs.
