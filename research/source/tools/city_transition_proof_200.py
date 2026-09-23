import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200';sys.path.insert(0,str(R/'tools'))
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
from middle_rubble_palette_204 import apply as palette204
a204=palette204(s);(O/'palette204-proof-audit.json').write_text(json.dumps(a204,indent=2))
for g in(g149,g156,g161,g192):g(s,embed=False)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=True;s.render.use_freestyle=True
box=(1080,880,2720,1530);s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=box[0]/3840;s.render.border_max_x=box[2]/3840;s.render.border_min_y=1-box[3]/2885;s.render.border_max_y=1-box[1]/2885;s.render.filepath=str(O/'transition-204-native.png')
t=time.time();bpy.ops.render.render(write_still=True);(O/'proof-performance.json').write_text(json.dumps(dict(seconds=time.time()-t,region_native=box,resolution=[3840,2885],guards=[149,156,161,192],native_compositor=True),indent=2));print('200_PROOF_DONE',flush=True)
