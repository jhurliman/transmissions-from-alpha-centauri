import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/final-geometry-242';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/hybrid-finish-241/scene.blend'));s=bpy.context.scene
from service_fit_242 import apply as fit
from service_footing_242 import apply as footing
from damage_edges_242 import apply as damage, apply_impact
from roofline_242 import apply as roof
from footing_ink_fix_242 import apply as footink
rows={'service_fit':fit(s),'footing':footing(s),'damage':damage(s),'roof':roof(s),'footing_ink':footink(s),'cited_impact':apply_impact(s)}
(O/'audit.json').write_text(json.dumps(rows,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('242 BUILD DONE',flush=True)
