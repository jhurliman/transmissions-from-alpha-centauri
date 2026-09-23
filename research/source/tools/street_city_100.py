"""100: continuous inward-facing distant street; approved099 rocks untouched."""
import bpy,sys,json,math,random
from pathlib import Path
from collections import defaultdict
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-100';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/density-099/scene.blend'));s=bpy.context.scene;rng=random.Random(100031)
groups=defaultdict(list)
for o in s.objects:
 if not o.hide_render and (o.name.startswith('FAR075 ') or o.name.startswith('CITY099 ')):
  groups[tuple(round(v,5) for row in o.matrix_world for v in row)].append(o)
records=[]
for obs in groups.values():
 pts=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];lo=Vector([min(v[k] for v in pts) for k in range(3)]);hi=Vector([max(v[k] for v in pts) for k in range(3)])
 records.append(dict(obs=obs,center=(lo+hi)*.5,lo=lo,hi=hi))
audit=[]
for side in [-1,1]:
 row=sorted([r for r in records if r['center'].x*side>0],key=lambda r:(r['center'].y,abs(r['center'].x)))
 # Broadly preserve palette and size progression with depth.
 for i,r in enumerate(row):
  street=i<48
  j=i if street else (i-48)//2
  outer=(i-48)%2 if not street else 0
  y=(49+j*4.25) if street else (59+j*8.25)
  y+=rng.uniform(-.30,.30)
  angle=(-side*math.pi/2) if street else rng.uniform(-.12,.12)
  rot=Matrix.Rotation(angle,4,'Z');c=r['center'];anchor=Vector((c.x,c.y,0))
  local=[rot@(o.matrix_world@Vector(v)-anchor) for o in r['obs'] for v in o.bound_box]
  inner=min(p.x*side for p in local)
  road_edge=8.3 if street else 12.7+outer*4.3
  x=side*(road_edge-inner)
  xf=Matrix.Translation((x,y,0))@rot@Matrix.Translation(-anchor)
  for o in r['obs']:
   o.matrix_world=xf@o.matrix_world;o['street100_role']='inward facade' if street else 'outer block'
  audit.append({'side':side,'street':street,'center':[x,y],'inner_edge_m':road_edge,'parts':len(r['obs'])})
# Only far-city placement changed, so regenerate geometry ink for the final camera.
for name in ['096 contacts ink','096 damage ink']:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
(O/'layout.json').write_text(json.dumps({'towers':len(records),'frontages':sum(a['street'] for a in audit),'road_clear_width_m':16.6,'road_starts_y':49,'road_last_frontage_y':248.75,'far_near_perspective_ratio':(49+14)/(248.75+14),'buildings':audit},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'placement.blend'))
s.render.use_freestyle=False;s.render.resolution_percentage=75;s.render.filepath=str(O/'preview.png');bpy.ops.render.render(write_still=True)
