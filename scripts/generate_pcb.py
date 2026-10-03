#!/usr/bin/python3
"""Rebuild original DriveDot carrier CAD using KiCad 9's pcbnew Python module.
No hours, measurements of physical parts, or hardware test results are generated.
"""
from pathlib import Path
import uuid, json, math, heapq, subprocess, xml.etree.ElementTree as ET
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'hardware/pcb'; OUT.mkdir(parents=True,exist_ok=True)
LIB=OUT/'DriveDot.pretty'; LIB.mkdir(exist_ok=True)
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/MrWxlfz/drivedot/revA/'+key))
def q(s):return json.dumps(str(s))
# Actual XIAO physical pads, viewed from component side, USB upward.
names={1:'D0/GPIO1',2:'D1/GPIO2',3:'D2/GPIO3',4:'D3/GPIO4',5:'D4/GPIO5/SDA',6:'D5/GPIO6/SCL',7:'D6/GPIO43',8:'D7/GPIO44',9:'D8/GPIO7',10:'D9/GPIO8',11:'D10/GPIO9',12:'3V3_OUT',13:'GND',14:'5V_USB'}
connections={'U1':{4:'BUTTON',5:'SDA',6:'SCL',12:'+3V3',13:'GND'},'J1':{1:'GND',2:'+3V3',3:'SCL',4:'SDA'},'J2':{1:'+3V3',2:'GND',3:'SCL',4:'SDA'},'SW1':{1:'BUTTON',2:'GND'},'R1':{1:'+3V3',2:'SDA'},'R2':{1:'+3V3',2:'SCL'}}
# Symbol pin definitions: number,name,x,y,angle,electrical type.
xpins=[]
for n in range(1,8):xpins.append((n,names[n],-20.32,15.24-(n-1)*5.08,0,'bidirectional'))
for n in range(14,7,-1):xpins.append((n,names[n],20.32,15.24-(14-n)*5.08,180,'power_out' if n==12 else 'passive'))
specs={'XIAO_ESP32S3':('U',xpins,(-15.24,20.32,15.24,-20.32)), 'OLED_4Pin':('J',[(n,s,-10.16,7.62-(n-1)*5.08,0,'passive') for n,s in enumerate(['GND','VCC','SCL','SDA'],1)],(-5.08,12.7,10.16,-12.7)), 'IMU_4Pin':('J',[(n,s,-10.16,7.62-(n-1)*5.08,0,'passive') for n,s in enumerate(['VCC','GND','SCL','SDA'],1)],(-5.08,12.7,10.16,-12.7)), 'Resistor':('R',[(1,'~',-7.62,0,0,'passive'),(2,'~',7.62,0,180,'passive')],(-3.81,1.27,3.81,-1.27)), 'Pushbutton':('SW',[(1,'~',-7.62,0,0,'passive'),(2,'~',7.62,0,180,'passive')],None)}
lib=[]
for name,(prefix,pins,rect) in specs.items():
 lines=[f'(symbol {q(name)} (pin_names (offset 0.8)) (in_bom yes) (on_board yes)',f'(property "Reference" {q(prefix)} (at 0 24 0) (effects (font (size 1.27 1.27))))',f'(property "Value" {q(name)} (at 0 21 0) (effects (font (size 1.27 1.27))))']
 g=[]
 if rect:
  a,b,c,d=rect;g.append(f'(rectangle (start {a} {b}) (end {c} {d}) (stroke (width 0.254) (type default)) (fill (type background)))')
 else:
  g += ['(polyline (pts (xy -5.08 0) (xy 5.08 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))','(polyline (pts (xy 0 2.54) (xy 0 5.08)) (stroke (width 0.254) (type default)) (fill (type none)))']
 lines.append(f'(symbol {q(name+"_0_1")} '+''.join(g)+')')
 lines.append(f'(symbol {q(name+"_1_1")}')
 for n,nm,x,y,ang,typ in pins:
  length=5.08 if name not in ['Resistor','Pushbutton'] else 3.81 if name=='Resistor' else 2.54
  lines.append(f'(pin {typ} line (at {x} {y} {ang}) (length {length}) (name {q(nm)} (effects (font (size 1.0 1.0)))) (number "{n}" (effects (font (size 1 1)))))')
 lines.append('))');lib.append('\n'.join(lines))
