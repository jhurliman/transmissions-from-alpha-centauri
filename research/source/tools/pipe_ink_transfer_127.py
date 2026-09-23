"""Move only baked ink attached to the explicitly edited pipe surfaces."""
import bpy
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree

def apply(before,after,tolerance=.025):
 vertices=[];newvertices=[];triangles=[];owners=[]
 assert set(before)==set(after)
 for name,b in before.items():
  a=after[name];assert b['triangles']==a['triangles'] and len(b['vertices'])==len(a['vertices']),name
  offset=len(vertices);vertices.extend(Vector(v)for v in b['vertices']);newvertices.extend(Vector(v)for v in a['vertices']);triangles.extend(tuple(offset+i for i in t)for t in b['triangles']);owners.extend([name]*len(b['triangles']))
 tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);rows=[]
 for name in ['096 contacts ink','096 damage ink']:
  ob=bpy.data.objects[name];moved=0;nearest=0;max_distance=0;by_owner={};total=0;iv=ob.matrix_world.inverted()
  for layer in ob.data.layers:
   for frame in layer.frames:
    for stroke in frame.drawing.strokes:
     for point in stroke.points:
      total+=1;p=ob.matrix_world@point.position;hit=tree.find_nearest(p,tolerance)
      if hit is None or hit[0] is None:continue
      nearest+=1;t=triangles[hit[2]];old=[vertices[i]for i in t];new=[newvertices[i]for i in t]
      if max((a-b).length for a,b in zip(old,new))<1e-7:continue
      nold=(old[1]-old[0]).cross(old[2]-old[0]);nnew=(new[1]-new[0]).cross(new[2]-new[0])
      if nold.length<1e-9 or nnew.length<1e-9:continue
      q=geometry.barycentric_transform(hit[0],*old,*new)+nnew.normalized()*(p-hit[0]).dot(nold.normalized());point.position=iv@q;moved+=1;max_distance=max(max_distance,hit[3]);owner=owners[hit[2]];by_owner[owner]=by_owner.get(owner,0)+1
    frame.drawing.tag_positions_changed()
  rows.append({'object':name,'points_total':total,'points_moved':moved,'points_near_affected_surfaces':nearest,'maximum_original_attachment_distance_m':max_distance,'components':by_owner})
 return {'method':'Barycentric surface correspondence; preserve stroke normal offset. Only points within25mm of original edited pipe surfaces eligible. Unrelated strokes and materials unchanged.','rows':rows,'changed_objects':[r['object']for r in rows if r['points_moved']]}
