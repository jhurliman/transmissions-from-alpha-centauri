"""Optional localized upper-wall details; operates on supplied native110collection.
Evidence UCL-01: sparse worn aperture surrounds and connected damage near crown losses.
No broad noise, painted planes, texture images, or rear construction.
"""
import bpy,math,bmesh
from mathutils import Matrix,Vector

def add_damage_details(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;lean=Matrix.Rotation(math.radians(2),4,'X');start=-math.pi
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 a=start+(4+.5)*step;auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(a,4,'Z');delta=anchor.matrix_world@auth.inverted()
 def p(rr,aa,z):
  b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(aa),rr*b*math.sin(aa),z));return delta@Vector((v.x,cy+v.y,v.z))
 def mesh(name,vs,fs,role='detail'):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL110 '+name,me);collection.objects.link(ob);ob['coliseum_role']=role;ob['tier']=3;ob['bay']=-1;return ob
 def box(name,aa,bb,z0,z1,r0,r1,role='detail'):
  vs=[p(rr,ang,z) for z in [z0,z1] for rr in [r0,r1] for ang in [aa,bb]];return mesh(name,vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],role)
 added=[];cuts=[]
 # A few visibly worn individual aperture surrounds; substantial quiet walls remain.
 for j in [3,5,8,10,14]:
  a=start+(j+.5)*step;sw=step*.08;z0=62.56;z1=64.76
  added.append(box(f'U{j} weathered projecting aperture sill',a-sw-.004,a+sw+.004,z0-.20,z0+.12,rad-.08,rad+.48,'band'))
  # Unequal paired lintel fragments preserve localized losses, not regular intact bright frames.
  added.append(box(f'U{j} surviving aperture lintel left',a-sw-.003,a+.001,z1-.07,z1+.30,rad-.06,rad+.25,'detail'))
  if j in [3,10]:added.append(box(f'U{j} surviving aperture lintel right',a+.004,a+sw+.002,z1-.07,z1+.24,rad-.06,rad+.19,'detail'))
  for sign in [-1,1]:
   aa=a+sign*(sw+.002)
   # Not every stone survives to full opening height.
   zz=z0+.18 if (j+sign)%3 else z0+.72
   added.append(box(f'U{j} aperture reveal cheek{sign}',aa-.0018,aa+.0018,zz,z1-.05,rad-.05,rad+.22,'arch_molding'))
 # Narrow true recessed fracture paths branch from three crown losses.
 for j,ztop,zbottom in [(5,76.4,68.0),(9,74.4,66.2),(14,72.4,65.8)]:
  target=next(o for o in collection.objects if o.get('bay')==j and 'fractured upper wall L' in o.name)
  target.data=target.data.copy() # Never modify another linked kit instance.
  vals=[(.18,ztop,.16),(.17,ztop-1.6,.13),(.22,ztop-2.7,.12),(.205,ztop-4.0,.085),(.24,zbottom,.025)]
  vs=[]
  for rr in [rad-.42,rad+.28]:
   for frac,z,w in vals:
    aa=start+j*step+frac*step;vs.extend([p(rr,aa-w/rad,z),p(rr,aa+w/rad,z)])
  N=len(vals);L=2*N;fs=[]
  for k in range(N-1):
   q=2*k;fs +=[(q,q+2,q+3,q+1),(L+q,L+q+1,L+q+3,L+q+2),(q,L+q,L+q+2,q+2),(q+1,q+3,L+q+3,L+q+1)]
  fs +=[(0,1,L+1,L),(L-2,2*L-2,2*L-1,L-1)]
  cutter=mesh(f'U{j} fracture cutter',vs,fs,'fracture');modifier=target.modifiers.new('Native shallow crown fracture','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
  bpy.context.view_layer.objects.active=target;target.select_set(True)
  bpy.ops.object.modifier_apply(modifier=modifier.name);target.select_set(False);bpy.data.objects.remove(cutter,do_unlink=True);target['localized_damage']='shallow crown-connected geometric recess';cuts.append(target.name)
 return {'added_aperture_parts':len(added),'native_recess_paths':cuts,'reference':'UCL-01','preserves_rear_open':True,'projected_artwork':False}
