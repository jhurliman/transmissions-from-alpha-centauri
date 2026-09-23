import bpy,sys,json,hashlib,struct
from array import array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-prefabs-211';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-209/scene.blend'))
def state(o):
 h=hashlib.sha256();h.update(str(tuple(tuple(x)for x in o.matrix_world)).encode());h.update(str([(s.link,s.material.name if s.material else None)for s in o.material_slots]).encode())
 if o.type=='MESH':
  for seq,prop,size,kind in [(o.data.vertices,'co',3,'f'),(o.data.vertices,'normal',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'normal',3,'f')]:
   buf=array(kind,[0])*(len(seq)*size);seq.foreach_get(prop,buf);h.update(buf.tobytes())
 return h.hexdigest()
before={o.name:(state(o),o.hide_render)for o in bpy.data.objects};oldmats={m.name:(len(m.node_tree.nodes),len(m.node_tree.links)) if m.use_nodes else None for m in bpy.data.materials}
from city_prefabs_211 import apply
a=apply(bpy.context.scene);allowed={n for x in a['instances']for n in x['source_objects']};changed=[]
for name,(fp,hide) in before.items():
 o=bpy.data.objects[name];assert state(o)==fp,name
 if o.hide_render!=hide:assert name in allowed;changed.append(name)
assert len(changed)==106,len(changed)
for name,ns in oldmats.items():
 m=bpy.data.materials[name];assert ((len(m.node_tree.nodes),len(m.node_tree.links)) if m.use_nodes else None)==ns
(O/'preservation.json').write_text(json.dumps({'source_objects_checked':len(before),'original_geometry_normals_transforms_material_bindings_unchanged':True,'only106city_render_visibility_changes':True,'old_material_node_link_counts_unchanged':len(oldmats),'note':'node count assertion complements module ownership: no original material is edited'},indent=2))
(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
