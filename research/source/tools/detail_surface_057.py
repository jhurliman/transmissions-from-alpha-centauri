import bpy
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-057'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
# Native high-resolution camera crops, not enlarged preview pixels.
s.render.resolution_x=4320;s.render.resolution_y=3240;s.render.use_border=True;s.render.use_crop_to_border=True
for name,box in [('pipes',(280,120,560,670))]:
 x0,y0,x1,y1=box;s.render.border_min_x=x0/1440;s.render.border_max_x=x1/1440;s.render.border_min_y=1-y1/1080;s.render.border_max_y=1-y0/1080;s.render.filepath=str(O/(name+'-detail.png'));bpy.ops.render.render(write_still=True)
