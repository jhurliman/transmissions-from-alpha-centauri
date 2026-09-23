"""Read-only native contact support comparison; never saves source scenes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-169/contact';O.mkdir(parents=True,exist_ok=True)
names=[r['object']for r in json.load(open(R/'art/studies/coliseum-167/geometry/audit.json'))['targets']]
out={};segments=[]
for label,path in [('before',R/'art/studies/coliseum-166/scene.blend'),('after',R/'art/studies/coliseum-168/scene.blend' if (R/'art/studies/coliseum-168/scene.blend').exists()else R/'art/studies/coliseum-167/geometry/scene.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();trees={}
 for name in names:
  ob=bpy.data.objects.get(name)
  if not ob:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();trees[name]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
 gp=bpy.data.objects['110 Landmark contact ink'];count=0
 if label=='before':
  for li,layer in enumerate(gp.data.layers):
   for fi,frame in enumerate(layer.frames):
    for si,stroke in enumerate(frame.drawing.strokes):
     count+=1;vv=[gp.matrix_world@p.position for p in stroke.points]
     for pi,(a,b)in enumerate(zip(vv,vv[1:])):
      if any(max(a[k],b[k])<lo or min(a[k],b[k])>hi for k,lo,hi in [(0,-15,-8),(1,173,202),(2,35,45)]):continue
      segments.append({'layer':li,'frame':fi,'stroke':si,'segment':pi,'points':[list(a),list(b)],'samples':[list(a.lerp(b,t))for t in [0,.25,.5,.75,1]]})
 def near(p):
  vv=[]
  for n,t in trees.items():
   hit=t.find_nearest(Vector(p))
   if hit[0]is not None:vv.append((hit[3],n,list(hit[0]),list(hit[1])))
  d,n,p,no=min(vv);return {'distance':d,'object':n,'nearest':p,'normal':no}
 for seg in segments:seg[label]=[near(p)for p in seg['samples']]
 out[label]={'source':str(path.relative_to(R)),'target_count':len(trees),'gp_modifiers':[m.name for m in gp.modifiers],'gp_properties':{k:str(v)for k,v in gp.items()},'stroke_count':count if label=='before'else None}
out['segments']=segments;out['summary']={'candidate_segments':len(segments),'candidate_strokes':len(set((r['layer'],r['frame'],r['stroke'])for r in segments)),'all_samples_old_within_002_new_far_01':sum(all(a['distance']<.02 and b['distance']>.1 for a,b in zip(r['before'],r['after']))for r in segments),'any_sample_old_within_002_new_far_01':sum(any(a['distance']<.02 and b['distance']>.1 for a,b in zip(r['before'],r['after']))for r in segments)}
(O/'support-diagnosis.json').write_text(json.dumps(out,indent=2));print(out['summary'],flush=True)
