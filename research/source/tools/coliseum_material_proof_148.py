import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-148/material';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-weathering-147/actual/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
from coliseum_weathering_148 import apply
result=apply(C)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_compositing=False;s.render.use_freestyle=True;s.render.threads_mode='FIXED';s.render.threads=4
x0,y0,x1,y1=1720,480,2120,850;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');t=time.time();bpy.ops.render.render(write_still=True);result['seconds']=time.time()-t;result['crop']=[x0,y0,x1,y1];(O/'audit.json').write_text(json.dumps(result,indent=2))
