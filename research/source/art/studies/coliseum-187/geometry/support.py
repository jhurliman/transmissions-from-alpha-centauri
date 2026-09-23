import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';names=json.load(open(R/'config/coliseum-left-course-187.json'))['targets']
def trees():
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for n in names:
  ob=bpy.data.objects[n].evaluated_get(dg);me=ob.to_mesh();me.calc_loop_triangles();out[n]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);ob.to_mesh_clear()
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));before=trees();dg=bpy.context.evaluated_depsgraph_get();samples={}
for name in ['131 Recessed crown joint ink','COL120 bay10 arcade2 dentil03']:
 ob=bpy.data.objects[name].evaluated_get(dg);me=ob.to_mesh();M=ob.matrix_world;N=M.to_3x3().inverted().transposed();pts=[]
 if name.startswith('131'):
  pts=[M@v.co for v in me.vertices if 16<(M@v.co).x<21.5 and 195<(M@v.co).y<216 and 39.5<(M@v.co).z<43.5]
 else:
  for f in me.polygons:
   if (N@f.normal).normalized().z>.5:
    pts+=[M@me.vertices[i].co for i in f.vertices]+[M@f.center]
 samples[name]=list({tuple(p):p for p in pts}.values());ob.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(O/'HELD-diagnostic.blend'));after=trees();rows={}
for name,pts in samples.items():
 rr=[]
 for p in pts:
  b=min((t.find_nearest(p)[3],n)for n,t in before.items());a=min((t.find_nearest(p)[3],n)for n,t in after.items());rr.append({'point':list(p),'before_m':b[0],'before_owner':b[1],'after_m':a[0],'after_owner':a[1]})
 rows[name]={'samples':rr,'before_within2cm':sum(r['before_m']<=.02 for r in rr),'lost_2cm_support':sum(r['before_m']<=.02 and r['after_m']>.03 for r in rr),'max_after_m':max((r['after_m']for r in rr),default=None)}
(O/'support-samples.json').write_text(json.dumps({'method':'Native131 evaluated mesh vertices in declared worldROI; dentil03 upward-facing polygon corners/centers. Nearest solid six target surfaces before/after; all unrelated surfaces unchanged. Discrete support screen, not continuous certificate.','rows':rows},indent=2));print({k:{a:b for a,b in v.items()if a!='samples'}for k,v in rows.items()})
