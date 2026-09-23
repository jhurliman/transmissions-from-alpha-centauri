import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/midground-230'
bpy.ops.wm.open_mainfile(filepath=str(O/'layout-only.blend'));s=bpy.context.scene
from far_facades_230 import apply as facades
from far_services_roofs_230 import apply as services
from broken_wall_weathering_230 import apply as walls
a={};a['facades']=facades(s);print('230 FACADES INTEGRATED',flush=True);a['services']=services(s);print('230 SERVICES INTEGRATED',flush=True);a['walls']=walls(s);print('230 WALLS INTEGRATED',flush=True)
from landmark_contact_visibility_210 import restore_unclipped,apply as clip
a['contact_restore']=restore_unclipped(s,'84e3787b91152c4f17587b201a6808531ae69a1e5a96d71e8eda62c2e5da8358');a['external_contact_visibility']=clip(s)
from arcade_sills_225 import solid_tree,clip_lost_contacts
C=bpy.data.collections['110 Coliseum detailed front ruin'];targets=[o for o in C.objects if o.get('tier')==0 and(o.get('125 inset platform')or o.name.endswith(' sill'))];hidden={o:o.hide_render for o in targets}
try:
 for o in targets:o.hide_render=False
 oldtree,oldvs=solid_tree(targets)
finally:
 for o,v in hidden.items():o.hide_render=v
a['preserved225_contact_cleanup']=clip_lost_contacts(s,oldtree,oldvs,C)
(O/'integration-audit.json').write_text(json.dumps(a,indent=2));s.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
kit=R/'art/components/facades/v230';kit.mkdir(parents=True,exist_ok=True);cols={r.instance_collection for r in bpy.data.collections['215 Short alley composition'].objects if r.instance_collection};bpy.data.libraries.write(str(kit/'midground-buildings.blend'),cols,fake_user=True,compress=True);print('230 COMBINED READY',flush=True)
