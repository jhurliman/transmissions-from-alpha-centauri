import bpy,sys,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/colosseum-scale-210'
from landmark_contact_visibility_210 import apply
label=sys.argv[sys.argv.index('--')+1];dest=O/label;held=O/'held-previsibility'/label;held.mkdir(parents=True,exist_ok=True)
for name in ('scene.blend','preview.png','audit.json'):
 if (dest/name).exists() and not (held/name).exists():shutil.copy2(dest/name,held/name)
bpy.ops.wm.open_mainfile(filepath=str(held/'scene.blend'));a=apply(bpy.context.scene,dest/'contact-visibility.json');bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'));print('VISIBILITY_BUILT',label,a['result_points'],flush=True)
