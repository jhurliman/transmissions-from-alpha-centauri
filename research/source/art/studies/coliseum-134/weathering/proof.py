import bpy,sys,json,time,hashlib
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_weathering_134 import apply
O=R/'art/studies/coliseum-134/weathering';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scene-details-133/scene.blend'));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=3;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1530/3840;s.render.border_max_x=2210/3840;s.render.border_min_y=1-920/2885;s.render.border_max_y=1-460/2885
s.render.filepath=str(O/'before.png');bpy.ops.render.render(write_still=True)
before={o.name:(o.data.as_pointer(),len(o.data.vertices),len(o.data.polygons))for o in C.all_objects if o.type=='MESH'}
t=time.time();a=apply(C);a['apply_seconds']=time.time()-t;a['geometry_unchanged']=all(before[o.name]==(o.data.as_pointer(),len(o.data.vertices),len(o.data.polygons)) for o in C.all_objects if o.type=='MESH');(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True)
