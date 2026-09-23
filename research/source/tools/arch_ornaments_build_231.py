import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/arch-ornaments-231';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entry-surround-229/scene.blend'));s=bpy.context.scene
before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for row in o.matrix_world for x in row),o.hide_render,tuple(sl.material.name if sl.material else None for sl in o.material_slots))for o in bpy.data.objects}
from arch_ornaments_231 import apply
a=apply(s)
for name,(data,matrix,hidden,mats)in before.items():
 o=bpy.data.objects[name];assert (o.data.as_pointer()if o.data else None)==data,name;assert tuple(x for row in o.matrix_world for x in row)==matrix,name;assert o.hide_render==hidden,name;assert tuple(sl.material.name if sl.material else None for sl in o.material_slots)==mats,name
a['preservation']={'source_objects':len(before),'all_source_geometry_transforms_materials_visibility_exact':True};(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'ornaments-only.blend'));print('231 READY',a['continuous_impost_extensions'],a['upper_pyramids'],flush=True)
