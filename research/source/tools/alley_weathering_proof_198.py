"""Root-scheduled native proof; requires a GPU reservation."""
import bpy,json,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-198'
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
sys.path.insert(0,str(R/'tools'))
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
for guard in (g149,g156,g161,g192):guard(s,embed=False)
# Keep inherited compositing and separate ink architecture. Native 4K proof.
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'main-4k.png')
t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'render_seconds':time.time()-t,'resolution':[3840,2885],'inherited_compositor':True},indent=2))
