import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from soil_study_081 import mat,apply,CFG
O=R/'art/studies/soil-081'
for mode,freq,detail in [('fine',18,2),('discrete',26,1.8)]:
 cfg={**CFG,'grain_mode':mode,'noise_scale':freq,'noise_detail':detail}
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1370;s.render.resolution_y=746
 # A true close view samples a3.625m soil field; no image upscaling.
 for ob in s.objects:
  if ob.type=='MESH' and ob.name!='081 editable soil slab':ob.hide_render=True
 g=bpy.data.objects['081 editable soil slab'];g.data.materials[0]=mat(cfg);s.camera.location=(0,-10,8);s.camera.rotation_euler=(Vector((0,0,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=3.625;s.render.filepath=str(O/(mode+'-clean.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-079/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;apply(s,cfg);s.render.filepath=str(O/(mode+'-main.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(mode+'-scene.blend')));bpy.ops.render.render(write_still=True)
