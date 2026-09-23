import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-118';bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];members=set(C.objects);dep=bpy.context.evaluated_depsgraph_get();cam=s.camera.matrix_world.translation
v=[];f=[];lv=[];lf=[]
for inst in dep.object_instances:
 ob=inst.object
 if ob.type!='MESH'or ob.hide_render:continue
 is_landmark=ob.name in C.objects
 if not is_landmark:
  if any(w in ob.name.lower()for w in ['dust volume','cloud','sky']):continue
  bb=[inst.matrix_world@Vector(p)for p in ob.bound_box]
  if min(p.y for p in bb)>186 or max(p.y for p in bb)<0 or min(p.x for p in bb)>100 or max(p.x for p in bb)<-100 or max(p.z for p in bb)<.1:continue
 me=ob.to_mesh();vv,ff=(lv,lf)if is_landmark else(v,f);off=len(vv);vv.extend(inst.matrix_world@p.co for p in me.vertices);ff.extend(tuple(off+i for i in q.vertices)for q in me.polygons);ob.to_mesh_clear()
occ=BVHTree.FromPolygons(v,f);land=BVHTree.FromPolygons(lv,lf)
def visibility(p):
 q=world_to_camera_view(s,s.camera,p)
 if q.z<=0 or not(0<=q.x<=1 and 0<=q.y<=1):return'outside_frame',None
 d=p-cam;dist=d.length;d.normalize()
 if occ.ray_cast(cam,d,dist-.05)[0]is not None:return'near_city_occluded',(q.x*1440,(1-q.y)*1082)
 if land.ray_cast(cam,d,dist-.08)[0]is not None:return'landmark_self_occluded',(q.x*1440,(1-q.y)*1082)
 return'visible',(q.x*1440,(1-q.y)*1082)
# Actual upperwall frontfacing face samples, no invented points through openings.
results=[]
for bay in range(18):
 points=[]
 for ob in C.objects:
  if ob.type!='MESH'or ob.get('bay')!=bay or ob.get('tier')!=3:continue
  M=ob.matrix_world;N=M.to_3x3().inverted().transposed()
  for face in ob.data.polygons:
   p=M@face.center
   if (N@face.normal).dot(cam-p)>0 and face.area>.001:points.append(p)
 if len(points)>500:points=[points[round(i*(len(points)-1)/499)]for i in range(500)]
 counts={};screen=[]
 for p in points:
  status,xy=visibility(p);counts[status]=counts.get(status,0)+1
  if status=='visible':screen.append(xy)
 results.append({'bay':bay,'front_facing_upperwall_samples':len(points),'counts':counts,'visible_fraction':counts.get('visible',0)/max(1,len(points)),'visible_pixel_bounds':[[min(p[k]for p in screen),max(p[k]for p in screen)]for k in range(2)]if screen else None})
report={'method':'Deterministic front-facing upperwall polygon-center samples, up to500perbay, tested against evaluated nearcity/foreground and landmark self-occlusion; visibility fraction is sampled surface visibility, not pixel-area coverage.','bays':results,'recommended_bays':sorted(results,key=lambda r:r['visible_fraction'],reverse=True)[:5]};(O/'visibility-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
