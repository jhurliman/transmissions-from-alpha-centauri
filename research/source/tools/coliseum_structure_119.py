"""UCL01/UCL02/DP03: representative upper-wall masonry bay, authored through approved E warp."""
import bpy,bmesh,math,json,sys,os,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-119';O.mkdir(parents=True,exist_ok=True)
def build_visible_bay(C):
 started=time.time();anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_basis@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P;Fi=F.inverted();j=8;ac=-math.pi+(j+.5)*math.tau/36;zones=[(3.55,65.0,2.0,2.1),(4.65,62.9,1.0,1.8)];new=[];changed=[];audit=[]
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
  me=bpy.data.meshes.new('COL119 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL119 '+name,me);C.objects.link(ob);ob['bay']=j;ob['tier']=3;ob['coliseum_role']=role;ob['feature']=feature
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
   attrs(ob);changed.append(ob);rows.append({'object':ob.name,'vertices_before':before[0],'vertices_after':after[0],'nonmanifold_edges':bad,'volume':volume,'outside_cutter_max_error_m':outside_error})
  bpy.data.objects.remove(cutter,do_unlink=True);audit.append({'zone':label,'changes':rows})
 wall=lambda:[o for o in C.objects if o.type=='MESH'and o.get('bay')==j and o.get('tier')==3 and o.get('coliseum_role')=='wall']
 # Bay8's left crown is low67m, right crown rises to74m. The breach stays entirely below that inherited contour.
 breach=[(2.32,64.10),(2.48,63.65),(3.22,63.65),(3.43,63.43),(4.14,63.57),(4.47,63.94),(4.72,64.10),(4.70,64.73),(4.43,64.95),(4.61,65.54),(4.03,65.89),(3.78,66.12),(3.09,65.98),(2.85,65.63),(2.27,65.45),(2.40,64.88)]
 all_upper=lambda:[o for o in C.objects if o.type=='MESH'and o.get('bay')==j and o.get('tier')==3]
 cut('119 bay8 upper breach',breach,66,77,all_upper())
 # Different width/depth broken interior courses, never a repeated stair pattern.
 cut('119 short rear ledge loss',[(2.8,63.65),(3.0,63.44),(3.92,63.52),(4.0,64.35),(2.8,64.35)],67.0,69.4,wall())
 cut('119 offset middle ledge loss',[(3.25,63.55),(4.18,63.42),(4.26,63.95),(3.25,64.1)],70.2,72.9,wall())
 # Shallow true framed fields retain broad quiet masonry between the old aperture and new breach.
 for label,u0,u1,z0,z1 in [('left recessed panel',-4.75,-1.72,60.0,64.7),('right lower recessed panel',1.72,5.0,60.0,62.85)]:cut('119 '+label,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],74.58,75.14,wall())
 nichecenter=-3.25;niche=[(nichecenter-.57,60.72),(nichecenter+.57,60.72),(nichecenter+.57,62.08)]+[(nichecenter+.57*math.cos(a),62.08+.57*math.sin(a))for a in [math.pi*k/10 for k in range(1,11)]]
 cut('119 left blind arched niche',niche,73.94,75.16,wall())
 # Support-qualified thin pilasters and course framing follow the current local silhouette.
 verts=[];faces=[]
 for ob in wall():
  off=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices);faces.extend(tuple(off+i for i in face.vertices)for face in ob.data.polygons)
 support=BVHTree.FromPolygons(verts,faces);omitted=0
 def supports(u,z):
  a=p(78,u,z);b=p(73.8,u,z);return support.ray_cast(a,(b-a).normalized(),(b-a).length)[0]is not None
 def safe(label,u0,u1,z0,z1,r0,r1,role='detail'):
  nonlocal omitted
  if not all(supports(u,z)for u in [u0,(u0+u1)/2,u1]for z in [z0,(z0+z1)/2,z1]):omitted+=1;return
  return box(label,u0,u1,z0,z1,r0,r1,role,'supported panel frame')
 for u in [-5.0,5.13]:
  for k in range(12):safe('bay8 slender pilaster %.2f %d'%(u,k),u-.16,u+.16,59.45+k*.97,60.42+k*.97,74.86,75.39)
 for z in [59.58,64.94]:
  for k in range(10):safe('bay8 inset field course %.2f %d'%(z,k),-4.86+k*.986,-3.874+k*.986,z,z+.22,74.89,75.38,'band')
 safe('bay8 niche sill',-4.05,-2.45,60.46,60.7,74.84,75.46,'band')
 for k in range(7):
  a=k*math.pi/7;b=(k+1)*math.pi/7;outline=[(nichecenter+.68*math.cos(a),62.08+.68*math.sin(a)),(nichecenter+.68*math.cos(b),62.08+.68*math.sin(b)),(nichecenter+.85*math.cos(b),62.08+.85*math.sin(b)),(nichecenter+.85*math.cos(a),62.08+.85*math.sin(a))]
  if all(supports(u,z)for u,z in outline):prism('bay8 niche archivolt%d'%k,outline,74.88,75.36,'arch_molding','blind niche surround')
 # Local face failure touches the breach footing and interrupts the right field border without a long zigzag stripe.
 loss=[(4.1,63.4),(4.43,63.55),(4.92,63.12),(5.03,62.66),(4.74,62.45),(4.88,61.96),(4.39,61.76),(4.04,62.20),(4.27,62.67)]
 cut('119 bay8 connected field loss',loss,73.92,77,all_upper())
 # Remove near-zero-volume entablature scraps that bridge the broken opening.
 for name in ['COL111 U8 entablature footing4','COL111 U8 entablature lip4']:
  ob=bpy.data.objects.get(name)
  if ob:bpy.data.objects.remove(ob,do_unlink=True)
 result={'references':['UCL-01','UCL-02','DP-03'],'source':'116/scene.blend','bay':8,'new_objects':len(new),'support_omitted':omitted,'zones':audit,'weathering_regions_original_world':[{'name':'bay8 breach','center':list(original(p(75,3.55,65.0))[0]),'radius':1.6,'runoff_length':3.6},{'name':'bay8 field loss','center':list(original(p(75,4.65,62.9))[0]),'radius':1.15,'runoff_length':2.2}],'crown_preservation':'Front aperture remains below authored z66.12. Rear fracture tunnel rises4.2m into wall thickness to expose sky from actual low camera; front crown geometry is preserved; a small rear crown edge loss is allowed, and original meshes are not regenerated.','interior_ledges':'Two unequal offset pockets at radial67–69.4 and70.2–72.9, different widths, beneath irregular breach','seconds_generation':time.time()-started}
 return result
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];audit=build_visible_bay(C);(O/'geometry-audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(json.dumps(audit))
 if os.environ.get('GEOMETRY_RENDER')=='1':
  scene=bpy.context.scene;scene.render.use_freestyle=True;scene.render.resolution_x=1440;scene.render.resolution_y=1082;scene.render.resolution_percentage=100;scene.render.filepath=str(O/'main-geometry.png')
  for ob in bpy.data.objects:
   if 'Landmark contact ink'in ob.name:ob.hide_render=True
  bpy.ops.render.render(write_still=True)
 # Local geometry view, same main-facing direction, no change to integratedcamera.
 keep={o for o in C.objects if o.get('bay')==8}
 for ob in list(keep):
  while ob.parent:ob=ob.parent;keep.add(ob)
 keep.update(o for o in bpy.context.scene.objects if o.type in ['LIGHT','CAMERA']);bpy.data.batch_remove(ids=[o for o in list(bpy.context.scene.objects)if o not in keep]);scene=bpy.context.scene;points=[o.matrix_world@v.co for o in C.objects if o.type=='MESH'for v in o.data.vertices];points=[p for p in points if p.z>36];lo=Vector(tuple(min(p[k]for p in points)for k in range(3)));hi=Vector(tuple(max(p[k]for p in points)for k in range(3)));center=(lo+hi)/2;camera=scene.camera;camera.location=center+Vector((0,-1,.04)).normalized()*100;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=max(hi.z-lo.z,(hi.x-lo.x)*1.1)*1.15;scene.render.use_freestyle=False;scene.render.resolution_x=1300;scene.render.resolution_y=1300;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('119 Neutral proof');scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.23,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.65;bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry-proof.blend'))
 if os.environ.get('GEOMETRY_RENDER')=='1':
  scene.render.filepath=str(O/'sample-painted.png');bpy.ops.render.render(write_still=True);mat=bpy.data.materials.new('119 Neutral clay');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.45,.45,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
  for ob in C.objects:
   if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
  scene.render.filepath=str(O/'sample-clay.png');bpy.ops.render.render(write_still=True)
