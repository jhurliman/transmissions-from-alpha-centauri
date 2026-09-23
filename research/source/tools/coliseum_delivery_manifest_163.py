"""Hash-pinned incremental native163 recipe from the corrected159 scene."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-163'
INPUTS={
 'historical_native_inputs':['art/studies/coliseum-159/scene.blend','art/studies/coliseum-159/delivery-manifest.json'],
 'build_code':['tools/coliseum_integration_163.py','tools/coliseum_broad_age_162.py','tools/coliseum_facade_age_152.py','tools/coliseum_course_age_158.py','tools/scene_integration_138.py','tools/coliseum_ink_regression_149.py','tools/coliseum_foreground_visibility_156.py','tools/coliseum_foreground_visibility_161.py'],
 'configuration':['config/coliseum-broad-age-162.json','config/coliseum-course-age-158.json','config/coliseum-facade-age-152.json'],
 'delivery_code':['tools/coliseum_delivery_audit_163.py','tools/coliseum_kit_proof_163.py','tools/coliseum_validate_163.py','tools/publish_coliseum_163.py','tools/coliseum_delivery_manifest_163.py']}
OUTPUTS=['scene.blend','kit.blend','main-4k.png','generation.json','preservation.json','fresh-native-delivery-check.json','native-ink-visibility.json','foreground-ink-visibility.json','fascia-ink-visibility161.json','kit-proof/append-audit.json','critic.json']
def stamp(rel):
 p=R/rel;h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
out={
 'scope':'Incremental native163 build from corrected159; historical input is required to rebuild. Standalone saved scene is self-contained.',
 'runtime':{'blender':'5.2.1','build_dependencies':'Bundled bpy,bmesh,mathutils,numpy','delivery_dependencies':'Python3,Pillow,numpy,scipy'},
 'inputs':{k:[stamp(p)for p in v]for k,v in INPUTS.items()},
 'outputs':[stamp(str((O/p).relative_to(R)))for p in OUTPUTS],
 'commands_from_project_root':[
  'blender -b -t 4 --python tools/coliseum_integration_163.py',
  'blender -b -t 4 --python tools/coliseum_integration_163.py -- render',
  'blender -b -t 2 --python tools/coliseum_delivery_audit_163.py',
  'blender -b -t 4 --python tools/coliseum_kit_proof_163.py -- coliseum-163',
  'python3 tools/publish_coliseum_163.py',
  'python3 tools/coliseum_validate_163.py',
  'python3 tools/coliseum_delivery_manifest_163.py'],
 'standalone_saved_scene':{'external_files_required_to_render':False,'native_visibility_texts':['149 Native fascia visibility guard.py','156 Proven foreground occlusion guard.py','161 Proven fascia occlusion guard.py'],'instruction':'Run all three embedded texts before rendering, or use trusted auto-execution for this project file. No global preference change required.','portable_kit_collection':'110 Coliseum detailed front ruin'},
 'limits':['Reproduction may show small raster variation by Blender version or hardware.','Dependency and preservation checks do not imply globally clean topology or artistic approval.','Scores remain independent evidence, not completion guaranteed by a build.']}
(O/'delivery-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Recorded',sum(map(len,INPUTS.values())),'inputs and',len(OUTPUTS),'outputs')
