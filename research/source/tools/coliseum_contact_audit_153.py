import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/edge-diagnosis';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));s=bpy.context.scene;gp=bpy.data.objects['110 Landmark contact ink'];boxes={'central':[1908,577,1945,618],'right':[2137,603,2179,649]}
for ob in s.objects:
 if ob.type=='MESH'and('volume'in ob.name.lower()or ob.hide_render):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();org=s.camera.matrix_world.translation;rows=[]
for layer in gp.data.layers:
 for frame in layer.frames:
  d=frame.drawing
  for si,stroke in enumerate(d.strokes):
   vv=[gp.matrix_world@p.position for p in stroke.points];pp=[world_to_camera_view(s,s.camera,v)for v in vv];px=[(p.x*3840,(1-p.y)*2885)for p in pp]
   for label,box in boxes.items():
    picked=[i for i,p in enumerate(px)if box[0]<=p[0]<box[2]and box[1]<=p[1]<box[3]]
    if not picked:continue
    samples=[]
    for i in picked:
     di=vv[i]-org;ok,p,n,fi,ob,mat=s.ray_cast(dg,org,di.normalized());samples.append({'pixel':list(px[i]),'distance_behind_first_surface':di.length-(p-org).length if ok else None,'receiver':ob.name if ok else None})
    rows.append({'region':label,'layer':layer.name,'frame':frame.frame_number,'stroke':si,'point_count':len(vv),'samples':samples})
(O/'contact-strokes.json').write_text(json.dumps(rows,indent=2));print('STROKES',len(rows));print([(k,sum(r['region']==k for r in rows))for k in boxes])
