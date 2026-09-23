"""Fresh C-grounded camera blockout. blender -b --python tools/build_xenon.py"""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];OUT=R/'art/reviews/xenon-002';OUT.mkdir(exist_ok=True)
random.seed(41);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard';s.view_settings.look='None'
# Flat illustration colors are linearized to preserve intended display palette.
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in vals)
def mat(name,h):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb(h),1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*rgb(h),1);m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
wall=mat('Architecture - muted violet','575061');light=mat('Exposed planes - dusty lavender','85727a');dark=mat('Shadow - aubergine','292637');side=mat('Structure - mid violet','423c50');earth=mat('Street - clay','795143');rubble=mat('Rubble - dark plum','353040');edge=mat('Broken planes - rust','916455');far=mat('Distant ruins - dusty violet','8c6d7a');dome=mat('Dome - muted rust','aa6b60');sky=mat('Sky - vermilion','e25838');white=mat('Figure - pale suit','d8d7d7');purple=mat('Figure - sleeves','79387e');hair=mat('Figure - hair','d4a046');boot=mat('Figure - boots','17151c')
collections={}
def coll(name):
 c=bpy.data.collections.new(name);s.collection.children.link(c);collections[name]=c;return c
active=coll('01 Street')
def add(o,name,m):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 active.objects.link(o)
 o.data.materials.append(m);return o
