"""Finite native contact audit against all surviving local solid triangles."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-169/contact';data=json.load(open(O/'support-diagnosis.json'));out={};box=[(-15,-8),(173,202),(35,45)]
for label,path in [('129',R/'art/studies/coliseum-129/scene.blend'),('166',R/'art/studies/coliseum-166/scene.blend'),('after',R/'art/studies/coliseum-168/scene.blend' if (R/'art/studies/coliseum-168/scene.blend').exists()else R/'art/studies/coliseum-167/geometry/scene.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));gp=bpy.data.objects['110 Landmark contact ink'];sha=hashlib.sha256();attrs=[]
 for l in gp.data.layers:
  for f in l.frames:
   dr=f.drawing
   for a in dr.attributes:
    prop=next((k for k in ('vector','color','value')if len(a.data)and hasattr(a.data[0],k)),None)
    vals=[]
    if prop:
     for v in a.data:
      q=getattr(v,prop);vals.append(list(q)if hasattr(q,'__len__')else q)
    sha.update(json.dumps([a.name,a.domain,a.data_type,vals],sort_keys=True).encode());attrs.append({'name':a.name,'domain':a.domain,'type':a.data_type,'count':len(a.data),'prop':prop})
 out[label]={'source':str(path.relative_to(R)),'gp_attributes_sha256':sha.hexdigest(),'attributes':attrs}
 if label!='after':continue
 dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[];local=[]
 for ob in bpy.data.collections['110 Coliseum detailed front ruin'].all_objects:
  if ob.type!='MESH'or ob.hide_render:continue
  ev=ob.evaluated_get(dg);bb=[ev.matrix_world@Vector(v)for v in ev.bound_box]
  if any(max(v[k]for v in bb)<lo-.2 or min(v[k]for v in bb)>hi+.2 for k,(lo,hi)in enumerate(box)):continue
  me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices)
  fs.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);owners.extend([ob.name]*len(me.loop_triangles));local.append(ob.name);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);out['local_surviving_solids']=local
 for seg in data['segments']:
  seg['all_solid_after']=[]
  for p in seg['samples']:
   hit=tree.find_nearest(Vector(p));seg['all_solid_after'].append({'distance':hit[3],'object':owners[hit[2]],'nearest':list(hit[0])})
 data['all_solid_summary']={'any_sample_old_close_new_far':sum(any(a['distance']<.02 and b['distance']>.1 for a,b in zip(r['before'],r['all_solid_after']))for r in data['segments']),'all_samples_old_close_new_far':sum(all(a['distance']<.02 and b['distance']>.1 for a,b in zip(r['before'],r['all_solid_after']))for r in data['segments'])}
(O/'all-solid-support.json').write_text(json.dumps(data,indent=2));(O/'provenance.json').write_text(json.dumps(out,indent=2));print(data['all_solid_summary'],flush=True)
