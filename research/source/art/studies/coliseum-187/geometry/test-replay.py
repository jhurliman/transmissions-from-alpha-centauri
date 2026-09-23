import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'tools'));from coliseum_left_course_187 import apply
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));r=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(R/'art/studies/coliseum-187/geometry/replay-audit.json').write_text(json.dumps(r,indent=2));print('187 REPLAY PASS')
