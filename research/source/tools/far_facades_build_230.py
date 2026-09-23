import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/far-facades-230';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-230/layout-only.blend'));s=bpy.context.scene
before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for row in o.matrix_world for x in row),o.hide_render,tuple(sl.material.name if sl.material else None for sl in o.material_slots),o.instance_collection.name if o.instance_collection else None)for o in bpy.data.objects};roots={o.name for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection}
from far_facades_230 import apply
a=apply(s)
for name,(data,matrix,hidden,mats,col)in before.items():
 o=bpy.data.objects[name];assert (o.data.as_pointer()if o.data else None)==data,name;assert tuple(x for row in o.matrix_world for x in row)==matrix,name;assert o.hide_render==hidden,name;assert tuple(sl.material.name if sl.material else None for sl in o.material_slots)==mats,name
 if(o.instance_collection.name if o.instance_collection else None)!=col:assert name in roots,name
assert a['buildings']==18
a['preservation']={'all_original_object_data_matrices_materials_visibility_exact':True,'root_container_bindings_only_changed':sorted(roots)};(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'facades-only.blend'));bpy.data.libraries.write(str(O/'window-door-prefabs.blend'),{bpy.data.collections[n]for n in a['reusable_masters']},fake_user=True,compress=True);print('230_FACADES_READY',a['buildings'],len(a['openings']),a['new_native_mesh_objects'],flush=True)
