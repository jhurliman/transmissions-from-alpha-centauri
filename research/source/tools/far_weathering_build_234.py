import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/far-weathering-234';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/far-facade-damage-234/damage-only.blend'))
from far_facade_damage_234 import apply as damage
from window_stains_234 import apply as stains
s=bpy.context.scene;a={'damage':json.loads((R/'art/studies/far-facade-damage-234/audit.json').read_text()),'stains':stains(s)}
(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
K=R/'art/components/facades/v234';K.mkdir(parents=True,exist_ok=True);cols={o.instance_collection for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection};bpy.data.libraries.write(str(K/'midground-buildings.blend'),cols,fake_user=True,compress=True)
d=json.loads((R/'art/components/facades/v233/interfaces.json').read_text());d['source_scene']='art/studies/far-weathering-234/scene.blend';d['buildings']=sorted(c.name for c in cols);d['finish']='Broad scene-scale rain and light stains with native facade recesses and large fractures';(K/'interfaces.json').write_text(json.dumps(d,indent=2));print('234 BUILD READY',flush=True)
