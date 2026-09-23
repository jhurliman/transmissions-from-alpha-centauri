import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from alley_roof_seating_215 import apply
for name in ('current-sun','right-sun'):
 d=R/'art/studies/scene-direction-218'/name;bpy.ops.wm.open_mainfile(filepath=str(d/'scene.blend'))
 apply(bpy.context.scene,str(d/'roof-seating-audit.json'))
 bpy.ops.wm.save_as_mainfile(filepath=str(d/'scene.blend'))
 print('218 ROOFS SEATED',name,flush=True)
