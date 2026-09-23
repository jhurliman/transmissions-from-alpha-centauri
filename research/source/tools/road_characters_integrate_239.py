import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/road-characters-239';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rubble-variation-237/scene.blend'));s=bpy.context.scene
from road_paint_239 import apply as road
from character_shadows_239 import apply as shadows
from character_shadow_receiver_239 import apply as receiver
from sun_light_alignment_239 import apply as light
from sun_material_alignment_239 import apply as material_light
la=light(s);ma=material_light(s);r=road(s);sh=shadows(s);rc=receiver(s,sh['casters']);(O/'audit.json').write_text(json.dumps({'road':r,'shadows':sh,'receiver':rc,'sun_alignment':la,'material_alignment':ma},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
