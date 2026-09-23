import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-074';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
c=bpy.data.cameras.new('074 side alley inspection');o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);o.location=(9.8,3,8);o.rotation_euler=(Vector((9.8,6,8))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=17.2;s.camera=o
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1050;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.filepath=str(O/'side.png');bpy.ops.render.render(write_still=True)
