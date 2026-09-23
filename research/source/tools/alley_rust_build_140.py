import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/alley-rust-140';O.mkdir(exist_ok=True)
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t}));raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-138/scene.blend'));s=bpy.context.scene
# Reuse the audited snapshot functions without executing that module's builder.
src=(R/'tools/scene_integration_138.py').read_text();defs=src[src.index('def objects('):src.index("if 'render' not in sys.argv:")];exec(defs)
before=fingerprint(s);mats=material_snapshot()
from alley_rust_140 import apply
result=apply(s);after=fingerprint(s);changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};allowed={r['object']for r in result['changed_slots']};assert set(before)==set(after);assert all(k in allowed and fs==['materials']for k,fs in changes.items());ma=material_snapshot();assert all(v==ma[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'changed':changes,'all_geometry_normals_transforms_lights_camera_old_material_graphs_unchanged':True},indent=2));(O/'generation.json').write_text(json.dumps(result,indent=2));s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
