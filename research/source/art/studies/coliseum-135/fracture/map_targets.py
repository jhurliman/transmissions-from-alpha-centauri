import bpy,sys,json,types,math
from pathlib import Path
from collections import Counter
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector, geometry
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import strict_crossings
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;W=3840;H=2885;s.render.resolution_x=W;s.render.resolution_y=H
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
for ob in s.objects:
 if ob.type in ('MESH','CURVE') and ob.name not in C.all_objects:ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
rois={'left_crown':[1440,463,1620,598],'broken_cornice':[1900,585,2025,667]}
def project(v):
 p=world_to_camera_view(s,cam,v);return (p.x*W,(1-p.y)*H,p.z)
frame=cam.data.view_frame(scene=s);xl=min(v.x/-v.z for v in frame);xr=max(v.x/-v.z for v in frame);yb=min(v.y/-v.z for v in frame);yt=max(v.y/-v.z for v in frame)
result={'source':'coliseum-134/scene.blend','resolution':[W,H],'regions':{},'method':'6px ray sample for actual first visible ownership; projected bounds from evaluated vertices; projected triangle area proxy includes occluded faces and uses centroid within ROI, not clipped polygons.'}
for key,roi in rois.items():
 counts=Counter();anchors=[];x0,y0,x1,y1=roi
 for y in range(y0,y1,6):
  for x in range(x0,x1,6):
   v=Vector((xl+(xr-xl)*x/W,yb+(yt-yb)*(1-y/H),-1));d=cam.matrix_world.to_3x3()@v.normalized();hit,loc,n,fi,ob,mat=s.ray_cast(dg,cam.matrix_world.translation,d)
   if hit:
    counts[ob.name]+=1
    if key=='broken_cornice' and ob.name.startswith('COL') and (x-x0)%18==0 and (y-y0)%18==0:
     evh=ob.evaluated_get(dg);mh=evh.to_mesh();at=mh.attributes.get('115 Original world position');record={'pixel':[x,y],'object':ob.name,'world':list(loc),'normal':list(n)}
     if at and at.domain=='POINT' and fi<len(mh.polygons):
      mh.calc_loop_triangles();lp=evh.matrix_world.inverted()@loc;ts=[t for t in mh.loop_triangles if t.polygon_index==fi]
      if ts:
       t=min(ts,key=lambda t:(geometry.closest_point_on_tri(lp,*[mh.vertices[i].co for i in t.vertices])-lp).length);ids=t.vertices
       record['original_world']=list(geometry.barycentric_transform(lp,*[mh.vertices[i].co for i in ids],*[at.data[i].vector for i in ids]))
     anchors.append(record);evh.to_mesh_clear()
 rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH' or ob.hide_render:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();world=[ev.matrix_world@v.co for v in me.vertices];p=[project(v)for v in world]
  if not p:ev.to_mesh_clear();continue
  bounds=[min(v[0]for v in p),min(v[1]for v in p),max(v[0]for v in p),max(v[1]for v in p)]
  if bounds[0]>x1 or bounds[2]<x0 or bounds[1]>y1 or bounds[3]<y0:ev.to_mesh_clear();continue
  if counts[ob.name]==0:ev.to_mesh_clear();continue
  me.calc_loop_triangles();area=0;faces=0
  for t in me.loop_triangles:
   a,b,c=[p[i]for i in t.vertices];cx=(a[0]+b[0]+c[0])/3;cy=(a[1]+b[1]+c[1])/3
   if x0<=cx<=x1 and y0<=cy<=y1:
    wa,wb,wc=[world[i]for i in t.vertices];normal=(wb-wa).cross(wc-wa)
    if normal.dot(cam.matrix_world.translation-(wa+wb+wc)/3)>0:area+=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2;faces+=1
  row={'object':ob.name,'projected_bounds':bounds,'visible_ray_samples':counts[ob.name],'visible_area_sample_proxy_px2':counts[ob.name]*36,'camera_facing_projected_area_proxy_px2':area,'facing_triangles_in_roi':faces,'raw_strict_crossings':strict_crossings(ob),'evaluated_strict_crossings':strict_crossings(types.SimpleNamespace(data=me,matrix_world=ev.matrix_world)),'materials':[m.name if m else None for m in ob.data.materials]}
  rows.append(row);ev.to_mesh_clear();print(key,ob.name,counts[ob.name],row['raw_strict_crossings'],row['evaluated_strict_crossings'],flush=True)
 result['regions'][key]={'roi':roi,'surface_anchors':anchors,'all_first_hit_counts':dict(counts),'visible_meshes':sorted(rows,key=lambda r:-r['visible_ray_samples'])}
(R/'art/studies/coliseum-135/fracture/target-map.json').write_text(json.dumps(result,indent=2));print('DONE',flush=True)
