#!/usr/bin/env python3
"""Generate DriveDot rev A mechanical design. Requires cadquery 2.7, vtk, Pillow.

Units: mm. Coordinates are shared with hardware/pcb. This is the editable CAD
source; the STEP/STL files are generated outputs. No measured fit is implied.
"""
from pathlib import Path
import json
import hashlib
import math
import cadquery as cq

OUT = Path(__file__).resolve().parents[1] / 'hardware' / 'enclosure'
for folder in ['stl', 'step', 'renders', 'exports']:
    (OUT / folder).mkdir(parents=True, exist_ok=True)

# Dimension manifest plus primary parameters. W/D/H/T, OLED position/board size,
# PCB standoff position/height, and switch height are wired below. Other values
# document feature-local dimensions: edit those CAD features together. Changing
# board layout requires corresponding PCB/enclosure coordinates to be updated.
P = dict(width=90., depth=76., body_height=32., lid_thickness=2.4,
         wall=2.4, floor=2.4, corner=5., pcb_x=15., pcb_y=9.,
         pcb_bottom=6., pcb_thickness=1.6, pcb_width=60., pcb_depth=40.,
         oled_x=60., oled_y=26., oled_w=27., oled_d=25.,
         oled_total_height=4., oled_bottom=27.6,
         imu_x=55., imu_y=62., imu_w=20., imu_d=15., imu_bottom=4.8,
         imu_pcb_thickness=1.6, switch_height=5.0,
         pilot_m2=1.7, pilot_m3=2.6, clearance_m2=2.4, clearance_m3=3.4)
W,D,H,T=P['width'],P['depth'],P['body_height'],P['lid_thickness']
OX,OY,OW,OD=P['oled_x'],P['oled_y'],P['oled_w'],P['oled_d']
IX,IY,IW,ID=P['imu_x'],P['imu_y'],P['imu_w'],P['imu_d']
PX,PY,PZ=P['pcb_x'],P['pcb_y'],P['pcb_bottom']
# Other documented dimensions remain editable at their feature definitions.


def box(w,d,h,x,y,z):
    return cq.Workplane('XY').box(w,d,h,centered=(True,True,False)).translate((x,y,z))

def rounded(w,d,h,r,x,y,z):
    return box(w,d,h,x,y,z).edges('|Z').fillet(r)

def cyl(d,h,x,y,z):
    return cq.Workplane('XY').circle(d/2).extrude(h).translate((x,y,z))

def hole(s,d,h,x,y,z):
    return s.cut(cyl(d,h,x,y,z))

def slot(w,d,h,x,y,z):
    return cq.Workplane('XY').slot2D(w,d).extrude(h).translate((x,y,z))

lid_screws = [(5,5),(W-5,5),(W-5,D-5),(5,D-5)]
pcb_screws = [(PX+4,PY+4),(PX+56,PY+4),(PX+56,PY+36),(PX+4,PY+36)]
oled_screws = [(OX-19,OY-16),(OX+19,OY-16),(OX-19,OY+16),(OX+19,OY+16)]
imu_screws = [(44.8,51.8),(44.8,72.2),(65.2,51.8),(65.2,72.2)]

# Body, open at top. Broad front opening admits the USB plug through the wall.
body = rounded(W,D,H,5,W/2,D/2,0).cut(
    rounded(W-4.8,D-4.8,H,2.6,W/2,D/2,2.4))
body = body.cut(rounded(20,12,16,2,32,0,10))
for x,y in lid_screws:
    body=body.union(cyl(8,H-2.4,x,y,2.4))
    body=hole(body,2.6,9.1,x,y,H-9)
for x,y in pcb_screws:
    body=body.union(cyl(7,PZ-2.4,x,y,2.4))
    body=hole(body,2.6,PZ+.2,x,y,-.1)

# Four supports keep IMU PCB flat, 2.4mm above the floor. Locating walls leave
# 0.4mm clearance per side; clamp rails secure both side margins independently.
for x in [46.3,63.7]:
    for y in [60,64]:
        body=body.union(box(2.0,2.0,2.4,x,y,2.4))
for y in [53.7,70.3]:
    body=body.union(box(20.8,1.0,3.4,55,y,2.4))
