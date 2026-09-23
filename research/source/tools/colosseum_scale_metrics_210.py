"""CPU-only210 landmark distance anchor and full4K silhouette scale targets."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/colosseum-scale-210';SOURCE=R/'art/studies/scene-completion-205/scene.blend'

def collect(scene):
 C=bpy.data.collections['110 Coliseum detailed front ruin'];members=set(C.all_objects);members.add(bpy.data.objects['110 Landmark contact ink']);dg=bpy.context.evaluated_depsgraph_get();rows=[];points=[];triangles=[];edges=[];offset=0
 for ins in dg.object_instances:
  ob=ins.object.original
  if ob not in members and not(ins.parent and ins.parent.original in members):continue
  if ob.hide_render or ins.object.type not in ('MESH','CURVE','SURFACE','FONT'):continue
  me=ins.object.to_mesh();me.calc_loop_triangles();xyz=np.empty((len(me.vertices),3),np.float64)
  raw=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',raw);loc=raw.reshape(-1,3).astype(np.float64);M=np.array(ins.matrix_world);xyz=loc@M[:3,:3].T+M[:3,3]
  points.append(xyz);tris=np.array([t.vertices[:]for t in me.loop_triangles],dtype=np.int32);ee=np.array([e.vertices[:]for e in me.edges],dtype=np.int32)
  if len(tris):triangles.append(tris+offset)
  if len(ee):edges.append(ee+offset)
  rows.append({'name':ob.name,'first':offset,'last':offset+len(xyz),'vertices':len(xyz),'triangles':len(tris),'type':ob.type,'parent':ob.parent.name if ob.parent else None})
  offset+=len(xyz);ins.object.to_mesh_clear()
 P=np.concatenate(points);T=np.concatenate(triangles);E=np.concatenate(edges);return C,members,dg,rows,P,T,E

def nearest_plan(P,E,camera):
 A=P[E[:,0],:2];B=P[E[:,1],:2];D=B-A;den=np.sum(D*D,axis=1);f=np.clip(np.sum((camera[:2]-A)*D,axis=1)/np.maximum(den,1e-30),0,1);q=A+f[:,None]*D;dist=np.linalg.norm(q-camera[:2],axis=1);k=int(np.argmin(dist));point=P[E[k,0]]+f[k]*(P[E[k,1]]-P[E[k,0]])
 return {'distance':float(dist[k]),'surface_point':point.tolist(),'edge_index':k,'edge_vertices':E[k].tolist(),'edge_parameter':float(f[k])}

def project(scene,P):
 inv=np.array(scene.camera.matrix_world.inverted());view=P@inv[:3,:3].T+inv[:3,3];projection=np.array(scene.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=3840,y=2885));clip=np.concatenate((view,np.ones((len(view),1))),axis=1)@projection.T;xy=clip[:,:2]/clip[:,3:4];return np.stack(((xy[:,0]+1)*1920,(1-xy[:,1])*1442.5),axis=1)

def apparent_top(scene,P,rows):
 px=project(scene,P);eligible=np.flatnonzero((px[:,0]>=0)&(px[:,0]<=3840));idx=int(eligible[np.argmin(px[eligible,1])]);row=next(r for r in rows if r['first']<=idx<r['last']);return {'pixel':px[idx].tolist(),'world':P[idx].tolist(),'vertex_index':idx,'object':row['name']}

def transparent(ob):
 name=ob.name.lower()
 if any(t in name for t in ['haze','fog','cloud','sky','dust','ink']):return True
 return any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)

def visibility(scene,dg,p):
 origin=scene.camera.matrix_world.translation.copy();point=Vector(p);d=(point-origin).normalized();skipped=[]
 for _ in range(24):
  length=(point-origin).length
  hit=scene.ray_cast(dg,origin,d,distance=max(0,length-.002))
  if not hit[0]:return {'visible':True,'skipped':skipped}
  if transparent(hit[4]):skipped.append(hit[4].name);origin=hit[1]+d*.08;continue
  return {'visible':False,'occluder':hit[4].name,'gap':length-(hit[1]-origin).length,'skipped':skipped}
 return {'visible':False,'reason':'too many atmospheric shells','skipped':skipped}

def metrics(scene):
 C,members,dg,rows,P,T,E=collect(scene);camera=np.array(scene.camera.matrix_world.translation);anchor=nearest_plan(P,E,camera);zbase=float(P[:,2].min());pivot=np.array([anchor['surface_point'][0],anchor['surface_point'][1],zbase]);baseline=apparent_top(scene,P,rows);baseline['visibility']=visibility(scene,dg,baseline['world']);variants=[]
 # The highest geometry vertex of this view is confirmed opaque-scene visible before solving.
 assert baseline['visibility']['visible'],baseline
 tree=BVHTree.FromPolygons([Vector(p)for p in P],[tuple(t)for t in T],all_triangles=True);near=tree.find_nearest(Vector(camera));baseline['nearest_euclidean_surface_m']=float(near[3]);baseline['nearest_euclidean_point']=list(near[0])
 for fraction in [.10,.20,.70]:
  target=baseline['pixel'][1]*(1-fraction);lo=1.;hi=2.
  while apparent_top(scene,pivot+hi*(P-pivot),rows)['pixel'][1]>target:hi*=1.4
  for _ in range(45):
   mid=(lo+hi)/2;top=apparent_top(scene,pivot+mid*(P-pivot),rows)['pixel'][1]
   if top>target:lo=mid
   else:hi=mid
  scale=(lo+hi)/2;Q=pivot+scale*(P-pivot);top=apparent_top(scene,Q,rows);plan=nearest_plan(Q,E,camera);tree2=BVHTree.FromPolygons([Vector(p)for p in Q],[tuple(t)for t in T],all_triangles=True);near2=tree2.find_nearest(Vector(camera))
  variants.append({'sky_gap_fraction':fraction,'uniform_scale':scale,'target_top_pixel_y':target,'actual_geometric_top':top,'remaining_sky_gap_pixels':top['pixel'][1],'consumed_sky_pixels':baseline['pixel'][1]-top['pixel'][1],'nearest_plan_surface_distance_m':plan['distance'],'nearest_plan_distance_delta_m':plan['distance']-anchor['distance'],'minimum_world_z':float(Q[:,2].min()),'nearest_euclidean_surface_m':float(near2[3]),'nearest_euclidean_surface_delta_m':float(near2[3])-baseline['nearest_euclidean_surface_m']})
 roots=[ob for ob in members if ob.parent not in members]
 return {'source':str(SOURCE.relative_to(R)),'collection':C.name,'native_object_count':len(members),'transform_root_count':len(roots),'transform_roots':[o.name for o in roots],'evaluated_points':len(P),'evaluated_triangles':len(T),'objects':rows,'baseline':baseline,'anchor':anchor,'pivot_world':pivot.tolist(),'ground_z':zbase,'metric':'Consume10/20/70 percent of the full4K vertical gap between highest visible Colosseum point and image top. Uniform scale about the ground-projected nearest horizontal surface point, retaining exact nearest camera-to-footprint distance and ground elevation.','variants':variants}

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));report=metrics(bpy.context.scene);O.mkdir(parents=True,exist_ok=True);(O/'metrics.json').write_text(json.dumps(report,indent=2));print('210 METRICS',json.dumps({k:report[k]for k in ['native_object_count','transform_root_count','baseline','anchor','pivot_world','variants']}),flush=True)
