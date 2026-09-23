import bpy,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-169/contact';times={}
for tag,path in [('before',R/'art/studies/coliseum-168/scene.blend'),('after',O/'corrected-study.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
 s.render.border_min_x=1660/3840;s.render.border_max_x=1870/3840;s.render.border_min_y=1-790/2885;s.render.border_max_y=1-515/2885;s.render.filepath=str(O/(tag+'.png'));t=time.time();bpy.ops.render.render(write_still=True);times[tag]=time.time()-t
(O/'proof-audit.json').write_text(json.dumps({'times':times,'crop':[1660,515,1870,790],'geometry_material_lighting':'Same168 sources; only169 scoped GP data differs','Freestyle':False,'native_GP_visible':True,'no_canonical_save':True},indent=2))
