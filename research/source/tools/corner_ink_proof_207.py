import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/corner-ink-207';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-205/scene.blend'));s=bpy.context.scene
from coliseum_ink_regression_149 import apply as a149
from coliseum_foreground_visibility_156 import apply as a156
from coliseum_foreground_visibility_161 import apply as a161
from architecture_ink_visibility_192 import apply as a192
from architecture_ink_visibility_205 import apply as a205
for fn in(a149,a156,a161,a192,a205):fn(s,embed=False)
import architecture_ink_capture_192 as capture
capture.REGION=(325,12,430,108)
# Register capture after inherited guards and before207 so actual offending owners are retained in diagnostic output.
def install207(scene,*args):
 capture.install(scene,O/'native-strokes.json')
 import architecture_ink_visibility_207 as guard
 guard.install(scene,str(O/'native-guard-audit.json'))
bpy.app.handlers.render_pre.append(install207)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=True;s.render.use_compositing=True
box=(300,0,620,450);s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=box[0]/3840;s.render.border_max_x=box[2]/3840;s.render.border_min_y=1-box[3]/2885;s.render.border_max_y=1-box[1]/2885;s.render.filepath=str(O/'after-top-native.png')
t=time.time();bpy.ops.render.render(write_still=True);(O/'proof-performance.json').write_text(json.dumps({'seconds':time.time()-t,'region':box,'guards':[149,156,161,192,205,207],'native_current_scene_ink':True},indent=2));print('207_PROOF_DONE',flush=True)
