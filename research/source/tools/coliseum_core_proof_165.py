"""Native material-only165 proof with complete scene preservation comparison."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-165/material';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot()
from coliseum_core_response_165 import apply
d=apply(s);after=fingerprint(s);ma=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};allow={r['object']for r in d['assignments']}
assert set(before)==set(after)
assert all(fields==['materials'] and name in allow for name,fields in changes.items()),changes
assert all(v==ma[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'objects':len(before),'changes':changes,'geometry_normals_transforms_lights_camera_and_existing_material_graphs_unchanged':True},indent=2))
(O/'audit.json').write_text(json.dumps(d,indent=2));s.render.filepath='//main-4k.png';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
x0,y0,x1,y1=d['configuration']['proof_crop_native'];s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885;s.render.filepath=str(O/'after.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'native_proof_seconds':time.time()-t}))
