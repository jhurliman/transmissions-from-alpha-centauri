import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-recess-208'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-completion-205/scene.blend'))
from alley_recess_refinement_208 import apply
a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
