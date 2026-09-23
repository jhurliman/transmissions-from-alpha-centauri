import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/hybrid-atmosphere-240'
bpy.ops.wm.open_mainfile(filepath=str(O/'hybrid-only.blend'));s=bpy.context.scene
from haze_variance_240 import apply as haze
from left_blue_balance_240 import apply as blue
h=haze(s);b=blue(s);a={'hybrid':json.loads((O/'hybrid-audit.json').read_text()),'haze':h,'left_blue':b};(O/'audit.json').write_text(json.dumps(a,indent=2));s.eevee.shadow_pool_size='1024';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
