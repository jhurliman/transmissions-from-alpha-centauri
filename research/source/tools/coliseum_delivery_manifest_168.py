"""Hash-pinned incremental native168 recipe from the retained166 scene."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-168'
INPUTS={
 'historical_native_inputs':['art/studies/coliseum-166/scene.blend','art/studies/coliseum-166/delivery-manifest.json'],
 'build_code':['tools/coliseum_integration_168.py','tools/coliseum_shoulder_failure_167.py','tools/coliseum_contact_clip_169.py','tools/coliseum_contact_certificate_169.py','tools/coliseum_crown_continuation_154.py','tools/scene_integration_138.py','tools/coliseum_ink_regression_149.py','tools/coliseum_foreground_visibility_156.py','tools/coliseum_foreground_visibility_161.py'],
 'configuration':['config/coliseum-integration-168.json','config/coliseum-shoulder-failure-167.json','art/studies/coliseum-169/contact/clip-payload.json','art/studies/coliseum-169/contact/source-transform.json'],
 'delivery_code':['tools/coliseum_delivery_audit_168.py','tools/coliseum_contact_delivery_168.py','tools/coliseum_kit_proof_168.py','tools/coliseum_validate_168.py','tools/publish_coliseum_168.py','tools/coliseum_delivery_manifest_168.py']}
OUTPUTS=['scene.blend','kit.blend','main-4k.png','generation.json','preservation.json','contact-ink-preservation.json','continuous-contact-support.json','fresh-native-delivery-check.json','native-ink-visibility.json','foreground-ink-visibility.json','fascia-ink-visibility161.json','kit-proof/append-audit.json','critic.json']
def stamp(rel):
 p=R/rel;h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
out={
 'scope':'Incremental native168 build from retained166; historical input is required to rebuild. Standalone saved scene is self-contained.',
 'runtime':{'blender':'5.2.1','build_dependencies':'Bundled bpy,bmesh,mathutils,numpy','delivery_dependencies':'Python3,Pillow,numpy,scipy'},
 'inputs':{k:[stamp(p)for p in v]for k,v in INPUTS.items()},
 'outputs':[stamp(str((O/p).relative_to(R)))for p in OUTPUTS],
 'commands_from_project_root':[
  'blender -b -t 4 --python tools/coliseum_integration_168.py',
  'blender -b -t 4 --python tools/coliseum_integration_168.py -- render',
  'blender -b -t 2 --python tools/coliseum_delivery_audit_168.py',
  'blender -b -t 2 --python tools/coliseum_contact_delivery_168.py',
  'blender -b -t 4 --python tools/coliseum_kit_proof_168.py -- coliseum-168',
  'python3 tools/publish_coliseum_168.py',
  'python3 tools/coliseum_validate_168.py',
  'python3 tools/coliseum_delivery_manifest_168.py'],
 'standalone_saved_scene':{'external_files_required_to_render':False,'native_visibility_texts':['149 Native fascia visibility guard.py','156 Proven foreground occlusion guard.py','161 Proven fascia occlusion guard.py'],'instruction':'Run all three embedded texts before rendering, or use trusted auto-execution for this project file. No global preference change required.','portable_kit_collection':'110 Coliseum detailed front ruin','portable_kit_extra_object':'110 Landmark contact ink','kit_instruction':'Append the collection and the separate contact ink object, preserving their transforms.'},
 'limits':['Reproduction may show small raster variation by Blender version or hardware.','Dependency and preservation checks do not imply globally clean topology or artistic approval.','Scores remain independent evidence, not completion guaranteed by a build.']}
(O/'delivery-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Recorded',sum(map(len,INPUTS.values())),'inputs and',len(OUTPUTS),'outputs')
