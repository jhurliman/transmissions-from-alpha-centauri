"""Cornice supports inherit nearby bearing-wall material plus a15% darkening tint."""
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
  if source not in cache:
   m=source.copy();m.name='123 Cornice wall tint '+source.name;cache[source]=m
   n,l=m.node_tree.nodes,m.node_tree.links;em=next((q for q in n if q.type=='EMISSION'),None)
   if not em:raise RuntimeError('Expected painted masonry material')
   mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.label='User15% darker wall material';mix.inputs[0].default_value=1.;mix.inputs[2].default_value=(.85,.85,.85,1)
   if em.inputs[0].is_linked:l.new(em.inputs[0].links[0].from_socket,mix.inputs[1])
   else:mix.inputs[1].default_value=em.inputs[0].default_value
   l.new(mix.outputs[0],em.inputs[0])
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=cache[source]
  ob['123 bearing wall']=owner
  rows.append({'object':ob.name,'bearing_wall':owner,'material':cache[source].name,'nearest_surface_distance':hit[3]})
 return {'blocks':len(rows),'material_variants':len(cache),'linear_tint':.85,'constant_midpoint_removed':True,'rows':rows,'method':'Nearest actual wall/pier/tower surface supplies native material; only final color receives15% darkening'}
