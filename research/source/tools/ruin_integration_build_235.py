import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/ruin-integration-235';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ruined-wall-structure-235/scene-v2.blend'))
from ruined_wall_finish_235 import apply as finish,ink
from near_window_weathering_235 import apply as windows
s=bpy.context.scene;a={'structure':json.loads((R/'art/studies/ruined-wall-structure-235/audit.json').read_text()),'course_revision':json.loads((R/'art/studies/ruined-wall-structure-235/course-v2-audit.json').read_text()),'wall_finish':finish(s),'wall_ink':ink(s),'near_windows':windows(s)}
(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
K=R/'art/components/ruins/v235';K.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(K/'ruined-walls.blend'),{bpy.data.collections['133 Ruined transition structures']},fake_user=True,compress=True);print('235 INTEGRATION SAVED',flush=True)
