"""Combine reusable entrances, right-alley soil, and matching bank-stone dust."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-ground-update-225';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-floor-kit-222/scene.blend'));s=bpy.context.scene
assert s.objects['Distant dust volume - real lighting'].active_material.node_tree.nodes.get('221 Real opacity increase')
from right_alley_soil_224 import apply as soil
from foundation_dust_223 import apply as dust
from arcade_sills_225 import apply as sills
a={'source':'art/studies/ground-floor-kit-222/scene.blend','integration_order':[222,221,224,223,225],'soil':soil(s),'dust':dust(s),'arcade_sills':sills(s)}
s.render.filepath=str(O/'main-4k.png');(O/'integration-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('225 COMBINED READY',flush=True)
