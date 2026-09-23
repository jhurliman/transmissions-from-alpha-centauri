import bpy,sys,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-135/weathering';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));s=bpy.context.scene;C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library)
s.render.use_compositing=False;s.compositing_node_group=None;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;x0,y0,x1,y1=(1820,520,2110,760);s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885;s.render.filepath=str(O/'before.png');t=time.time();bpy.ops.render.render(write_still=True)
from coliseum_weathering_135 import apply
a=apply(C,1.0);(O/'audit.json').write_text(json.dumps(a,indent=2));s.render.filepath=str(O/'after.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'performance.json').write_text(json.dumps({'two_crop_render_seconds':time.time()-t,'crop':[x0,y0,x1,y1],'freestyle':False,'compositor':False},indent=2))
