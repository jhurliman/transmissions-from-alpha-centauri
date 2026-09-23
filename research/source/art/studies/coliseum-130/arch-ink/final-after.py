import bpy
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-130/arch-ink'
for label,path in [('after',O/'geometry.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.43;s.render.border_max_x=.53;s.render.border_min_y=.69;s.render.border_max_y=.80;s.render.filepath=str(O/(label+'-main4k.png'));bpy.ops.render.render(write_still=True)

 s.render.image_settings.color_mode='BW';bpy.data.images['Render Result'].save_render(str(O/(label+'-gray.png')),scene=s)
