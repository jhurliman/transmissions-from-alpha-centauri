import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/standalone/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin']
from coliseum_triangulation_134 import apply
r=apply(C);O=R/'art/studies/coliseum-134/topology-diagnostics';(O/'safe-module-audit.json').write_text(json.dumps(r,indent=2));bpy.data.libraries.write(str(O/'safe-triangulated-walls.blend'),{o for o in C.all_objects if o.get('134 safe prelayout triangulation')});print(json.dumps(r))
