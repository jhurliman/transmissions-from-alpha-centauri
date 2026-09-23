import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/final-geometry-242'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
from footing_ink_fix_242 import apply as footink
from damage_edges_242 import apply_impact
r={'footing_ink':footink(s),'cited_impact':apply_impact(s)}
(O/'finish-audit.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('242 FINISH READY',flush=True)
