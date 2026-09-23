"""Scene-depth correction for the proven dedicated landmark contact owner only."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-repeat-212';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));s=bpy.context.scene
assert not s.get('212 dedicated landmark ink visibility fixed'), 'Use preserved V1 to avoid re-clipping already corrected data.'
old_city_gp=bpy.data.objects.get('101 A city contacts')
if old_city_gp:old_city_gp.hide_render=True
from landmark_contact_visibility_210 import apply
report=apply(s,O/'landmark-contact-visibility-audit.json');s['212 dedicated landmark ink visibility fixed']=True
# Preserve reproducible depth guards for private far instances when native scripts are enabled.
code=f'''import bpy,sys
sys.path.insert(0,{str(R/'tools')!r})
from alley_repeat_212 import repeat_guard_pairs,install_far_guard_callbacks
repeat_guard_pairs(bpy.context.scene)
def far_pre_212(scene,*args):
 install_far_guard_callbacks(scene)
far_pre_212._far_pre212=True
bpy.app.handlers.render_pre[:]=[f for f in bpy.app.handlers.render_pre if not getattr(f,'_far_pre212',False)]
bpy.app.handlers.render_pre.append(far_pre_212)
'''
t=bpy.data.texts.get('212 Repeated alley native ink guards.py')or bpy.data.texts.new('212 Repeated alley native ink guards.py');t.clear();t.write(code);t.use_module=True
p=O/'audit.json';a=json.loads(p.read_text());a['dedicated_landmark_ink_visibility']={'owner':'110 Landmark contact ink','audit':'landmark-contact-visibility-audit.json','proof_of_owner':'gp-owner-projection-overlay.png','scope':'Only dedicated landmark GP runs genuinely hidden by scene opaque surfaces; original drawing retained with fake user','helper_sha256':hashlib.sha256((R/'tools/landmark_contact_visibility_210.py').read_bytes()).hexdigest()};a['old_city_GP_hidden']={'owner':'101 A city contacts','inventory':'old-city-gp-inventory.json','provenance':'render_city_101.py creates city-only contact companion; filter_city_101 retains contacts touching city only'};a['far_guard_callback_extension']={'styles':'212 Far architecture *','existing_native_rules':[192,205,207],'near_rules_unchanged':True};p.write_text(json.dumps(a,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('212_VISIBILITY_FIX_DONE',report['hidden_owner_counts'],flush=True)
