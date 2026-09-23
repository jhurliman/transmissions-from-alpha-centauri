import bpy
from mathutils import Vector
from pathlib import Path
O=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-047');bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.camera.location=(8.45,11.2,1.7);s.camera.rotation_euler=(Vector((9.85,11.539,1.274))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=70;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.use_freestyle=False;s.cycles.samples=32;s.render.filepath=str(O/'fastener-detail.png');bpy.ops.render.render(write_still=True)
