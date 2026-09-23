import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from soil_study_081 import apply,CFG
O=R/'art/studies/soil-081'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-079/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
apply(s,CFG);bpy.ops.wm.save_as_mainfile(filepath=str(O/'integrated-scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
for o in s.objects:
 if o.type in ['LIGHT','CAMERA']:continue
 if o.name=='Street foundation' or o.name.startswith(('077 broken earth lip','079')):continue
 o.hide_render=True
s.camera.location=(2,-7,3);s.camera.rotation_euler=(Vector((0,0,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=42;s.render.resolution_x=1370;s.render.resolution_y=746;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.filepath=str(O/'scene-closeup.png');bpy.ops.render.render(write_still=True)
