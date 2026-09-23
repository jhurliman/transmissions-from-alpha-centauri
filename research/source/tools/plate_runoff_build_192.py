"""Keep rust pigment out of native ink visibility; proof before publishing."""
import bpy, json, sys, time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/plate-runoff-192'
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
 s=bpy.context.scene
 for g in (g149,g156,g161):g(s,embed=False)
 g192(s,embed=False,audit_path=str(O/"side-return-ink-audit.json"))
 s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True)
 (O/'performance.json').write_text(json.dumps({'seconds':time.time()-t},indent=2))
else:
 bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
 from rust_ink_isolation_192 import apply
 audit=apply(s)
 for g in (g149,g156,g161):g(s,embed=True)
 g192(s,embed=True)
 s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100
 s.render.filepath='//main-4k.png'
 (O/'ink-isolation.json').write_text(json.dumps(audit,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