for x,y in imu_screws:
    body=body.union(cyl(5.2,4.0,x,y,2.4))
    body=hole(body,1.7,5.8,x,y,.7)

# Recessed pads for non-slip strips (user-supplied, 1mm nominal) on bottom.
for x in [12,78]:
    body=body.cut(rounded(12,52,.65,2,x,38,-.05))

# Lid print is inverted: outer face on build plate, all features grow upward.
lid=rounded(W,D,T,5,W/2,D/2,H)
for x,y in lid_screws:
    lid=hole(lid,3.4,T+.6,x,y,H-.1)
# 0.30mm lateral gap to case; split locating lips avoid the screw towers.
for x in [3.3,W-3.3]:
    lid=lid.union(box(1.2,D-25,2,x,D/2,H-2))
for y in [3.3,D-3.3]:
    lid=lid.union(box(W-25,1.2,2,W/2,y,H-2))
lid=lid.cut(rounded(23.0,13.2,T+2,1.0,OX,OY,H-1))
# OLED lateral guides. Clearance 0.4mm each side of a 27x25mm board.
for x in [OX-OW/2-.9,OX+OW/2+.9]:
    lid=lid.union(box(1.0,OD+.8,4.4,x,OY,H-4.4))
for y in [OY-OD/2-.9,OY+OD/2+.9]:
    lid=lid.union(box(OW+2.8,1.0,4.4,OX,y,H-4.4))
# M2 screws enter from the internal clamp and thread into blind lid bosses.
for x,y in oled_screws:
    lid=lid.union(cyl(6.2,4.4,x,y,H-4.4))
    lid=hole(lid,1.7,5.6,x,y,H-4.5)

# Button supported by a long coaxial sleeve, with flange stop at lower end.
button_x,button_y=PX+17,PY+30
switch_top=P['pcb_bottom']+P['pcb_thickness']+P['switch_height']
plunger_bottom=switch_top+.2
flange_top=plunger_bottom+1.2
guide_bottom=flange_top+.2
lid=lid.union(cyl(10,H-guide_bottom,button_x,button_y,guide_bottom))
lid=hole(lid,5.8,H+T+2,button_x,button_y,0)
plunger=cyl(8.4,1.2,button_x,button_y,plunger_bottom).union(
    cyl(5.2,H+T+1.9-flange_top,button_x,button_y,flange_top))

# Removable screwed cap provides a 0.45mm downward stop at the lid.
# With 0.20mm initial gap, modeled maximum switch compression is 0.25mm.
plunger=hole(plunger,1.7,4.8,button_x,button_y,H+T-2.8)
button_cap=cyl(8.4,2.8,button_x,button_y,H+T+.45)
button_cap=hole(button_cap,5.4,1.55,button_x,button_y,H+T+.35)
button_cap=hole(button_cap,2.4,4,button_x,button_y,H+T+.1)
# PCB corner stops clamp display between lid and backing frame.
for x in [OX-OW/2+1,OX+OW/2-1]:
    for y in [OY-OD/2+1,OY+OD/2-1]:
        lid=lid.union(box(1.4,1.4,2.8,x,y,H-2.8))

# Removable OLED backing frame. Its 25x23 window bears on 1mm of each PCB
# margin; headers/components remain in the open central region. Shim as needed.
oled_clamp=rounded(OW+17,OD+13,2,2,OX,OY,H-6.4).cut(
    box(OW-2,OD-2,3,OX,OY,H-6.5))
for x,y in oled_screws:
    oled_clamp=oled_clamp.cut(slot(4.8,2.4,3,x,y,H-6.5))

# Rear OLED header/harness exits through a central notch in the backing frame.
oled_clamp=oled_clamp.cut(box(14,9,3,OX,OY+16,H-6.5))

# IMU clamp rails bear on nominal 0.8mm edge margins. X slots accommodate
# minor PCB width variation; vertical position is fixed by 6.4mm screw bosses.
imu_clamps=[]
for x in [44.8,65.2]:
    outer_x = x-1.5 if x < 55 else x+1.5
    rail=box(2.0,20.4,2,outer_x,62,6.4)
    tab_x=45.05 if x<55 else 64.95
    rail=rail.union(box(1.5,4,2,tab_x,62,6.4))
    for y in [51.8,72.2]:
        rail=rail.union(cyl(5.2,2,x,y,6.4))
        rail=rail.cut(slot(3.4,2.4,3,x,y,6.3))
    imu_clamps.append(rail)
    # Rear clamp end pad sits in a shallow wall relief; 1mm outer wall remains.
    body=body.cut(cyl(5.6,2.4,x,72.2,6.4))

