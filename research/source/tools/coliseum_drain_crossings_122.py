import bpy,json
from pathlib import Path
from mathutils import geometry
from mathutils.bvhtree import BVHTree
R=Path('/PATH/TO/transmissions-from-alpha-centauri')
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-122/rhythm/scene.blend'))
out=[]
for name in ['COL110 U%d sill wall'%k for k in range(5,14)]:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];ts=list(me.loop_triangles);fs=[tuple(t.vertices)for t in ts];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
 for i,j in tree.overlap(tree):
  if i>=j or set(fs[i])&set(fs[j]):continue
  A=[vs[k]for k in fs[i]];B=[vs[k]for k in fs[j]];na=(A[1]-A[0]).cross(A[2]-A[0]);nb=(B[1]-B[0]).cross(B[2]-B[0])
  if na.length<1e-10 or nb.length<1e-10 or abs(na.normalized().dot(nb.normalized()))>.99999:continue
  hits=[]
  for V,W in [(A,B),(B,A)]:
   n=(W[1]-W[0]).cross(W[2]-W[0]).normalized()
   for k in range(3):
    a,b=V[k],V[(k+1)%3];d=b-a
    if d.length<1e-8:continue
    h=geometry.intersect_ray_tri(*W,d.normalized(),a,True)
    if h is None:continue
    distance=(h-a).dot(d.normalized())
    if not .00001<distance<d.length-.00001:continue
    e0,e1,q=W[1]-W[0],W[2]-W[0],h-W[0];aa,bb,cc,dd,ee=e0.dot(e0),e0.dot(e1),e1.dot(e1),q.dot(e0),q.dot(e1);den=aa*cc-bb*bb
    u=(cc*dd-bb*ee)/den;v=(aa*ee-bb*dd)/den
    hits.append({'point':list(h),'bary_min':min(u,v,1-u-v),'plane_distances':[(a-W[0]).dot(n),(b-W[0]).dot(n)]})
  if hits:rows.append({'triangles':[i,j],'polygons':[ts[i].polygon_index,ts[j].polygon_index],'same_polygon':ts[i].polygon_index==ts[j].polygon_index,'min_vertex_separation':min((a-b).length for a in A for b in B),'hits':hits,'strict_interior':any(h['bary_min']>1e-5 and min(h['plane_distances'])<-.00001 and max(h['plane_distances'])>.00001 for h in hits)})
 out.append({'object':name,'original_test_crossings':len(rows),'strict_crossings':sum(x['strict_interior']for x in rows),'same_polygon_pairs':sum(x['same_polygon']for x in rows),'pairs':rows})
p=R/'art/studies/coliseum-122/rhythm/drain-crossing-audit.json';p.write_text(json.dumps(out,indent=2));print([(x['object'],x['original_test_crossings'],x['strict_crossings'],x['same_polygon_pairs'])for x in out])
