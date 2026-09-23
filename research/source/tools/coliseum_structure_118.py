"""UCL01/UCL02/DP03: representative upper-wall masonry bay, authored through approved E warp."""
import bpy,bmesh,math,json,sys,os,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-118';O.mkdir(parents=True,exist_ok=True)
def refine_sample(C):
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
  me=bpy.data.meshes.new('COL118 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL118 '+name,me);C.objects.link(ob);ob['bay']=j;ob['tier']=3;ob['coliseum_role']=role;ob['feature']=feature
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
   if 'breach'in label or 'loss'in label or label.startswith('118 '):tag_core(ob,old)
   attrs(ob);changed.append(ob);rows.append({'object':ob.name,'vertices_before':before[0],'vertices_after':after[0],'nonmanifold_edges':bad,'volume':volume,'outside_cutter_max_error_m':outside_error})
  bpy.data.objects.remove(cutter,do_unlink=True);audit.append({'zone':label,'changes':rows})
 wall=lambda:[o for o in C.objects if o.type=='MESH'and o.get('bay')==4 and o.get('tier')==3 and o.get('coliseum_role')=='wall']
 # Interior-only broken courses; outer front aperture remains untouched (all cutters behind r74.65).
 samplewalls=wall()
 shelves=[('back lower return',67.00,69.1,-1.2,1.65,67.10),('middle lower return',69.1,71.0,-.9,1.9,66.91),('front lower return',71.0,73.15,-.7,1.65,66.76)]
 for label,r0,r1,u0,u1,z in shelves:
  outline=[(u0,z+.10),(u0+.35,z-.10),(u1-.4,z-.06),(u1,z+.14),(u1,68.25),(u0,68.25)]
  cut('118 '+label,outline,r0,r1,samplewalls)
 # Side-return pocket changes depth direction instead of continuing a straight chute.
 cut('118 right return stepped loss',[(1.65,68.25),(2.40,68.05),(2.62,68.35),(2.45,69.2),(1.65,69.45)],69.2,72.0,samplewalls)
 # Surviving short courses project into the large wound from solid masonry, breaking the continuous zigzag.
 tongues=[('upper right surviving course',[(4.15,65.18),(5.18,65.18),(5.18,65.60),(4.48,65.60),(4.43,65.48),(4.02,65.43)],73.1,75.19),('lower left surviving course',[(2.38,63.66),(3.50,63.66),(3.64,63.78),(3.48,64.04),(2.38,64.04)],73.1,75.10)]
 added=[]
 for label,outline,r0,r1 in tongues:
  ob=prism('118 '+label,outline,r0,r1,'wall','supported surviving masonry course');ob['damage_region']='117 connected panel and entablature loss';added.append(ob)
 # Small bite on the lower tongue exposes a rough joint end but leaves its left attachment intact.
 cut('118 lower course chipped end',[(3.35,63.45),(3.85,63.45),(3.85,64.25),(3.49,64.25),(3.44,64.05),(3.57,63.91),(3.38,63.84)],74.3,75.6,added)
 # Separate cavity-surface field for local crevice paint, measured against pre-recess116 surfaces.
 names=['COL110 Tower4 core','COL110 U4 sill wall','COL110 U4 fractured upper wall L','COL110 U4 fractured upper wall R']
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-116/scene.blend'),link=False)as(src,dst):dst.objects=list(names)
 def source_world(ob):return source_world(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis.copy()
 recess_counts=[]
 for name,source in zip(names,dst.objects):
  ob=C.objects.get(name)
  if not ob or not source:continue
  sw=source_world(source);surface=BVHTree.FromPolygons([sw@v.co for v in source.data.vertices],[tuple(f.vertices)for f in source.data.polygons]);me=ob.data;field=me.attributes.get('118 Recess interior')or me.attributes.new('118 Recess interior','FLOAT','FACE');count=0
  for face in me.polygons:
   center=ob.matrix_world@face.center;_,u,z=original(center);region=(-5.2<u<5.2 and 59.3<z<65.0)or(-7.4<u<-5.6 and 67.0<z<71.1);hit=surface.find_nearest(center);inside=region and hit and hit[0]is not None and hit[3]>.006;field.data[face.index].value=float(bool(inside));count+=bool(inside)
  recess_counts.append({'object':name,'recess_interior_faces':count})
 bpy.data.batch_remove(ids=[ob for ob in dst.objects if ob])
 result={'references':['UCL-01','UCL-02','DP-03'],'source':'117/geometry.blend','bay':4,'new_objects':len(new),'recess_face_mask':recess_counts,'zones':audit,'interior_cut_front_limit_authored_radius':73.15,'outer_front_radius':75,'preserves_outer_aperture':True,'surviving_courses':'Two short facing tongues embedded r73.1 into solid wound margins; no detached chunks','seconds_generation':time.time()-started}
 return result
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-117/geometry.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];audit=refine_sample(C);(O/'geometry-audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(json.dumps(audit))
 # Copy identical117 proof camera/world and isolate the same sample, preserving transform ancestors.
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-117/geometry-proof.blend'),link=False)as(src,dst):dst.scenes=[src.scenes[0]]
 ref=dst.scenes[0];camera_matrix=ref.camera.matrix_basis.copy();camera_data=ref.camera.data.copy();world=ref.world.copy();bpy.data.scenes.remove(ref)
 keep={o for o in C.objects if o.get('bay')==4}
 for ob in list(keep):
  while ob.parent:ob=ob.parent;keep.add(ob)
 keep.update(o for o in bpy.context.scene.objects if o.type in ['LIGHT','CAMERA']);bpy.data.batch_remove(ids=[o for o in list(bpy.context.scene.objects)if o not in keep]);scene=bpy.context.scene;scene.camera.matrix_world=camera_matrix;scene.camera.data=camera_data;scene.world=world;scene.render.resolution_x=1300;scene.render.resolution_y=1300;scene.render.resolution_percentage=100;scene.render.use_border=False;scene.render.use_crop_to_border=False;scene.render.use_freestyle=False;scene.render.filepath=str(O/'sample-painted.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry-proof.blend'))
 if os.environ.get('GEOMETRY_RENDER')=='1':
  bpy.ops.render.render(write_still=True);mat=bpy.data.materials.new('118 Neutral clay');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.45,.45,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
  for ob in C.objects:
   if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
  scene.render.filepath=str(O/'sample-clay.png');bpy.ops.render.render(write_still=True)
