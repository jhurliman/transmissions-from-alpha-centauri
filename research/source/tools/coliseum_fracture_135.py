"""135 single clean shared-boundary crown reconstruction; UCL01,UCL02,DP03."""
import bpy,bmesh,math,time
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology,strict_crossings
TARGETS=['COL110 U4 fractured upper wall L','COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L']
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
 if 'U5 ' in name:
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
  end=smooth(0,.32,u)*(1-smooth(width-.32,width,u));rr=r+.16*math.sin(u*3.7)+.055*math.sin(u*11.3)
  drop=(.12+.53*(1-smooth(73.1,73.65,rr))+.23*(1-smooth(70.65,71.1,rr))-.39*(1-smooth(68.9,69.4,rr)))*end
  jag=.065*math.sin(u*16.1+r*11.3)+.027*math.sin(u*31.7-r*8.7)
  centers=[.16,.43,.78]if 'U4 'in name else[.13,.48,.73,.89]
  chips=sum(.18*max(0.,1-abs(u/width-c)*width/.14)for c in centers)*smooth(73.9,75.,r)
  t=u/width
  irregular=.04+.13*patch(t,.08,.13,.32,.39)+.08*patch(t,.53,.59,.73,.79)+.035*patch(t,.84,.87,.92,.96)
  inset=irregular*end*smooth(73.65,75,r)
  return r-inset,height(u)-max(0.,drop+jag*end+chips)
 newverts=[]
 for p in vv:
  u,r=p;rr,z=top(u,r);newverts.append(bm.verts.new(iv@world(rr,amin+u/75,z)))
 # CDT identifies input boundary vertices even when coincident entries were merged.
 bmap={}
 for i,ids in enumerate(vorig):
  for k in ids:
   if k<N:bmap[k]=i
 if len(bmap)!=N:raise RuntimeError('Boundary correspondence incomplete')
 layer=bm.faces.layers.int.new('135 fracture cap');bm.verts.ensure_lookup_table()
 for f in ff:
  q=bm.faces.new([newverts[i]for i in f]);q[layer]=1
 # Three connected perimeter courses: sound lower wall, recessed fracture foot,
 # and one shallow supported lip. No disconnected masonry stones.
 rings=[ordered]
 for level in [0,1,2]:
  ring=[]
  for p in domain:
   u,r=p;h=top(u,r)[1];end=smooth(0,.32,u)*(1-smooth(width-.32,width,u));front=smooth(73.65,75.,r);band=smooth(width*.34,width*.41,u)*(1-smooth(width*.64,width*.74,u));notch=.32*end*front*band
   t=u/width;factor=[.66,.83,.945][level]
   # Unequal finite stone ledges. Outside these short spans the rings are
   # collinear on the broad surviving wall plane, so they do not make trim.
   windows=[[(.06,.13,.29,.36),(.67,.72,.86,.92)],[(.23,.29,.47,.55)],[(.43,.49,.62,.69),(.79,.83,.89,.94)]]
   w=sum(patch(t,*q)for q in windows[level]);rr=r+(top(u,r)[0]-r)*factor-[.18,.27,.14][level]*w*front*end
   zz=cutz+(h-cutz)*factor+[.12,-.13,.055][level]*w*front
   # A small nonuniform notch terminates one exposed course instead of
   # repeating teeth around the complete perimeter.
   rr-=.075*patch(t,.36,.375,.39,.42)*front*(level==1)
   ring.append(bm.verts.new(iv@world(rr,amin+u/75,zz)))
  rings.append(ring)
 rings.append([newverts[bmap[i]]for i in range(N)])
 for level in range(len(rings)-1):
  low,high=rings[level],rings[level+1]
  for i in range(N):
   j=(i+1)%N;verts=[low[i],low[j],high[j],high[i]];clean=[]
   for v in verts:
    if v not in clean:clean.append(v)
   if len(clean)>=3:
    q=bm.faces.new(clean);q[layer]=int(level>0)
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=old.copy();me.name='135 connected course crown';bm.to_mesh(me);bm.free();me.update()
 ob.data=me;mods=list(ob.modifiers)
 for m in mods:m.show_viewport=False;m.show_render=False
 attr=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');normals=[d.vector.copy()for d in me.corner_normals];core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');mask=me.attributes['135 fracture cap'];core_slot=next((i for i,s in enumerate(ob.material_slots)if s.material and('Exposed masonry core'in s.material.name or s.material.get('role')=='fracture')),0)
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
 ob['135 damage feature']='Broader connected unequal masonry-course returns and supported shallow lip'
 return {'target':ob.name,'references':['UCL-01','UCL-02','DP-03'],'before_raw':before_raw,'before_evaluated':before,'after_raw':check,'after_evaluated':evcheck,'cut_plane_authored_z':cutz,'top_band_authored_z':[cutz,max(height(0),height(width),74.74)],'layout_materialized_for_target_only':True,'boundary_vertices':N,'new_fracture_faces':sum(bool(x.value)for x in mask.data),'outside_max_local_surface_error':max(outside,default=0),'new_detached_objects':0,'scope':('U5L plain lower prism reconstructed from measured convex bottom footprint to remove inherited end-strip and bottom-face folds; separate architectural features unchanged.' if 'U5 ' in name else 'Existing crown return above67.8m rebuilt from its exact shared boundary; lower original vertices retained.'),'normals':'New fracture planes use actual normals; lower-wall split normals interpolated from accepted evaluated source.','seconds':time.time()-start}

def apply(C):
 return {'reference_ids':['UCL-01','UCL-02','DP-03'],'targets':[_one(C,name)for name in TARGETS],'new_detached_objects':0,'production_integration':False}
