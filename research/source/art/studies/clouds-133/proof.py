import bpy,sys,json,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from clouds_133 import apply
O=R/'art/studies/clouds-133';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-130/scene.blend'));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=2
C=bpy.data.collections['082 Derived flat clouds'];names={o.name for o in C.all_objects}
for o in s.objects:
 if o.name not in names and o.type!='CAMERA':o.hide_render=True
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1280/3840;s.render.border_max_x=2680/3840;s.render.border_min_y=1-700/2885;s.render.border_max_y=1.;s.render.filepath=str(O/'before-sky-4k.png');bpy.ops.render.render(write_still=True)
t=time.time();audit=apply(s);audit['apply_seconds']=time.time()-t;(O/'generation.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'sky-study.blend'));s.render.filepath=str(O/'after-sky-4k.png');bpy.ops.render.render(write_still=True)
