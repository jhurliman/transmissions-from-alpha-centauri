import bpy,time,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-prefabs-211';bpy.ops.wm.open_mainfile(filepath=str(O/'catalog.blend'));s=bpy.context.scene;s.render.filepath=str(O/'catalog-native.png');t=time.time();bpy.ops.render.render(write_still=True)
for ob in s.objects:
 if ob.type=='EMPTY' and ob.instance_collection and ob.instance_collection.get('211 stories')==10:ob.hide_render=True
s.camera.location=(17,-30,18);s.camera.rotation_euler=(Vector((-3,1,5.5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=23;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.filepath=str(O/'catalog-families-native.png');bpy.ops.render.render(write_still=True)
(O/'catalog-performance.json').write_text(json.dumps({'seconds':time.time()-t}));print('211_CATALOG_RENDER_DONE',flush=True)
