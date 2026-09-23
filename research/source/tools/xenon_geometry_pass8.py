import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-008';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-007/scene.blend'));s=bpy.context.scene;random.seed(808)
# Real-lighting value balance, not image overlays.
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.inputs[1].default_value==.6:n.inputs[1].default_value=1.65
sun=bpy.data.objects.get('Soft warm directional daylight');sun.data.energy=1.0;sun.data.angle=.10;sun.data.color=(1,.94,.91);s.view_settings.exposure=.15
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=38;n.inputs['Detail'].default_value=2
  if n.type=='VALTORGB':
   c=n.color_ramp.elements[1].color;n.color_ramp.elements[0].color=(c[0]*.90,c[1]*.90,c[2]*.90,1)
# Fissures need hairline taper, not giant black strokes.
for o in bpy.data.objects:
 if o.type=='CURVE' and o.name.startswith('Ground fissure'):o.data.bevel_depth*=.2
# Preserve collection helper context and base geometry; replace only dome armor.
C=bpy.data.collections.new('008 dome fracture details');s.collection.children.link(C)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);o.data.materials.append(m);return o
def beam(name,a,b,w,d,m):
 delta=Vector(b)-Vector(a);vs=[(i*w/2,j*d/2,k*delta.length/2) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];o=mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m);o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return o
for o in list(bpy.data.objects):
 if o.name.startswith('Dome individual torn armor'):bpy.data.objects.remove(o,do_unlink=True)
profile=[(0,33),(5,31),(10,28),(15,24.4),(20,19.8),(25,14),(29,9),(32,5.3)]
def radius(z):
 for (a,ra),(b,rb) in zip(profile,profile[1:]):
  if a<=z<=b:return ra+(rb-ra)*(z-a)/(b-a)
 return 5.3
def point(z,a):r=radius(z);return Vector((r*math.cos(a),103+r*math.sin(a),z))
mats=[m for m in bpy.data.materials if m.name.startswith('Dome oxidized')];metal=bpy.data.materials['Dome deep frame']
for j in range(22):
 z=j*32/22;zt=(j+1)*32/22
 for i in range(60):
  a=math.tau*i/60;b=math.tau*(i+1)/60
  if random.random()<(.55 if j>15 else .34):continue
  top=zt if random.random()>.23 else z+(zt-z)*random.uniform(.5,.9)
  pts=[point(z,a+.004),point(z,b-.004),point(top,b-.004),point(top,a+.004)]
  # Sheared corner and variable lengths break the tile grid.
  if i%3==0:pts.insert(3,pts[2]*.75+pts[1]*.25);pts[2]=pts[2]*.75+pts[3]*.25
  o=mesh('Dome fractured metal plate',pts,[tuple(range(len(pts)))],random.choice(mats));sol=o.modifiers.new('Actual plate thickness','SOLIDIFY');sol.thickness=.15
for j in range(2,22,2):
 z=j*32/22
 for i in range(60):
  if random.random()<.18:continue
  beam('Fine secondary dome brace',point(z,math.tau*i/60),point(z,math.tau*(i+1)/60),.09,.12,metal)
# Broken protrusions interrupt the crown profile instead of a perfect saw-free ring.
for i in [2,6,9,13,16,21,25,31,36,42]:
 a=math.tau*i/44;p=point(31.6,a);beam('Crown broken spar',p,p+Vector((random.uniform(-.4,.4),random.uniform(-.4,.4),random.uniform(.3,1.2))),.18,.21,metal)
# Distant atmosphere is an actual participating volume behind the player.
vol=bpy.data.materials.new('Actual distant dust volume');vol.use_nodes=True;n=vol.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');sc=n.new('ShaderNodeVolumeScatter');sc.inputs['Color'].default_value=(.73,.60,.65,1);sc.inputs['Density'].default_value=.009;sc.inputs['Anisotropy'].default_value=.25;vol.node_tree.links.new(sc.outputs[0],out.inputs['Volume'])
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,85,26));o=bpy.context.object;o.name='Distant dust volume - real lighting';o.dimensions=(150,110,60);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(vol);o.display_type='WIRE'
s.cycles.samples=48;s.render.filepath=str(O/'render.png');s['stage']='Geometry-only round008'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
