import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-092';bpy.ops.wm.open_mainfile(filepath=str(O/'scene-B.blend'));s=bpy.context.scene
for im in bpy.data.images:
 if 'pigment-B' in im.name:im.filepath=str(O/'pigment-B.png');im.reload();im.pack()
s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/'main-B.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-B.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.16;s.render.border_max_x=.80;s.render.border_min_y=.16;s.render.border_max_y=.45;s.render.filepath=str(O/'detail-B.png');bpy.ops.render.render(write_still=True)
