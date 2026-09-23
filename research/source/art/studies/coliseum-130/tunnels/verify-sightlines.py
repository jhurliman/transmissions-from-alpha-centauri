import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-130/tunnels';bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'));s=bpy.context.scene;c=s.camera;f=c.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in f);xmax=max(v.x/-v.z for v in f);ymin=min(v.y/-v.z for v in f);ymax=max(v.y/-v.z for v in f)
obs=[o for o in s.objects if o.get('130 barrel tunnel')];bv=[]
for o in obs:bv.append((o,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons])))
# Actual baseline sky pixels restrict tests to already-visible openings, so no hidden city rays are counted.
w,h=3840,2885;rows=[];miss=[]
for sel in json.loads((O/'baseline-sky-pixels.json').read_text()):
 bay=sel['bay'];samples=[]
 for x,y in sel['points']:
  d=(c.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*(x+.5)/w,ymin+(ymax-ymin)*(1-(y+.5)/h),-1))).normalized();hits=[]
  for o,tree in bv:
   q,n,idx,dist=tree.ray_cast(c.matrix_world.translation,d)
   if q is not None:hits.append((dist,o.name,list(q)))
  if hits:
   hit=min(hits);samples.append({'p':[x,y],'hit':hit[1],'position':hit[2]})
  else:samples.append({'p':[x,y],'hit':None});miss.append({'bay':bay,'p':[x,y],'direction':list(d)})
 rows.append({'bay':bay,'baseline_visible_sky_samples':len(samples),'blocked':sum(p['hit']is not None for p in samples),'unblocked':sum(p['hit']is None for p in samples),'samples':samples})
(O/'sightlines.json').write_text(json.dumps({'stride_native_px':1,'baseline_source':'129/main-4k.png','selection':'Visible sky-color pixels inside three ground-arch screen ROIs','rows':rows,'misses':miss},indent=2));print([(r['bay'],r['baseline_visible_sky_samples'],r['blocked'],r['unblocked'])for r in rows])
