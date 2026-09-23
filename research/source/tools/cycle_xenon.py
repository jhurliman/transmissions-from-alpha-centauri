"""Creator passes; generate real geometry/materials without projecting the target image."""
import bpy,math,random,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];roundid=sys.argv[-1] if sys.argv[-1].isdigit() else '004';O=R/'art/reviews'/('xenon-'+roundid);O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-003/xenon-refinement-shaded.blend'));s=bpy.context.scene;random.seed(400)
C=bpy.data.collections.new('Creator 004 - facade and rubble');s.collection.children.link(C)
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in a)
def material(name,h,texture=True):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb(h),1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');l.new(e.outputs[0],o.inputs[0]);col=(*rgb(h),1)
 g=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.4,-.35,.85);l.new(g.outputs['Normal'],dot.inputs[0])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT';els=ramp.color_ramp.elements;els[0].position=.0;els[0].color=(*(v*.72 for v in col[:3]),1);els[1].position=.55;els[1].color=col
 l.new(dot.outputs['Value'],ramp.inputs[0]);prev=ramp.outputs[0]
 if texture:
  noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7;l.new(g.outputs['Position'],noise.inputs['Vector'])
  nr=n.new('ShaderNodeValToRGB');nr.color_ramp.elements[0].position=.37;nr.color_ramp.elements[0].color=(.45,.39,.4,1);nr.color_ramp.elements[1].position=.61;nr.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],nr.inputs[0])
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.55;l.new(prev,mix.inputs[1]);l.new(nr.outputs[0],mix.inputs[2]);prev=mix.outputs[0]
 ao=n.new('ShaderNodeAmbientOcclusion');ao.samples=8;ao.inputs['Distance'].default_value=1.5
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.55;l.new(prev,mix.inputs[1]);l.new(ao.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],e.inputs[0]);return m
plate=material('004 steel lavender cladding','898493');rust=material('004 ochre damage','a3866e');black=material('004 dark outline','342d3b',False);steel=material('004 steel shaded','595566');ground=material('004 brown street','84624b');far=material('004 distant haze','a68b98');dark=material('004 foreground','3d3645');dust=material('004 pale debris','a39583');orange=material('004 dome plates','a57968');white=material('004 suit','dedbdd');purple=material('004 purple cloth','7e4388');skin=material('004 skin','d0a075');hair=material('004 hair','d5a248');boots=material('004 boots','211f29')
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);o.data.materials.append(m);return o
def box(name,loc,dims,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def rod(name,a,b,r,m,n=8):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 C.objects.link(o);return o
def curve(name,points,width,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=width;cu.bevel_resolution=0;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 o=bpy.data.objects.new(name,cu);C.objects.link(o);o.data.materials.append(m);return o
# Remove thin decorative rectangles and make actual larger facing planes.
for o in list(bpy.data.objects):
 if o.name.startswith(('Remaining wall panel','Recess behind broken cladding','Panel fracture')):
  bpy.data.objects.remove(o,do_unlink=True);continue
 if o.name.startswith('Left vertical structure'):o.scale.y*=.55
 if o.name.startswith('Right exposed pillar'):o.scale.y*=.6
 if o.name.startswith('Right diagonal buttress'):
  o.data.materials.clear();o.data.materials.append(plate)
for side in [-1,1]:
 for j,y in enumerate([-5,-1.5,2.5,6.5,10.5,14.5,18.5,22.5]):
  for k,z in enumerate([1.65,5.1,9.0,13.0,17.0]):
   if (j+2*k)%9==0:continue
   x=side*(7.45 if side<0 else 7.38);w=3.25;hh=2.75
   # Chipped boundary; local area variations, not universal bevels.
   vs=[(x,y-w/2,z-hh/2),(x,y+w/2,z-hh/2),(x,y+w/2,z+hh*.2),(x,y+w*.41,z+hh*.23),(x,y+w*.39,z+hh/2),(x,y-w*.3,z+hh/2),(x,y-w/2,z+hh*.35)]
   o=mesh('Authored broken cladding',vs,[tuple(range(7))],plate if (j+k)%5 else rust)
   sol=o.modifiers.new('Plate thickness','SOLIDIFY');sol.thickness=.14
   for q in range(2):
    yy=y+random.uniform(-1.2,1.2);zz=z+random.uniform(-1.1,1.1)
    # Thin irregular missing-paint spots with clustered placement.
    points=[(x-side*.014,yy,zz),(x-side*.014,yy+.12,zz+.03),(x-side*.014,yy+.17,zz+.17),(x-side*.014,yy+.07,zz+.12),(x-side*.014,yy-.05,zz+.2)]
    mesh('Local flaked paint',points,[tuple(range(5))],black)
   if (j+k)%3==0:
    xx=x-side*.018;curve('Cladding stress crack',[(xx,y-.8,z+.8),(xx,y-.55,z+.5),(xx,y-.66,z+.2),(xx,y-.4,z-.05)],.013,black)
# Narrow services to avoid hiding facade value masses.
for o in bpy.data.objects:
 if o.name.startswith(('Left service riser','Pipe collar')):
  o.data.materials.clear();o.data.materials.append(steel)
# Dome extends across the opening with a flat-ish broken crown.
for o in bpy.data.objects:
 if o.name.startswith(('Dome radial frame','Dome horizontal frame','Dome surviving armor plate')):
  o.location.x*=1.24
  if o.type=='MESH':
   for v in o.data.vertices:v.co.x*=1.24
  # Parts authored around global coordinates or local beam coordinates retain height.
  if o.name.startswith('Dome surviving armor plate'):
   o.data.materials.clear();o.data.materials.append(orange)
# Rebuild spatially varied skyline silhouettes at multiple depths.
for o in list(bpy.data.objects):
 if o.name.startswith(('Distant city silhouette','Distant broken tower')):bpy.data.objects.remove(o,do_unlink=True)
for layer,ybase in enumerate([32,42,53,63]):
 m=material('004 haze layer '+str(layer),['726374','857080','9a7e8b','ac8d98'][layer])
 for j in range(25):
  xx=random.uniform(-14,14);yy=ybase+random.uniform(-3,3);hh=random.uniform(2,8.5)
  if abs(xx)<2:hh*=.2
  w=random.uniform(.3,1.3);d=random.uniform(.5,1.8)
  vs=[(xx-w,yy-d,0),(xx+w,yy-d,0),(xx+w,yy+d,0),(xx-w,yy+d,0),(xx-w,yy-d,hh),(xx+.2*w,yy-d,hh*.88),(xx+w,yy-d,hh*1.13),(xx+w,yy+d,hh),(xx-w,yy+d,hh*.8)]
  mesh('Broken distant tower',vs,[(0,1,6,5,4),(1,2,7,6),(2,3,8,7),(3,0,4,8),(4,5,6,7,8)],m)
# Rock mesh with unequal cut planes.
def rock(name,pos,size,m):
 x,y,z=pos;sx,sy,sz=size;vs=[(-.6,-.4,0),(.5,-.4,0),(.5,.5,0),(-.4,.5,0),(-.4,-.25,.65),(.2,-.3,.9),(.35,.3,.55),(-.35,.35,.75)]
 return mesh(name,[(x+a*sx,y+b*sy,z+c*sz) for a,b,c in vs],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
for i in range(280):
 side=random.choice([-1,1]);y=random.uniform(-8,31);x=side*random.uniform(5.2,7.6)
 rock('Rubble varied overlapping',(x,y,0),(random.uniform(.15,.8),random.uniform(.18,.8),random.uniform(.12,.65)),random.choice([steel,dust,rust]))
for i in range(110):
 x=random.uniform(-5.5,5.5);y=random.uniform(-10,-8.6)
 rock('Foreground overlapping wreckage',(x,y,random.uniform(.01,.2)),(random.uniform(.2,.85),random.uniform(.2,.7),random.uniform(.1,.6)),random.choice([dark,steel,rust]))
for i in range(75):
 x=random.uniform(-6,6);y=random.uniform(22,31)
 rock('Midground rubble',(x,y,0),(random.uniform(.3,1.3),random.uniform(.3,1.1),random.uniform(.25,1.1)),random.choice([steel,dust,rust]))
road=bpy.data.objects.get('Open traversable street');road.data.materials.clear();road.data.materials.append(ground)
for p in road.data.polygons:p.material_index=0
# Sparse patches rather than an evenly scattered noisy ground.
for i in range(90):
 x=random.uniform(-6,6);y=random.uniform(-8,30);a=random.uniform(.02,.14)
 mesh('Ground chipped fleck',[(x,y,-.018),(x+a,y+.07,-.018),(x+a*.4,y+.14,-.018),(x-.02,y+.08,-.018)],[(0,1,2,3)],rust if i%4==0 else steel)
# Human proxy with tapered limbs and torso; no borrowed art textures.
for o in list(bpy.data.objects):
 if o.name.startswith('Figure '):bpy.data.objects.remove(o,do_unlink=True)
y=-6.5
for dx in [-.105,.105]:
 rod('Roger trouser upper',(dx,y,.94),(dx,y,.54),.10,white)
 rod('Roger trouser lower',(dx,y,.54),(dx,y,.22),.076,white)
 o=box('Roger boot',(dx,y-.035,.12),(.16,.27,.24),boots)
verts=[]
for z,w,d in [(.89,.18,.10),(1.05,.16,.105),(1.37,.235,.12),(1.49,.19,.1)]:
 verts.extend([(-w,y-d,z),(w,y-d,z),(w,y+d,z),(-w,y+d,z)])
fs=[(0,3,2,1),(12,13,14,15)]
for j in range(3):
 for k in range(4):fs.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
mesh('Roger tapered suit',verts,fs,white)
for sign in [-1,1]:
 rod('Roger upper sleeve',(sign*.235,y,1.38),(sign*.27,y,1.14),.07,purple)
 rod('Roger lower sleeve',(sign*.27,y,1.14),(sign*.255,y-.01,.98),.058,purple)
 rod('Roger hand',(sign*.255,y-.01,.98),(sign*.255,y-.01,.89),.049,skin)
rod('Roger neck',(0,y,1.45),(0,y,1.56),.07,skin)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=(0,y,1.65));o=bpy.context.object;o.name='Roger head';o.scale=(.113,.11,.157);o.data.materials.append(hair)
# Sky bands on distant backdrop provide a sparse graphic cloud rhythm.
C=bpy.data.collections.new('004 sky shapes');s.collection.children.link(C)
cloud=material('004 distant cloud bands','ca573f',False)
for zz,offset in [(24,-12),(34,4),(41,-4)]:
 vs=[]
 for i in range(12):vs.append((-65+i*12,140,zz+math.sin(i*1.7+offset)*1.2))
 vs+= [(67,140,zz+2.8),(-65,140,zz+2.8)]
 mesh('Distant sky band',vs,[tuple(range(len(vs)))],cloud)
s.cycles.samples=24;s.render.filepath=str(O/'render.png');s.render.resolution_percentage=100;s.render.use_freestyle=True;s.render.line_thickness=.60
s['stage']='Creator-critic round '+roundid;s['reference']='selected-third.png; not used as texture'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
