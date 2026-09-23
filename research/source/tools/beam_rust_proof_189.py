import bpy,sys,time,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
O=R/'art/studies/rust-189/beam'
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
for g in (g149,g156,g161):g(s,embed=False)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440
s.render.use_border=True;s.render.use_crop_to_border=True
x0,y0,x1,y1=(120,830,820,2040)
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
s.render.filepath=str(O/'left-native.png');t=time.time();bpy.ops.render.render(write_still=True)
(O/'proof.json').write_text(json.dumps({'box':[x0,y0,x1,y1],'seconds':time.time()-t}))
