"""Combine reviewed broad facing loss and material age with latest147 scene."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-148';O.mkdir(exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]}));raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-weathering-147/actual/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot();C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
from coliseum_spall_141 import apply as spall
from coliseum_weathering_148 import apply as weather
from coliseum_cornice_loss_148 import apply as cornice
result={'geometry':spall(C),'cornice':cornice(C),'material':weather(C,1.0)};after=fingerprint(s);mat_after=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};geonames={r['object']for r in result['geometry']['targets']+result['cornice']['targets']};matnames={r['object']for r in result['material']['assignments']}
assert set(before)==set(after)
for k,fields in changes.items():
 for field in fields:
  assert (field=='materials' and k in (matnames|geonames))or(field in ['geometry','normals']and k in geonames),(k,fields)
assert all(v==mat_after[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'changes':changes,'existing_material_graphs_unchanged':True,'only_authorized_landmark_geometry_and_material_slots':True,'all147alley_camera_lights_and_unrelated_geometry_unchanged':True},indent=2));(O/'generation.json').write_text(json.dumps(result,indent=2));s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
