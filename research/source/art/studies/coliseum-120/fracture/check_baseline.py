import bpy,json
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-120/fracture';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));rows=[]
for ob in bpy.data.objects:
 if ob.name not in ['COL110 U8 fractured upper wall L','COL110 U8 fractured upper wall R','COL110 U8 sill wall']:continue
 me=ob.data;me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices)for t in me.loop_triangles];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);pairs=tree.overlap(tree);cross=[]
 for i,j in pairs:
  if i>=j or set(fs[i])&set(fs[j]):continue
  A=[vs[k]for k in fs[i]];B=[vs[k]for k in fs[j]];na=(A[1]-A[0]).cross(A[2]-A[0]);nb=(B[1]-B[0]).cross(B[2]-B[0])
  if na.length<1e-10 or nb.length<1e-10:continue
  if abs(na.normalized().dot(nb.normalized()))>.99999:continue
  found=False
  for V,W in [(A,B),(B,A)]:
   for k in range(3):
    a=V[k];b=V[(k+1)%3];d=b-a
    if d.length<1e-8:continue
    hit=geometry.intersect_ray_tri(*W,d.normalized(),a,True)
    if hit is not None:
     distance=(hit-a).dot(d.normalized())
     if .00001<distance<d.length-.00001:found=True;break
   if found:break
  if found:cross.append((i,j))
 rows.append({'object':ob.name,'triangles':len(fs),'nonadjacent_proper_crossings':len(cross),'examples':cross[:8]})
(O/'intersection-baseline.json').write_text(json.dumps(rows,indent=2));print(rows)
