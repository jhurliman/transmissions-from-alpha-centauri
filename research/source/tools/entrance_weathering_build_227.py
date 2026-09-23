import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/entrance-weathering-227';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/far-building-layout-226/scene.blend'));s=bpy.context.scene
before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for row in o.matrix_world for x in row),o.hide_render,tuple(sl.material.name if sl.material else None for sl in o.material_slots))for o in bpy.data.objects}
def dependencies(m):
 rows=[];seen=set()
 def walk(t):
  if t.as_pointer()in seen:return
  seen.add(t.as_pointer())
  for n in t.nodes:
   if n.type in('ATTRIBUTE','VERTEX_COLOR','UVMAP','TEX_COORD','OBJECT_INFO'):rows.append({'tree':t.name,'node':n.name,'type':n.type,'attribute':getattr(n,'attribute_name',getattr(n,'layer_name',getattr(n,'uv_map',''))),'linked_outputs':[q.name for q in n.outputs if q.is_linked]})
   if n.type=='GROUP'and n.node_tree:walk(n.node_tree)
 walk(m.node_tree);return rows
hosts=[bpy.data.objects[n].material_slots[0].material for n in('Gallery base panel.011','Utility base.022')]
deps={m.name:dependencies(m)for m in hosts};(O/'facade-dependencies.json').write_text(json.dumps(deps,indent=2));print('DEPENDENCIES',deps,flush=True)
from entrance_weathering_227 import apply
a=apply(s);allowed={r['object']for r in a['material_assignments']};changed=[]
for name,(data,matrix,hidden,slots)in before.items():
 o=bpy.data.objects[name];assert (o.data.as_pointer()if o.data else None)==data,name;assert tuple(x for row in o.matrix_world for x in row)==matrix,name;assert o.hide_render==hidden,name
 after=tuple(sl.material.name if sl.material else None for sl in o.material_slots)
 if slots!=after:assert name in allowed,name;changed.append(name)
a['preservation']={'source_objects':len(before),'only_222_material_bindings_changed':changed,'allgeometry_transforms_visibility_exact':True,'no_new_geometry_or_ink':True};a['source_material_dependencies']=deps
(O/'entrance-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'entrance-only.blend'));print('227_READY',len(changed),a['new_materials'],flush=True)
