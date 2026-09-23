"""UCL01/UCL02/DP03: representative upper-wall masonry bay, authored through approved E warp."""
import bpy,bmesh,math,json,sys,os,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-117';O.mkdir(parents=True,exist_ok=True)
def build_sample(C):
 started=time.time();anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_basis@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P;Fi=F.inverted();j=4;ac=-math.pi+(j+.5)*math.tau/36;zones=[(1.0,69.2,3.0,3.5),(3.9,64.7,1.6,3.7)];new=[];changed=[];audit=[]
 mats={}
 for ob in C.objects:
  if ob.type=='MESH' and ob.get('coliseum_role')not in mats:mats[ob.get('coliseum_role')]=list(ob.data.materials)
 def p(rr,u,z):
  r=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
  if r<outer:r=outer+.55*(r-outer)
  a=-math.pi/2+.68*(ac+u/75+math.pi/2);return F@Vector((r*math.cos(a),r*math.sin(a),z))
 def original(w):
  q=Fi@w;r=math.hypot(q.x,q.y);a=math.atan2(q.y,q.x)
  if a>math.pi/2:a-=math.tau
  a=-math.pi/2+(a+math.pi/2)/.68;outer=75*(1-.055*q.z/78)
  if r<outer:r=outer+(r-outer)/.55
  return P@Vector((r*math.cos(a),r*math.sin(a),q.z)),(a-ac)*75,q.z
 def attrs(ob):
  me=ob.data;a=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');d=me.attributes.get('117 Damage proximity')or me.attributes.new('117 Damage proximity','FLOAT','POINT')
  for v in me.vertices:
   old,u,z=original(ob.matrix_world@v.co);a.data[v.index].vector=old;d.data[v.index].value=max(max(0,1-math.hypot((u-x)/rx,(z-y)/rz))for x,y,rx,rz in zones)
 def mesh(name,vs,fs,role='detail',feature='panel',material=True):
  me=bpy.data.meshes.new('COL117 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL117 '+name,me);C.objects.link(ob);ob['bay']=j;ob['tier']=3;ob['coliseum_role']=role;ob['feature']=feature
  if material:
   for m in mats.get(role,mats['wall']):me.materials.append(m)
   attrs(ob);new.append(ob)
  return ob
 def prism(name,outline,back,front,role='detail',feature='panel',material=True):
  N=len(outline)
  if not material and ('breach' in name or 'entablature loss' in name):
   levels=6;uc=sum(u for u,z in outline)/N;zc=sum(z for u,z in outline)/N;vs=[]
   for ring in range(levels):
    t=ring/(levels-1);rr=back+(front-back)*t;scale=.77+.25*t
    for k,(u,z)in enumerate(outline):
     du=.14*math.sin(k*2.17+ring*1.3)*math.sin(math.pi*t);dz=.16*math.cos(k*1.71-ring*.8)*math.sin(math.pi*t)
     vs.append(p(rr,uc+(u-uc)*scale+du,zc+(z-zc)*scale+dz))
   fs=[tuple(range(N-1,-1,-1)),tuple(range((levels-1)*N,levels*N))]
   for ring in range(levels-1):
    for k in range(N):
     a=ring*N+k;b=ring*N+(k+1)%N;c=b+N;d=a+N;fs.extend([(a,b,c),(a,c,d)])
  else:
   vs=[p(rr,u,z)for rr in [back,front]for u,z in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
  return mesh(name,vs,fs,role,feature,material)
 def box(name,u0,u1,z0,z1,r0,r1,role='detail',feature='panel'):return prism(name,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],r0,r1,role,feature)
 def tag_core(ob,old):
  coords=[ob.matrix_world@v.co for v in old.vertices];tree=BVHTree.FromPolygons(coords,[tuple(f.vertices)for f in old.polygons]);me=ob.data;mask=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');mat=mats.get('fracture',mats['wall'])[0];slot=next((i for i,m in enumerate(me.materials)if m==mat),None)
  if slot is None:slot=len(me.materials);me.materials.append(mat)
  exposed=0
  for face in me.polygons:
   center=ob.matrix_world@face.center;near=tree.find_nearest(center);core=mask.data[face.index].value>.5 or bool(near and near[0]is not None and near[3]>.003);mask.data[face.index].value=float(core)
   if core:face.material_index=slot;exposed+=1
  ob['117 exposed core faces']=exposed
 def cut(label,outline,back,front,targets,custom=None):
  cutter=custom or prism(label+' cutter',outline,back,front,material=False);rows=[]
  for ob in list(targets):
   if ob.type!='MESH':continue
   cb=[cutter.matrix_world@Vector(v)for v in cutter.bound_box];bb=[ob.matrix_world@Vector(v)for v in ob.bound_box]
   if any(max(v[k]for v in cb)<min(v[k]for v in bb)or max(v[k]for v in bb)<min(v[k]for v in cb)for k in range(3)):continue
   old=ob.data;ob.data=old.copy();before=(len(old.vertices),len(old.polygons));mod=ob.modifiers.new('117 True masonry loss','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=ob
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except Exception:
    if mod.name in ob.modifiers:ob.modifiers.remove(mod)
    ob.data=old;continue
   bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();after=(len(bm.verts),len(bm.faces));bm.free()
   if bad or (after[0]and volume<=0):ob.data=old;rows.append({'object':ob.name,'rejected_nonmanifold':bad,'volume':volume});continue
   preserved=True;outside_error=0.0
   if after[0]:
    surface=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices)for f in ob.data.polygons]);low=[min(v[k]for v in cb)-.004 for k in range(3)];high=[max(v[k]for v in cb)+.004 for k in range(3)]
    for vertex in old.vertices:
     point=ob.matrix_world@vertex.co
     if any(point[k]<low[k]or point[k]>high[k]for k in range(3)):
      hit=surface.find_nearest(point);outside_error=max(outside_error,hit[3]if hit and hit[0]is not None else 1000.)
    preserved=outside_error<.005
   else:
    low=[min(v[k]for v in cb)-.004 for k in range(3)];high=[max(v[k]for v in cb)+.004 for k in range(3)]
    preserved=all(all(low[k]<=point[k]<=high[k]for k in range(3))for vertex in old.vertices for point in [ob.matrix_world@vertex.co])
    if not preserved:outside_error=1000.
   if not preserved:ob.data=old;rows.append({'object':ob.name,'rejected_outside_cutter_surface_error_m':outside_error});continue
   if after==before:ob.data=old;continue
   if not after[0]:
    rows.append({'object':ob.name,'removed':True})
    if ob in new:new.remove(ob)
    changed[:]=[v for v in changed if v!=ob]
    bpy.data.objects.remove(ob,do_unlink=True);continue
   ob['damage_region']=label;ob['feature']=label
   if 'breach'in label or 'loss'in label:tag_core(ob,old)
   attrs(ob);changed.append(ob);rows.append({'object':ob.name,'vertices_before':before[0],'vertices_after':after[0],'nonmanifold_edges':bad,'volume':volume,'outside_cutter_max_error_m':outside_error})
  bpy.data.objects.remove(cutter,do_unlink=True);audit.append({'zone':label,'changes':rows})
 wall=lambda:[o for o in C.objects if o.type=='MESH'and o.get('bay')==4 and o.get('tier')==3 and o.get('coliseum_role')=='wall']
 cleanup=[]
 for ob in wall():
  if 'fractured upper wall L'not in ob.name:continue
  old=ob.data;data=[]
  for vertex in old.vertices:
   ow,u,z=original(ob.matrix_world@vertex.co);q=P.inverted()@ow;rr=math.hypot(q.x,q.y)/(1-.055*z/78);data.append((u,z,rr))
  u0=min(v[0]for v in data);u1=max(v[0]for v in data);z0=min(v[1]for v in data);r0=min(v[2]for v in data);r1=max(v[2]for v in data);steps=28;us=[u0+(u1-u0)*k/steps for k in range(steps+1)];profiles=[]
  for rr in [r0,r1]:
   profile=[]
   for u in us:
    pool=[v for v in data if abs(v[0]-u)<(u1-u0)/steps*.75 and abs(v[2]-rr)<1.0]
    if not pool:pool=sorted(data,key=lambda v:abs(v[0]-u)+.2*abs(v[2]-rr))[:8]
    profile.append(max(v[1]for v in pool))
   profiles.append(profile)
  L=len(us);vs=[]
  for ir,rr in enumerate([r0,r1]):
   for top in [False,True]:vs.extend(p(rr,u,profiles[ir][k]if top else z0)for k,u in enumerate(us))
  fs=[]
  for k in range(steps):fs.extend([(k,k+1,L+k+1,L+k),(2*L+k,3*L+k,3*L+k+1,2*L+k+1),(k,2*L+k,2*L+k+1,k+1),(L+k,L+k+1,3*L+k+1,3*L+k)])
  fs.extend([(0,L,3*L,2*L),(L-1,3*L-1,4*L-1,2*L-1)])
  clean=mesh('clean leftwall temporary',vs,fs,'wall','clean supported masonry',material=False);M=ob.matrix_world.inverted();me=clean.data;me.transform(M);me.update();ob.data=me
  for mat in old.materials:me.materials.append(mat)
  bpy.data.objects.remove(clean,do_unlink=True);attrs(ob);ob['feature']='clean closed upperwall with inherited crown';cleanup.append({'object':ob.name,'method':'closed radial loft from116 crown front/back extrema','u_bounds':[u0,u1],'z_base':z0,'r_bounds':[r0,r1],'upper_crown_profiles':profiles,'source_vertices':len(old.vertices),'new_vertices':len(me.vertices)})
 # Large real ragged aperture incorporates former small opening: stepped masonry remnants, varied fracture slope.
 breach=[(-1.45,67.25),(-.45,67.25),(-.3,66.85),(1.2,66.85),(1.25,67.25),(2.3,67.35),(2.6,68.1),(2.15,68.4),(2.5,69.7),(2.0,70.15),(1.9,71.1),(.5,71.15),(.25,71.55),(-.9,71.3),(-.95,70.5),(-1.7,70.5),(-1.8,69.3),(-1.4,68.9)]
 cut('117 upper wall breach',breach,66,77,[o for o in C.objects if o.type=='MESH'and o.get('bay')==4 and o.get('tier')==3])
 # Sculpt a genuine blind shaft niche into the engaged tower core and chamfer its long outer shoulders.
 towercenter=-.5*math.tau/36*75;core=[o for o in C.objects if o.name=='COL110 Tower4 core']
 tower_niche=[(towercenter-.64,67.3),(towercenter+.64,67.3),(towercenter+.64,70.05)]+[(towercenter+.64*math.cos(a),70.05+.64*math.sin(a))for a in [math.pi*k/10 for k in range(1,11)]]
 cut('117 tower blind arch',tower_niche,76.30,78.2,core)
 for sign in [-1,1]:
  section=[(77.25,towercenter+sign*2.55),(78.15,towercenter+sign*2.55),(78.15,towercenter+sign*1.83)];vs=[p(rr,u,z)for z in [59.3,77.2]for rr,u in section];cutter=mesh('tower shoulder chamfer',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],material=False)
  cut('117 integrated tower shoulder chamfer',[],0,0,core,custom=cutter)
 # Facing pockets are shallow actual recesses. Wide quiet planes remain between them.
 for label,u0,u1,z0,z1 in [('left lower panel',-4.7,-1.75,59.7,64.5),('right lower panel',1.7,4.7,59.7,64.5)]:cut('117 '+label,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],74.52,75.15,wall())
 # A compact blind arch niche below the main breach; its back is surviving masonry.
 niche=[(-.75,60.15),(.75,60.15),(.75,61.75)]+[(.75*math.cos(a),61.75+.75*math.sin(a))for a in [math.pi*k/10 for k in range(1,11)]]
 cut('117 blind arched niche',niche,73.9,75.15,wall())
 # Support-test all projected pilaster/frame blocks on surviving actual walls.
 verts=[];faces=[]
 for ob in wall():
  off=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend(tuple(off+i for i in f.vertices)for f in ob.data.polygons)
 tree=BVHTree.FromPolygons(verts,faces);omitted=0
 def supported(u,z):
  a=p(78,u,z);b=p(73.8,u,z);return tree.ray_cast(a,(b-a).normalized(),(b-a).length)[0]is not None
 def safe(name,u0,u1,z0,z1,r0,r1,role='detail',feature='pilaster'):
  nonlocal omitted
  if not all(supported(u,z)for u in [u0,(u0+u1)/2,u1]for z in [z0,(z0+z1)/2,z1]):omitted+=1;return None
  return box(name,u0,u1,z0,z1,r0,r1,role,feature)
 for u in [-4.95,4.95]:
  for k in range(13):safe('slender pilaster %.2f course%d'%(u,k),u-.18,u+.18,58.7+k*1.15,59.85+k*1.15,74.85,75.46)
 for z in [59.38,64.72,65.85,73.45]:
  for k in range(10):safe('recessed field framing %.2f block%d'%(z,k),-4.8+k*.96,-3.84+k*.96,z,z+.24,74.9,75.36,'band','panel frame')
 safe('blind niche sill',-1.0,1.0,59.86,60.12,74.84,75.6,'band','niche sill')
 # Segmented narrow arch surround, shared masonry vocabulary with large openings.
 for k in range(9):
  a=k*math.pi/9;b=(k+1)*math.pi/9;outline=[(.88*math.cos(a),61.75+.88*math.sin(a)),(.88*math.cos(b),61.75+.88*math.sin(b)),(1.08*math.cos(b),61.75+1.08*math.sin(b)),(1.08*math.cos(a),61.75+1.08*math.sin(a))]
  if all(supported(u,z)for u,z in outline):prism('blind niche archivolt%d'%k,outline,74.88,75.44,'arch_molding','blind niche surround')
 # Coherent loss interrupts the new vertical frame and existing65m band, exposing a deep ragged facing/core boundary.
 scar=[(-4.3,67.6),(-3.4,67.9),(-2.8,67.1),(-3.05,66.4),(-2.55,65.8),(-2.9,65.1),(-2.55,64.6),(-3.1,63.7),(-2.85,62.9),(-3.4,62.4),(-3.85,63.1),(-3.7,63.9),(-4.15,64.45),(-3.9,65.25),(-4.45,65.85),(-4.05,66.6)]
 scar=[(u+7.2,z)for u,z in scar]
 cut('117 connected panel and entablature loss',scar,73.5,77,[o for o in C.objects if o.type=='MESH'and o.get('bay')==4 and o.get('tier')==3])
 result={'references':['UCL-01','UCL-02','DP-03'],'bay':4,'new_objects':len([o for o in new if o.name in C.objects]),'changed_objects':len({o.name for o in changed if o.name in C.objects}),'support_omitted':omitted,'pre_boolean_sliver_cleanup':cleanup,'zones':audit,'damage_centers_authored_tangential_height_radii':zones,'weathering_regions_original_world':[{'name':'upper breach','center':list(original(p(75,1.,69.2))[0]),'radius':2.8,'runoff_length':4.5},{'name':'panel entablature loss','center':list(original(p(75,3.9,64.7))[0]),'radius':1.9,'runoff_length':4.0}],'ledge_heights_authored':[59.38,64.72,65.05,65.85,73.45],'attributes':['115 Original world position','117 Damage proximity','117 Exposed core'],'mapping':'Native world-space sample through exact authored ring→angular.68/inner radial.55→E affine→116yaw. Existing assembly unchanged outside sample.','seconds_generation':time.time()-started}
 return result
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];audit=build_sample(C);(O/'geometry-audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(json.dumps(audit))
 # Native proof isolates sample without dismantling inherited affine parents.
 keep={o for o in C.objects if o.get('bay')==4};
 for ob in list(keep):
  while ob.parent:ob=ob.parent;keep.add(ob)
 keep.update(o for o in bpy.context.scene.objects if o.type in ['LIGHT','CAMERA']);bpy.data.batch_remove(ids=[o for o in list(bpy.context.scene.objects)if o not in keep]);s=bpy.context.scene;cam=s.camera;points=[o.matrix_world@v.co for o in keep if o.type=='MESH'for v in o.data.vertices];points=[v for v in points if v.z>37];lo=Vector(tuple(min(v[k]for v in points)for k in range(3)));hi=Vector(tuple(max(v[k]for v in points)for k in range(3)));target=(lo+hi)/2;cam.location=target+Vector((-.12,-1,.10)).normalized()*110;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(hi.z-lo.z,(hi.x-lo.x)*1.2)*1.2
 s.world=bpy.data.worlds.new('117 Neutral proof');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.23,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.65;s.render.resolution_x=1300;s.render.resolution_y=1300;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=False;s.render.filepath=str(O/'geometry-painted.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry-proof.blend'))
 if os.environ.get('GEOMETRY_RENDER')=='1':
  bpy.ops.render.render(write_still=True);clay=bpy.data.materials.new('117 neutral stone proof');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.42,.42,.42,1)
  for ob in keep:
   if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(clay)
  s.render.filepath=str(O/'geometry-clay.png');bpy.ops.render.render(write_still=True)
