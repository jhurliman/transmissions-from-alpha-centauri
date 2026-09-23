import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-174/native';sys.path[:0]=[str(R/'tools'),str(O)]
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));from repair_174 import apply
a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'api-audit.json').write_text(json.dumps(a,indent=2));print(a)
