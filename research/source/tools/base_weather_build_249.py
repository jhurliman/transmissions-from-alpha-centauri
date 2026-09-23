import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/base-weather-249';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ruin-ink-248/scene.blend'));s=bpy.context.scene
from step_weather_249 import apply as steps
from column_weather_249 import apply as column
from step_crack_ink_249 import apply as cracks
a={'steps':steps(s),'column':column(s),'crack_lines':cracks(s)};(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
