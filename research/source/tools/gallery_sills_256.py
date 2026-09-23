import bpy,bmesh
from mathutils.bvhtree import BVHTree

def apply(s):
 root=s.objects['right_vertical_galleries'];cache={};kits=[];count=0
 def clone(c):
  nonlocal count
  if c in cache:return cache[c]
  if c.get('part_id')=='floor_band':
   new=bpy.data.collections.new('256 Closed sill | '+c.name);new.use_fake_user=True;new['part_id']='closed_sill_256'
   source=next(o for o in c.objects if o.name.startswith('Floor fascia panel'));mat=source.material_slots[0].material
   profile=[(-.23,-.045),(-.23,.245),(-.20,.275),(.27,.275),(.27,-.045)];N=len(profile)
   vs=[(x,y,z)for x in [-1.4,1.4]for y,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(j,(j+1)%N,(j+1)%N+N,j+N)for j in range(N)]
   me=bpy.data.meshes.new('256 Closed sill solid');me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();me.materials.append(mat)
   o=bpy.data.objects.new('256 Continuous warm sill with closed ends',me);new.objects.link(o);kits.append(o.name);cache[c]=new;return new
  changed={o:clone(o.instance_collection)for o in c.objects if o.instance_collection}
  if not any(v!=o.instance_collection for o,v in changed.items()):cache[c]=c;return c
  new=bpy.data.collections.new('256 Private sill path | '+c.name);new.use_fake_user=True;new.instance_offset=c.instance_offset
  for o in c.objects:
   if o in changed and changed[o]!=o.instance_collection:
    q=o.copy();q.instance_collection=changed[o];new.objects.link(q)
    if changed[o].get('part_id')=='closed_sill_256':count+=1
   else:new.objects.link(o)
  for child in c.children:new.children.link(child)
  cache[c]=new;return new
 root.instance_collection=clone(root.instance_collection)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();vs=[];tris=[];owners=[];instances=0
 for ins in dg.object_instances:
  if not ins.object.original.name.startswith('256 Continuous warm sill'):continue
  instances+=1;me=ins.object.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ins.matrix_world@v.co for v in me.vertices);tris.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);owners.extend([ins.object.original.name]*len(me.loop_triangles));ins.object.to_mesh_clear()
 assert instances==15,instances
 import landmark_contact_visibility_210 as clip
 tree=BVHTree.FromPolygons(vs,tris,all_triangles=True);clip.external_tree=lambda scene:(tree,owners,{'scope':'Only new closed gallery sills','instances':instances});clip.NAME='096 contacts ink';ink=clip.apply(s,max_pixel_step=.35,gap_m=.005);ink['scope']='Only old096contact-ink occluded by fifteen new solid sills.'
 return {'instances':instances,'closed_manifold_geometry':True,'new_kits':kits,'front_face':'Continuous warm fascia extended to original front lip depth','end_caps':'Same masonry palette and closed geometry','top':'Small30mm bevel','old_component_geometry':'Private original gallery path replaced; other buildings retain old kit','contact_ink':ink}
