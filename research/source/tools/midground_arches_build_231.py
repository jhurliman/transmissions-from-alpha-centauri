import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/midground-arches-231';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-230/scene.blend'))
from arch_ornaments_231 import apply
a=apply(bpy.context.scene);(O/'arch-audit.json').write_text(json.dumps(a,indent=2));bpy.context.scene.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('231 COMBINED READY',flush=True)
