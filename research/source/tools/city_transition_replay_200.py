import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from city_transition_refinement_200 import apply
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));a=apply(bpy.context.scene);(R/'art/studies/city-transition-200/replay-audit.json').write_text(json.dumps(a,indent=2));print('200_REPLAY_PASS',flush=True)
