import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-finish-244';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/footing-243/scene.blend'));s=bpy.context.scene
from roof_edge_244 import apply as roof
from window_bank_244 import apply as windows
from tunnel_shading_244 import apply as tunnels
from footing_curve_ink_244 import apply as footing
r={'roof':roof(s),'windows':windows(s),'tunnels':tunnels(s),'footing_ink':footing(s)};(O/'audit.json').write_text(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('244 BUILD COMPLETE',flush=True)