(OUT/'DriveDot.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator "drivedot")\n'+'\n'.join(lib)+'\n)\n')
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "DriveDot")(type "KiCad")(uri "${KIPRJMOD}/DriveDot.kicad_sym")(options "")(descr "Original DriveDot symbols")))\n')
(OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "DriveDot")(type "KiCad")(uri "${KIPRJMOD}/DriveDot.pretty")(options "")(descr "Original DriveDot footprints")))\n')
# positions all on a 50mil schematic grid.
components={'U1':('XIAO_ESP32S3',71.12,78.74,'XIAO ESP32S3','XIAO_Socket'), 'J1':('OLED_4Pin',172.72,58.42,'OLED / SSD1306','Header_1x04'), 'J2':('IMU_4Pin',172.72,104.14,'GY-521 / MPU6050','Header_1x04'), 'SW1':('Pushbutton',76.2,132.08,'Start / stop','Tactile_6mm'), 'R1':('Resistor',114.3,137.16,'4.7k DNP','R_Axial_P7.62'), 'R2':('Resistor',165.1,137.16,'4.7k DNP','R_Axial_P7.62')}
schid=uid('sheet'); sch=[f'(kicad_sch (version 20231120) (generator "eeschema") (uuid "{schid}") (paper "A4") (title_block (title "DriveDot | revision A carrier") (date "2026-10-02") (rev "A") (company "Luke Nordin / DriveDot") (comment 1 "USB-powered module carrier; physical prototype not tested")) (lib_symbols']
for definition,name in zip(lib,specs):sch.append(definition.replace(f'(symbol "{name}"',f'(symbol "DriveDot:{name}"',1))
sch.append(')')
for ref,(name,x,y,value,fp) in components.items():
 syuid=uid(ref);dn='(dnp yes)' if ref.startswith('R') else '(dnp no)'
 sch.append(f'(symbol (lib_id "DriveDot:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) {dn} (uuid "{syuid}") (property "Reference" "{ref}" (at {x} {y-24 if ref=="U1" else y-18 if ref.startswith("J") else y-10 if ref=="SW1" else y-8} 0) (effects (font (size 1.5 1.5)))) (property "Value" {q(value)} (at {x} {y-21 if ref=="U1" else y-15 if ref.startswith("J") else y-7 if ref=="SW1" else y-5} 0) (effects (font (size 1.2 1.2)))) (property "Footprint" "DriveDot:{fp}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide)) (instances (project "drivedot" (path "/{schid}" (reference "{ref}") (unit 1)))) )')
 for num,nm,px,py,ang,typ in specs[name][1]:
  xx,yy=x+px,y-py;net=connections[ref].get(num)
  if net:
   endx=xx+(-7.62 if ang==0 else 7.62)
   sch.append(f'(wire (pts (xy {xx:.4f} {yy:.4f}) (xy {endx:.4f} {yy:.4f})) (stroke (width 0) (type default)) (uuid "{uid(ref+str(num)+"wire")}"))')
   labelang=0 if ang==0 else 180
   sch.append(f'(label {q(net)} (at {endx:.4f} {yy:.4f} {labelang}) (effects (font (size 1.27 1.27)) (justify {"left" if ang==0 else "right"} bottom)) (uuid "{uid(ref+str(num)+"label")}"))')
  else:sch.append(f'(no_connect (at {xx:.4f} {yy:.4f}) (uuid "{uid(ref+str(num)+"nc")}"))')
