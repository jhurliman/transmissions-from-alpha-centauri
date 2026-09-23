import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/hybrid-finish-241';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/hybrid-atmosphere-240/scene.blend'));s=bpy.context.scene
from atmosphere_finish_241 import apply as fog
from highlight_fix_241 import apply as highlight
from ruin_ink_241 import apply as ink
from tunnel_caps_241 import apply as caps
a={'fog':fog(s),'highlight':highlight(s),'ruin_ink':ink(s),'tunnel_caps':caps(s)}
(O/'audit.json').write_text(json.dumps(a,indent=2));s.eevee.shadow_pool_size='1024';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('241 BUILD COMPLETE',flush=True)