parts={'body':body,'lid':lid,'button-plunger':plunger,
       'button-cap':button_cap,'oled-clamp':oled_clamp,'imu-clamp-left':imu_clamps[0],
       'imu-clamp-right':imu_clamps[1]}

# Simplified purchased-part keepout volumes. Actual vendor models supersede
# these during physical fit verification; USB and header heights are estimates.
pcb=box(60,40,1.6,PX+30,PY+20,PZ)
for x,y in pcb_screws:
    pcb=hole(pcb,3.2,2,x,y,PZ-.1)
xiao=box(17.8,21,1.2,32,20,18.6)
usb=box(9,7.5,3.5,32,10,19.8)
sockets=box(2.8,17.78,11.0,24.38,20,7.6).union(
    box(2.8,17.78,11.0,39.62,20,7.6))
headers=box(10.2,3,12,61.81,16,7.6).union(box(10.2,3,12,61.81,29,7.6))
switch=box(6,6,3.4,32,39,7.6).union(cyl(3.5,P['switch_height']-3.4,32,39,11))
oled_board=box(OW,OD,1.6,OX,OY,H-4.4)
oled_glass=rounded(24.7,16.5,2.4,.5,OX,OY,H-2.8)
oled_screen=box(21.744,10.864,.05,OX,OY,H-.4)
imu_board=box(20,15,1.6,55,62,4.8)
imu_chip=box(4,4,1,55,62,6.4)

electronics={'carrier-pcb':pcb,'xiao-pcb':xiao,'usb-envelope':usb,
             'xiao-sockets':sockets,'connector-keepouts':headers,
             'tactile-switch':switch,'oled-pcb':oled_board,
             'oled-glass':oled_glass,'oled-active-area':oled_screen,
             'imu-pcb':imu_board,'imu-chip':imu_chip,
             'imu-header-keepout':box(20.32,2.54,12,55,55.77,6.4),
             'imu-header-tails':box(20.32,2.54,2.2,55,55.77,2.6),
             'oled-header-keepout':box(10.16,2.54,12,OX,OY+11.23,H-16.4)}

def print_orientation(name,shape):
    # CAD exports retain assembly coordinates; STL print files sit on z=0.
    if name in ['lid','button-cap']:
        s=shape.rotate((0,0,0),(1,0,0),180)
    else:
        s=shape
    bb=s.val().BoundingBox()
    return s.translate((-bb.xmin,-bb.ymin,-bb.zmin))

for name,shape in parts.items():
    if not shape.val().isValid():
        raise RuntimeError(f'Invalid CAD solid: {name}')
    if len(shape.solids().vals()) != 1:
        raise RuntimeError(f'Expected one solid: {name}')
    cq.exporters.export(print_orientation(name,shape),str(OUT/'stl'/f'{name}.stl'),
                        tolerance=.06,angularTolerance=.12)
    cq.exporters.export(shape,str(OUT/'step'/f'{name}.step'))

assembly=cq.Assembly(name='DriveDot-revA')
colors={'body':(.13,.15,.18),'lid':(.18,.20,.24),
        'button-plunger':(.39,.65,.86),'button-cap':(.39,.65,.86),'oled-clamp':(.36,.39,.43),
        'imu-clamp-left':(.36,.39,.43),'imu-clamp-right':(.36,.39,.43),
        'carrier-pcb':(.03,.31,.19),'xiao-pcb':(.02,.27,.24),
        'usb-envelope':(.72,.74,.77),'xiao-sockets':(.10,.10,.11),
        'connector-keepouts':(.78,.56,.20),'tactile-switch':(.33,.34,.35),
        'oled-pcb':(.03,.21,.39),'oled-glass':(.025,.03,.045),
        'oled-active-area':(.10,.20,.25),'imu-pcb':(.10,.30,.56),
        'imu-chip':(.06,.07,.09),'imu-header-keepout':(.18,.19,.20),
        'imu-header-tails':(.60,.62,.65),'oled-header-keepout':(.18,.19,.20)}
