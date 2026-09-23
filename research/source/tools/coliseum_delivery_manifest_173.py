"""Hash-pinned incremental native173 recipe from the retained168 scene."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-173'
INPUTS={
 'historical_native_inputs':['art/studies/coliseum-168/scene.blend','art/studies/coliseum-168/delivery-manifest.json'],
 'build_code':['tools/coliseum_integration_173.py','tools/coliseum_primary_chroma_172.py','tools/scene_integration_138.py','tools/coliseum_ink_regression_149.py','tools/coliseum_foreground_visibility_156.py','tools/coliseum_foreground_visibility_161.py'],
 'configuration':['config/coliseum-primary-chroma-172.json','config/coliseum-integration-173.json'],
 'delivery_code':['tools/coliseum_delivery_audit_173.py','tools/coliseum_contact_clip_169.py','tools/coliseum_kit_proof_173.py','tools/coliseum_validate_173.py','tools/publish_coliseum_173.py','tools/coliseum_delivery_manifest_173.py']}
OUTPUTS=['scene.blend','kit.blend','main-4k.png','generation.json','preservation.json','fresh-native-delivery-check.json','native-ink-visibility.json','foreground-ink-visibility.json','fascia-ink-visibility161.json','kit-proof/append-audit.json','kit-proof/primary-painted.png','kit-proof/primary-clay.png','critic.json','review.json']
def stamp(rel):
 p=R/rel;h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
out={
 'scope':'Incremental native173 build from retained168; historical input is required to rebuild. Standalone saved scene is self-contained.',
 'runtime':{'blender':'5.2.1','build_dependencies':'Bundled bpy,bmesh,mathutils,numpy','delivery_dependencies':'Python3,Pillow,numpy,scipy'},
 'inputs':{k:[stamp(p)for p in v]for k,v in INPUTS.items()},
 'outputs':[stamp(str((O/p).relative_to(R)))for p in OUTPUTS],
 'commands_from_project_root':[
  'blender -b -t 4 --python tools/coliseum_integration_173.py',
  'blender -b -t 4 --python tools/coliseum_integration_173.py -- render',
  'blender -b -t 2 --python tools/coliseum_delivery_audit_173.py',
  'blender -b -t 4 --python tools/coliseum_kit_proof_173.py -- coliseum-173',
  'python3 tools/publish_coliseum_173.py',
  'python3 tools/coliseum_validate_173.py',
  'python3 tools/coliseum_delivery_manifest_173.py'],
 'standalone_saved_scene':{'external_files_required_to_render':False,'native_visibility_texts':['149 Native fascia visibility guard.py','156 Proven foreground occlusion guard.py','161 Proven fascia occlusion guard.py'],'instruction':'Run all three embedded texts before rendering, or use trusted auto-execution for this project file. No global preference change required.','portable_kit_collection':'110 Coliseum detailed front ruin','portable_kit_extra_object':'110 Landmark contact ink','kit_instruction':'Append the collection and the separate contact ink object, preserving their transforms.'},
 'limits':['Reproduction may show small raster variation by Blender version or hardware.','Dependency and preservation checks do not imply globally clean topology or artistic approval.','Scores remain independent evidence, not completion guaranteed by a build.']}
(O/'delivery-manifest.json').write_text(json.dumps(out,indent=2)+'\n')
print('Recorded',sum(map(len,INPUTS.values())),'inputs and',len(OUTPUTS),'outputs')