def box(name,loc,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=add(bpy.context.object,name,m);o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(dark);o.data.materials.append(m)
 for p in o.data.polygons:
  if p.normal.x>.5:p.material_index=1
  elif p.normal.z>.5:p.material_index=2
 return o
def rod(name,a,b,r,m,verts=8):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=add(bpy.context.object,name,m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
box('Open traversable street',(0,33,-.18),(70,120,.3),earth)
active=coll('02 Left ruined buildings')
for i,(y,w,h) in enumerate([(-3,3,18),(5,3.5,21),(14,3,19),(23,3,16)]):
 box('Left architectural mass %02d'%i,(-8-w/2,y,h/2),(w,8,h),wall)
 for z in [3.5,8,13]:box('Left interrupted ledge',(-7.8,y,z),(.55,7,.24),side)
 for yy in [y-2,y+2]:box('Left vertical structure',(-7.5,yy,h*.48),(.65,.55,h*.96),side)
# Landmark forms visible in C, not surface dressing.
rod('Left service riser',(-6.9,1,0),(-6.9,1,17),.46,wall,12)
for z in range(1,17,2):rod('Pipe collar',(-6.9,1,z),(-6.9,1,z+.18),.57,side,12)
box('Left broken canopy',(-6.75,-1,5.1),(2.6,5,.3),side)
rod('Left diagonal canopy brace',(-7.1,-3,1.5),(-5.55,-3,5),.12,dark,4)
active=coll('03 Right ruined buildings')
for i,(y,h) in enumerate([(-4,20),(5,18),(14,22),(23,16)]):
 box('Right architectural mass %02d'%i,(10,y,h/2),(4.5,8,h),wall)
 for z in [4.2,8.5,12.8]:
  box('Right projecting horizontal ledge',(7.55,y,z),(1.35,7.8,.35),side)
 for yy in [y-3,y,y+3]:box('Right exposed pillar',(7.6,yy,h/2),(.65,.6,h),side)
for y in [-2,2,6,10,14]:
 o=box('Right diagonal buttress',(6.9,y,2.0),(.58,.75,4.7),light);o.rotation_euler.y=.39
active=coll('04 Distant dome and ruins')
# Dome's shape is editable mesh, deliberately broad and broken into ribs and bands.
cy=73;radius=20;height=25;segments=24;rings=7
verts=[]
for j in range(rings+1):
 t=j/rings;rr=3+(radius-3)*(1-t)**.78;z=height*t
 for i in range(segments):
  a=2*math.pi*i/segments;verts.append((rr*math.cos(a),cy+rr*math.sin(a),z))
faces=[]
for j in range(rings):
 for i in range(segments):
  if random.random()<.10 and j>3:continue
  faces.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
mesh=bpy.data.meshes.new('Dome shell mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Distant broken dome shell',mesh);active.objects.link(o);o.data.materials.append(dome);o.data.materials.append(far)
for p in mesh.polygons:p.material_index=1 if random.random()<.25 else 0
for i in range(0,segments,2):
 for j in range(rings):rod('Dome silhouette rib',verts[j*segments+i],verts[(j+1)*segments+i],.23,edge,4)
for i in range(34):
 y=random.uniform(32,66);x=random.choice([-1,1])*random.uniform(4,16);h=random.uniform(2,10)
 box('Distant broken tower',(x,y,h/2),(random.uniform(.7,2),random.uniform(1,3),h),far)
active=coll('05 Foreground rubble')
# Broad foreground shapes; deliberately limited count and larger pieces.
for i in range(38):
 x=random.uniform(-6,6);y=random.uniform(-9.4,-8.1);z=random.uniform(.05,.35)
 o=box('Foreground broken slab',(x,y,z),(random.uniform(.35,1.3),random.uniform(.25,.7),random.uniform(.25,.8)),rubble);o.rotation_euler=(random.uniform(-.6,.6),random.uniform(-.6,.6),random.uniform(-1,1))
for sign in [-1,1]:
 for i in range(22):
  y=random.uniform(-5,30);x=sign*random.uniform(6.2,8.4)
  o=box('Side rubble cluster',(x,y,.15),(random.uniform(.3,1.0),random.uniform(.3,.9),random.uniform(.2,.6)),edge);o.rotation_euler.z=random.uniform(-2,2)
active=coll('06 Roger scale figure - 1.8m')
x=0;y=-6.5
# Simple articulated mannequin; not a finished Roger model.
for dx in [-.12,.12]:
 rod('Figure leg',(x+dx,y,.18),(x+dx,y,.92),.095,white)
 box('Figure boot',(x+dx,y-.035,.13),(.18,.29,.26),boot)
box('Figure pelvis',(x,y,.93),(.37,.22,.25),white)
box('Figure torso',(x,y,1.25),(.43,.25,.49),white)
for dx in [-.29,.29]:rod('Figure purple sleeve',(x+dx,y,1.44),(x+dx,y,1.02),.085,purple)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(x,y,1.65));o=add(bpy.context.object,'Figure head',hair);o.scale=(.13,.12,.17)
active=coll('07 Camera and backdrop')
bpy.ops.object.camera_add(location=(0,-14,3.65));cam=bpy.context.object;cam.name='C composition camera';cam.rotation_euler=(Vector((0,30,-1.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=25.7;cam.data.sensor_width=36;cam.data.clip_end=500;s.camera=cam
s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(*rgb('e25838'),1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=1
# Camera-space reference available as background overlay but not rendered into geometry.
im=bpy.data.images.load(str(R/'art/reviews/xenon-001/selected-third.png'));im.pack();cam.data.show_background_images=True;bg=cam.data.background_images.new();bg.image=im;bg.alpha=.25;bg.display_depth='FRONT';bg.show_background_image=False
s['art_target']='Study C selected by user';s['stage']='Unapproved geometry and camera blockout, not finished art';s['figure_height_m']=1.8
bpy.context.view_layer.update();pts={}
for name,p in {'roger_feet':(0,-6.5,0),'roger_head':(0,-6.5,1.82),'dome_peak':(0,73,24.75)}.items():
 v=world_to_camera_view(s,cam,Vector(p));pts[name]=[round(v.x,4),round(1-v.y,4)]
(OUT/'landmarks.json').write_text(json.dumps(pts,indent=2))
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
s.render.filepath=str(OUT/'blockout-v2.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'xenon-blockout-v2.blend'));bpy.ops.render.render(write_still=True)
print('LANDMARKS',pts)
