import bpy,math,random,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-003';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-002/xenon-blockout-v2.blend'))
s=bpy.context.scene;random.seed(83)
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in a)
def mat(name,h):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb(h),1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*rgb(h),1);m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
ink=mat('Ink recess','2e2937');stone=mat('Dust gray lavender','776d7a');edge=mat('Exposed rust planes','a17460');dim=mat('Deep violet structures','464253');rust=mat('Dome shadow skeleton','79524f');dust=mat('Distant dust','a78383');earth=mat('Clay ground muted','6d4b40');dark=mat('Foreground ink violet','302b39')
active=bpy.data.collections.new('08 Architectural refinement');s.collection.children.link(active)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);active.objects.link(o);o.data.materials.append(m);return o
def box(name,loc,size,m):
 x,y,z=loc;a,b,c=[v/2 for v in size];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 o=mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m);o.data.materials.append(ink);o.data.materials.append(edge)
 for p in o.data.polygons:
  if p.normal.z>.5:p.material_index=2
  elif p.normal.x>.5:p.material_index=1
 return o
def beam(name,a,b,width,depth,m):
 d=Vector(b)-Vector(a);o=box(name,(0,0,0),(width,depth,d.length),m);o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def line(name,points,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.resolution_u=1;cu.bevel_resolution=0;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,cu);active.objects.link(o);o.data.materials.append(m);return o
# Selective panel rhythm on the two major facades: different treatments by side.
for sign in [-1,1]:
 for yi,y in enumerate([-4,0,4,8,12,17,22]):
  x=sign*(7.68 if sign>0 else 7.94)
  for zi,z in enumerate([1.6,5.7,10.1,14.6]):
   if (yi+zi)%5==0:continue
   length=2.5 if yi%2 else 3.0
   box('Recess behind broken cladding',(x,y,z),(.045,length,2.4),ink)
   # Uneven cladding fragments keep large areas quiet between joints.
   width=length*(.38 if (yi+zi)%3==0 else .78)
   box('Remaining wall panel',(x-sign*.07,y-.2,z+.28),(.12,width,1.62),stone if sign<0 else dim)
   if zi<3 and yi%2==0:
    line('Panel fracture',[(x-sign*.145,y-.9,z+.9),(x-sign*.146,y-.7,z+.55),(x-sign*.146,y-.83,z+.26),(x-sign*.146,y-.51,z-.17)],.018,ink)
# Break silhouettes of the rear building blocks into stepped, leaning remnants.
for o in list(bpy.data.objects):
 if o.name.startswith(('Left architectural mass 03','Right architectural mass 03')):
  o.scale.z=.63;o.location.z*=.63
for sign in [-1,1]:
 for i,y in enumerate([20,23,27,30]):
  h=[15,12,10,7][i]+(1.5 if sign>0 else 0)
  b=box('Broken skyline remnant',(sign*(7.8+random.uniform(-.6,.7)),y,h/2),(random.uniform(.5,1.2),1.4,h),dim);b.rotation_euler.y=sign*random.uniform(-.07,.07)
  beam('Exposed skyline spar',(sign*7.8,y,h-.5),(sign*7.6,y+.55,h+1.4),.13,.13,ink)
# Deliberate X bracing and suspended service cable visible on left.
for y in [5,13]:
 beam('Left exposed diagonal',(-7.7,y-1.4,4.3),(-7.7,y+1.4,8.0),.13,.18,ink)
 beam('Left exposed diagonal',(-7.7,y+1.4,4.3),(-7.7,y-1.4,8.0),.13,.18,ink)
line('Sagging cable under canopy',[(-6.6,-3,4.9),(-6.5,-2.3,4.2),(-6.5,-1.3,3.95),(-6.55,0,4.25),(-6.6,1,4.9)],.045,ink)
# Dome now uses a dark inner volume and detached plates over a continuous open skeleton.
old=bpy.data.objects.get('Distant broken dome shell');old.hide_render=True;old.hide_viewport=True
for o in list(bpy.data.objects):
 if o.name.startswith('Dome silhouette rib'):bpy.data.objects.remove(o,do_unlink=True)
cy=73;rad=20;h=25;seg=32;rings=12
pts=[]
for j in range(rings+1):
 t=j/rings;rr=3+(rad-3)*(1-t)**.78
 pts.append([(rr*math.cos(2*math.pi*i/seg),cy+rr*math.sin(2*math.pi*i/seg),h*t) for i in range(seg)])
for i in range(seg):
 for j in range(rings):beam('Dome radial frame',pts[j][i],pts[j+1][i],.22,.22,rust)
for j in range(1,rings+1):
 for i in range(seg):
  if j==rings and i%4==0:continue
  beam('Dome horizontal frame',pts[j][i],pts[j][(i+1)%seg],.21,.18,rust)
