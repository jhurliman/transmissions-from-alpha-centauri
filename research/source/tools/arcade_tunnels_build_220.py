import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/arcade-tunnels-220'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-direction-218/current-sun/scene.blend'));s=bpy.context.scene
before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for r in o.matrix_world for x in r),tuple(sl.material.as_pointer()if sl.material else None for sl in o.material_slots),o.hide_render)for o in s.objects}
from arcade_tunnels_220 import apply
a=apply(s);changed=[]
for name,(data,matrix,mats,hidden)in before.items():
 o=bpy.data.objects[name]
 assert (o.data.as_pointer()if o.data else None)==data,name
 assert tuple(x for r in o.matrix_world for x in r)==matrix,name
 assert tuple(sl.material.as_pointer()if sl.material else None for sl in o.material_slots)==mats,name
 if hidden!=o.hide_render:changed.append(name)
assert set(changed)==set(a['hidden_old_tunnels']);a['preservation']={'original_objects':len(before),'only_visibility_changes':changed,'alloriginal_mesh_material_transform_bindings_exact':True}
(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('220 CPU DONE',a['ground_portals'],'INTERSECTIONS',a['neighbor_surface_intersections'],flush=True)
