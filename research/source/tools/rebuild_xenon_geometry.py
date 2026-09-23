"""Geometry-only Xenon rebuild. No image textures, full-frame projections or compositing."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-007';O.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;random.seed(702)
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=-.2
C=None
def coll(name):
 global C
 C=bpy.data.collections.new(name);s.collection.children.link(C)
def linear(h):
 return tuple((v/255)/12.92 if v/255<.04045 else ((v/255+.055)/1.055)**2.4 for v in [int(h[i:i+2],16) for i in (0,2,4)])
def mat(name,h,wear=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*linear(h),1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.94;p.inputs['Specular IOR Level'].default_value=.05
 if wear:
  g=n.new('ShaderNodeTexCoord');no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=3.5;no.inputs['Detail'].default_value=2.2;l.new(g.outputs['Object'],no.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.32;ramp.color_ramp.elements[0].color=(*(v*.73 for v in linear(h)),1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=m.diffuse_color;l.new(no.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 return m
wall=mat('Painted lavender steel','817b88',True);wallwarm=mat('Sun-worn warm cladding','a38b76',True);shadow=mat('Recessed structural iron','383746');metal=mat('Exposed weathered steel','626271',True);light=mat('Chipped light edges','ad9b8a');earth=mat('Weathered street','79604c',True);rust=mat('Oxidized edges','93684e',True);rubbledark=mat('Foreground dark steel','49414b',True)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);o.data.materials.append(m);return o
def box(name,loc,size,m):
 x,y,z=loc;a,b,c=[v/2 for v in size];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
def beam(name,a,b,w,d,m):
 delta=Vector(b)-Vector(a);o=box(name,(0,0,0),(w,d,delta.length),m);o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
def pipe(name,a,b,r,thick,m,n=16):
 delta=Vector(b)-Vector(a);ln=delta.length;vs=[]
 for z,rr in [(0,r),(ln,r),(0,r-thick),(ln,r-thick)]:vs.extend([(rr*math.cos(i*math.tau/n),rr*math.sin(i*math.tau/n),z) for i in range(n)])
 fs=[]
 for i in range(n):
  k=(i+1)%n;fs.extend([(i,k,n+k,n+i),(n+i,n+k,3*n+k,3*n+i),(2*n+i,3*n+i,3*n+k,2*n+k),(i,2*n+i,2*n+k,k)])
 o=mesh(name,vs,fs,m);o.location=Vector(a);o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
def wire(name,pts,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=0;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for v,p in zip(sp.points,pts):v.co=(*p,1)
 o=bpy.data.objects.new(name,cu);C.objects.link(o);o.data.materials.append(m)
def plate(name,side,x,y,z,w,h,m,damage=.15):
 # Extruded facade plate with an individually broken corner, not an intact box.
 cut=damage*h
 pts=[(x,y-w/2,z-h/2),(x,y+w/2,z-h/2),(x,y+w/2,z+h/2-cut),(x,y+w/2-w*.13,z+h/2-cut*.8),(x,y+w*.31,z+h/2),(x,y-w/2,z+h/2)]
 vs=pts+[(xx+side*.16,yy,zz) for xx,yy,zz in pts];fs=[tuple(range(5,-1,-1)),tuple(range(6,12))]
 for i in range(6):j=(i+1)%6;fs.append((i,j,j+6,i+6))
 return mesh(name,vs,fs,m)
coll('01 Street and modeled wear');box('Street foundation',(0,65,-.19),(100,180,.3),earth)
# Fine fissures branch and change length; avoid repeating cartoon zigzags.
for i in range(42):
 x=random.uniform(-6,6);y=random.uniform(-8,29);pts=[(x,y,-.035)]
 for j in range(random.randrange(3,7)):
  x+=random.uniform(-.22,.26);y+=random.uniform(.16,.75);pts.append((x,y,-.035))
 wire('Ground fissure',pts,random.uniform(.008,.022),shadow)
coll('02 Left facade - sloped shell, canopy and services')
# Actual mass profile: a sloped foot, recessed story, projecting service bay.
for yi,(ystart,length,x,h) in enumerate([(-8,10,-8.3,20),(2,9,-7.9,23),(11,9,-8.1,19),(20,10,-8.6,15)]):
 box('Left deep wall core',(x-.65,ystart+length/2,h/2),(1.0,length,h),shadow)
 for row,(z,hh) in enumerate([(1.5,2.8),(4.7,3.2),(8.4,3.6),(12.4,3.7),(16.6,3.8),(20.8,3.8)]):
  if z>h:continue
  # Wide cladding planes dominate; narrow joints, not facade-wide grids.
  widths=[3.05,2.6,3.5];pos=ystart
  for j,w in enumerate(widths):
   if (yi,row,j) in [(0,1,0),(1,2,1),(2,3,2)]:pos+=w+.12;continue
   xx=x+(max(0,3-z)*.18)
   plate('Left broad battered cladding',-1,xx,pos+w/2,z,w,hh,wallwarm if (yi+row+j)%5==0 else wall,random.uniform(.02,.23));pos+=w+.12
 for yy in [ystart+.12,ystart+length-.12]:
  beam('Left corner rib',(x+.15,yy,0),(x+.15,yy,h),.17,.22,metal)
 for z in [3.15,6.65,10.5,14.55]:box('Left narrow story joint',(x+.10,ystart+length/2,z),(.2,length,.12),metal)
# Left canopy is two long sheared I beams with unequal supports.
for yy in [-3.5,1.7]:
 beam('Canopy broken upper rail',(-8.15,yy,5.55),(-5.85,yy,5.32),.16,.25,metal)
 beam('Canopy diagonal support',(-7.95,yy,2.65),(-6.10,yy,5.28),.13,.18,metal)
beam('Canopy outer longitudinal beam',(-5.92,-3.7,5.30),(-5.92,2.15,5.40),.22,.18,metal)
for yy in [-2.9,-1.6,0,.95]:
 wire('Hanging canopy cable',[(-7.95,yy,5.4),(-7.35,yy,4.63),(-6.75,yy,4.75),(-5.95,yy,5.32)],.042,shadow)
pipe('Main left service trunk',(-7.0,4.0,0),(-7.0,4.0,22),.49,.08,metal)
for z in [1,3.4,6.8,9.1,12.6,16.2,20]:
 pipe('Service trunk flange',(-7,4,z),(-7,4,z+.14),.58,.06,shadow)
 for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
  xx=-7+math.cos(angle)*.54;yy=4+math.sin(angle)*.54;box('Flange bolt',(xx,yy,z+.18),(.075,.075,.10),metal)
for xx,yy,r in [(-7.25,5.3,.16),(-7.15,6,.10),(-7.5,3,.085)]:
 pipe('Secondary riser',(xx,yy,1.1),(xx,yy,20),r,.025,metal,10)
for yy in [7,15,22]:
 beam('Exposed bay brace',(-7.6,yy,7),(-7.6,yy+2,10),.1,.13,metal)
coll('03 Right facade - interrupted horizontal floors')
for i,(y,length,x,h) in enumerate([(-8,10,8.25,21),(2,10,8.0,20),(12,9,8.3,24),(21,11,8.8,16)]):
 box('Right shadow core',(x+.7,y+length/2,h/2),(1.1,length,h),shadow)
 for z in [2.2,6.2,10.3,14.5,18.8]:
  if z>h:continue
  # Three independent cladding groups; the open slots reveal structural rails.
  for j,(offset,w) in enumerate([(1.5,2.8),(4.6,3.0),(8.0,3.3)]):
   if j==1 and z in [6.2,14.5]:continue
   plate('Right facade plate',1,x,y+offset,z,w,3.2,wallwarm if (i+j+int(z))%6==0 else wall,random.uniform(.015,.15))
 for z in [4.2,8.5,12.7,17.0]:
  box('Right cantilevered floor edge',(x-.28,y+length/2,z),(.70,length,.21),metal)
  box('Right floor lip',(x-.60,y+length/2,z+.13),(.12,length,.14),wall)
 for yy in [y+.5,y+5.7,y+9.4]:beam('Right narrow upright',(x-.10,yy,0),(x-.1,yy,h),.15,.19,metal)
for yy,top,foot in [(-2,4.1,6.95),(2.3,4.1,6.72),(7,4.1,6.6),(12.2,4.1,7.0),(18,4.1,7.3)]:
 beam('Right structural buttress',(foot,yy,.02),(7.95,yy,top),.38,.40,wall)
 beam('Buttress inset spine',(foot+.09,yy+.18,.06),(8.04,yy+.18,top),.10,.07,shadow)
# Broken rail and circular ventilation mouth, a deliberate landmark.
pipe('Right recessed ventilation throat',(8.05,7,7.0),(7.7,7,7.0),.55,.09,shadow)
coll('04 Broken distant buildings')
# Taller nearer fragments at edges; short middle silhouettes leave a view through the street.
for layer,(ybase,num) in enumerate([(30,18),(43,23),(60,30),(77,35)]):
 m=mat('Distance layer '+str(layer),['706477','847080','927c8b','a48a93'][layer],True)
 for j in range(num):
  xx=random.uniform(-18,18);yy=ybase+random.uniform(-4,4);hh=random.uniform(2,9)
  if abs(xx)<2.5:hh*=.32
  w=random.uniform(.35,1.25);d=random.uniform(.5,1.4)
  # Actual extruded fractured profile, avoiding rows of needles.
  profile=[(-w,0),(w,0),(w,hh*.82),(w*.45,hh*.82),(w*.45,hh),(-w*.35,hh*.91),(-w*.35,hh*.69),(-w,hh*.69)]
  vs=[(xx+a,yy+b,zz) for b in [-d,d] for a,zz in profile];n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
  fs += [(k,(k+1)%n,(k+1)%n+n,k+n) for k in range(n)]
  mesh('Fractured city remnant',vs,fs,m)
  if j%4==0:beam('Exposed remnant spine',(xx,yy,hh*.8),(xx+.10,yy,hh+1.3),.09,.12,m)
coll('05 Dome - truncated shell and broken ribs')
# Custom profile: broad base tapering to a flat crown, with missing structural segments.
profile=[(0,33),(5,31),(10,28),(15,24.4),(20,19.8),(25,14),(29,9),(32,5.3)];cy=103;N=44
mats=[mat('Dome oxidized plate '+str(i),h,True) for i,h in enumerate(['997565','aa8068','8a6862','b48c75'])];ribmat=mat('Dome deep frame','715751')
pts=[]
for j,(z,rr) in enumerate(profile):
 pts.append([(rr*math.cos(math.tau*i/N),cy+rr*math.sin(math.tau*i/N),z) for i in range(N)])
for j in range(len(profile)-1):
 for i in range(N):
  a=pts[j][i];b=pts[j+1][i]
  if not (j==6 and i%7==0):beam('Dome radial structural rib',a,b,.28,.30,ribmat)
  if random.random()<(.42 if j>4 else .14):continue
  k=(i+1)%N;quad=[pts[j][i],pts[j][k],pts[j+1][k],pts[j+1][i]]
  # Deliberate variable-length armor ending before the rib junction.
  q=[tuple(quad[v][axis]*.95+sum(p[axis] for p in quad)/4*.05 for axis in range(3)) for v in range(4)]
  if i%4==0:q[2]=tuple(q[2][a]*.84+q[1][a]*.16 for a in range(3))
  o=mesh('Dome individual torn armor',q,[(0,1,2,3)],random.choice(mats));mod=o.modifiers.new('Armor thickness','SOLIDIFY');mod.thickness=.09
for j in range(1,len(profile)):
 for i in range(N):
  if (i+j)%9==0:continue
  beam('Dome interrupted belt',pts[j][i],pts[j][(i+1)%N],.24,.20,ribmat)
coll('06 Actual foreground wreckage and rubble')
# The same mesh helpers create separate editable objects, not a billboard.
def shard(name,pos,scale,m):
 x,y,z=pos;a,b,c=scale;vs=[(-.65,-.45,0),(.45,-.5,0),(.6,.4,.05),(-.4,.5,.05),(-.42,-.25,.63),(.26,-.32,.91),(.33,.29,.52),(-.32,.31,.76)]
 return mesh(name,[(x+i*a,y+j*b,z+k*c) for i,j,k in vs],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
for i in range(310):
 sign=random.choice([-1,1]);y=random.uniform(-7,31);x=sign*random.uniform(5.4,8.0);a=random.uniform(.12,.70)
 shard('Side crushed masonry',(x,y,-.02),(a,random.uniform(.15,.7),random.uniform(.08,.5)),random.choice([wall,wallwarm,metal,rust]))
for i in range(115):
 x=random.uniform(-6,6);y=random.uniform(26,33)
 shard('Midground rubble pile',(x,y,-.02),(random.uniform(.2,1.1),random.uniform(.2,1),random.uniform(.12,.9)),random.choice([wall,wallwarm,metal]))
for i in range(150):
 x=random.uniform(-5.8,5.8);y=random.uniform(-10.3,-8.9)
 shard('Foreground broken structure',(x,y,random.uniform(-.03,.18)),(random.uniform(.22,.8),random.uniform(.2,.85),random.uniform(.1,.65)),random.choice([rubbledark,metal,rust]))
for x,y,dx,dy,dz in [(-3.4,-8.7,.33,.12,.78),(3.5,-9.1,-.25,.2,.70),(-2.5,-9.6,.2,.2,.5)]:
 pipe('Broken foreground hollow pipe',(x,y,.12),(x+dx,y+dy,dz),.27,.045,rubbledark)
for a,b in [((-2,-9.4,.2),(-.6,-9.3,.9)),((1.8,-9.5,.2),(3.3,-9.1,.9)),((-.9,-9.5,.1),(.9,-9.4,.5))]:
 beam('Fallen I girder web',a,b,.07,.24,metal)
 delta=Vector(b)-Vector(a);right=delta.cross(Vector((0,0,1))).normalized()*.14
 for sign in [-1,1]:beam('Fallen girder flange',Vector(a)+right*sign,Vector(b)+right*sign,.10,.035,rust)
coll('07 Human scale proxy')
with bpy.data.libraries.load(str(R/'art/reviews/xenon-005/geometry.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('Roger')]
for o in b.objects:
 if o:C.objects.link(o)
# Replace proxy materials with actual diffuse materials; no inherited emission projection.
figurem={'suit':mat('Suit diffuse','d8d7dc'),'trouser':mat('Trouser diffuse','d8d7dc'),'sleeve':mat('Sleeve diffuse','804689'),'head':mat('Hair diffuse','d2a44c'),'neck':mat('Skin diffuse','c69e76'),'hand':mat('Hand diffuse','c69e76'),'boot':mat('Boot diffuse','211e26')}
for o in C.objects:
 for key,m in figurem.items():
  if key in o.name.lower():o.data.materials.clear();o.data.materials.append(m);break
coll('08 Camera and real lights')
bpy.ops.object.camera_add(location=(0,-14,3.65));cam=bpy.context.object;cam.name='Geometry acceptance camera';cam.rotation_euler=(Vector((0,30,-1.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=25.7;cam.data.sensor_width=36;cam.data.clip_end=400;s.camera=cam
bpy.ops.object.light_add(type='SUN',location=(-10,-8,30));sun=bpy.context.object;sun.name='Soft warm directional daylight';sun.rotation_euler=(Vector((0,10,0))-sun.location).to_track_quat('-Z','Y').to_euler();sun.data.energy=2.0;sun.data.angle=.045;sun.data.color=(1,.85,.72)
s.world=bpy.data.worlds.new('Orange sky with neutral ambient');s.world.use_nodes=True;n=s.world.node_tree.nodes;n.clear();l=s.world.node_tree.links;out=n.new('ShaderNodeOutputWorld');mix=n.new('ShaderNodeMixShader');lp=n.new('ShaderNodeLightPath');amb=n.new('ShaderNodeBackground');amb.inputs[0].default_value=(.42,.45,.56,1);amb.inputs[1].default_value=.6;sky=n.new('ShaderNodeBackground');sky.inputs[0].default_value=(*linear('eb623e'),1);l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(amb.outputs[0],mix.inputs[1]);l.new(sky.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
s.render.use_freestyle=True;s.render.line_thickness=.55;ls=bpy.context.view_layer.freestyle_settings.linesets[0];ls.linestyle=bpy.data.linestyles.new('Geometry contour');ls.linestyle.color=(.03,.025,.04);ls.linestyle.thickness=.55;ls.select_crease=False
# Assert no image textures/projection tricks in the actual evaluation scene.
for m in bpy.data.materials:
 if m.use_nodes:assert not any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes),m.name
s['acceptance']='GEOMETRY ONLY - no image textures, material overrides, painted plate or compositing';s['stage']='Rebuild 007 awaiting critic';s.render.filepath=str(O/'render.png')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_world=True;area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
