import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';result={}
for stage,path in [('before',R/'art/studies/coliseum-173/scene.blend'),('after',O/'HELD-diagnostic.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();C=bpy.data.collections['110 Coliseum detailed front ruin'];ob=bpy.data.objects['COL120 bay10 arcade2 dentil03'].evaluated_get(dg);me=ob.to_mesh();points=[ob.matrix_world@v.co for v in me.vertices]+[ob.matrix_world@f.center for f in me.polygons]
 for e in me.edges:
  a,b=[ob.matrix_world@me.vertices[i].co for i in e.vertices];points.extend(a.lerp(b,t)for t in [.25,.5,.75])
 ob.to_mesh_clear();pts=np.array([tuple(p)for p in points]);lo=pts.min(axis=0)-.1;hi=pts.max(axis=0)+.1;solids=[]
 for o in C.all_objects:
  if o.type!='MESH' or o.hide_render or 'ink'in o.name.lower()or o.name=='COL120 bay10 arcade2 dentil03':continue
  bb=np.array([tuple(o.matrix_world@Vector(p))for p in o.bound_box])
  if np.any(bb.max(axis=0)<lo)or np.any(bb.min(axis=0)>hi):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();vv=[ev.matrix_world@v.co for v in m.vertices];tt=[tuple(t.vertices)for t in m.loop_triangles];arr=np.array([[tuple(vv[i])for i in t]for t in tt]);tree=BVHTree.FromPolygons(vv,tt,all_triangles=True);solids.append((o.name,arr,tree));ev.to_mesh_clear()
 rr=[]
 for idx,p in enumerate(pts):
  support=[]
  for n,arr,tree in solids:
   distance=tree.find_nearest(Vector(p))[3]
   q=arr-p;l=np.linalg.norm(q,axis=2);num=np.einsum('ij,ij->i',q[:,0],np.cross(q[:,1],q[:,2]));den=l.prod(axis=1)+np.einsum('ij,ij->i',q[:,0],q[:,1])*l[:,2]+np.einsum('ij,ij->i',q[:,1],q[:,2])*l[:,0]+np.einsum('ij,ij->i',q[:,2],q[:,0])*l[:,1];w=float(np.sum(2*np.arctan2(num,den))/(4*np.pi))
   if abs(w)>.5 or distance<.02:support.append({'object':n,'winding':w,'distance':distance})
  rr.append({'sample':idx,'world':p.tolist(),'support':support})
 result[stage]={'nearby_solids':[s[0]for s in solids],'samples':rr,'supported_samples':sum(bool(r['support'])for r in rr)}
(O/'dentil-bearing.json').write_text(json.dumps(result,indent=2));print({k:v['supported_samples']for k,v in result.items()})
