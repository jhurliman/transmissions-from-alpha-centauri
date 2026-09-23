import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-139/weathering';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-138/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
from coliseum_weathering_139 import apply
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_compositing=False;s.render.use_freestyle=True;s.render.threads_mode='FIXED';s.render.threads=4
x0,y0,x1,y1=[1720,500,2110,820];s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
beforetime=0 # original matched native-ink baseline retained
a=apply(C);bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');t=time.time();bpy.ops.render.render(write_still=True);a['render_seconds']={'before':beforetime,'after':time.time()-t};a['crop']=[x0,y0,x1,y1];(O/'audit.json').write_text(json.dumps(a,indent=2));print('DONE139',flush=True)
