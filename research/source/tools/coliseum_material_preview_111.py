import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_materials_111 import apply_materials
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-110/scene.blend'))
apply_materials(bpy.data.collections['110 Coliseum detailed front ruin'])
s=bpy.context.scene;s.render.resolution_x=2560;s.render.resolution_y=1923;s.render.line_thickness=2560/1440
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.335;s.render.border_max_x=.665;s.render.border_min_y=.58;s.render.border_max_y=.93
s.render.filepath=str(R/'art/studies/coliseum-111/material-preview.png');bpy.ops.render.render(write_still=True)