notes=[(35.56,25.4,'DRIVEDOT / MODULE CARRIER'),(35.56,31.75,'XIAO USB-C is the only power input. All module VCC pins receive 3.3 V.'),(35.56,165.1,'J1: wire to OLED labels GND / VCC / SCL / SDA. J2: wire to IMU labels VCC / GND / SCL / SDA.'),(35.56,171.45,'GY-521 AD0 must be low for 0x68. Keep the IMU horizontal, rigidly mounted, and align axes.'),(35.56,177.8,'R1/R2 are optional pull-up footprints: DO NOT POPULATE until the breakout pull-ups are checked.'),(35.56,184.15,'D3 button uses firmware INPUT_PULLUP. No battery, car wiring, or radio functionality is used.')]
for x,y,s in notes:sch.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {1.6 if y==25.4 else 1.27} {1.6 if y==25.4 else 1.27})) (justify left bottom)) (uuid "{uid(s)}"))')
sch.append(')');(OUT/'drivedot.kicad_sch').write_text('\n'.join(sch)+'\n')
# Footprints are originals, numeric dimensions verified against reference resources.
def footprint(name,pads,body,courtyard):
 lines=[f'(footprint "{name}" (version 20240108) (generator "pcbnew") (layer "F.Cu") (attr {"board_only exclude_from_bom exclude_from_pos_files" if name=="MountingHole_M3" else "through_hole"})',f'(property "Reference" "REF**" (at 0 -12 0) (layer "F.SilkS") (effects (font (size 1 1)(thickness 0.15))))',f'(property "Value" "{name}" (at 0 12 0) (layer "F.Fab") (effects (font (size 1 1)(thickness 0.15))))']
 if body:
  x1,y1,x2,y2=body
  lines.append(f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.12)(type solid)) (fill none)(layer "F.Fab"))')
 if body and name!='Tactile_6mm':
  if name=='R_Axial_P7.62':x1,x2=1.3,6.32
  lines.append(f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.12)(type solid)) (fill none)(layer "F.SilkS"))')
 if name=='Tactile_6mm':
  for x1,y1,x2,y2 in [(-2,-3.2,2,-3.2),(-2,3.2,2,3.2),(-3,-1,-3,1),(3,-1,3,1)]:lines.append(f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.12)(type solid))(layer "F.SilkS"))')
 if courtyard:
  x1,y1,x2,y2=courtyard
  lines.append(f'(fp_rect (start {x1} {y1})(end {x2} {y2})(stroke (width 0.05)(type solid))(fill none)(layer "F.CrtYd"))')
 for num,x,y,diam,drill in pads:
  shape='rect' if num=='1' and name=='Header_1x04' else 'circle'
  typ='np_thru_hole' if num=='' else 'thru_hole'
  lines.append(f'(pad "{num}" {typ} {shape} (at {x} {y}) (size {diam} {diam}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
 lines.append(')');(LIB/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
xpads=[(str(n),-7.62,-7.62+(n-1)*2.54,1.8,1) for n in range(1,8)]+[(str(n),7.62,-7.62+(14-n)*2.54,1.8,1) for n in range(8,15)]
footprint('XIAO_Socket',xpads,(-8.9,-10.5,8.9,10.5),(-9.2,-10.8,9.2,10.8))
footprint('Header_1x04',[(str(n),2.54*(n-1),0,1.8,1) for n in range(1,5)],(-1.27,-1.27,8.89,1.27),(-1.55,-1.55,9.17,1.55))
footprint('Tactile_6mm',[('1',-3.25,-2.25,2,1.1),('1',3.25,-2.25,2,1.1),('2',-3.25,2.25,2,1.1),('2',3.25,2.25,2,1.1)],(-3,-3,3,3),(-4.5,-3.5,4.5,3.5))
footprint('R_Axial_P7.62',[('1',0,0,1.8,0.9),('2',7.62,0,1.8,0.9)],(0.7,-1.1,6.9,1.1),(-1.2,-1.4,8.82,1.4))
footprint('MountingHole_M3',[('',0,0,3.2,3.2)],None,(-2.9,-2.9,2.9,2.9))
b=p.BOARD(); b.SetCopperLayerCount(2)
def pt(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o','/tmp/drivedot-net.xml',str(OUT/'drivedot.kicad_sch')],check=True)
netdoc=ET.parse('/tmp/drivedot-net.xml');nets={};padnets={}
for i,node in enumerate(netdoc.findall('./nets/net'),1):
 n=node.attrib['name'];n=n.replace('/', '{slash}') if n.startswith('unconnected-') else n;ni=p.NETINFO_ITEM(b,n,i);b.Add(ni);nets[n.lstrip('/')]=ni
 for child in node.findall('node'):padnets[(child.attrib['ref'],child.attrib['pin'])]=ni
placements={'U1':(17,11),'J1':(43,7),'J2':(43,20),'SW1':(17,30),'R1':(30,27),'R2':(30,33)}
allpads=[]
for ref,(_,sx,sy,value,fpname) in components.items():
 fp=p.FootprintLoad(str(LIB),fpname);fp.SetReference(ref);fp.SetValue(value);fp.SetPosition(pt(*placements[ref]));fp.SetPath(p.KIID_PATH('/'+schid+'/'+uid(ref)));fp.SetFPID(p.LIB_ID('DriveDot',fpname))
 x,y=placements[ref];fp.Reference().SetPosition(pt(x+ (3.81 if ref.startswith('J') or ref.startswith('R') else 0),y+ (3 if ref.startswith('J') else -3 if ref.startswith('R') else 12 if ref=='U1' else -5)))
 fp.Value().SetVisible(False)
 if ref.startswith('R'):fp.SetAttributes(fp.GetAttributes()|p.FP_DNP)
 for pad in fp.Pads():
  nn=connections[ref].get(int(pad.GetNumber()));net=nn or ''
  pad.SetNet(padnets[(ref,pad.GetNumber())])
  x0,y0=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)
  allpads.append((x0,y0,p.ToMM(pad.GetSize().x)/2,net,ref,pad))
 b.Add(fp)
for i,(x,y) in enumerate([(4,4),(56,4),(56,36),(4,36)],1):
 fp=p.FootprintLoad(str(LIB),'MountingHole_M3');fp.SetReference('H'+str(i));fp.SetValue('M3');fp.SetPosition(pt(x,y));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);fp.SetAttributes(p.FP_BOARD_ONLY|p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);fp.SetFPID(p.LIB_ID('DriveDot','MountingHole_M3'));b.Add(fp);allpads.append((x,y,1.6,'HOLE','H'+str(i),None))
for a,c in [((0,0),(60,0)),((60,0),(60,40)),((60,40),(0,40)),((0,40),(0,0))]:
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(pt(*a));s.SetEnd(pt(*c));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
def text(s,x,y,size=.85):
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(pt(x,y));t.SetTextSize(pt(size,size));t.SetTextThickness(p.FromMM(.13));t.SetLayer(p.F_SilkS);b.Add(t)
text('DriveDot  Rev A',42,37,1.3);text('USB',17,1.7,.8)

for i,label in enumerate(['GND','3V3','SCL','SDA']):text(label,43+2.54*i,4,.8)
for i,label in enumerate(['3V3','GND','SCL','SDA']):text(label,43+2.54*i,17,.8)
text('OLED',46.8,11.5,.8);text('IMU',46.8,24.5,.8);text('START / STOP',17,36,.8);text('DNP',41,30,.8)
# Grid router uses conservative obstacle inflation; native KiCad DRC is authoritative.
STEP=.25;NX=241;NY=161;blocked=[{} for _ in range(2)]
def disk(layer,cx,cy,r,net):
 for ix in range(max(3,math.floor((cx-r)/STEP)),min(NX-3,math.ceil((cx+r)/STEP))+1):
  for iy in range(max(3,math.floor((cy-r)/STEP)),min(NY-3,math.ceil((cy+r)/STEP))+1):
   if math.hypot(ix*STEP-cx,iy*STEP-cy)<=r:blocked[layer].setdefault((ix,iy),set()).add(net)
for x,y,r,n,ref,pad in allpads:
 for z in range(2):disk(z,x,y,r+.35,n if n else ref)
def free(x,y,z,net):return 3<=x<NX-3 and 3<=y<NY-3 and not(blocked[z].get((x,y),set())-{net})
def route(a,d,net):
 start=(round(a[0]/STEP),round(a[1]/STEP));goal=(round(d[0]/STEP),round(d[1]/STEP))
 heap=[];cost={};prev={}
 for z in range(2):s=(*start,z);cost[s]=0;heapq.heappush(heap,(math.dist(start,goal),0,s))
 finish=None
 while heap:
  _,c,s=heapq.heappop(heap)
  if c!=cost.get(s):continue
  x,y,z=s
  if (x,y)==goal:finish=s;break
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1),(0,0)]:
   zz=1-z if dx==dy==0 else z;xx=x+dx;yy=y+dy
   if not free(xx,yy,zz,net):continue
   if dx and dy and (not free(x+dx,y,z,net) or not free(x,y+dy,z,net)):continue
   if zz!=z and any(not free(xx+ddx,yy+ddy,l,net) for l in range(2) for ddx,ddy in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]):continue
   nc=c+(12 if zz!=z else 1.41421356 if dx and dy else 1)
   ns=(xx,yy,zz)
   if nc<cost.get(ns,1e30):cost[ns]=nc;prev[ns]=s;heapq.heappush(heap,(nc+math.dist((xx,yy),goal),nc,ns))
 if finish is None:raise RuntimeError('Cannot route '+net+str((a,d)))
 path=[finish]
 while path[-1] in prev:path.append(prev[path[-1]])
 path.reverse()
 # Greedy line-of-sight smoothing preserves obstacle margins, reduces staircase routing.
 smooth=[path[0]];idx=0
 while idx<len(path)-1:
  chosen=idx+1
  for j in range(idx+1,len(path)):
   if path[j][2]!=path[idx][2]:break
   ax,ay,z=path[idx];bx,by,_=path[j];steps=max(1,math.ceil(math.hypot(bx-ax,by-ay)*3))
   if all(free(round(ax+(bx-ax)*k/steps),round(ay+(by-ay)*k/steps),z,net) for k in range(steps+1)):chosen=j
  smooth.append(path[chosen]);idx=chosen
 path=smooth
 # Compress collinear grid segments, retaining changes of layer.
 pts=[(a[0],a[1],path[0][2])]+[(x*STEP,y*STEP,z) for x,y,z in path]+[(d[0],d[1],path[-1][2])]
 clean=[]
 for v in pts:
  if clean and v==clean[-1]:continue
  while len(clean)>1 and clean[-2][2]==clean[-1][2]==v[2] and abs((clean[-1][0]-clean[-2][0])*(v[1]-clean[-1][1])-(clean[-1][1]-clean[-2][1])*(v[0]-clean[-1][0]))<1e-9:clean.pop()
  clean.append(v)
 pts=clean
 for (x,y,z),(xx,yy,zz) in zip(pts,pts[1:]):
  if z!=zz:
   v=p.PCB_VIA(b);v.SetPosition(pt(x,y));v.SetWidth(p.FromMM(.7));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);b.Add(v)
   for layer in range(2):disk(layer,x,y,.75,net)
  elif math.hypot(xx-x,yy-y)>1e-6:
   t=p.PCB_TRACK(b);t.SetStart(pt(x,y));t.SetEnd(pt(xx,yy));t.SetWidth(p.FromMM(.25));t.SetLayer(p.F_Cu if z==0 else p.B_Cu);t.SetNet(nets[net]);b.Add(t)
   for j in range(math.ceil(math.hypot(xx-x,yy-y)/.1)+1):
    frac=j/math.ceil(math.hypot(xx-x,yy-y)/.1);disk(z,x+(xx-x)*frac,y+(yy-y)*frac,.5,net)
 return len(path)
