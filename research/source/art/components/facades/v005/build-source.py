"""Facade assembly proofs built from the verified panel/window vocabulary."""
from pathlib import Path
src=(Path(__file__).parent/'build_facade_kit.py').read_text()
exec(src[:src.index('# Neutral studio')])
# Keep the first proof pieces available in this .blend, but render the new assemblies only.
for k,col in proofs.items():col.hide_render=True;col.hide_viewport=True
base_proofs=dict(proofs);proofs={}
for key,col in base_proofs.items():
 s.collection.children.unlink(col);col.hide_render=False;col.hide_viewport=False
 col.asset_mark();col['part_id']=key;col['interface_json']=json.dumps({'kind':'facade_assembly','width':2.8 if key=='window_bay' else 1.6,'up':[0,0,1],'outward':[0,-1,0]});assets[key]=col

# Repeatable utility: native dimensioned channel between two endpoints.
def beam(a,b,width=.12,depth=.14):
 a=Vector(a);b=Vector(b);L=(b-a).length;before=set(C.objects)
 box('Channel web',(0,0,L/2),(width,.018,L),steel)
 for x in [-width/2+.009,width/2-.009]:box('Channel flange',(x,-depth/2,L/2),(.018,depth,L),steel)
 M=Matrix.Translation(a)@(b-a).to_track_quat('Z','Y').to_matrix().to_4x4()
 for ob in set(C.objects)-before:ob.matrix_world=M

def canopy():
 # A wall-mounted deck; support assembly reaches a shared foot datum.
 for x in [-1.20,1.20]:
  beam((x,-.90,0),(x,-.90,.90),.13,.15)
  # 30 degrees from vertical; both arms meet the same canopy crossmember.
  for side in [-1,1]:beam((x,-.90,.90),(x+side*.52,-.90,1.80),.10,.12)
  box('Stem splice plate',(x,-1.04,.90),(.22,.035,.25),edge)
  for dx in [-.07,.07]:
   for z in [.82,.98]:screw(x+dx,-1.065,z)
  box('Support foot plate',(x,-.90,.035),(.28,.29,.07),steel)
 for y in [-.15,-.9]:beam((-1.85,y,1.82),(1.85,y,1.82),.14,.18)
 for x in [-1.65,-.55,.55,1.65]:beam((x,-.1,1.85),(x,-1.15,1.85),.085,.10)
 for x in [-1.245,0,1.245]:box('Canopy deck panel',(x,-.62,1.96),(1.22,1.15,.035),paint)
 box('Canopy front fascia',(0,-1.21,1.87),(3.74,.035,.22),pale)
 box('Canopy folded lip',(0,-1.23,1.755),(3.74,.09,.028),steel)
 for x in [-1.87,1.87]:box('Canopy side return',(x,-.64,1.87),(.035,1.16,.22),pale)
 # Wall brackets provide an explicit mount plane at Y=0.
 for x in [-1.65,1.65]:
  box('Wall mounting plate',(x,0,1.82),(.26,.065,.34),edge)
  for dx in [-.085,.085]:
   for z in [1.72,1.92]:screw(x+dx,-.042,z)
register('canopy_y_support',canopy,{'kind':'canopy','wall_plane_y':0,'width':3.78,'height':2,'depth':1.28,'brace_rake_degrees':30,'services_mount':{'position':[0,-.6,1.70],'outward':[0,0,-1],'up':[0,-1,0],'clearance':.20}})

def slotted():
 # Two narrow openings bounded by regular plate fields; no wall behind slots.
 for x,w in [(-1.275,.25),(0,1.26),(1.275,.25)]:
  before=set(C.objects);panel(w,1.6,paint)
  for ob in set(C.objects)-before:ob.location.x=x
 for x in [-.89,.89]:
  for z in [.075,1.525]:box('Slot top/bottom cladding',(x,0,z),(.48,.035,.15),pale)
  before=set(C.objects)
  frame_ring('Narrow slot reveal',[(-.045,.49,1.28,.33,1.12,.80),(.10,.49,1.28,.23,1.02,.80),(.28,.49,1.28,.23,1.02,.80)],pale)
  box('Slot dark recess',(0,.34,.80),(.27,.03,1.08),dark)
  for z in [.38,.58,.78,.98,1.18]:box('Recessed slot crossbar',(0,.26,z),(.23,.04,.018),steel)
  for ob in set(C.objects)-before:ob.location.x=x
