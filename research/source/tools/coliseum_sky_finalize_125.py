import bpy,json,sys,time,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-125';sys.path.insert(0,str(R/'tools'))
from sky_gradient_125 import apply
shutil.copyfile(O/'scene.blend',O/'scene-before-sky.blend');bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
(O/'sky-integration.json').write_text(json.dumps(apply(),indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'main-sky-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'sky-render-performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]},indent=2))
