import bpy,sys,json,time
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-156/regression';from coliseum_ink_regression_149 import apply as oldguard
from coliseum_foreground_visibility_156 import apply
if 'render'in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'guarded.blend'));s=bpy.context.scene;oldguard(s,embed=False);apply(s,embed=False);s.render.filepath=str(O/'guarded.png');bpy.ops.render.render(write_still=True)
 import parameter_editor
 (O/'visibility-render-audit.json').write_text(json.dumps([f._guard156_audit for f in parameter_editor.callbacks_modifiers_post if getattr(f,'_guard156',False)],indent=2))
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;oldguard(s,embed=True);apply(s,embed=True);s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'guarded.blend'))
