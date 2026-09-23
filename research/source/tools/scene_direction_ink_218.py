import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from alley_ink_atmosphere_215 import apply
for label in ('current-sun','right-sun'):
 d=R/'art/studies/scene-direction-218'/label;bpy.ops.wm.open_mainfile(filepath=str(d/'scene.blend'))
 audit=apply(bpy.context.scene);(d/'far-ink-atmosphere-audit.json').write_text(json.dumps(audit,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(d/'scene.blend'));print('218 FAR INK FIXED',label,flush=True)
