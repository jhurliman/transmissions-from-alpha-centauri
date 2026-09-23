import bpy,math,random,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-013';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-010/scene.blend'));s=bpy.context.scene;random.seed(1101)
# Preserve projected dome size while changing actual distance and scale.
cam=s.camera;origin=cam.location.copy();factor=4.2;xf=Matrix.Translation(origin)@Matrix.Scale(factor,4)@Matrix.Translation(-origin)
count=0
for ob in s.objects:
 if ob.name.startswith(('Dome ','Fine secondary dome','Crown broken spar')):
  ob.matrix_world=xf@ob.matrix_world;count+=1
cam.data.clip_end=1600
# Replace former short wall of upright remnants, preserve alley and nearby rubble.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('Fractured city remnant','Exposed remnant spine')):bpy.data.objects.remove(ob,do_unlink=True)
road=bpy.data.objects.get('Street foundation')
# Street foundation uses world-space vertices; extend only far edge.
for v in road.data.vertices:
 if v.co.y>100:v.co.y=680
# Remove the hard-sided dust box; use long low-density actual volumetric atmosphere.
for ob in bpy.data.objects:
 if ob.name.startswith('Distant dust volume'):
  ob.location=(0,310,35);ob.dimensions=(700,560,80)
  for n in ob.data.materials[0].node_tree.nodes:
   if n.type=='VOLUME_SCATTER':n.inputs['Density'].default_value=.0022
C=bpy.data.collections.new('013 Long ruined city - depth layers');s.collection.children.link(C)
base=bpy.data.materials['Exposed weathered steel'];warm=bpy.data.materials['Sun-worn warm cladding'];dark=bpy.data.materials['Recessed structural iron']
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);o.data.materials.append(m);return o
def box(name,loc,size,m):
 x,y,z=loc;a,b,c=[v/2 for v in size];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
def beam(name,a,b,w,d,m):
 delta=Vector(b)-Vector(a);ob=box(name,(0,0,0),(w,d,delta.length),m);ob.location=(Vector(a)+Vector(b))/2;ob.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return ob
# Keep approximate real architectural scale across depth; their projected size diminishes naturally.
layers=[(39,10,22),(57,13,28),(83,18,36),(120,23,48),(168,29,64),(224,34,86),(288,40,115),(353,44,140)]
for layer,(ybase,n,spread) in enumerate(layers):
 for i in range(n):
  x=random.uniform(-spread,spread);y=ybase+random.uniform(-5,7);height=random.uniform(*([(1.0,3.0),(4,10),(8,19)]+[(10,24)]*5)[layer]);width=random.uniform(2.8,5.6);depth=random.uniform(2.5,5.5)
  # Meandering discontinuous sightline through ruin field, not a straight empty boulevard.
  corridor=math.sin(y*.033)*2.2
  if abs(x-corridor)<(5.5 if layer<4 else 7):continue
  # Thick broken walls with missing corner, not thin upright sticks.
  pts=[(-width/2,0),(width/2,0),(width/2,height*.58),(width*.25,height*.58),(width*.25,height*.93),(-width*.04,height),(-width*.04,height*.72),(-width/2,height*.72)]
  t=.16;vs=[(x+xx,y+yy,zz) for yy in [-t,t] for xx,zz in pts];ns=len(pts);fs=[tuple(range(ns-1,-1,-1)),tuple(range(ns,ns*2))]+[(k,(k+1)%ns,(k+1)%ns+ns,k+ns) for k in range(ns)]
  if height<5 or i%4!=0:
   mesh('Layer %02d broken building wall'%layer,vs,fs,base if i%3 else warm)
  else:
   # Window openings and broken floor edges expose real space through the ruins.
   for col in range(3):
    xx=x-width/2+col*width/2
    hh=height*random.uniform(.68,1)
    box('Layer %02d shattered facade pier'%layer,(xx,y,hh/2),(.35,.45,hh),base)
   for level in range(int(height/2.7)):
    z=level*2.7+.9
    box('Layer %02d broken window sill'%layer,(x,y,z),(width,.4,.65),base if i%3 else warm)
    if level%2==0:
     box('Layer %02d surviving wall bay'%layer,(x-width*.25,y,z+1.0),(width*.5,.32,1.7),base)
  # Return walls and partial floors make remnants recognizable as collapsed buildings.
  if i%2==0:
   box('Layer %02d return wall'%layer,(x-width/2,y+depth/2,height*.26),(.19,depth,height*.52),base)
  if i%3==0:
   ob=box('Layer %02d fractured floor slab'%layer,(x,y+depth*.4,height*.34),(width*.8,depth*.75,.15),warm);ob.rotation_euler.y=random.uniform(-.2,.2)
  if i%4==0:
   beam('Layer %02d exposed bent frame'%layer,(x-width*.35,y,0),(x-width*.25,y+.25,height+.7),.13,.15,dark)
   beam('Layer %02d collapsed cross member'%layer,(x-width*.25,y+.25,height+.7),(x+width*.6,y+.4,height*.55),.13,.15,dark)
  # Piles at each base connect walls into a ruin field instead of isolated pillars.
  for k in range(12 if layer<4 else 5):
   xx=x+random.uniform(-width*1.4,width*1.4);yy=y+random.uniform(-depth*1.5,depth*1.5);a=random.uniform(.4,1.7);vs=[(xx-a,yy-a,0),(xx+a,yy-a,0),(xx+a,yy+a,0),(xx-a,yy+a,0),(xx-a*.35,yy-a*.2,a*.65),(xx+a*.4,yy-a*.3,a),(xx+a*.2,yy+a*.45,a*.5)]
   mesh('Layer %02d collapsed rubble'%layer,vs,[(0,1,5,4),(1,2,6,5),(2,3,4,6),(3,0,4),(4,5,6)],warm if k%2 else base)
# Small low debris immediately beyond the alley; architecture rises farther behind it.
for ob in bpy.data.objects:
 if ob.name.startswith(('Midground rubble pile','Midground overlapping rubble')):
  for v in ob.data.vertices:v.co.z*=.62
s['depth_design']='Small nearby rubble -> eight native building-remnant layers at 39–353m -> dome centered 491m ahead of camera.'
s['geometry_only']=True;s.cycles.samples=40;s.render.filepath=str(O/'render.png')
(O/'depth-layout.json').write_text(json.dumps({'camera':list(origin),'dome_scale_factor':factor,'dome_objects_transformed':count,'dome_center_y':origin.y+(103-origin.y)*factor,'layers':[{'y':a,'groups':b,'half_width':c} for a,b,c in layers],'painted_finish':False},indent=2)+'\n')
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
s.use_nodes=False
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
