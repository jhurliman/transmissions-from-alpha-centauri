"""Hash-pinned incremental native159 recipe and deliverable inventory."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-159'
INPUTS={
    'historical_native_inputs':['art/studies/coliseum-156/scene.blend','art/studies/coliseum-160/repair/candidate.blend','art/studies/coliseum-160/repair/preservation-audit.json'],
    'build_code':['tools/coliseum_cornice_failure_157.py','tools/coliseum_cornice_proof_157.py','tools/coliseum_crown_repair_123.py','tools/coliseum_course_age_158.py','tools/coliseum_facade_age_152.py','tools/coliseum_pairing_159.py','tools/coliseum_integration_159.py','tools/scene_integration_138.py','tools/coliseum_return_apply_160.py','tools/coliseum_ink_regression_149.py','tools/coliseum_foreground_visibility_156.py','tools/coliseum_foreground_visibility_161.py'],
    'configuration':['config/coliseum-cornice-failure-157.json','config/coliseum-course-age-158.json','config/coliseum-facade-age-152.json','config/coliseum-pairing-159.json'],
    'delivery_code':['tools/coliseum_delivery_audit_159.py','tools/coliseum_kit_proof_159.py','tools/coliseum_validate_159.py','tools/publish_coliseum_159.py','tools/coliseum_delivery_manifest_159.py']}
OUTPUTS=['scene.blend','kit.blend','main-4k.png','generation.json','preservation.json','fresh-native-delivery-check.json','native-ink-visibility.json','foreground-ink-visibility.json','fascia-ink-visibility161.json','kit-proof/append-audit.json','critic.json']
def stamp(rel):
    p=R/rel;h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return {'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
out={
    'scope':'Incremental native159 build from retained156 plus independently validated160 mesh payload; not a build without historical inputs.',
    'runtime':{'blender':'5.2.1','build_dependencies':'Bundled bpy,bmesh,mathutils,numpy','delivery_dependencies':'Python3,Pillow,numpy,scipy'},
    'inputs':{k:[stamp(p)for p in v]for k,v in INPUTS.items()},
    'outputs':[stamp(str((O/p).relative_to(R)))for p in OUTPUTS],
    'commands_from_project_root':[
        'blender -b -t 4 --python tools/coliseum_cornice_proof_157.py',
        'blender -b -t 4 --python tools/coliseum_pairing_159.py',
        'blender -b -t 4 --python tools/coliseum_integration_159.py -- --include-return',
        'blender -b -t 4 --python tools/coliseum_integration_159.py -- render',
        'blender -b -t 2 --python tools/coliseum_delivery_audit_159.py',
        'blender -b -t 4 --python tools/coliseum_kit_proof_159.py -- coliseum-159',
        'python3 tools/publish_coliseum_159.py',
        'python3 tools/coliseum_validate_159.py',
        'python3 tools/coliseum_delivery_manifest_159.py'],
    'standalone_saved_scene':{'external_files_required_to_render':False,'native_visibility_texts':['149 Native fascia visibility guard.py','156 Proven foreground occlusion guard.py','161 Proven fascia occlusion guard.py'],'instruction':'Run all three embedded texts before rendering, or use trusted auto-execution for this project file. No global preference change required.','portable_kit_collection':'110 Coliseum detailed front ruin'},
    'limits':['The exact historical native inputs are included in this inventory;160 payload reconstruction is a separate documented technical study.','Reproduction may show small raster variation by Blender version or hardware.','The dependency/preservation checks do not imply globally clean topology or artistic approval.']}
(O/'delivery-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Recorded',sum(map(len,INPUTS.values())),'inputs and',len(OUTPUTS),'outputs')
