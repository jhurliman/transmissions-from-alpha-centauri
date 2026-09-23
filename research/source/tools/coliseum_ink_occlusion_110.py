"""Clip native contact curves against actual camera-visible meshes."""
import bpy
from mathutils import Vector

def clip_contacts(scene):
 ob=bpy.data.objects.get('110 Landmark contact ink')
 if not ob:return {'strokes':0}
 dep=bpy.context.evaluated_depsgraph_get();cam=scene.camera.matrix_world.translation
 from mathutils.bvhtree import BVHTree
 vv=[];ff=[];cv=[];cf=[]
 for obj in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
  if obj.type!='MESH':continue
  ob_eval=obj.evaluated_get(dep);me=ob_eval.to_mesh();off=len(cv);cv.extend(ob_eval.matrix_world@v.co for v in me.vertices);cf.extend(tuple(off+i for i in p.vertices) for p in me.polygons);ob_eval.to_mesh_clear()
 surface=BVHTree.FromPolygons(cv,cf)
 for inst in dep.object_instances:
  obj=inst.object
  if obj.type!='MESH' or obj.name.startswith('COL110') or 'dust volume' in obj.name.lower() or 'cloud' in obj.name.lower() or 'sky' in obj.name.lower():continue
  if obj.hide_render:continue
  bounds=[inst.matrix_world@Vector(v) for v in obj.bound_box]
  if min(p.y for p in bounds)>186 or max(p.y for p in bounds)<0 or min(p.x for p in bounds)>100 or max(p.x for p in bounds)<-100 or max(p.z for p in bounds)<.1:continue
  me=obj.to_mesh();off=len(vv);vv.extend(inst.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in p.vertices) for p in me.polygons);obj.to_mesh_clear()
 tree=BVHTree.FromPolygons(vv,ff)
 def visible(p):
  if surface.find_nearest(p,.22)[0] is None:return False
  ray=p-cam;dist=ray.length
  if dist<.001:return False
  ray.normalize();hit=tree.ray_cast(cam,ray,dist-.12)
  return hit[0] is None
 total=0;removed=0
 for layer in ob.data.layers:
  for frame in layer.frames:
   dr=frame.drawing;runs=[]
   for st in dr.strokes:
    samples=[]
    for i,p in enumerate(st.points):
     if i:
      prev=st.points[i-1];length=(p.position-prev.position).length;steps=max(1,int(length/.5)+1)
      for k in range(1,steps):samples.append((prev.position.lerp(p.position,k/steps),p.radius,p.opacity))
     samples.append((p.position.copy(),p.radius,p.opacity))
    run=[]
    for p,r,a in samples:
     if visible(ob.matrix_world@p):run.append((p,r,a))
     else:
      removed+=1
      if len(run)>1:runs.append(run)
      run=[]
    if len(run)>1:runs.append(run)
   dr.remove_strokes(indices=list(range(len(dr.strokes))))
   if runs:
    dr.add_strokes(sizes=[len(r) for r in runs])
    for st,run in zip(dr.strokes,runs):
     for p,(pos,r,a) in zip(st.points,run):p.position=pos;p.radius=r;p.opacity=a
   total+=len(runs)
 return {'retained_runs':total,'occluded_samples_removed':removed,'method':'Camera rays against evaluated foreground/city occluder meshes; volume bounds ignored'}
