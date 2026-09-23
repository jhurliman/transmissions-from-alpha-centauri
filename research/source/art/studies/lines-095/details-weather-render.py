import bpy
from pathlib import Path
O=Path('/PATH/TO/transmissions-from-alpha-centauri/art/studies/lines-095');bpy.ops.wm.open_mainfile(filepath=str(O/'details-weather.blend'));s=bpy.context.scene;ink=bpy.data.objects['095 Weathering material boundary ink']
ink.data.stroke_depth_order='3D'
for label,visible in [('before',False),('after',True)]:
 ink.hide_render=not visible;s.render.filepath=str(O/('details-weather-'+label+'.png'));bpy.ops.render.render(write_still=True)