for j in range(rings):
 for i in range(seg):
  if random.random()<(.55 if j>7 else .28):continue
  vs=[pts[j][i],pts[j][(i+1)%seg],pts[j+1][(i+1)%seg],pts[j+1][i]]
  mesh('Dome surviving armor plate',vs,[(0,1,2,3)],edge if (i+j)%4 else rust)
# Lower skyline should conceal dome base and provide atmospheric depth.
for i in range(58):
 x=random.uniform(-16,16);y=random.uniform(48,64);hh=random.uniform(1.8,7)
 if abs(x)<2.4:hh*=.38
 box('Distant city silhouette',(x,y,hh/2),(random.uniform(.3,1.1),random.uniform(.3,1.2),hh),dust)
# Replace the random foreground band with three composed piles of fragments.
for o in list(bpy.data.objects):
 if o.name.startswith(('Foreground broken slab','Side rubble cluster')):bpy.data.objects.remove(o,do_unlink=True)
active=bpy.data.collections.new('09 Composed rubble');s.collection.children.link(active)
def shard(name,x,y,z,sx,sy,sz,m):
 vs=[(-.5,-.5,0),(.4,-.5,0),(.5,.4,0),(-.35,.5,0),(-.3,-.35,.65),(.3,-.35,.9),(.28,.35,.55),(-.4,.3,.8)]
 o=mesh(name,[(x+a*sx,y+b*sy,z+c*sz) for a,b,c in vs],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m);o.data.materials.append(edge);o.data.materials.append(ink)
 for p in o.data.polygons:p.material_index=1 if p.normal.z>.5 else (2 if p.normal.x>.5 else 0)
 return o
for cx,cy,n,span in [(-3.7,-8.4,36,1.7),(0,-9.8,20,1.2),(3.7,-8.65,32,1.6)]:
 for i in range(n):
  x=cx+random.uniform(-span,span);y=cy+random.uniform(-.5,.5)
  shard('Foreground concrete fragment',x,y,random.uniform(0,.2),random.uniform(.22,.8),random.uniform(.2,.7),random.uniform(.2,.65),dark)
for a,b in [((-3.8,-8.5,.2),(-3,-8.35,.9)),((2.8,-8.7,.1),(3.8,-8.5,.9)),((-.8,-9.5,.1),(.1,-9.4,.9))]:beam('Foreground broken girder',a,b,.16,.32,dim)
# A hollow pipe is a major foreground silhouette landmark.
for x,y,z in [(-3.3,-8.3,.65),(3.55,-8.65,.58)]:
 n=12;vs=[]
 for zz,rr in [(0,.30),(.65,.30),(0,.22),(.65,.22)]:
  vs.extend([(x+rr*math.cos(i*2*math.pi/n),y+rr*math.sin(i*2*math.pi/n),z+zz) for i in range(n)])
 fs=[]
 for i in range(n):
  k=(i+1)%n;fs.extend([(i,k,n+k,n+i),(n+i,n+k,3*n+k,3*n+i),(2*n+i,3*n+i,3*n+k,2*n+k)])
 mesh('Hollow foreground pipe',vs,fs,dim)
for sign in [-1,1]:
 for cx,cy in [(sign*7,-2),(sign*6.5,7),(sign*6,18),(sign*5.5,27)]:
  for i in range(20):shard('Side debris group',cx+random.uniform(-1,1),cy+random.uniform(-1.8,1.8),0,random.uniform(.2,.7),random.uniform(.2,.65),random.uniform(.15,.6),stone)
# Mid-distance barrier from target, kept well behind the scale figure.
for i in range(40):shard('Distant debris barrier',random.uniform(-6,6),random.uniform(27,30),0,random.uniform(.3,1),random.uniform(.3,1),random.uniform(.3,1.1),dim)
# Ground marks follow perspective. No fine texture noise during shape review.
active=bpy.data.collections.new('10 Ground value accents');s.collection.children.link(active)
road=bpy.data.objects.get('Open traversable street');road.data.materials[0]=earth;road.data.materials[2]=earth
for x,y,length in [(-2,-2,2.3),(3,2,1.8),(-3,9,3),(1,15,2.2),(-.5,24,2)]:
 line('Sparse ground fissure',[(x,y,-.018),(x+.14,y+length*.3,-.018),(x-.07,y+length*.7,-.018),(x+.13,y+length,-.018)],.018,ink)
# Preserve the camera/figure; reduce the previously boxy torso outline slightly.
fig=bpy.data.objects.get('Figure torso');fig.scale.x=.86
# Correct material-preview world and pack authoritative target in the review file.
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.shading.type='MATERIAL';a.spaces.active.shading.use_scene_world=True;a.spaces.active.shading.use_scene_world_render=True;a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.region_3d.view_camera_zoom=10
s['stage']='Geometry refinement 003, not final art';s['selected_reference']='selected-third.png';s.camera.data.passepartout_alpha=1
s.render.filepath=str(O/'refinement.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'xenon-refinement.blend'));bpy.ops.render.render(write_still=True)