for name,shape in {**parts,**electronics}.items():
    assembly.add(shape,name=name,color=cq.Color(*colors[name]))
assembly.save(str(OUT/'step'/'drivedot-assembly.step'))

# Geometric checks exercise the actual solids and nominal purchased envelopes.
# Contacts at mounting faces count as zero volume. Intentional screw engagement
# is not represented because screws are purchased hardware.
checks=[]
def clear(a,b):
    volume=parts[a].intersect(electronics[b]).val().Volume()
    checks.append({'first':a,'second':b,'intersection_mm3':round(volume,8),
                   'pass':volume<1e-6})
for name in parts:
    for ename in electronics:
        clear(name,ename)
for i,a in enumerate(parts):
    for b in list(parts)[i+1:]:
        volume=parts[a].intersect(parts[b]).val().Volume()
        checks.append({'first':a,'second':b,'intersection_mm3':round(volume,8),
                       'pass':volume<1e-6})

# Targeted electronics keepout checks; contacting board and solder volumes are
# intentional and excluded from this selected interference matrix.
for a,b in [('oled-header-keepout','connector-keepouts'),
            ('oled-header-keepout','xiao-pcb'),
            ('oled-header-keepout','usb-envelope'),
            ('oled-header-keepout','xiao-sockets')]:
    volume=electronics[a].intersect(electronics[b]).val().Volume()
    checks.append({'first':a,'second':b,'intersection_mm3':round(volume,8),
                   'pass':volume<1e-6})

# Export assembly-position meshes only for rendering, not printing.
for name,shape in {**parts,**electronics}.items():
    cq.exporters.export(shape,str(OUT/'exports'/f'{name}.stl'),
                        tolerance=.10,angularTolerance=.15)

