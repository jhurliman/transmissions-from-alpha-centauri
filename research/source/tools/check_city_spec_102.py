import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-102'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
for m in bpy.data.materials:
 if m.name.startswith('CITY102') and m.get('actual_specular'):
  for n in m.node_tree.nodes:
   if n.label=='Restrained grouped specular catch':
    for e in n.color_ramp.elements:e.color=(0,0,0,1)
s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=540/1440;s.render.border_max_x=960/1440;s.render.border_min_y=1-490/1082;s.render.border_max_y=1-260/1082;s.render.filepath=str(O/'spec-off-city.png');bpy.ops.render.render(write_still=True)
