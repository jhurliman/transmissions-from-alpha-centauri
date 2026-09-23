"""Native111 crown silhouette + engaged tower hierarchy. UCL-01 primary architecture,
DP-03 large/small structural layers and UX-01 distance readability. No reference projection.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix

def upgrade_structure(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;start=-math.pi;lean=Matrix.Rotation(math.radians(2),4,'X')
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(start+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted()
 def p(rr,aa,z):
  b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(aa),rr*b*math.sin(aa),z));return delta@Vector((v.x,cy+v.y,v.z))
 def mesh(name,vs,fs,role='tower',bay=-1):
  me=bpy.data.meshes.new('COL111 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL111 '+name,me);collection.objects.link(ob);ob['coliseum_role']=role;ob['tier']=-1;ob['bay']=bay;return ob
 def band(name,ri,ro,z0,z1,a0,a1,n=6,role='band',bay=-1):
  L=n+1;vs=[p(rr,a0+(a1-a0)*k/n,z) for z in [z0,z1] for rr in [ri,ro] for k in range(L)];fs=[]
  for k in range(n):fs.extend([(k,k+1,L+k+1,L+k),(2*L+k,3*L+k,3*L+k+1,2*L+k+1),(k,2*L+k,2*L+k+1,k+1),(L+k,L+k+1,3*L+k+1,3*L+k)])
  fs.extend([(0,L,3*L,2*L),(n,2*L+n,3*L+n,L+n)]);return mesh(name,vs,fs,role,bay)
 def crowncut(label,samples,bays):
  # One connected fracture silhouette removes masonry above a jagged profile.
  L=len(samples);vs=[]
  for rr in [rad-9.2,rad+1.65]:
   for q,z in samples:vs.extend([p(rr,start+q*step,z),p(rr,start+q*step,86)])
  N=2*L;fs=[]
  for k in range(L-1):
   q=2*k;fs.extend([(q,q+2,q+3,q+1),(N+q,N+q+1,N+q+3,N+q+2),(q,N+q,N+q+2,q+2),(q+1,q+3,N+q+3,N+q+1)])
  fs.extend([(0,1,N+1,N),(N-2,2*N-2,2*N-1,N-1)]);cut=mesh(label+' cutter',vs,fs,'fracture');changed=[]
  for ob in list(collection.objects):
   if ob==cut or ob.type!='MESH' or ob.get('tier')!=3 or ob.get('bay') not in bays:continue
   ca=[cut.matrix_world@Vector(v) for v in cut.bound_box];oa=[ob.matrix_world@Vector(v) for v in ob.bound_box]
   if any(max(v[k] for v in ca)<min(v[k] for v in oa) or max(v[k] for v in oa)<min(v[k] for v in ca) for k in range(3)):continue
   old=ob.data;before=len(old.vertices);ob.data=old.copy();mod=ob.modifiers.new('111 connected full thickness crown loss','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
   bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();after=len(bm.verts);bm.free()
   if bad or (after and volume<=0):ob.data=old;continue
   if not after:changed.append({'object':ob.name,'removed':True});bpy.data.objects.remove(ob,do_unlink=True);continue
   if after!=before:ob['localized_breakage']=label;changed.append({'object':ob.name,'vertices':after,'nonmanifold':bad})
   else:ob.data=old
  bpy.data.objects.remove(cut,do_unlink=True);return changed
 # Large intact upper masses remain, but their edges expose uneven fracture returns.
 zones=[]
 profiles=[('left stepped masonry crown',[(3.0,74.2),(3.50,74.2),(3.52,73.6),(3.57,73.9),(3.62,72.1),(3.68,72.3),(3.85,72.3),(3.88,74.7),(4.35,74.7),(4.40,73.8),(4.46,74.2),(4.50,72.6),(4.78,72.6),(4.82,74.3),(5.18,74.3),(5.20,72.7),(5.26,73.0),(5.30,70.8),(5.45,70.8),(5.47,69.7),(5.54,70.0),(5.59,68.4),(6.0,68.4)],list(range(3,7))),
 ('center architectural stepped breach',[(9,73.3),(9.43,73.3),(9.45,71.9),(9.51,72.2),(9.56,70.6),(9.74,70.6),(9.77,73.0),(10.28,73.0),(10.30,72.4),(10.36,72.7),(10.40,71.5),(10.58,71.5),(10.61,73.1),(11.05,73.1),(11.08,71.2),(11.15,71.5),(11.19,69.4),(11.48,69.4),(11.52,67.4),(11.59,67.8),(11.65,66.5),(12,66.5)],list(range(9,13))),
 ('right surviving horizontal courses',[(14,71.1),(14.36,71.1),(14.39,70.2),(14.45,70.6),(14.49,68.7),(14.67,68.7),(14.70,71.0),(15.10,71.0),(15.13,70.1),(15.19,70.4),(15.23,68.9),(15.49,68.9),(15.52,70.1),(15.78,70.1),(15.81,68.6),(15.87,68.9),(15.92,68.2),(16,68.2)],list(range(14,17)))]
 for label,samples,bays in profiles:zones.append({'zone':label,'changed':crowncut(label,samples,bays)})
 # Engage tall shafts with strong tier collars and depth-changing paired ribs.
 removed=[];added=[]
 for j in [1,4,7,10,13,16]:
  aa=start+j*step;w=step*.19
  for ob in list(collection.objects):
   if ob.get('bay')==j and ob.name.startswith('COL110 Tower') and ('flanking rib' in ob.name or any(f'collar{z:.1f}' in ob.name for z in [20.8,39.1,57.5])):
    removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
  for tier,z in enumerate([20.8,39.1,57.5]):
   # Broad shadow-bearing capital and split lip at every structural floor.
   profile=[(-1.0,.46,3.55,1.18),(-.54,.66,4.08,1.32),(.12,.70,4.70,1.47),(.82,.40,4.18,1.35),(1.22,.27,4.47,1.42)]
   for k,(dz,hh,rr,ww) in enumerate(profile):added.append(band(f'Tower{j} tier{tier} stepped belt{k}',rad-2.12,rad+rr,z+dz,z+dz+hh,aa-w*ww,aa+w*ww,bay=j))
  # Tall panel is now physically inset between tier-specific deep ribs.
  top={1:75.5,4:80,7:76.5,10:79,13:74,16:71}[j]
  for tier,(z0,z1) in enumerate([(3.7,19.8),(22.29,38.1),(40.59,56.5),(58.99,top-2.5)]):
   for sign in [-1,1]:
    ca=aa+sign*w*.72;half=w*.155
    ribtop=min(z1,74.7) if j==10 and tier==3 and sign==1 else z1
    added.append(band(f'Tower{j} tier{tier} projecting shaft rib{sign}',rad+2.65,rad+3.85,z0,ribtop,ca-half,ca+half,3,'tower',j))
    added.append(band(f'Tower{j} tier{tier} rib base{sign}',rad+2.65,rad+4.02,z0,z0+.55,ca-half*1.30,ca+half*1.30,3,'band',j))
    added.append(band(f'Tower{j} tier{tier} rib shoulder{sign}',rad+2.65,rad+4.09,ribtop-.65,ribtop,ca-half*1.36,ca+half*1.36,3,'band',j))
 checks=[]
 for ob in added:
  bm=bmesh.new();bm.from_mesh(ob.data);checks.append(sum(not e.is_manifold for e in bm.edges));bm.free()
 from bpy_extras.object_utils import world_to_camera_view
 projection=[];scene=bpy.context.scene
 for j in [4,7,10,13]:
  aa=start+j*step;w=step*.19;zz=39.55
  def width(half,front):
   xs=[world_to_camera_view(scene,scene.camera,p(rr,a,zz)).x for rr in [rad-2.12,front] for a in [aa-half,aa+half]]
   return (max(xs)-min(xs))*scene.render.resolution_x
  core=width(w,rad+2.8);collar=width(w*1.47,rad+4.7);projection.append({'tower':j,'core_pixels':core,'collar_pixels':collar,'ratio':collar/core})
 return {'projected_collar_widths':projection,'reference_ids':['UCL-01','DP-03','UX-01'],'crown_zones':zones,'removed_tower_parts':len(removed),'new_tower_parts':len(added),'nonmanifold_new_parts':sum(n>0 for n in checks),'collar_max_width_ratio_to_core':1.47,'crown_profile':'horizontal courses with abrupt broken steps and short fracture facets','native_geometry_only':True,'preserved_camera':True}
