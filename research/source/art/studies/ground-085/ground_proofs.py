import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-085';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
# Same project camera, native 2x road crop. Not an enlargement of finished pixels.
s.render.resolution_x=2880;s.render.resolution_y=2164;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=240/1440;s.render.border_max_x=650/1440;s.render.border_min_y=1-875/1082;s.render.border_max_y=1-650/1082
s.render.use_freestyle=False;s.render.filepath=str(O/'road-detail-native.png');bpy.ops.render.render(write_still=True)