def render():
    # Small deterministic CPU z-buffer renderer: no OpenGL, X server or browser.
    import vtk
    import numpy as np
    from vtk.util.numpy_support import vtk_to_numpy
    from PIL import Image, ImageDraw, ImageFont
    meshes={}
    for name in {**parts,**electronics}:
        r=vtk.vtkSTLReader();r.SetFileName(str(OUT/'exports'/f'{name}.stl'));r.Update()
        data=r.GetOutput();xyz=vtk_to_numpy(data.GetPoints().GetData())
        ids=vtk_to_numpy(data.GetPolys().GetConnectivityArray()).reshape(-1,3)
        meshes[name]=xyz[ids].astype(np.float64)
    light=np.array([-.4,-.6,1.]);light/=np.linalg.norm(light)
    font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    def save(filename,title,subtitle,exploded=False,body_only=False):
        triangles=[];facecolors=[]
        for name,tri in meshes.items():
            if body_only and name!='body': continue
            dz=0;dx=0;dy=0
            if exploded:
                if name=='lid':dz=63
                elif name=='button-cap':dz=65
                elif name=='button-plunger':dz=42
                elif name=='oled-clamp':dz=31
                elif name.startswith('oled-'):dz=47
                elif name.startswith('imu-clamp'):dz=37;dx=20;dy=19
                elif name.startswith('imu-'):dz=22;dx=20;dy=19
                elif name in electronics:dz=20
            tr=tri.copy();tr+=np.array([dx,dy,dz])
            normals=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0])
            lengths=np.linalg.norm(normals,axis=1);lengths[lengths==0]=1
            normals/=lengths[:,None]
            diffuse=np.maximum(0,normals@light)
            brightness=.55+.45*diffuse
            shade=np.clip(brightness[:,None]*np.array(colors[name]),0,1)
            triangles.append(tr);facecolors.append(shade)
        tri=np.concatenate(triangles);rgb=(np.concatenate(facecolors)*255).astype(np.uint8)
        az=math.radians(-65);el=math.radians(38 if exploded else 44)
        near=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)])
        right=np.array([-math.sin(az),math.cos(az),0]);up=np.cross(near,right)
        projected=np.stack([tri@right,-tri@up,tri@near],axis=2)
        low=projected[:,:,:2].min(axis=(0,1));high=projected[:,:,:2].max(axis=(0,1))
        scale=min(1500/(high[0]-low[0]),1060/(high[1]-low[1]))
        center=(low+high)/2
        projected[:,:,0]=(projected[:,:,0]-center[0])*scale+900
        projected[:,:,1]=(projected[:,:,1]-center[1])*scale+760
        canvas=np.full((1400,1800,3),(240,242,245),dtype=np.uint8)
        depth=np.full((1400,1800),-np.inf,dtype=np.float32)
        for t,c in zip(projected,rgb):
            x0=max(0,int(np.floor(t[:,0].min())));x1=min(1799,int(np.ceil(t[:,0].max())))
            y0=max(0,int(np.floor(t[:,1].min())));y1=min(1399,int(np.ceil(t[:,1].max())))
            if x1<x0 or y1<y0:continue
            a,b,cpt=t
            den=(b[1]-cpt[1])*(a[0]-cpt[0])+(cpt[0]-b[0])*(a[1]-cpt[1])
            if abs(den)<1e-8:continue
            yy,xx=np.mgrid[y0:y1+1,x0:x1+1];xx=xx+.5;yy=yy+.5
            wa=((b[1]-cpt[1])*(xx-cpt[0])+(cpt[0]-b[0])*(yy-cpt[1]))/den
            wb=((cpt[1]-a[1])*(xx-cpt[0])+(a[0]-cpt[0])*(yy-cpt[1]))/den
            wc=1-wa-wb;z=wa*a[2]+wb*b[2]+wc*cpt[2]
            old=depth[y0:y1+1,x0:x1+1]
            mask=(wa>=-1e-7)&(wb>=-1e-7)&(wc>=-1e-7)&(z>old)
            old[mask]=z[mask];canvas[y0:y1+1,x0:x1+1][mask]=c
        img=Image.fromarray(canvas)
        d=ImageDraw.Draw(img)
        d.text((68,44),title,font=ImageFont.truetype(font_path,49),fill=(24,32,40))
        d.text((70,109),subtitle,font=ImageFont.truetype(font_path,24),fill=(85,97,108))
        d.text((70,1340),'REV A • CAD DESIGN • PHYSICAL FIT UNTESTED',font=ImageFont.truetype(font_path,20),fill=(85,97,108))
        img.save(OUT/'renders'/f'{filename}.png')
    save('assembled','DriveDot','90 × 76 × 34.4 mm enclosure • USB powered • replaceable modules')
    save('exploded','DriveDot / exploded','Screw-fastened lid • removable display clamp • rigid, flat IMU mount',True)
    save('body-interior','DriveDot / base','Four PCB standoffs • USB access • sensor cradle • four lid screw towers',body_only=True)

def validate_meshes():
    import vtk
    result={}
    for name in parts:
        r=vtk.vtkSTLReader();r.SetFileName(str(OUT/'stl'/f'{name}.stl'));r.Update()
        edge=vtk.vtkFeatureEdges();edge.SetInputConnection(r.GetOutputPort())
        edge.BoundaryEdgesOn();edge.NonManifoldEdgesOn();edge.FeatureEdgesOff();edge.ManifoldEdgesOff();edge.Update()
        n=edge.GetOutput().GetNumberOfCells()
        result[name]={'closed_manifold':n==0,'boundary_or_nonmanifold_edges':n,
                      'triangles':r.GetOutput().GetNumberOfCells(),
                      'solid_volume_mm3':round(parts[name].val().Volume(),3)}
    return result

meshes=validate_meshes()
report={'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'parameters_mm':P,'cad_solids_valid':True,'mesh_checks':meshes,
        'nominal_fit_checks':checks,'all_nominal_fit_checks_pass':all(c['pass'] for c in checks),
        'physical_fit_tested':False,'printer_tolerance_tested':False,
        'notes':['Generic module envelopes and socket heights remain assumptions.',
                 'Clamps contact PCB edge margins; inspect actual components before fitting.',
                 'Sensor axes must be verified against the actual module silkscreen.']}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'mesh_checks':meshes,'failed_nominal_fit_checks':[c for c in checks if not c['pass']]},indent=2))
render()
