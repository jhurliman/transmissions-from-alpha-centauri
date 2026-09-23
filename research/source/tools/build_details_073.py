import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-073';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-072/scene.blend'));s=bpy.context.scene
camera=s.camera.matrix_world.copy();changes={}
# Restore the accepted pre-reflection glazing verbatim.
old=bpy.data.materials['Infill | smoked blue opaque study']
with bpy.data.libraries.load(str(R/'art/reviews/xenon-071/scene.blend'),link=False) as (a,b):b.materials=[old.name]
old.user_remap(b.materials[0]);bpy.data.materials.remove(old);b.materials[0].name='Infill | smoked blue opaque study'
for ob in list(bpy.data.objects):
 if ob.type=='LIGHT_PROBE' and ob.name.startswith('072'):bpy.data.objects.remove(ob,do_unlink=True)
steel=bpy.data.materials['Structure | charcoal steel'];metal=bpy.data.materials['DUCT | muted blue-gray sheet'];C=s.collection
F=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
def mesh(n,vs,fs,m,bev=.008):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(n,me);C.objects.link(ob)
 if bev:q=ob.modifiers.new('45 degree manufactured chamfer','BEVEL');q.width=bev;q.segments=1
 return ob
def box(n,p,d,m,bev=.008):
 return mesh(n,[(p[0]+i*d[0]/2,p[1]+j*d[1]/2,p[2]+k*d[2]/2) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],F,m,bev)
def prism(n,x0,x1,p,m):
 N=len(p);return mesh(n,[(x,y,z) for x in [x0,x1] for y,z in p],[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m)
C=bpy.data.objects['right_horizontal_utility'].instance_collection
old=bpy.data.objects['072 45 degree cantilever return'];m=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
# Window bay is at +0.45; its trim projects -0.24 to +0.21. Match that edge.
prism('073 full projection soffit',-7.39,7.39,[(.21,10.14),(1.14,9.21),(1.24,9.21),(1.24,10.14)],m)
# Finish the exposed side of each pier all the way down to the kick base.
count=0
for C in list(bpy.data.collections):
 jamb=next((o for o in C.objects if o.name.startswith('Inset window jamb return')),None)
 if not jamb:continue
 m=jamb.data.materials[0]
 for x in [-.982,.982]:box('073 kick side column return',(x,.073,.28),(.018,.146,.52),m,.001)
 count+=2
changes['window_side_returns']=count
# Reusable four-anchor plate and gusset. Local -Y points out from wall.
C=bpy.data.collections.new('KIT | 073 bolted wall shoe');C.asset_mark();C['part_id']='bolted_wall_shoe';C['interface']='wall Y=0; outward -Y; arm centered Z=0; four anchors, two gussets'
box('073 anchor backplate',(0,-.035,0),(.58,.07,.5),metal,.02)
for x in [-.205,.205]:
 for z in [-.16,.16]:
  # Twelve-sided washer and hexagonal head, axes perpendicular to wall.
  for N,r,y,thick,ma in [(12,.064,-.083,.015,steel),(6,.045,-.11,.035,metal)]:
   vs=[(x+r*math.cos(i*math.tau/N),y+j*thick,z+r*math.sin(i*math.tau/N)) for j in [0,1] for i in range(N)]
   mesh('073 anchor washer' if N==12 else '073 hex anchor',vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],ma,.002)
for x in [-.095,.095]:prism('073 bracket gusset',x-.025,x+.025,[(-.07,-.2),(-.37,-.055),(-.07,-.055)],metal)
shoe=C
# Existing world-axis standoffs: extend to receiving facade where that facade was inset.
C=bpy.data.collections.new('073 wall fastenings');s.collection.children.link(C);mounts=0
for ob in list(s.objects):
 if ob.type!='MESH' or ob.hide_render or not ob.name.startswith(('Riser wall standoff','Duct wall saddle','U return extended wall mount','Companion standoff')):continue
 pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2;z=(lo[2]+hi[2])/2;side=1 if x>0 else -1;wall=hi[0] if side>0 else lo[0]
 if side>0 and 6<y<17.2:
  wall=10.15
  # Fill only missing length between existing arm and actual receiving wall.
  if hi[0]<wall:box('073 standoff wall extension',((hi[0]+wall)/2,y,z),(wall-hi[0],hi[1]-lo[1],hi[2]-lo[2]),steel)
 q=bpy.data.objects.new('073 bolted wall shoe',None);q.instance_type='COLLECTION';q.instance_collection=shoe;C.objects.link(q);q.matrix_world=Matrix.Translation((wall,y,z))@Matrix.Rotation(-side*math.pi/2,4,'Z');mounts+=1
changes['wall_shoes']=mounts
# Panel-specific metal with mottled iron corrosion (separate from facade coating).
rust=metal.copy();rust.name='073 rusty sheet metal access panel';nt=rust.node_tree
for em in [n for n in nt.nodes if n.type=='EMISSION' and n.inputs[0].is_linked]:
 src=em.inputs[0].links[0].from_socket;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=13;noise.inputs['Detail'].default_value=3
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.50;ramp.color_ramp.elements[1].position=.68;nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(ramp.outputs[0],mix.inputs[0]);nt.links.new(src,mix.inputs[1]);mix.inputs[2].default_value=(.17,.059,.026,1);nt.links.new(mix.outputs[0],em.inputs[0])
for col in bpy.data.collections:
 if 'access_insert' not in col.name:continue
 for ob in col.objects:
  if ob.type=='MESH' and 'surround' not in ob.name.lower() and 'screw' not in ob.name.lower() and 'slot' not in ob.name.lower():
   ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(rust)
# Floor-band ends are embedded into broad structural blades; give them explicit
# narrow collars at the receiving face, not smooth coincident intersections.
for C in list(bpy.data.collections):
 core=next((o for o in C.objects if o.name.startswith('Floor band core')),None)
 if not core:continue
 for x in [-1.285,1.285]:
  box('073 trim termination shadow joint',(x,-.07,.12),(.022,.36,.29),steel,.001)
  box('073 trim termination folded collar',(x+(.018 if x<0 else -.018),-.072,.12),(.035,.38,.30),metal,.003)
K=R/'art/components/facades/v073';K.mkdir(exist_ok=True);bpy.data.libraries.write(str(K/'wall-fastening.blend'),{shoe},fake_user=True)
changes['glass']='Restored exact 071 material; removed 072 planar probes';changes['soffit']='Full 0.93m projection to trim at 45 degrees';changes['crack_gradient']='55 to 100 unchanged'
(O/'changes.json').write_text(json.dumps(changes,indent=2));assert s.camera.matrix_world==camera
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.62;s.render.border_max_x=1;s.render.border_min_y=.22;s.render.border_max_y=.95;s.render.filepath=str(O/'right.png');bpy.ops.render.render(write_still=True)
