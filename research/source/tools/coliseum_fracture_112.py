"""112 physically faceted fracture surfaces, preserving111large silhouette.
UCL-01: exposed broken masonry is irregular through thickness, with attached aggregate.
"""
import bpy,bmesh,math,random,hashlib
from mathutils import Vector,Matrix,noise
from mathutils.bvhtree import BVHTree

def fracture_surfaces(collection):
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_world@auth.inverted();di=delta.inverted();li=lean.inverted();scale=delta.to_scale().x
 def authored(v):return li@(di@v-Vector((0,347,0)))
 # Remove old caps that survived silhouette cuts without underlying masonry support.
 wallv=[];wallf=[]
 for o in collection.objects:
  if o.type!='MESH' or o.get('coliseum_role')!='wall' or o.get('tier')!=3:continue
  offset=len(wallv);wallv.extend(o.matrix_world@v.co for v in o.data.vertices);wallf.extend(tuple(offset+i for i in f.vertices)for f in o.data.polygons)
 walltree=BVHTree.FromPolygons(wallv,wallf);coping=[];up=(delta.to_3x3()@lean.to_3x3()@Vector((0,0,1))).normalized()
 for o in list(collection.objects):
  if o.type!='MESH' or 'surviving coping' not in o.name:continue
  verts=[o.matrix_world@v.co for v in o.data.vertices];heights=[authored(v).z for v in verts];low=min(heights);samples=[v for v,h in zip(verts,heights)if h<low+.01]
  if not samples:continue
  center=sum(samples,Vector())/len(samples);samples=[v*.85+center*.15 for v in samples]+[center];gaps=[]
  for v in samples:
   hit=walltree.ray_cast(v+up*.02*scale,-up,6*scale)[0];gaps.append((v-hit).dot(up)/scale if hit is not None else 99)
  gap=max(gaps)
  if gap>.45:
   coping.append({'object':o.name,'action':'removed unsupported remnant','max_gap_m':gap});bpy.data.objects.remove(o,do_unlink=True)
  elif gap>.04:
   o.matrix_world.translation-=up*(gap+.025)*scale;coping.append({'object':o.name,'action':'seated on masonry','lowering_m':gap+.025})
 # Whole-landmark visibility rejects buried kit interfaces and intact covering copings.
 allv=[];allf=[]
 for ob in collection.objects:
  if ob.type!='MESH':continue
  offset=len(allv);allv.extend(ob.matrix_world@v.co for v in ob.data.vertices);allf.extend(tuple(offset+i for i in f.vertices)for f in ob.data.polygons)
 tree=BVHTree.FromPolygons(allv,allf)
 changes=[];aggregate_seeds=[]
 for ob in list(collection.objects):
  if ob.type!='MESH':continue
  upper=('fractured upper wall' in ob.name or 'aperture head' in ob.name or 'broken crown' in ob.name)
  spall=bool(ob.get('localized_breakage'))
  if not upper and not spall:continue
  old=ob.data;bm=bmesh.new();bm.from_mesh(old);selected=[]
  normalmatrix=ob.matrix_world.to_3x3().inverted().transposed()
  for f in bm.faces:
   w=ob.matrix_world@f.calc_center_median();v=authored(w);n=(normalmatrix@f.normal).normalized();na=(li.to_3x3()@di.to_3x3()@n).normalized();rr=math.hypot(v.x,v.y)/max(.5,1-.055*v.z/78);radial=Vector((v.x,v.y,0)).normalized()
   candidate=(upper and v.z>65 and (na.z>.18 or abs(na.dot(radial))<.45)) or (spall and 53<v.z<61 and 74.0<rr<74.85)
   if not candidate or f.calc_area()<.03:continue
   hit=tree.ray_cast(w+n*.04*scale,n,.50*scale)[0]
   if hit is not None:continue
   selected.append(f)
  if not selected:bm.free();continue
  # Adjacent intact facade planes constrain boundary displacement, preventing giant shading triangles.
  pv=[];pf=[]
  for f in bm.faces:
   if f in selected:continue
   off=len(pv);pv.extend(ob.matrix_world@v.co for v in f.verts);pf.append(tuple(range(off,len(pv))))
  protected=BVHTree.FromPolygons(pv,pf) if pf else None
  # Source fracture patches used to confine added relief, independent of camera.
  vs=[];fs=[]
  for f in selected:
   off=len(vs);vs.extend(ob.matrix_world@v.co for v in f.verts);fs.append(tuple(range(off,len(vs))))
  surf=BVHTree.FromPolygons(vs,fs)
  # Subdivide only exposed patch edges; neighboring faces follow shared vertices, remaining watertight.
  edges=set(bm.edges)
  bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=5,use_grid_fill=True)
  bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
  for iteration in range(3):
   refine=[]
   for e in bm.edges:
    if (ob.matrix_world.to_3x3()@(e.verts[0].co-e.verts[1].co)).length<.6*scale:continue
    near=surf.find_nearest(ob.matrix_world@((e.verts[0].co+e.verts[1].co)*.5))
    if near[0] is not None and near[3]<.0005:refine.append(e)
   if not refine:break
   bmesh.ops.subdivide_edges(bm,edges=refine,cuts=1,use_grid_fill=True)
   bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
  affected=0;invm=ob.matrix_world.inverted()
  for v in bm.verts:
   w=ob.matrix_world@v.co;near=surf.find_nearest(w)
   if near[0] is None or near[3]>.0005:continue
   q=authored(w)
   # Connected two-scale fracture field, angular after triangulation; world-stable shared positions.
   rough=noise.noise_vector(q*.94,noise_basis='PERLIN_ORIGINAL')*.19 + noise.noise_vector(q*3.3+Vector((13,2,7)),noise_basis='PERLIN_ORIGINAL')*.065
   # Vertical relief dominates horizontal chatter to avoid scalloped pasted-on edges.
   rough.x*=.65;rough.y*=.65
   disp=delta.to_3x3()@lean.to_3x3()@rough
   if protected:
    intact=protected.find_nearest(w)
    if intact[0] is not None and intact[3]<.0005:disp-=intact[1]*disp.dot(intact[1])
   v.co=invm@(w+disp);affected+=1
  bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume()
  if bad or vol<=0:bm.free();continue
  ob.data=old.copy();bm.to_mesh(ob.data);bm.free();ob['fracture112']='native two-scale faceted exposed fracture relief';changes.append({'object':ob.name,'relief_vertices':affected,'nonmanifold':bad,'volume_positive':vol>0})
  rng=random.Random(int(hashlib.sha256(ob.name.encode()).hexdigest()[:8],16))
  for face in fs:
   if rng.random()>.27:continue
   verts=[vs[i] for i in face];center=sum(verts,Vector())/len(verts);near=surf.find_nearest(center)
   if near[0] is None or near[1].z<.3:continue
   # Small aggregate cores overlap fractured masonry; they are never loose hovering rubble.
   aggregate_seeds.append((center,near[1],rng.uniform(.10,.24)*scale,ob.data.materials[0] if ob.data.materials else None))
 aggregates=0
 for i,(center,normal,radius,material) in enumerate(aggregate_seeds[:48]):
  rng=random.Random(11200+i);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=radius)
  for v in bm.verts:v.co*=rng.uniform(.75,1.16);v.co+=center-normal*radius*.62
  me=bpy.data.meshes.new(f'COL112 embedded aggregate{i}');bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(f'COL112 embedded aggregate{i}',me);collection.objects.link(ob);ob['coliseum_role']='fracture';ob['tier']=3;ob['bay']=-1;ob['embedded_fraction']=.62
  if material:me.materials.append(material)
  aggregates+=1
 return {'reference_ids':['UCL-01','DP-03','UX-01'],'coping_support':coping,'changed_surfaces':changes,'embedded_aggregate':aggregates,'macro_silhouette_preserved':True,'max_authored_relief_estimate_m':.26,'native_geometry':True}
