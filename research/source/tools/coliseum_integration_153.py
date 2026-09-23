"""Integrate five bounded cornice-pigment corrections on retained152."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-153';O.mkdir(exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
from coliseum_ink_regression_149 import apply as visibility
if 'render'in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;visibility(s,embed=False);s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]}))
 import parameter_editor
 (O/'native-ink-visibility.json').write_text(json.dumps([f._guard_149_audit for f in parameter_editor.callbacks_modifiers_post if getattr(f,'_guard_149',False)],indent=2));raise SystemExit
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot();C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
from coliseum_edge_material_153 import apply as quiet
result={'cornice_readability':quiet(C),'native_visibility':visibility(s,embed=True)};after=fingerprint(s);ma=material_snapshot();changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};geo=set();mat={r['object']for r in result['cornice_readability']['assignments']}
assert set(before)==set(after)
for name,fields in changes.items():
 for field in fields:assert(field in ['geometry','normals']and name in geo)or(field=='materials'and name in geo|mat),(name,field)
assert all(v==ma[k]for k,v in mats.items())
(O/'preservation.json').write_text(json.dumps({'changes':changes,'existing_material_graphs_unchanged':True,'unrelated_geometry_normals_camera_lights_transforms_unchanged':True,'geometry_targets':sorted(geo),'compared_objects':len(before),'scope':'Five private local material assignments; geometry and all lighting unchanged'},indent=2));(O/'generation.json').write_text(json.dumps(result,indent=2));s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_freestyle=True;s.render.use_compositing=False;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
