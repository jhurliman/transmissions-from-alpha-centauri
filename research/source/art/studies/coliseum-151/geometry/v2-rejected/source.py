"""135 single clean shared-boundary crown reconstruction; UCL01,UCL02,DP03."""
import bpy,bmesh,math,time
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology,strict_crossings
TARGETS=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L']
def evaluate(ob):
 dg=bpy.context.evaluated_depsgraph_get();return bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg)
def _one(C,name):
 start=time.time();ob=next(o for o in C.objects if o.name==name);source=ob.data;before_raw=topology(ob);old=evaluate(ob);tmp=bpy.data.objects.new('135 source validation',old);tmp.matrix_world=ob.matrix_world;before=topology(tmp);bpy.data.objects.remove(tmp);original,world,unpack=mapping();iv=ob.matrix_world.inverted();cutz=67.80
 coords=[unpack(ob.matrix_world@v.co)for v in old.vertices];amin=min(p[1]for p in coords);amax=max(p[1]for p in coords);width=(amax-amin)*75
 def uval(a):return (a-amin)*75
 old.calc_loop_triangles();tris=list(old.loop_triangles);ovs=[v.co.copy()for v in old.vertices];tree=BVHTree.FromPolygons(ovs,[tuple(t.vertices)for t in tris],all_triangles=True);orig=[d.vector.copy()for d in old.attributes['115 Original world position'].data];source_points={tuple(v.co):orig[v.index]for v in old.vertices};cn=[d.vector.copy()for d in old.corner_normals]
 bm=bmesh.new();bm.from_mesh(old);po=world(75,amin,cutz);wn=(world(76,amin,cutz)-po).cross(world(75,amin+.001,cutz)-po).normalized();ln=(ob.matrix_world.to_3x3().transposed()@wn).normalized()
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=iv@po,plane_no=ln,clear_inner=False,clear_outer=False)
 upper=[f for f in bm.faces if unpack(ob.matrix_world@f.calc_center_median())[2]>cutz+.00001];bmesh.ops.delete(bm,geom=upper,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 if False: #149 lower geometry is valid and must be preserved

  # This inherited wall also has crossed end strips reaching its bottom face.
  # Rebuild its plain lower masonry as a convex shared-boundary prism; its
  # separate sill, aperture head, pilasters, niches and cornices stay untouched.
  base=[Vector(((a-amin)*75,r)) for r,a,z in coords if z<62.561]
  hull=geometry.convex_hull_2d(base);base=[base[i] for i in hull]
  coarse=base;base=[]
  for i,p in enumerate(coarse):
   q=coarse[(i+1)%len(coarse)];n=max(1,math.ceil((q-p).length/.35))
   base.extend(p.lerp(q,k/n)for k in range(n))
  bm.free();bm=bmesh.new();bottom=[bm.verts.new(iv@world(p.y,amin+p.x/75,62.56))for p in base];topring=[bm.verts.new(iv@world(p.y,amin+p.x/75,cutz))for p in base]
  bm.faces.new(bottom[::-1])
  for i in range(len(base)):
   j=(i+1)%len(base);bm.faces.new([bottom[i],bottom[j],topring[j],topring[i]])
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
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
 def height(u):
  t=u/width
  knots=[(0,74.74),(.83,74.74),(.86,74.55),(.89,74.55),(.93,74.06),(1,73.65)] if 'U4 fractured upper wall L'in name else [(0,72.58),(.50,72.58),(.54,72.74),(.56,73.1),(.595,73.1),(.61,73.65),(.64,73.65),(.65,74.30),(1,74.30)] if 'U4 'in name else [(0,74.30),(.365,74.30),(.382,73.7),(.41,73.7),(.423,72.80),(.55,72.96),(.58,72.80),(.606,72.1),(.625,72.1),(.65,71.30),(.67,70.80),(1,70.80)]
  for (a,x),(b,y)in zip(knots,knots[1:]):
   if a<=t<=b:return x+(y-x)*(t-a)/(b-a)
  return knots[0 if t<0 else -1][1]
 def patch(t,a,b,c,d):
  return smooth(a,b,t)*(1-smooth(c,d,t))
 def top(u,r):
  # One connected return across the shared U4R/U5L crest, open to the sky.
  global_u=(amin+u/75+2.3194)*75;span=9.665
  envelope=smooth(0,.65,global_u)*(1-smooth(span-.65,span,global_u))
  # Rear surviving spine retains the macro profile. Two finite broken course
  # terraces step downward toward the camera; they are not an inset box.
  stagger=.22*math.sin(global_u*.87)+.11*math.sin(global_u*2.8)
  rr=r+stagger
  drop=.12+1.0*smooth(68.6,69.1,rr)+1.25*smooth(71.0,71.5,rr)+1.30*smooth(73.0,73.6,rr)
  jag=(.035*math.sin(global_u*5.1+r*2.1)+.014*math.sin(global_u*11.7-r*4.7))*envelope
  back_rise=2.40*(1-smooth(71.5,73.3,r))*envelope
  z=max(cutz+.30,height(u)+back_rise-drop*envelope-jag)
  return r-.055*envelope*smooth(73.5,75.,r),z
 newverts=[]
 for p in vv:
  u,r=p;rr,z=top(u,r);newverts.append(bm.verts.new(iv@world(rr,amin+u/75,z)))
 # CDT identifies input boundary vertices even when coincident entries were merged.
 bmap={}
 for i,ids in enumerate(vorig):
  for k in ids:
   if k<N:bmap[k]=i
 if len(bmap)!=N:raise RuntimeError('Boundary correspondence incomplete')
 layer=bm.faces.layers.int.new('151 fracture cap');bm.verts.ensure_lookup_table()
 for f in ff:
  q=bm.faces.new([newverts[i]for i in f]);q[layer]=1
 # Three connected perimeter courses: sound lower wall, recessed fracture foot,
 # and one shallow supported lip. No disconnected masonry stones.
 rings=[ordered]
 rings.append([newverts[bmap[i]]for i in range(N)])
 for level in range(len(rings)-1):
  low,high=rings[level],rings[level+1]
  for i in range(N):
   j=(i+1)%N;verts=[low[i],low[j],high[j],high[i]];clean=[]
   for v in verts:
    if v not in clean:clean.append(v)
   if len(clean)>=3:
    q=bm.faces.new(clean);q[layer]=1
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=old.copy();me.name='151 broad connected exposed return';bm.to_mesh(me);bm.free();me.update()
 ob.data=me;mods=list(ob.modifiers)
 for m in mods:m.show_viewport=False;m.show_render=False
 attr=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');normals=[d.vector.copy()for d in me.corner_normals];core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');mask=me.attributes['151 fracture cap'];core_slot=next((i for i,s in enumerate(ob.material_slots)if s.material and('Exposed masonry core'in s.material.name or s.material.get('role')=='fracture')),0)
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
  raise RuntimeError('Reconstruction rejected '+name+' boundary '+str(N)+' '+str(check))
 for m in mods:ob.modifiers.remove(m)
 bpy.context.view_layer.update();evaluated=evaluate(ob);tmp=bpy.data.objects.new('135 final validation',evaluated);tmp.matrix_world=ob.matrix_world;evcheck=topology(tmp);bpy.data.objects.remove(tmp);bpy.data.meshes.remove(evaluated)
 outside=[]
 newtree=BVHTree.FromPolygons([v.co.copy()for v in me.vertices],[tuple(f.vertices)for f in me.polygons])
 for v,p in zip(old.vertices,coords):
  if p[2]<cutz-.001:outside.append(newtree.find_nearest(v.co)[3])
 ob['151 damage feature']='Broad open terraced fracture return, preserved rear spine'
 return {'target':ob.name,'references':['UCL-01','UCL-02','DP-03'],'before_raw':before_raw,'before_evaluated':before,'after_raw':check,'after_evaluated':evcheck,'cut_plane_authored_z':cutz,'top_band_authored_z':[cutz,max(height(0),height(width),74.74)],'layout_materialized_for_target_only':True,'boundary_vertices':N,'new_fracture_faces':sum(bool(x.value)for x in mask.data),'outside_max_local_surface_error':max(outside,default=0),'new_detached_objects':0,'scope':'Only existing crown above67.8 rebuilt; original lower geometry retained on both targets','normals':'New fracture planes use actual normals; lower-wall split normals interpolated from accepted evaluated source.','seconds':time.time()-start}

def apply(C):
 return {'reference_ids':['UCL-01','UCL-02','DP-03'],'targets':[_one(C,name)for name in TARGETS],'new_detached_objects':0,'production_integration':False}
