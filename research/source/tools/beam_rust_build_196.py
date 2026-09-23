import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/beam-rust-196'
from coliseum_ink_regression_149 import apply as g149
from coliseum_foreground_visibility_156 import apply as g156
from coliseum_foreground_visibility_161 import apply as g161
from architecture_ink_visibility_192 import apply as g192
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
 for g in(g149,g156,g161,g192):g(s,embed=False)
 s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t}))
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-weathering-195/scene.blend'));s=bpy.context.scene
 source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);before=fingerprint(s);old=material_snapshot()
 from beam_rust_connections_196 import apply
 result=apply(s);after=fingerprint(s);changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};assert len(changes)==18 and all(set(v)=={'materials'}for v in changes.values());new=material_snapshot();assert all(new[k]==v for k,v in old.items())
 (O/'generation.json').write_text(json.dumps(result,indent=2));(O/'preservation.json').write_text(json.dumps({'changes':changes,'all_source_geometry_transforms_normals_and_old_materials_unchanged':True},indent=2));s.render.filepath='//main-4k.png';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
