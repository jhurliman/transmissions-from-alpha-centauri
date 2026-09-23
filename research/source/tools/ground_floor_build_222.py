import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/ground-floor-kit-222'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/arcade-tunnels-220/scene.blend'));s=bpy.context.scene
before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for r in o.matrix_world for x in r),o.instance_collection.as_pointer()if o.instance_collection else None,tuple(sl.material.as_pointer()if sl.material else None for sl in o.material_slots),o.hide_render)for o in s.objects}
from ground_floor_kit_222 import apply
a=apply(s)
allowedgp={r['object']for r in a['contact_clip']if r['changed_strokes']};allowedroots={r['root']for r in a['host_modifications']};changed=[]
for name,(data,matrix,instance,mats,hidden)in before.items():
 o=bpy.data.objects[name]
 if (o.data.as_pointer()if o.data else None)!=data:assert name in allowedgp;changed.append((name,'privateGPdrawing'))
 assert tuple(x for r in o.matrix_world for x in r)==matrix,name
 assert tuple(sl.material.as_pointer()if sl.material else None for sl in o.material_slots)==mats,name
 assert o.hide_render==hidden,name
 if (o.instance_collection.as_pointer()if o.instance_collection else None)!=instance:assert name in allowedroots;changed.append((name,'privatehostcollection'))
a['preservation']={'original_scene_objects':len(before),'changed_original_bindings':changed,'alloriginal_transforms_materials_visibility_exact':True,'alloriginal_source_meshes_unchanged':True}
(O/'audit.json').write_text(json.dumps(a,indent=2))
from haze_texture_221 import apply as haze
ha=haze(s);(O/'haze-221-audit.json').write_text(json.dumps(ha,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('222 CPU CANDIDATE READY',a['new_component_objects'],a['contact_clip'],flush=True)
