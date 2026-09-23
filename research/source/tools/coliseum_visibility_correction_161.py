"""Render the isolated native161 visibility correction against159."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-161/visibility'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-159/scene.blend'));s=bpy.context.scene
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
before=fingerprint(s);mats=material_snapshot()
from coliseum_ink_regression_149 import apply as a
from coliseum_foreground_visibility_156 import apply as b
from coliseum_foreground_visibility_161 import apply as c
a(s,embed=False);b(s,embed=False);c(s,embed=True)
assert before==fingerprint(s);assert mats==material_snapshot()
s.render.filepath='//main-4k.png';bpy.ops.wm.save_as_mainfile(filepath=str(O/'guarded.blend'))
s.render.filepath=str(O/'guarded.png');t=time.time();bpy.ops.render.render(write_still=True)
import parameter_editor
audit={'native_data_unchanged':True,'objects':len(before),'existing_material_graphs_unchanged':True,'render_seconds':time.time()-t}
for flag,name in [('_guard_149','guard149'),('_guard156','guard156'),('_guard161','guard161')]:
    audit[name]=[getattr(f,flag+'_audit')for f in parameter_editor.callbacks_modifiers_post if getattr(f,flag,False)]
(O/'guarded-render-audit.json').write_text(json.dumps(audit,indent=2))
