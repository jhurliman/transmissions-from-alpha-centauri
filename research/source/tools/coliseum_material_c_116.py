import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_detail_116 import refine
O=R/'art/studies/coliseum-116/material'
for label,strength in [('C',1.)]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-115/E/scene.blend'));s=bpy.context.scene;a=refine(bpy.data.collections['110 Coliseum detailed front ruin'],strength)
 s.render.use_freestyle=False;s.render.resolution_x=2560;s.render.resolution_y=1923;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.335;s.render.border_max_x=.665;s.render.border_min_y=.58;s.render.border_max_y=.93;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True);(O/(label+'.json')).write_text(json.dumps(a,indent=2))
