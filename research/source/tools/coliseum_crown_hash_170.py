import bpy,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-170/mapping';old=json.load(open(R/'art/studies/coliseum-156/preflight/audit.json'));prior={}
def walk(v):
 if isinstance(v,dict):
  if 'evaluated_geometry_world_sha256'in v:prior[v['object']]=v
  for q in v.values():walk(q)
 elif isinstance(v,list):
  for q in v:walk(q)
walk(old);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));dg=bpy.context.evaluated_depsgraph_get();out=[]
for name in ['COL110 U4 fractured upper wall L','COL110 U4 aperture head','COL110 U5 aperture head','COL110 U5 fractured upper wall R']:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();h=hashlib.sha256();h.update(repr(tuple(tuple(r)for r in ev.matrix_world)).encode())
 for coll,key,size,code in [(me.vertices,'co',3,'f'),(me.loops,'vertex_index',1,'i'),(me.polygons,'loop_start',1,'i'),(me.polygons,'loop_total',1,'i')]:
  a=array.array(code,[0])*(len(coll)*size);coll.foreach_get(key,a);h.update(a.tobytes())
 out.append({'object':name,'current_evaluated_geometry_hash':h.hexdigest(),'matches156':h.hexdigest()==prior[name]['evaluated_geometry_world_sha256'],'reused_crossing_count':prior[name]['crossings']});ev.to_mesh_clear()
(O/'inherited-topology.json').write_text(json.dumps(out,indent=2));print(out)
