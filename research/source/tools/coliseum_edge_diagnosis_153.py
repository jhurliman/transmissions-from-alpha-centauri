import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/edge-diagnosis';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=3;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1725/3840;s.render.border_max_x=2330/3840;s.render.border_min_y=1-960/2885;s.render.border_max_y=1-560/2885
s.render.filepath=str(O/'no-freestyle.png');bpy.ops.render.render(write_still=True)
ink=[]
for o in s.objects:
 if 'Landmark contact ink'in o.name or ('ink'in o.name.lower()and o in list(C.all_objects)):
  ink.append({'name':o.name,'type':o.type,'previous_hide_render':o.hide_render});o.hide_render=True
s.render.filepath=str(O/'no-contact-ink.png');bpy.ops.render.render(write_still=True)
# Actual visible native receivers, excluding transparent volume geometry for rays only.
for o in s.objects:
 if o.type=='MESH'and('volume'in o.name.lower()or o.hide_render):o.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;inv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation;rows=[]
for label,cx,cy in [('central',1925,596),('right',2155,623)]:
 for y in range(cy-16,cy+17,4):
  for x in range(cx-16,cx+17,4):
   q=inv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,n,fi,ob,mat=s.ray_cast(dg,org,di)
   if ok:rows.append({'region':label,'pixel':[x,y],'object':ob.name,'face':fi,'point':list(p),'normal':list(n)})
(O/'diagnosis-inputs.json').write_text(json.dumps({'source':'150','hidden_native_ink':ink,'rays':rows},indent=2));print('RECEIVERS',sorted(set(r['object']for r in rows)))
