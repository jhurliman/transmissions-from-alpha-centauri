import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/midground-damage-232'
bpy.ops.wm.open_mainfile(filepath=str(O/'walls-roofs.blend'))
from colosseum_arch_fractures_232 import apply
from window_pipe_refine_232 import apply as windowpipes
from arch_proportions_232 import apply as proportions
from broken_wall_finish_balance_232 import apply as finishbalance
s=bpy.context.scene
a=json.loads((O/'walls-roofs-audit.json').read_text());a['windowpipes']=windowpipes(s);a['proportions']=proportions(s);a['finish_balance']=finishbalance(s)
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

a['arches']=apply(s)
(O/'integration-audit.json').write_text(json.dumps(a,indent=2));bpy.context.scene.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('232 FINAL READY',flush=True)

K=R/'art/components/facades/v232';cols={o.instance_collection for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection};bpy.data.libraries.write(str(K/'midground-buildings.blend'),cols,fake_user=True,compress=True)
