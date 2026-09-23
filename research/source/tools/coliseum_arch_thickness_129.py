"""UCL-01/UCL-02/DP-03: thicken two-ring masonry profile inward, outer contour fixed."""
import bpy,math,sys,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-129/arches';sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology
H=75*math.tau/36*.34;OUTER=.83

def params(t,b):
 sw,sh=(1.,1.)if(t,b)==(2,10)else(.8,.95)
 base=2.73+t*18.33+.35;spring=2.73+(t+1)*18.33-2.184-H
 return H*sw,H*sh,base+sh*(spring-base)
def closest(u,v,rx,rz):
 # Orthogonal projection onto upper ellipse; normal-offset source profile.
 th=max(0.,min(math.pi,math.atan2(max(0.,v)/rz,u/rx)))
 for _ in range(16):
  c,s=math.cos(th),math.sin(th);ex,ey=rx*c,rz*s;tx,ty=-rx*s,rz*c
  f=(ex-u)*tx+(ey-v)*ty;df=tx*tx+ty*ty+(ex-u)*(-rx*c)+(ey-v)*(-rz*s)
  if abs(df)<1e-10:break
  q=max(0.,min(math.pi,th-f/df))
  if abs(q-th)<1e-11:th=q;break
  th=q
 c,s=math.cos(th),math.sin(th);nx,ny=c/rx,s/rz;ln=math.hypot(nx,ny);nx/=ln;ny/=ln
 return (u-rx*c)*nx+(v-rz*s)*ny,nx,ny

def apply(C,factor=1.75):
 original,world,unpack=mapping();rows=[];maxouter=0.;delta=(factor-1)*(.83+.03);walls=[o for o in C.objects if o.name.startswith('COL127 T')and'continuous arcade wall'in o.name];parts=[o for o in C.objects if o.type=='MESH'and any(q in o.name for q in [' archivolt',' jamb ',' impost '])and o.get('tier')in [0,1,2]]
 if any(ob.get('129 profile thickness factor')for ob in walls+parts):raise RuntimeError('Apply once to fresh128 geometry')
 for ob in walls+parts:
  old=ob.data;iswall=ob in walls;t=int(ob['tier']);before=topology(ob);me=old.copy();ob.data=me;iv=ob.matrix_world.inverted();at=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');moves=0;peak=0.;outerchange=0.
  for ve in me.vertices:
   rr,a,z=unpack(ob.matrix_world@ve.co);b=min(17,max(0,int((a+math.pi)/(math.tau/36))))if iswall else int(ob['bay']);ac=-math.pi+(b+.5)*math.tau/36;u=(a-ac)*75;rx,rz,sp=params(t,b);v=z-sp
   if iswall and z<2.73+t*18.33+.35-.0001:continue
   if v>=0:d,nx,ny=closest(u,v,rx,rz)
   else:d,nx,ny=abs(u)-rx,math.copysign(1.,u),0.
   if abs(d-OUTER)<.002:continue
   if iswall:
    amount=delta*max(0.,min(1.,1-d/OUTER))
   else:
    amount=(factor-1)*max(0.,OUTER-d)
   if amount<1e-6:continue
   uu=u-amount*nx;zz=z-amount*ny;new=iv@world(rr,ac+uu/75,zz);dist=(new-ve.co).length;peak=max(peak,dist)
   if abs(d-OUTER)<.0001:outerchange=max(outerchange,dist)
   ve.co=new;at.data[ve.index].vector=original(rr,ac+uu/75,zz);moves+=1
  me.update()
  # Curved outer masonry remains analytically smooth; returns remain real hard faces.
  if iswall:
   normals=[]
   for p in me.polygons:
    front=all(abs(unpack(ob.matrix_world@me.vertices[i].co)[0]-75)<.001 for i in p.vertices);p.use_smooth=front
    for i in p.vertices:
     if front:
      rr,a,z=unpack(ob.matrix_world@me.vertices[i].co);da=world(rr,a+.0001,z)-world(rr,a-.0001,z);dz=world(rr,a,z+.01)-world(rr,a,z-.01);normal=da.cross(dz).normalized()
      if normal.dot(p.normal)<0:normal=-normal
      normals.append(normal)
     else:normals.append(p.normal.copy())
   me.normals_split_custom_set(normals);after=topology(ob)
   if after['nonmanifold']or after['strict_crossings']>before['strict_crossings']:
    ob.data=old;raise RuntimeError('Unsafe wall deformation '+ob.name+str(after))
  else:
   after=topology(ob)
   if after['nonmanifold']>before['nonmanifold']or after['strict_crossings']>before['strict_crossings']:
    ob.data=old;raise RuntimeError('Unsafe profile deformation '+ob.name+str(after))
  ob['129 profile thickness factor']=factor;rows.append({'name':ob.name,'moved_vertices':moves,'max_displacement_world':peak,'outer_contour_max_change':outerchange,'before':before,'after':after})
 return {'factor':factor,'inner_curve_inset_authored':delta,'profile':'Combined two-ring normal profile scales inward around fixed outermost0.83 offset; ring gap scales with profile','walls_and_parts':rows,'bay_count':54,'B10':'Earlier circular opening retained as source; same inward inset applied','platforms_and_depth':'Fixed; actual wall opening boundary shrunk; radial depth coordinates unchanged'}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));from coliseum_b10_prepared_128 import apply as repair
 repair(bpy.data.collections['110 Coliseum detailed front ruin']);a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('ARCH129',len(a['walls_and_parts']))