for net in ['BUTTON','+3V3','SDA','SCL','GND']:
 endpoints=[(x,y) for x,y,r,n,ref,pad in allpads if n==net]
 done=[endpoints.pop(0)]
 while endpoints:
  _,ai,di=min((math.dist(a,d),i,j) for i,a in enumerate(done) for j,d in enumerate(endpoints))
  d=endpoints.pop(di);count=route(done[ai],d,net);done.append(d);print('routed',net,done[ai],d,count)
settings=b.GetDesignSettings();settings.m_MinClearance=p.FromMM(.2);settings.m_TrackMinWidth=p.FromMM(.25);settings.m_CopperEdgeClearance=p.FromMM(.3)
b.SetFileName(str(OUT/'drivedot.kicad_pcb'));p.SaveBoard(str(OUT/'drivedot.kicad_pcb'),b)
# Minimal project keeps normal ERC/DRC severities; no exclusions.
pro={'meta':{'filename':'drivedot.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.2,'min_track_width':.25,'min_through_hole_diameter':.3,'min_copper_edge_clearance':.3},'drc_exclusions':[]}},'net_settings':{'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.7,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.25,'diff_pair_gap':.2,'diff_pair_via_gap':.25}],'meta':{'version':3}}}
(OUT/'drivedot.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
print('Created schematic and PCB at',OUT)
