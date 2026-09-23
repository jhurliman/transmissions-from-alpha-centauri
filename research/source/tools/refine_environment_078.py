import bpy,sys,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/reviews/xenon-078';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-077/scene.blend'));s=bpy.context.scene
from ground_finish_078 import apply
apply(s)
from ground_connections_078 import apply as connections
connections(s)
if os.environ.get('INCLUDE_DETAILS'):
 from end_rubble_077 import apply_detail
 apply_detail(s)
 from scrap_strip_refine_078 import apply as strips
 strips(s)
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
