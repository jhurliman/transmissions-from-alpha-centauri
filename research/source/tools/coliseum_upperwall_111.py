"""Sparse connected upper-wall masonry articulation grounded in UCL-01.
Continuous course, supported panel borders, three true upper apertures. No painted windows.
"""
import bpy,bmesh,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree

def articulate_upperwall(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;start=-math.pi;lean=Matrix.Rotation(math.radians(2),4,'X')
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(start+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted()
 def p(rr,aa,z):
  b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(aa),rr*b*math.sin(aa),z));return delta@Vector((v.x,cy+v.y,v.z))
 def mesh(name,vs,fs,role='detail',bay=-1):
  me=bpy.data.meshes.new('COL111 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL111 '+name,me);collection.objects.link(ob);ob['coliseum_role']=role;ob['tier']=3;ob['bay']=bay;return ob
 def box(name,aa,bb,z0,z1,r0,r1,role='detail',bay=-1):
  vs=[p(rr,ang,z) for z in [z0,z1] for rr in [r0,r1] for ang in [aa,bb]];return mesh(name,vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],role,bay)
 cuts=[]
 for j,z0,z1,w in [(4,67.5,70.3,1.42),(10,66.7,69.4,1.35),(14,66.2,68.25,1.12)]:
  ac=start+(j+.5)*step;outline=[(-w,z0),(-w,z1-.30),(-w+.24,z1),(w-.34,z1),(w,z1-.26),(w,z0)]
  vs=[p(rr,ac+u/rad,z) for rr in [rad-9,rad+1] for u,z in outline];N=len(outline);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
  cutter=mesh(f'U{j} upper aperture cutter',vs,fs,'detail');changed=[]
  for ob in list(collection.objects):
   if ob==cutter or ob.type!='MESH' or ob.get('bay')!=j or ob.get('tier')!=3 or ob.get('coliseum_role')!='wall':continue
   old=ob.data;ob.data=old.copy();before=len(old.vertices);mod=ob.modifiers.new('True upper masonry aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
   bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();after=len(bm.verts);bm.free()
   if bad or volume<=0:ob.data=old;continue
   if before!=after:ob['upper_aperture']=True;changed.append(ob.name)
   else:ob.data=old
  bpy.data.objects.remove(cutter,do_unlink=True);cuts.append({'bay':j,'changed':changed,'bottom':z0,'top':z1,'half_width':w})
 # Build support BVH after cuts; no detail may bridge missing masonry or protrude past a broken crown.
 vs=[];fs=[]
 for ob in collection.objects:
  if ob.type!='MESH' or ob.get('tier')!=3 or ob.get('coliseum_role')!='wall':continue
  offset=len(vs);vs +=[ob.matrix_world@v.co for v in ob.data.vertices];fs +=[tuple(offset+i for i in f.vertices)for f in ob.data.polygons]
 tree=BVHTree.FromPolygons(vs,fs)
 def supported(aa,z):
  origin=p(rad+3,aa,z);end=p(rad-.3,aa,z);hit=tree.ray_cast(origin,(end-origin).normalized(),(end-origin).length+.01)[0];return hit is not None
 added=[];omitted=0
 def safe_box(name,aa,bb,z0,z1,r0,r1,role='detail',bay=-1):
  nonlocal omitted
  if not all(supported(a,z)for a in [aa,(aa+bb)/2,bb]for z in [z0,(z0+z1)/2,z1]):omitted+=1;return
  added.append(box(name,aa,bb,z0,z1,r0,r1,role,bay))
 # Two restrained continuous stone courses connect large wallpanels below the high apertures.
 for j in range(18):
  for k in range(6):
   aa=start+(j+k/6)*step+.00012;bb=start+(j+(k+1)/6)*step-.00012
   safe_box(f'U{j} entablature footing{k}',aa,bb,65.05,65.31,rad-.08,rad+.34,'band',j)
   safe_box(f'U{j} entablature lip{k}',aa,bb,65.31,65.51,rad-.08,rad+.62,'band',j)
 # Sparse broad panel boundaries on surviving upper masses, joined to that course.
 for j in [3,4,5,9,10,11,14,15]:
  aa=start+(j+.065)*step
  for k in range(8):
   z0=65.51+k*.84;z1=z0+.84
   safe_box(f'U{j} upright panel border{k}',aa-.002,aa+.002,z0,z1,rad-.06,rad+.22,'detail',j)
 # Frame only the three genuine high openings, with strong sill and restrained stone jambs.
 for item in cuts:
  j=item['bay'];ac=start+(j+.5)*step;z0=item['bottom'];z1=item['top'];w=item['half_width']
  safe_box(f'U{j} high aperture sill',ac-(w+.24)/rad,ac+(w+.24)/rad,z0-.31,z0-.03,rad-.06,rad+.57,'band',j)
  safe_box(f'U{j} high aperture lintel',ac-(w+.19)/rad,ac+(w+.19)/rad,z1+.025,z1+.32,rad-.06,rad+.33,'arch_molding',j)
  for sign in [-1,1]:
   aa=ac+sign*(w+.14)/rad
   safe_box(f'U{j} high aperture jamb{sign}',aa-.10/rad,aa+.10/rad,z0+.05,z1-.05,rad-.06,rad+.31,'arch_molding',j)
 return {'reference':'UCL-01','true_upper_apertures':cuts,'new_supported_masonry_parts':len(added),'unsupported_segments_omitted':omitted,'support_check':'9 native ray tests per detail part against surviving upperwall','no_projected_art':True}
