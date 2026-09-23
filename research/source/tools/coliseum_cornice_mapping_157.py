import bpy,json,sys
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
from collections import Counter
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-157/mapping';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;cam=s.camera;W,H=3840,2885
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
regions={'upper_right_failure':[2080,555,2280,745]}
result={'source':'art/studies/coliseum-156/scene.blend','resolution':[W,H],'spacing_px':4,'regions':{},'objects':{}}
for key,(x0,y0,x1,y1) in regions.items():
 hits=[ray(x,y)for y in range(y0,y1,4)for x in range(x0,x1,4)];counts=Counter(q['object']for q in hits);result['regions'][key]={'box':[x0,y0,x1,y1],'samples':hits,'counts':dict(counts)};print(key,len(hits),flush=True)
from mathutils.bvhtree import BVHTree
from types import SimpleNamespace
sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
names=[name for name,count in counts.items()if name and count>=2 and any(k in name.lower()for k in ['band','cornice','course','sill wall','upper wall','continuous arcade','tower'])]
for name in names:
 ob=bpy.data.objects[name];ev,me,ts=mesh(ob);me.calc_loop_triangles();world=[ev.matrix_world@v.co for v in me.vertices];bv=BVHTree.FromPolygons(world,[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);attr=me.attributes.get('115 Original world position');points=[]
 for i,w in enumerate(world):
  pp=world_to_camera_view(s,cam,w);points.append({'index':i,'world':list(w),'original':list(attr.data[i].vector)if attr else None,'screen':[pp.x*W,(1-pp.y)*H]})
 localhits=[q for q in hits if q['object']==name]
 for q in localhits:
  v=Vector(q['world']);n=Vector(q['normal_world']);h=bv.ray_cast(v-n*.002,-n,30.);q['inward_solid_thickness_m']=h[3]+.002 if h[0] is not None else None;q['inner_exit_world']=list(h[0])if h[0]is not None else None
 result['objects'][name]={'raw_topology':topology(ob),'evaluated_topology':topology(SimpleNamespace(data=me,matrix_world=ev.matrix_world)),'modifiers':[(m.name,m.type)for m in ob.modifiers],'props':{k:str(v)for k,v in ob.items()},'vertices':points,'faces':[{'index':f.index,'vertices':list(f.vertices),'normal':list(f.normal),'material':me.materials[f.material_index].name if me.materials else None}for f in me.polygons],'visible_sample_count':len(localhits)}
 print(name,len(localhits),result['objects'][name]['evaluated_topology'],flush=True)
(O/'native-map.json').write_text(json.dumps(result,indent=2));print('DONE',flush=True)
