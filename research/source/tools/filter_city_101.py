"""Restrict native intersection output to contacts touching the new city only."""
import bpy
from mathutils.bvhtree import BVHTree

def apply(scene=None):
 s=scene or bpy.context.scene;d=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
 for obj in bpy.data.collections['101 Original city layout study'].objects:
  if obj.type!='MESH':continue
  ob=obj.evaluated_get(d);me=ob.to_mesh();me.calc_loop_triangles();off=len(vv);vv.extend(ob.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);ob.to_mesh_clear()
 tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);retained=0
 for ob in s.objects:
  if not ob.name.startswith('101 ') or 'city contacts' not in ob.name:continue
  for layer in ob.data.layers:
   for f in layer.frames:
    dr=f.drawing;runs=[]
    for st in dr.strokes:
     run=[]
     for p in st.points:
      if p.position.y>42 and tree.find_nearest(p.position,.018)[0] is not None:run.append((tuple(p.position),p.radius,p.opacity))
      else:
       if len(run)>1:runs.append(run)
       run=[]
     if len(run)>1:runs.append(run)
    dr.remove_strokes(indices=list(range(len(dr.strokes))))
    if runs:
     dr.add_strokes(sizes=[len(r) for r in runs])
     for st,run in zip(dr.strokes,runs):
      for p,(pos,r,op) in zip(st.points,run):p.position=pos;p.radius=r;p.opacity=op
    retained+=len(runs)
 return retained
