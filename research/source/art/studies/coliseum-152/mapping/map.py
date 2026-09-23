import bpy,json,sys
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
from collections import Counter
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-152/mapping';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));s=bpy.context.scene;cam=s.camera;W,H=3840,2885
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library);allow={o.name for o in C.all_objects}
for ob in s.objects:
 if ob.type in {'MESH','CURVE'} and ob.name not in allow:ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=cam.data.view_frame(scene=s);origin=cam.matrix_world.translation;cache={}
def mesh(ob):
 if ob.name not in cache:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();cache[ob.name]=(ev,me,{p.index:[]for p in me.polygons})
  for t in me.loop_triangles:cache[ob.name][2][t.polygon_index].append(tuple(t.vertices))
 return cache[ob.name]
def ray(x,y):
 top=frame[3].lerp(frame[0],x/W);bottom=frame[2].lerp(frame[1],x/W);d=(cam.matrix_world@top.lerp(bottom,y/H)-origin).normalized();hit,loc,n,fi,ob,matrix=s.ray_cast(dg,origin,d)
 if not hit:return {'pixel':[x,y],'object':None}
 rec={'pixel':[x,y],'object':ob.name,'face':fi,'world':list(loc),'normal_world':list(n)}
 if ob.type!='MESH':return rec
 ev,me,ts=mesh(ob);p=matrix.inverted()@loc;attr=me.attributes.get('115 Original world position')
 if attr and fi in ts and ts[fi]:
  ids=min(ts[fi],key=lambda ids:(geometry.closest_point_on_tri(p,*[me.vertices[i].co for i in ids])-p).length)
  pts=[me.vertices[i].co for i in ids];aps=[attr.data[i].vector for i in ids];op=geometry.barycentric_transform(p,*pts,*aps);no=(aps[1]-aps[0]).cross(aps[2]-aps[0]).normalized();up=(Vector((0,0,1))-no*no.z).normalized();ac=up.cross(no).normalized()
  # Consistent across points toward image right where a local tangent can be recovered.
  wp=geometry.barycentric_transform(op+ac,*aps,*pts);proj=world_to_camera_view(s,cam,matrix@wp);proj0=world_to_camera_view(s,cam,loc)
  if proj.x<proj0.x:ac=-ac
  rec.update(original_world=list(op),normal_original=list(no),across_original=list(ac),up_original=list(up),material=me.materials[me.polygons[fi].material_index].name if me.materials else None)
 return rec
regions={'primary_review':[1665,535,2085,930],'secondary_review':[2070,505,2325,985],'primary_proposed':[1685,580,1900,790],'secondary_proposed':[2090,580,2260,755]}
result={'source':'art/studies/coliseum-150/scene.blend','resolution':[W,H],'spacing_px':6,'regions':{},'anchors':{}}
for key,(x0,y0,x1,y1) in regions.items():
 hits=[ray(x,y)for y in range(y0,y1,6)for x in range(x0,x1,6)];counts=Counter(q['object']for q in hits);result['regions'][key]={'box':[x0,y0,x1,y1],'samples':hits,'counts':dict(counts)};print(key,len(hits),flush=True)
for label,xy in {'P_collar':(1725,593),'P_ledge':(1790,596),'P_flat_face':(1775,624),'P_shoulder':(1742,687),'P_lower_ledge':(1762,768),'S_collar':(2110,605),'S_flat_face':(2165,634),'S_shoulder':(2135,707),'S_ledge':(2195,610)}.items():result['anchors'][label]=ray(*xy)
(O/'raw-map.json').write_text(json.dumps(result,indent=2));print('DONE',flush=True)