register('slot_wall',slotted,{'kind':'slotted_wall','width':2.8,'height':1.6,'depth':.36,'slope_applied_at_assembly':15})

def buttress():
 # Solid cross-section with horizontal foot and head. 30-degree principal rake.
 d=2.20*math.tan(math.radians(30));pts=[(-d-.18,0),(-d+.18,0),(.18,2.20),(-.18,2.20)]
 vs=[(x,y,z) for x in [-.17,.17] for y,z in pts];mesh('Solid raked buttress',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete,.014)
 box('Buttress footing',(0,-d,.03),(.49,.60,.06),concrete)
 box('Buttress head bearing',(0,0,2.20),(.43,.48,.08),steel)
register('buttress_30',buttress,{'kind':'solid_support','height':2.24,'rake':30,'foot':[0,-2.2*math.tan(math.radians(30)),0],'head':[0,0,2.20]})

def left():
 for x in [-.84,.304]:
  inst('plate_broad',(x,0,.02));inst('plate_square',(x,0,1.464))
 inst('plate_narrow',(1.08,0,.02))
 box('Bay edge filler',(1.35,0,1.08),(.10,.024,2.12),pale)
 # Inclined wall transition; all attached panels and slot details share its transform.
 ob=inst('slot_wall',(0,0,2.18));ob.rotation_euler.x=-math.radians(15)
 ztop=2.18+1.6*math.cos(math.radians(15));ytop=1.6*math.sin(math.radians(15))
 for x in [-.84,.304]:inst('plate_broad',(x,ytop,ztop+.024))
 inst('plate_narrow',(1.08,ytop,ztop+.024))
 box('Upper edge filler',(1.35,ytop,ztop+.734),(.10,.024,1.42),pale)
 inst('floor_band',(0,0,1.89));inst('access_insert',(-.4,-.018,.67))
 inst('canopy_y_support',(0,0,-.30))
 box('Left base plinth',(0,.17,-.16),(2.85,.48,.3),concrete)

def right():
 for x in [-1.412,1.412]:
  inst('window_broken' if x<0 else 'window_open',(x,0,2.50))
  # Recessed frontage is visibly behind the supports; panel strips share a fixed grid.
  for dx in [-.84,.304]:
   inst('plate_broad',(x+dx,.48,.03));inst('plate_square',(x+dx,.48,1.474))
  inst('plate_narrow',(x+1.08,.48,.03))
  box('Lower edge filler',(x+1.35,.48,1.08),(.10,.024,2.12),pale)
  inst('access_insert',(x-.3,.462,.61))
  inst('floor_band',(x,.39,2.16))
 for x in [-2.65,0,2.65]:inst('buttress_30',(x,-.02,-.30))
 # Recess returns make the depth difference into an architectural volume.
 for x in [-2.82,2.82]:box('Ground frontage end return',(x,.26,1.0),(.06,.49,2.6),paint)

proof('left_inclined_bay',left);proof('right_window_frontage',right)
proof('canopy',lambda:inst('canopy_y_support',(0,0,-.30)))
# Reuse the exact studio, metadata and render machinery, with sample-specific framing.
tail=src[src.index('# Neutral studio'):]
tail=tail.replace("for key,col in proofs.items():\n",'''for key,col in proofs.items():
 target=Vector((0,.1,2.35 if key!='canopy' else .85))
 cam.location=target+Vector((5,-11,4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 d.ortho_scale=10.2 if key=='right_window_frontage' else (8.7 if key=='left_inclined_bay' else 6.3)
''')
exec(tail)
