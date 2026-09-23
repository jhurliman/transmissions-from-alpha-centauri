import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/plate-runoff-192/ink-diagnostic';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));s=bpy.context.scene;rows=[]
for ob in s.objects:
 if ob.type!='GREASEPENCIL' or ob.hide_render:continue
 for layer in ob.data.layers:
  for frame in layer.frames:
   for si,stroke in enumerate(frame.drawing.strokes):
    pts=[ob.matrix_world@p.position for p in stroke.points];pp=[world_to_camera_view(s,s.camera,p)for p in pts];xy=[(p.x*3840,(1-p.y)*2885)for p in pp]
    for i,(a,b)in enumerate(zip(xy,xy[1:])):
     if max(a[0],b[0])<370 or min(a[0],b[0])>430 or max(a[1],b[1])<275 or min(a[1],b[1])>330:continue
     rows.append(dict(object=ob.name,layer=layer.name,frame=frame.frame_number,stroke=si,segment=i,pixel=[a,b],world=[list(pts[i]),list(pts[i+1])],opacity=[stroke.points[i].opacity,stroke.points[i+1].opacity]))
(O/'upper-gp-ownership.json').write_text(json.dumps(rows,indent=2));print('GPSEGMENTS',len(rows),flush=True)
