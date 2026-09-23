import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-recess-208';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
from coliseum_ink_regression_149 import apply as a149
from coliseum_foreground_visibility_156 import apply as a156
from coliseum_foreground_visibility_161 import apply as a161
from architecture_ink_visibility_192 import apply as a192
from architecture_ink_visibility_205 import apply as a205
for fn in(a149,a156,a161,a192,a205):fn(s,embed=False)
def g207(scene,*args):
 from architecture_ink_visibility_207 import install
 install(scene,str(O/'207-guard-proof.json'))
bpy.app.handlers.render_pre.append(g207)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=True;s.render.use_compositing=True
box=(0,810,760,1950);s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=box[0]/3840;s.render.border_max_x=box[2]/3840;s.render.border_min_y=1-box[3]/2885;s.render.border_max_y=1-box[1]/2885;s.render.filepath=str(O/'after-first-building.png')
t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'box':box}));print('208_PROOF_DONE',flush=True)
