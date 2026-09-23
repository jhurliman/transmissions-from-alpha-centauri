import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/ruin-ink-248'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-length-247/scene.blend'))
from far_ruin_ink_248 import apply
(O/'audit.json').write_text(json.dumps(apply(bpy.context.scene),indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
