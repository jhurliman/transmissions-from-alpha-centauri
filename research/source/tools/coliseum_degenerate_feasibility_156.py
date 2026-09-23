"""In-memory bounded numerical cleanup feasibility. Never saves a scene."""
import bpy,bmesh,json,sys,time,types,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_repair_123 import strict_crossings
O=R/'art/studies/coliseum-156/preflight';audit=json.loads((O/'audit.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'))
def health(me):
 bm=bmesh.new();bm.from_mesh(me);d={'vertices':len(bm.verts),'faces':len(bm.faces),'zero1e10':sum(f.calc_area()<1e-10 for f in bm.faces),'zero1e14':sum(f.calc_area()<1e-14 for f in bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'boundary':sum(e.is_boundary for e in bm.edges),'noncontiguous':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'volume':bm.calc_volume(signed=True)};bm.free();return d
def worlddata(me,matrix):
 me.calc_loop_triangles();vs=[matrix@v.co for v in me.vertices];ts=[tuple(t.vertices)for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,ts,all_triangles=True);kd=KDTree(len(vs))
 for i,v in enumerate(vs):kd.insert(v,i)
 kd.balance();return vs,ts,tree,kd
def trisignatures(vs,ts):
 return {tuple(sorted(tuple(vs[i])for i in tri)):((vs[tri[1]]-vs[tri[0]]).cross(vs[tri[2]]-vs[tri[0]])).length/2 for tri in ts}
def samples(vs,ts):return vs+[sum((vs[i]for i in tri),Vector())/3 for tri in ts]
def deviation(points,tree):
 return max((tree.find_nearest(p)[3] or 0 for p in points),default=0)
rows=[];t=time.time()
for entry in audit['near_zero_issue_objects']:
 ob=bpy.data.objects[entry['object']];old=ob.data;orig=health(old);orig['raw_crossings']=strict_crossings(ob);v0,t0,bvh0,kd0=worlddata(old,ob.matrix_world);attr0=old.attributes.get('115 Original world position');trials=[];control=deviation(samples(v0,t0),bvh0);sig0=trisignatures(v0,t0)
 for operation in ['dissolve_degenerate','merge_component','merge_then_dissolve']:
  for worldtol in [1e-6,1e-5]:
   bm=bmesh.new();bm.from_mesh(old);fid=bm.faces.layers.int.new('156 source face');vid=bm.verts.layers.int.new('156 source vertex')
   for f in bm.faces:f[fid]=f.index
   for v in bm.verts:v[vid]=v.index
   scale=max(ob.matrix_world.to_3x3().col[i].length for i in range(3));tol=worldtol/scale
   if operation.startswith('merge'):
    pending=set(bm.verts);groups=[]
    while pending:
     group={pending.pop()};stack=list(group)
     while stack:
      v=stack.pop()
      for e in v.link_edges:
       q=e.other_vert(v)
       if q in pending:pending.remove(q);group.add(q);stack.append(q)
     groups.append(group)
    for group in groups:bmesh.ops.remove_doubles(bm,verts=list(group),dist=tol)
   if operation in ['dissolve_degenerate','merge_then_dissolve']:bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tol)
   me=bpy.data.meshes.new('156 TEMP feasibility');bm.to_mesh(me);bm.free();me.update();h=health(me);h['raw_crossings']=strict_crossings(types.SimpleNamespace(data=me,matrix_world=ob.matrix_world));v1,t1,bvh1,kd1=worlddata(me,ob.matrix_world)
   delta=max((kd0.find(v)[2]for v in v1),default=0);forward=deviation(samples(v1,t1),bvh0);reverse=deviation(samples(v0,t0),bvh1)
   attrs=[a.name for a in me.attributes];a1=me.attributes.get('115 Original world position');coorderror=max(((a1.data[i].vector-attr0.data[kd0.find(v)[1]].vector).length for i,v in enumerate(v1)),default=0)if attr0 and a1 else None
   fa=me.attributes.get('156 source face');va=me.attributes.get('156 source vertex');lineage=bool(fa and va);badlineage=0;max_normal=0
   if lineage:
    for f in me.polygons:
     oi=fa.data[f.index].value
     if not 0<=oi<len(old.polygons):badlineage+=1;continue
     source=old.polygons[oi];max_normal=max(max_normal,math.degrees(f.normal.angle(source.normal,0)))
   sig1=trisignatures(v1,t1);missing=[a for k,a in sig0.items()if k not in sig1];added=[a for k,a in sig1.items()if k not in sig0]
   trial={'source_self_BVH_error_m':control,'removed_triangle_max_area_m2':max(missing,default=0),'added_triangle_max_area_m2':max(added,default=0),'source_retained_nondegenerate_triangle_loss':sum(a>1e-12 for a in missing),'candidate_new_nondegenerate_triangles':sum(a>1e-12 for a in added),'operation':operation,'world_tolerance_m':worldtol,'health':h,'max_vertex_distance_to_source_m':delta,'sampled_new_to_old_surface_m':forward,'sampled_old_to_new_surface_m':reverse,'115_attribute_nearest_source_error':coorderror,'attribute_names_lost':sorted(set(a.name for a in old.attributes)-set(attrs)),'source_face_vertex_lineage_retained':lineage,'invalid_source_face_lineage':badlineage,'max_surviving_face_normal_angle_degrees':max_normal,'custom_split_normals_preserved_automatically':False,'normal_restore_strategy':'Use retained source face lineage and source vertex/corner mapping. Merged conflicting material coordinates require explicit handling; none is silently averaged as approval.','potential':h['zero1e10']==0 and h['nonmanifold']==0 and h['noncontiguous']==0 and h['raw_crossings']<=orig['raw_crossings'] and delta<2e-5 and (max(missing+added,default=0)<1e-12 or max(forward,reverse)<2e-5) and (coorderror is None or coorderror<1e-4)}
   trials.append(trial);bpy.data.meshes.remove(me);print(ob.name,operation,worldtol,'zero',h['zero1e10'],'nm',h['nonmanifold'],'cross',h['raw_crossings'],'potential',trial['potential'],flush=True)
 rows.append({'object':ob.name,'baseline':orig,'trials':trials})
report={'source':'152','read_only':True,'seconds':time.time()-t,'world_tolerances_m':[1e-6,1e-5],'rows':rows,'limitations':['Finite vertex+triangle-centroid surface samples are not exact Hausdorff proof.','Custom corner normals require explicit source-lineage restore and visual validation before integration.','Only numerical degeneracy cleanup considered; existing genuine folded return geometry is not solved by these operations.','No evaluated-modifier or render preservation claim yet.']};(O/'degenerate-cleanup-feasibility.json').write_text(json.dumps(report,indent=2));print('DONE',report['seconds'],flush=True)
