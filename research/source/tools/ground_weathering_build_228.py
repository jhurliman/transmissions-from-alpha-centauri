"""Integrate approved entrance geometry with stronger wear, dust and base steps."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/ground-weathering-steps-228';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entrance-weathering-227/entrance-only.blend'));s=bpy.context.scene
from stone_dust_227 import apply as dust
from colosseum_steps_228 import apply as stairs
a={'source':'art/studies/entrance-weathering-227/entrance-only.blend','dust':dust(s),'stairs':stairs(s)}
s.render.filepath=str(O/'main-4k.png');(O/'integration-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('228 COMBINED READY',flush=True)
