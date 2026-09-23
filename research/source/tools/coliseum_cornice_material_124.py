"""Cornice supports inherit the unmodified nearby bearing-wall material."""
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy

def apply(C):
 deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
 for ob in C.objects:
  if ob.type!='MESH' or ob.get('coliseum_role') not in ['wall','tower','pier']:continue
  evaluated=ob.evaluated_get(deps);me=evaluated.to_mesh();offset=len(vs);vs.extend(evaluated.matrix_world@v.co for v in me.vertices)
  for face in me.polygons:
   fs.append(tuple(offset+k for k in face.vertices));idx=min(face.material_index,max(0,len(ob.material_slots)-1));mat=ob.material_slots[idx].material if ob.material_slots else None;owners.append((ob.name,mat))
  evaluated.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,fs);cache={};rows=[]
 for ob in C.objects:
  if ob.type!='MESH' or ob.get('feature')!='shared undercornice dentil':continue
  ev=ob.evaluated_get(deps);me=ev.to_mesh();center=sum((ev.matrix_world@v.co for v in me.vertices),Vector())/len(me.vertices);ev.to_mesh_clear();hit=tree.find_nearest(center)
  if not hit or hit[0] is None:raise RuntimeError('No bearing wall for '+ob.name)
  owner,source=owners[hit[2]]
  if not source:raise RuntimeError('Missing bearing material '+owner)
  cache[source]=source
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=source
  ob['124 bearing wall']=owner
  rows.append({'object':ob.name,'bearing_wall':owner,'material':source.name,'nearest_surface_distance':hit[3]})
 return {'blocks':len(rows),'material_variants':len(cache),'linear_tint':1.0,'rows':rows,'method':'Unmodified native material from nearest bearing wall face; no additional color filter'}
