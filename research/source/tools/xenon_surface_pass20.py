import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-020';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-019/scene.blend'));s=bpy.context.scene;random.seed(2020)
C=bpy.data.collections.new('020 Fine broken surface and weather seams');s.collection.children.link(C)
src=(R/'tools/rebuild_xenon_geometry.py').read_text();exec(src[src.index('def mesh('):src.index("coll('01 Street")])
metal=bpy.data.materials['Exposed weathered steel'];earth=bpy.data.materials['Weathered street'];rust=bpy.data.materials['Oxidized edges'];shadow=bpy.data.materials['Recessed structural iron']
# Ground fissures were overdrawn; replace with small actual fragments and surface patches.
for o in list(s.objects):
 if o.name.startswith('Ground fissure'):bpy.data.objects.remove(o,do_unlink=True)
for i in range(1000):
 y=random.uniform(-8,31);x=random.uniform(-7.5,7.5)
 if abs(x)<1.2 and y<5 and random.random()<.8:continue
 size=random.uniform(.015,.12)*(1.4 if abs(x)>5 else 1)
 angle=random.random()*math.tau;pts=[]
 for j in range(5):
  a=angle+j*math.tau/5;rr=size*random.uniform(.65,1.2);pts.append((x+math.cos(a)*rr,y+math.sin(a)*rr*1.7,random.uniform(-.025,.005)))
 pts.append((x,y,random.uniform(.008,.04)))
 mesh('Small angular street fragment',pts,[(j,(j+1)%5,5) for j in range(5)],random.choice([metal,earth,earth,rust]))
# Broken patches: thin actual irregular polygon surfaces set into roadway.
for i in range(70):
 x=random.uniform(-7,7);y=random.uniform(-7,31);a=random.uniform(.12,.6)
 pts=[(x+math.cos(j*math.tau/9)*a*random.uniform(.6,1.1),y+math.sin(j*math.tau/9)*a*random.uniform(.6,1.1),-.036) for j in range(9)]
 mesh('Flaked road surface',pts,[tuple(range(9))],earth if i%3 else shadow)
# A warmer raking key and cooler reduced ambient make steel planes distinguishable.
sun=bpy.data.objects['Soft warm directional daylight'];sun.data.energy=3.2;sun.data.color=(1,.73,.49);sun.location=(-15,-2,28);sun.rotation_euler=(Vector((0,15,2))-sun.location).to_track_quat('-Z','Y').to_euler()
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.inputs['Strength'].default_value>1.1:n.inputs['Strength'].default_value=.95
for o in s.objects:
 if o.name.startswith('Distant dust volume'):
  for n in o.data.materials[0].node_tree.nodes:
   if n.type=='VOLUME_SCATTER':n.inputs['Density'].default_value=.0017
s.use_nodes=False;s.cycles.samples=48;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
