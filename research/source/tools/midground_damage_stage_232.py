import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/midground-damage-232';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/broken-walls-232/scene.blend'));s=bpy.context.scene
from rooftop_variety_232 import apply as roofs
from broken_wall_weathering_refine_232 import apply as walls

a={};a['roofs']=roofs(s);print('232 ROOFS INTEGRATED',flush=True);a['walls']=json.loads((R/'art/studies/broken-walls-232/audit.json').read_text());print('232 WALLS INTEGRATED',flush=True)
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


(O/'walls-roofs-audit.json').write_text(json.dumps(a,indent=2));s.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'walls-roofs.blend'))
K=R/'art/components/facades/v232';K.mkdir(parents=True,exist_ok=True);cols={o.instance_collection for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection};bpy.data.libraries.write(str(K/'midground-buildings.blend'),cols,fake_user=True,compress=True);print('232 COMBINED READY',flush=True)
