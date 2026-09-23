import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_degenerate_cleanup_156 import apply
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];d=apply(C);O=R/'art/studies/coliseum-156/preflight/cleanup';(O/'audit.json').write_text(json.dumps(d,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'));print('PASS',d['removed_exact_zero_faces'])
