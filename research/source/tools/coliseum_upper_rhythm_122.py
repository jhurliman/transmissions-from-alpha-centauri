"""UCL01/UCL02/DP03: representative upper-wall masonry bay, authored through approved E warp."""
import bpy,bmesh,math,json,sys,os,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122/rhythm';O.mkdir(parents=True,exist_ok=True)
def build_rhythm(C,j,spec):
 started=time.time();anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_basis@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P;Fi=F.inverted();ac=-math.pi+(j+.5)*math.tau/36;zones=[(0,64,6,8)];new=[];changed=[];audit=[]
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
  me=bpy.data.meshes.new('COL122 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL122 '+name,me);C.objects.link(ob);ob['bay']=j;ob['tier']=3;ob['coliseum_role']=role;ob['feature']=feature
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
     # Rising broken return follows a plausible oblique failure through the deep wall.
     rise=4.2*(max(0,(75-rr)/(75-back))) if 'upper breach' in name else 0
     vs.append(p(rr,uc+(u-uc)*scale+du,zc+(z-zc)*scale+dz+rise))
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
   elif 'panel'in label or 'niche'in label:
    tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in old.vertices],[tuple(f.vertices)for f in old.polygons]);field=ob.data.attributes.get('118 Recess interior')or ob.data.attributes.new('118 Recess interior','FLOAT','FACE')
    for face in ob.data.polygons:
     hit=tree.find_nearest(ob.matrix_world@face.center);field.data[face.index].value=float(field.data[face.index].value>.5 or bool(hit and hit[0]is not None and hit[3]>.004))
   if 'drainage'in label:
    oldsurface=BVHTree.FromPolygons([ob.matrix_world@v.co for v in old.vertices],[tuple(f.vertices)for f in old.polygons]);mask=ob.data.attributes.get('122 Drain interior')or ob.data.attributes.new('122 Drain interior','FLOAT','FACE')
    for face in ob.data.polygons:
     near=oldsurface.find_nearest(ob.matrix_world@face.center);mask.data[face.index].value=float(near and near[0]is not None and near[3]>.004)
   attrs(ob);changed.append(ob);rows.append({'object':ob.name,'vertices_before':before[0],'vertices_after':after[0],'nonmanifold_edges':bad,'volume':volume,'outside_cutter_max_error_m':outside_error})
  bpy.data.objects.remove(cutter,do_unlink=True);audit.append({'zone':label,'changes':rows})
 wall=lambda:[o for o in C.objects if o.type=='MESH'and o.get('bay')==j and o.get('tier')==3 and o.get('coliseum_role')=='wall']


 # Uniform low drainage row: clipped-corner squat mouth with a true closed-end tunnel.
 u=0;z0=60.25;z1=60.83;hw=.525;ch=.085
 drain=[(-hw,z0),(hw,z0),(hw,z1-ch),(hw-ch,z1),(-hw+ch,z1),(-hw,z1-ch)]
 targets=[o for o in wall()if 'sill wall'in o.name]
 cut('122 bay%d drainage niche'%j,drain,73.6,75.20,targets)
 for ob in changed:ob['122 cavity depth authored']=1.4;ob['122 cavity family']='lower shelf drainage'
 # The existing slim field jambs stay in place; solid lower-third bodies deepen their profile.
 verts=[];faces=[]
 for ob in wall():
  off=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend(tuple(off+i for i in f.vertices)for f in ob.data.polygons)
 support=BVHTree.FromPolygons(verts,faces);omitted=[]
 def supports(u,z):
  a=p(78,u,z);b=p(73.8,u,z);return support.ray_cast(a,(b-a).normalized(),(b-a).length)[0]is not None
 if spec:
  left,right=spec['fields_u0_u1_z0_z1'];w=.12 if spec['family']=='low_intact'else .16
  columns=[(left[0]-w/2,left[2]-.1,left[3]+w),(right[1]+w/2,right[2]-.1,right[3]+w)]
 elif j==8:columns=[(-5.0,59.5,65.0),(5.13,59.5,68.0)]
 else:columns=[(-5.3,59.5,68.6),(5.3,59.5,68.6)]
 column_reports=[]
 for idx,(u,z0,z1)in enumerate(columns):
  z0=59.32
  # Clip proposed height down to the actual continuous surviving wall.
  validtop=z0
  for k in range(max(1,math.ceil((z1-z0)/.25))):
   zz=min(z1,z0+(k+1)*.25)
   if not all(supports(uu,zz)for uu in [u-.14,u,u+.14]):break
   validtop=zz
  z1=validtop
  if z1-z0<1.8:omitted.append({'column':idx,'reason':'insufficient continuous wall'});continue
  stepz=z0+(z1-z0)/3
  # Existing bay8 columns are wider; other columns align with existing field jambs.
  half=.16 if j==8 else .12
  if not all(supports(uu,zz)for uu in [u-half,u,u+half]for zz in [z0+.10,(z0+stepz)/2,stepz]):omitted.append({'column':idx,'reason':'lower-body rear support absent'});continue
  lower=prism('bay%d pilaster%d deep lower third'%(j,idx),[(u-half*1.25,z0),(u+half*1.25,z0),(u+half,stepz),(u-half,stepz)],74.84,75.72,'detail','stepped pilaster lower third');lower['122 depth authored']=.72;lower['122 segment']='lower third'
  # Only bay10 lacks the accepted121 paired field jambs; add matching shallow upper bodies there.
  if j in [5,10,13]:
   upper=box('bay%d pilaster%d shallow upper two thirds'%(j,idx),u-half,u+half,stepz,z1,74.9,75.23,'detail','stepped pilaster upper two thirds');upper['122 depth authored']=.23;upper['122 segment']='upper two thirds'
  column_reports.append({'u':u,'bottom':z0,'step_height':stepz,'top':z1,'lower_projection':.72,'upper_projection_existing':.39 if j==8 else .18,'new_shallow_upper':j in[5,10,13]})
 return list(set(new+changed)),{'bay':j,'drainage':{'center_u':0,'bottom':60.25,'top':60.83,'width':1.05,'recess_depth':1.4,'closed_tunnel_back':True},'cuts':audit,'columns':column_reports,'omitted':omitted,'new_objects':[o.name for o in new],'changed_objects':sorted(set(o.name for o in changed)),'weathering_regions_original_world':[{'name':'bay%d drain lintel'%j,'center':list(original(p(75,0,60.85))[0]),'radius':.4,'runoff_length':1.1}],'seconds':time.time()-started}
def apply(C):
 plan=json.loads((R/'art/studies/coliseum-119/assembly-feature-plan.json').read_text());objects=[];reports=[]
 for j in range(5,14):
  spec=next((x for x in plan['bays']if x['bay']==j),None);parts,report=build_rhythm(C,j,spec);objects+=parts;reports.append(report)
 return list(set(objects)),{'reference_ids':['UCL-08','UCL-01','UCL-03'],'source':'121 native scene','grammar':'One centered squat drainage tunnel per bay at a shared shelf elevation, paired pilasters whose lower third projects deeper than their upper two thirds. Existing panels retained.','bay_reports':reports,'weathering_regions_original_world':[v for r in reports for v in r['weathering_regions_original_world']]}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-121/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];parts,audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print(json.dumps(audit))
