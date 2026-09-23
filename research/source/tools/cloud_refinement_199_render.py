import bpy,sys,time,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/clouds-199'
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
s=bpy.context.scene
for g in(g149,g156,g161,g192):g(s,embed=False)
s.render.filepath=str(O/'main-4k.png');s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t}))
