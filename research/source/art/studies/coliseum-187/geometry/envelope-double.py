import bpy,json,numpy as np,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';rows=json.load(open(O/'envelope-classification.json'));groups={}
for r in rows:groups.setdefault(r['object'],[]).append(r)
bpy.ops.wm.open_mainfile(filepath=str(O/'fixed-shape-technical.blend'));cand={}
for name in groups:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();lookup={tuple(sum((me.vertices[i].co for i in t.vertices),Vector())/3):t for t in me.loop_triangles};v=np.array([tuple(v.co)for v in me.vertices]);M=np.array(ob.matrix_world);cand[name]=(lookup,v,M)
 # Cache actual tri vertices before load destroys RNA
 for r in groups[name]:
  t=lookup.get(tuple(r['point_local']));r['actual_triangle_local']=v[list(t.vertices)].tolist()if t else None
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));dg=bpy.context.evaluated_depsgraph_get()
def closest(p,arr):
 a,b,c=arr[:,0],arr[:,1],arr[:,2];ab=b-a;ac=c-a;n=np.cross(ab,ac);nn=np.einsum('ij,ij->i',n,n);q=p-n*(np.einsum('ij,ij->i',p-a,n)/np.maximum(nn,1e-300))[:,None]
 u=np.einsum('ij,ij->i',np.cross(b-q,c-q),n)/np.maximum(nn,1e-300);v=np.einsum('ij,ij->i',np.cross(c-q,a-q),n)/np.maximum(nn,1e-300);w=1-u-v;inside=(u>=-1e-10)&(v>=-1e-10)&(w>=-1e-10)&(nn>0);best=np.where(inside,np.linalg.norm(q-p,axis=1),np.inf);pts=q.copy()
 for x,y in [(a,b),(b,c),(c,a)]:
  d=y-x;t=np.clip(np.einsum('ij,ij->i',p-x,d)/np.maximum(np.einsum('ij,ij->i',d,d),1e-300),0,1);z=x+t[:,None]*d;ds=np.linalg.norm(z-p,axis=1);pick=ds<best;best[pick]=ds[pick];pts[pick]=z[pick]
 i=int(np.argmin(best));return float(best[i]),pts[i],i
for name,rr in groups.items():
 ob=bpy.data.objects[name].evaluated_get(dg);me=ob.to_mesh();me.calc_loop_triangles();M=np.array(ob.matrix_world);vv=np.array([tuple(v.co)for v in me.vertices]);world=vv@M[:3,:3].T+M[:3,3];arr=world[np.array([tuple(t.vertices)for t in me.loop_triangles])]
 for r in rr:
  if r['actual_triangle_local']is None:r['held']='No center correspondence';continue
  tr=np.array(r['actual_triangle_local']);p=tr.mean(axis=0)@M[:3,:3].T+M[:3,3];d,q,i=closest(p,arr);r['double_center_world']=p.tolist();r['double_nearest_m']=d;r['double_source_triangle']=i;r['double_source_polygon']=me.loop_triangles[i].polygon_index;r['double_nearest_world']=q.tolist()
 ob.to_mesh_clear()
(O/'envelope-double.json').write_text(json.dumps(rows,indent=2));print('max double',max(r.get('double_nearest_m',0)for r in rows));print([(r['object'],r['nearest_world_m'],r.get('double_nearest_m'))for r in rows if r['nearest_world_m']>.0005])
