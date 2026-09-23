"""134 single clean shared-boundary crown reconstruction; UCL01,UCL02,DP03."""
import bpy,bmesh,math,time
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology
TARGET='COL110 U9 fractured upper wall L'
def evaluate(ob):
 dg=bpy.context.evaluated_depsgraph_get();return bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg)
def apply(C):
 start=time.time();ob=next(o for o in C.objects if o.name==TARGET);source=ob.data;old=evaluate(ob);tmp=bpy.data.objects.new('134 source validation',old);tmp.matrix_world=ob.matrix_world;before=topology(tmp);bpy.data.objects.remove(tmp);original,world,unpack=mapping();iv=ob.matrix_world.inverted();cutz=72.10
 coords=[unpack(ob.matrix_world@v.co)for v in old.vertices];amin=min(p[1]for p in coords);amax=max(p[1]for p in coords);width=(amax-amin)*75
 def uval(a):return (a-amin)*75
 old.calc_loop_triangles();tris=list(old.loop_triangles);ovs=[v.co.copy()for v in old.vertices];tree=BVHTree.FromPolygons(ovs,[tuple(t.vertices)for t in tris],all_triangles=True);orig=[d.vector.copy()for d in old.attributes['115 Original world position'].data];source_points={tuple(v.co):orig[v.index]for v in old.vertices};cn=[d.vector.copy()for d in old.corner_normals]
 bm=bmesh.new();bm.from_mesh(old);po=world(75,amin,cutz);wn=(world(76,amin,cutz)-po).cross(world(75,amin+.001,cutz)-po).normalized();ln=(ob.matrix_world.to_3x3().transposed()@wn).normalized()
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=iv@po,plane_no=ln,clear_inner=False,clear_outer=False)
 upper=[f for f in bm.faces if unpack(ob.matrix_world@f.calc_center_median())[2]>cutz+.00001];bmesh.ops.delete(bm,geom=upper,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 boundary=[e for e in bm.edges if e.is_boundary]
 if not boundary:raise RuntimeError('No crown boundary')
 edges=set(boundary);ordered=[boundary[0].verts[0]];v=ordered[0]
 while edges:
  e=next((e for e in edges if v in e.verts),None)
  if e is None:raise RuntimeError('More than one boundary loop')
  edges.remove(e);v=e.other_vert(v)
  if v==ordered[0]:break
  ordered.append(v)
 if edges:raise RuntimeError('Unexpected disconnected cut boundary')
 # The cut loop exactly attaches to surviving masonry; top region is reconstructed, not displaced old faces.
 domain=[]
 for v in ordered:
  r,a,z=unpack(ob.matrix_world@v.co);domain.append(Vector((uval(a),r)))
 # Dense enough for local curvature, modest enough to inspect and edit.
 N=len(domain);uv=list(domain)
 for i in range(1,int(width/.30)):
  u=i*.30
  for j in range(1,16):uv.append(Vector((u,67+j*.5)))
 cd=geometry.delaunay_2d_cdt(uv,[(i,(i+1)%N)for i in range(N)],[list(range(N))],1,.000001,True);vv,ee,ff,vorig,eorig,forig=cd
 def smooth(a,b,x):
  t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
 newverts=[];new_indices=[]
 for p in vv:
  u,r=p;a=amin+u/75;end=smooth(0,.40,u)*(1-smooth(width-.4,width,u));rr=r+.07*math.sin(u*3.1)+.04*math.sin(u*8.7)
  drop=(.12+.67*(1-smooth(72.9,73.55,rr))-.36*(1-smooth(69.7,70.3,rr))+.045*math.sin(u*13.4+r*7.1)+.025*math.sin(u*23.7-r*5.4))*end
  inset=(.55+.075*math.sin(u*4.2)+.035*math.sin(u*12.3))*end*smooth(73.8,75,r)
  z=73.30-max(0,drop);newverts.append(bm.verts.new(iv@world(r-inset,a,z)))
 # CDT identifies input boundary vertices even when coincident entries were merged.
 bmap={}
 for i,ids in enumerate(vorig):
  for k in ids:
   if k<N:bmap[k]=i
 if len(bmap)!=N:raise RuntimeError('Boundary correspondence incomplete')
 layer=bm.faces.layers.int.new('134 fracture cap');bm.verts.ensure_lookup_table()
 for f in ff:
  q=bm.faces.new([newverts[i]for i in f]);q[layer]=1
 for i in range(N):
  j=(i+1)%N
  if bmap[i]==bmap[j]:
   q=bm.faces.new([ordered[i],ordered[j],newverts[bmap[i]]]);q[layer]=1;continue
  q=bm.faces.new([ordered[i],ordered[j],newverts[bmap[j]],newverts[bmap[i]]]);q[layer]=1
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=old.copy();me.name='134 connected course crown';bm.to_mesh(me);bm.free();me.update()
 ob.data=me;mods=list(ob.modifiers)
 for m in mods:m.show_viewport=False;m.show_render=False
 attr=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');normals=[d.vector.copy()for d in me.corner_normals];core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');mask=me.attributes['134 fracture cap'];core_slot=next((i for i,s in enumerate(ob.material_slots)if s.material and('Exposed masonry core'in s.material.name or s.material.get('role')=='fracture')),0)
 for v in me.vertices:
  if tuple(v.co)in source_points:attr.data[v.index].vector=source_points[tuple(v.co)];continue
  hit=tree.find_nearest(v.co);t=tris[hit[2]];attr.data[v.index].vector=geometry.barycentric_transform(hit[0],*[ovs[i]for i in t.vertices],*[orig[i]for i in t.vertices])
 for p in me.polygons:
  if mask.data[p.index].value:p.material_index=core_slot;core.data[p.index].value=1.;p.use_smooth=False
  else:
   hit=tree.find_nearest(p.center);source_face=tris[hit[2]].polygon_index;local_tris=[t for t in tris if t.polygon_index==source_face]
   for li in p.loop_indices:
    point=me.vertices[me.loops[li].vertex_index].co;candidates=[(geometry.closest_point_on_tri(point,*[ovs[i]for i in t.vertices]),t)for t in local_tris];near,t=min(candidates,key=lambda q:(q[0]-point).length_squared);normals[li]=geometry.barycentric_transform(near,*[ovs[i]for i in t.vertices],*[cn[i]for i in t.loops]).normalized()
 me.normals_split_custom_set(normals);check=topology(ob)
 if check['nonmanifold']or check['strict_crossings']or check['volume']<=0:
  ob.data=source
  for m in mods:m.show_viewport=True;m.show_render=True
  raise RuntimeError('Reconstruction rejected '+str(check))
 for m in mods:ob.modifiers.remove(m)
 bpy.context.view_layer.update();evaluated=evaluate(ob);tmp=bpy.data.objects.new('134 final validation',evaluated);tmp.matrix_world=ob.matrix_world;evcheck=topology(tmp);bpy.data.objects.remove(tmp);bpy.data.meshes.remove(evaluated)
 outside=[]
 newtree=BVHTree.FromPolygons([v.co.copy()for v in me.vertices],[tuple(f.vertices)for f in me.polygons])
 for v,p in zip(old.vertices,coords):
  if p[2]<cutz-.001:outside.append(newtree.find_nearest(v.co)[3])
 ob['134 damage feature']='One connected course-stepped crown with attached chipped shoulder'
 return {'target':ob.name,'references':['UCL-01','UCL-02','DP-03'],'before_evaluated':before,'after_raw':check,'after_evaluated':evcheck,'cut_plane_authored_z':cutz,'top_band_authored_z':[72.10,73.30],'layout_materialized_for_target_only':True,'boundary_vertices':N,'new_fracture_faces':sum(bool(x.value)for x in mask.data),'outside_max_local_surface_error':max(outside,default=0),'new_detached_objects':0,'scope':'Only upper1.2m of U9L rebuilt from exact ordered boundary; lower masonry and all other objects retained. Removed inherited0.85m near-zero-thickness end sliver as part of actual crown repair.','normals':'New fracture planes use actual normals; lower-wall split normals interpolated from accepted evaluated source.','seconds':time.time()-start}
