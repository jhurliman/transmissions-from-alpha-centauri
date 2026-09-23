"""Reject terrain/helper-only contacts; retain true non-soil solid contacts.
The native Line Art pass handles visibility. This stage validates physical
proximity to a rendered solid, excluding buried soil and shadow helper meshes.
"""
import bpy,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def filter_contact_ink(ink,tolerance=.012):
 start=time.time();d=bpy.context.evaluated_depsgraph_get();vertices=[];faces=[];objects=0
 def helper(o):
  n=o.name.lower()
  return n=='street foundation' or 'broken earth lip' in n or 'contact accent' in n or 'contact shadow' in n or 'dust volume' in n or 'fog volume' in n
 for ins in d.object_instances:
  o=ins.object
  if o.type!='MESH' or o.hide_render or helper(o):continue
  me=o.to_mesh();me.calc_loop_triangles();off=len(vertices);mat=ins.matrix_world
  vertices.extend(mat@v.co for v in me.vertices);faces.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);objects+=1;o.to_mesh_clear()
 tree=BVHTree.FromPolygons(vertices,faces,all_triangles=True);total=0;removed=0;empty=0;new_removed=0
 for f in ink.data.layers[0].frames:
  for st in f.drawing.strokes:
   visible=0
   for p in st.points:
    total+=1;near=tree.find_nearest(Vector(p.position),tolerance)
    if near[0] is None:
     if p.opacity>0:new_removed+=1
     p.opacity=0;removed+=1
    else:visible+=1
   if not visible:empty+=1
 # Rebuild only contiguous accepted runs. Do not leave fading bridges through
 # discarded helper geometry or isolated dot remnants.
 retained=0
 for frame in ink.data.layers[0].frames:
  drawing=frame.drawing;runs=[]
  for stroke in drawing.strokes:
   run=[]
   for p in stroke.points:
    if p.opacity>0:run.append((tuple(p.position),p.radius,p.opacity))
    else:
     if len(run)>=2:runs.append(run)
     run=[]
   if len(run)>=2:runs.append(run)
  if len(drawing.strokes):drawing.remove_strokes(indices=list(range(len(drawing.strokes))))
  if runs:
   drawing.add_strokes(sizes=[len(run) for run in runs])
   for stroke,run in zip(drawing.strokes,runs):
    for p,(pos,radius,opacity) in zip(stroke.points,run):p.position=pos;p.radius=radius;p.opacity=opacity
  retained+=len(runs)
 return {'retained_contact_strokes':retained,'solid_objects':objects,'solid_triangles':len(faces),'contact_points':total,'rejected_helper_points':removed,'new_rejected_points':new_removed,'fully_hidden_helper_strokes':empty,'tolerance_m':tolerance,'elapsed_s':time.time()-start}
