import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cam=s.camera.matrix_world.translation;rows=[]
for i in dg.object_instances:
 o=i.object
 if o.type!='MESH' or not o.name.startswith(('073 anchor backplate','Y splice')):continue
 mat=i.matrix_world.copy();bb=[Vector(v)for v in o.bound_box];lo=Vector([min(p[k]for p in bb)for k in range(3)]);hi=Vector([max(p[k]for p in bb)for k in range(3)]);axis=min(range(3),key=lambda k:hi[k]-lo[k]);n=(mat.to_3x3()@Vector([int(k==axis)for k in range(3)])).normalized();center=mat@((lo+hi)/2)
 if n.dot(cam-center)<0:n=-n
 surf=[]
 for f in o.data.polygons:
  normal=(mat.to_3x3().inverted().transposed()@f.normal).normalized()
  if normal.dot(n)>.9:surf.append(f)
 if not surf:continue
 f=max(surf,key=lambda f:f.area);v=[mat@o.data.vertices[k].co for k in f.vertices];c=sum(v,Vector())/len(v);points=[c]
 for p in v:points.extend([c.lerp(p,.35),c.lerp(p,.7)])
 hits=[]
 for p in points:
  v=p-cam;dist=v.length;v.normalize();hit,loc,no,fi,obj,ma=s.ray_cast(dg,cam,v,distance=dist+.02)
  hits.append({'visible':bool(hit and abs((loc-cam).length-dist)<.025),'first':obj.name if hit else None,'gap':float(dist-(loc-cam).length)if hit else None})
 uv=world_to_camera_view(s,s.camera,c);key=o.name+'|'+str(i.parent.name if i.parent else '')+'|'+','.join('%.5f'%p for p in center)
 rows.append({'key':key,'name':o.name,'parent':i.parent.name if i.parent else None,'center':list(center),'projection':list(uv),'visible_count':sum(x['visible']for x in hits),'samples':len(hits),'fraction':sum(x['visible']for x in hits)/len(hits),'hits':hits})
O=R/'art/studies/rust-189/plate-visibility.json';O.write_text(json.dumps(rows,indent=2));print(json.dumps([{k:v for k,v in x.items()if k!='hits'}for x in sorted(rows,key=lambda x:-x['fraction'])],indent=2))
