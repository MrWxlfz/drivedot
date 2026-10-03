#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
pcb=hardware/pcb
mkdir -p "$pcb/exports" "$pcb/validation" "$pcb/fabrication"
# Never leave an old manufacturing ZIP available if a new design fails checks.
rm -f "$pcb/drivedot-rev-a-gerbers.zip" "$pcb/validation/summary.json"
kicad-cli sch erc --exit-code-violations --severity-all -o "$pcb/validation/erc.rpt" "$pcb/drivedot.kicad_sch"
kicad-cli pcb drc --exit-code-violations --schematic-parity --severity-all -o "$pcb/validation/drc.rpt" "$pcb/drivedot.kicad_pcb"
kicad-cli sch export svg -o "$pcb/exports/" "$pcb/drivedot.kicad_sch"
kicad-cli sch export pdf -o "$pcb/exports/drivedot-schematic.pdf" "$pcb/drivedot.kicad_sch"
kicad-cli sch export netlist --format kicadxml -o "$pcb/exports/drivedot-netlist.xml" "$pcb/drivedot.kicad_sch"
kicad-cli pcb export svg --layers F.Cu,B.Cu,F.Silkscreen,Edge.Cuts --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$pcb/exports/drivedot-board.svg" "$pcb/drivedot.kicad_pcb"
kicad-cli pcb export svg --layers F.Cu,F.Silkscreen,Edge.Cuts --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$pcb/exports/drivedot-front.svg" "$pcb/drivedot.kicad_pcb"
kicad-cli pcb export svg --layers B.Cu,Edge.Cuts --mirror --mode-single --fit-page-to-board --exclude-drawing-sheet -o "$pcb/exports/drivedot-back.svg" "$pcb/drivedot.kicad_pcb"
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts -o "$pcb/fabrication/" "$pcb/drivedot.kicad_pcb"
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path "$pcb/validation/drill.rpt" -o "$pcb/fabrication/" "$pcb/drivedot.kicad_pcb"

python3 - <<'PYEXPORT'
from pathlib import Path
import hashlib, json, re, subprocess, zipfile
p = Path('hardware/pcb')
erc = (p/'validation/erc.rpt').read_text()
drc = (p/'validation/drc.rpt').read_text()
def count(pattern, report):
    m = re.search(pattern, report)
    if not m:
        raise RuntimeError('Could not parse validation report: ' + pattern)
    return int(m.group(1))
summary = {
    'tool': 'KiCad ' + subprocess.check_output(['kicad-cli','version'], text=True).strip(),
    'erc_violations': count(r'ERC messages:\s*(\d+)', erc),
    'drc_violations': count(r'Found (\d+) DRC violations', drc),
    'unconnected_items': count(r'Found (\d+) unconnected pads', drc),
    'schematic_parity_issues': count(r'Found (\d+) Footprint errors', drc),
    'physical_prototype_tested': False,
    'files_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in [p/'drivedot.kicad_sch', p/'drivedot.kicad_pcb']},
}
for field in ['erc_violations','drc_violations','unconnected_items','schematic_parity_issues']:
    if summary[field]:
        raise RuntimeError('Validation failed; fabrication ZIP was not generated')
# KiCad was run with --severity-all, so excluded errors would also be reported.
summary['exclusions'] = 0
allowed = {'.gtl','.gbl','.gts','.gbs','.gto','.gbo','.gm1','.gbrjob','.drl'}
files = [f for f in sorted((p/'fabrication').iterdir()) if f.suffix in allowed]
required = {'drivedot-F_Cu.gtl','drivedot-B_Cu.gbl','drivedot-F_Mask.gts',
            'drivedot-B_Mask.gbs','drivedot-Edge_Cuts.gm1','drivedot-PTH.drl',
            'drivedot-NPTH.drl'}
if not required.issubset({f.name for f in files}):
    raise RuntimeError('Manufacturing exports are incomplete')
with zipfile.ZipFile(p/'drivedot-rev-a-gerbers.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, f.name)
summary['fabrication_zip_sha256'] = hashlib.sha256((p/'drivedot-rev-a-gerbers.zip').read_bytes()).hexdigest()
(p/'validation/summary.json').write_text(json.dumps(summary, indent=2)+'\n')
# Optional preview dependency: remove old images before attempting regeneration.
previews = [('drivedot.svg','drivedot-schematic.png'),
            ('drivedot-board.svg','drivedot-board.png'),
            ('drivedot-front.svg','drivedot-front.png'),
            ('drivedot-back.svg','drivedot-back.png')]
for src, dest in previews:
    (p/'exports'/dest).unlink(missing_ok=True)
try:
    import cairosvg
except ImportError:
    print('Fabrication ZIP and validation refreshed. Install CairoSVG to regenerate optional PNG previews; current SVG previews are available.')
else:
    for src, dest in previews:
        cairosvg.svg2png(url=str(p/'exports'/src), write_to=str(p/'exports'/dest),
                        output_width=1600 if src=='drivedot.svg' else 1200)
    print('Fabrication ZIP, validation hashes and PNG previews refreshed.')
PYEXPORT
