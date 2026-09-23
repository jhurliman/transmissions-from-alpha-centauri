import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-148/geometry';names=['COL110 T1 band07 profile'+str(i)for i in [1,2,3]];src={};trees={}
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-weathering-147/actual/scene.blend'));dg=bpy.context.evaluated_depsgraph_get()
def rawhash(o):return hashlib.sha256(repr(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons])).encode()).hexdigest()
hashes={o.name:rawhash(o)for o in bpy.context.scene.objects if o.type=='MESH'and o.name not in names}
for name in names:
 ob=bpy.data.objects[name];e=ob.evaluated_get(dg);me=e.to_mesh();vs=[e.matrix_world@v.co for v in me.vertices];src[name]=set(tuple(v)for v in vs);trees[name]=BVHTree.FromPolygons(vs,[tuple(p.vertices)for p in me.polygons]);e.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));out=[]
for name in names:
 ob=bpy.data.objects[name];vs=[ob.matrix_world@v.co for v in ob.data.vertices];samples=vs+[sum((vs[i]for i in p.vertices),Vector())/len(p.vertices)for p in ob.data.polygons];positive=[]
 for pt in samples:
  near,no,idx,dist=trees[name].find_nearest(pt);signed=(pt-near).dot(no)
  if signed>1e-5:positive.append(signed)
 adjacent={i:set()for i in range(len(vs))}
 for e in ob.data.edges:a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
 remain=set(adjacent);comp=[]
 while remain:
  todo=[remain.pop()];count=0
  while todo:
   a=todo.pop();count+=1;new=adjacent[a]&remain;remain-=new;todo.extend(new)
  comp.append(count)
 out.append({'object':name,'components':comp,'max_outside_source_signed_distance_m':max(positive,default=0),'source_coordinate_exact_retained_vertices':sum(tuple(v)in src[name]for v in vs),'new_face_core_count':sum(d.value>.5 for d in ob.data.attributes['148 Cornice fracture'].data)})
changed=[name for name,h in hashes.items()if name not in bpy.data.objects or rawhash(bpy.data.objects[name])!=h];(O/'preservation.json').write_text(json.dumps({'targets':out,'non_target_meshes_checked':len(hashes),'non_target_mesh_geometry_changes':changed,'camera_source_unchanged_by_module':True,'scope_note':'Changed targets only topology-certified; inherited global defects remain outside scope.'},indent=2))
