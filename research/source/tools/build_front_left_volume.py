"""Section-driven front-left architecture, preserving approved service geometry."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-033';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-031/scene.blend'));s=bpy.context.scene
cam=[list(v) for v in s.camera.matrix_world];lens=s.camera.data.lens
old=bpy.data.collections['027 Reviewed architecture assembly']
# Track all existing objects and native mesh coordinates; changes are confined to visibility of selected facade objects.
def sig(o):return ([list(v) for v in o.matrix_world],len(o.data.vertices) if o.type=='MESH' else 0)
snapshot={o.name:sig(o) for o in s.objects};hidden=[]
keys={'layout_broad','layout_access','layout_transition','slot_wall','floor_band','column_recessed_4m8'}
for ob in old.objects:
 hide=False
 if ob.instance_collection and ob.instance_collection.get('part_id') in keys and ob.location.x<0 and -8.1<ob.location.y<.41:hide=True
 if ob.type=='MESH' and ob.name.startswith(('Building structural backing','Building side return','Return horizontal joint','Vertical structural pier','Ground bay plinth')):
  pts=[ob.matrix_world@v.co for v in ob.data.vertices];cx=sum(p.x for p in pts)/len(pts);cy=sum(p.y for p in pts)/len(pts)
  if cx<0 and -8.1<cy<.41:hide=True
 if hide:ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
C=bpy.data.collections.new('033 Front left section architecture');s.collection.children.link(C)
kit=bpy.data.collections.new('FAC | front_left_section');kit.asset_mark();kit['part_id']='front_left_section';host=bpy.data.objects.new('Front-left section instance',None);host.instance_type='COLLECTION';host.instance_collection=kit;C.objects.link(host)
M=Matrix.Translation((-7.65,-3.8,0))@Matrix.Rotation(math.pi/2,4,'Z');host.matrix_world=M
paint=bpy.data.materials['Cladding | slate enamel'];pale=bpy.data.materials['Cladding | pale mineral blue'];steel=bpy.data.materials['Structure | charcoal steel'];dark=bpy.data.materials['Recess | dark backing'];concrete=bpy.data.materials['Structure | bare mineral']
def mesh(n,vs,fs,m,transform=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);ob=bpy.data.objects.new(n,me);kit.objects.link(ob);ob.matrix_world=transform or Matrix.Identity(4);be=ob.modifiers.new('Manufactured edge','BEVEL');be.width=.012;be.segments=2;return ob
F=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
def box(n,p,d,m,transform=None):
 x,y,z=p;a,b,c=[v/2 for v in d];v=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(n,v,F,m,transform)
def prism(n,u0,u1,profile,m):
 N=len(profile);vs=[(u,d,z) for u in [u0,u1] for d,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];return mesh(n,vs,fs,m)
def panel(n,u0,u1,z0,z1,depth,m=paint,transform=None):
 gap=.022;return box(n,((u0+u1)/2,depth+.04,(z0+z1)/2),(u1-u0-gap,.08,z1-z0-gap),m,transform)
# The building is an extruded section, with actual side returns rather than a decorated plane.
rake=math.radians(30);rise=2.4;run=rise*math.tan(rake);outset=-.65;shoulder_top=outset+run;top_depth=shoulder_top+.35
profile=[(.75,0),(.75,4.42),(outset,4.42),(outset,4.8),(shoulder_top,7.2),(shoulder_top,10.2),(top_depth,10.55),(top_depth,20),(3.8,20),(3.8,0)]
# Deep core closes the building; side caps expose the same front silhouette.
box('Deep structural core',(0,3.65,10),(8.4,.3,20),dark)
for u0,u1 in [(-4.2,-4.08),(4.08,4.2)]:prism('Continuous profile side return',u0,u1,profile,paint)
# Recessed base wall: larger panels within the structural frame.
for u0,u1 in [(-4.08,-2.9),(-2.9,-.15),(-.15,2.65),(2.65,4.08)]:
 for z0,z1 in [(.26,1.55),(1.55,3.2),(3.2,4.42)]:panel('Recessed base wall',u0,u1,z0,z1,.75,paint)
box('Ground plinth',(0,.74,.13),(8.4,.5,.26),concrete)
# Two heavy columns: feet, 15-degree transition, straight shaft, bearing capital.
for u in [-3.65,3.65]:
 foot_to_shaft=1.15*math.tan(math.radians(15))
 shape=[(-foot_to_shaft,.05),(-foot_to_shaft,.45),(0,1.60),(0,4.44),(.58,4.44),(.58,.05)]
 prism('Tapered column structural volume',u-.47,u+.47,shape,concrete)
 for edge in [u-.42,u+.42]:box('Column edge cladding',(edge,-.028,2.90),(.10,.10,2.84),paint)
 for z0,z1 in [(1.66,2.86),(2.98,4.18)]:
  panel('Recessed column face',u-.34,u+.34,z0,z1,.065,pale)
 for z in [1.61,2.92,4.24]:box('Column cross bearing',(u,-.035,z),(.94,.12,.10),paint)
 prism('Forty-five-degree column corbel',u-.47,u+.47,[(0,3.78),(-.65,4.43),(.58,4.43),(.58,3.78)],concrete)
 box('Column head capital',(u,-.04,4.40),(1.14,1.32,.24),pale)
# Continuous bearing belt and real horizontal underside of the projecting shoulder.
box('Shoulder underside',(0,.05,4.45),(8.4,1.4,.10),paint)
for u0,u1 in [(-4.2,-1.4),(-1.4,1.4),(1.4,4.2)]:panel('Shoulder edge belt',u0,u1,4.45,4.8,outset-.015,pale)
# Sloped face in its own tangent frame: two deeply recessed slots within broad plate fields.
S=Matrix.Translation((0,outset,4.8))@Matrix.Rotation(-rake,4,'X');L=rise/math.cos(rake)
slots=[(-2.95,-2.48),(.75,1.22)]
for u0,u1 in [(-4.08,-2.95),(-2.48,-.90),(-.90,.75),(1.22,2.64),(2.64,4.08)]:
 for z0,z1 in [(0,L*.52),(L*.52,L)]:panel('Thirty-degree shoulder panel',u0,u1,z0,z1,0,paint,S)
for u0,u1 in slots:
 bottom=.25;top=L-.25
 for z0,z1 in [(0,bottom),(top,L)]:panel('Slot head and foot',u0,u1,z0,z1,0,pale,S)
 # Four-sided deep reveals, with a recessed back and regular louvers.
 for uu in [u0+.035,u1-.035]:box('Slot reveal cheek',(uu,.23,(bottom+top)/2),(.07,.46,top-bottom),pale,S)
 for zz in [bottom,top]:box('Slot reveal end',((u0+u1)/2,.23,zz),(u1-u0,.46,.065),pale,S)
 box('Slot deep shadow',((u0+u1)/2,.47,(bottom+top)/2),(u1-u0-.10,.04,top-bottom-.06),dark,S)
 for j in range(6):box('Slot louver',((u0+u1)/2,.37,bottom+.18+j*(top-bottom-.36)/5),(u1-u0-.13,.16,.045),steel,S)
# Upper mass sits back behind the shoulder; one restrained 45-degree retreat changes the section again.
for depth,z0,z1 in [(shoulder_top,7.2,10.2),(top_depth,10.55,20)]:
 cuts=[z0]
 while cuts[-1]+1.65<z1:cuts.append(cuts[-1]+1.65)
 cuts.append(z1)
 for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
  us=[-4.08,-1.7,1.05,4.08] if i%3 else [-4.08,-2.8,-.05,2.6,4.08]
  for ua,ub in zip(us,us[1:]):panel('Upper recessed mass panel',ua,ub,a,b,depth,paint)
T=Matrix.Translation((0,shoulder_top,10.2))@Matrix.Rotation(-math.pi/4,4,'X')
for ua,ub in [(-4.08,-1.4),(-1.4,1.4),(1.4,4.08)]:panel('Forty-five-degree upper transition',ua,ub,0,.35*math.sqrt(2),0,pale,T)
# Ground-level inset access hatch adds one local event rather than filling all bays.
panel('Recessed maintenance cover',-.7,.35,.52,1.22,.68,steel)
for u in [-.58,.23]:box('Access cover fastener',(u,.655,.65),(.045,.035,.045),pale)
kit['section_rules']=json.dumps({'foot_angle':15,'main_shoulder_angle':30,'upper_transition_angle':45,'recessed_base_depth':.75,'shoulder_outset':outset,'shoulder_rise':2.4,'shoulder_setback':run,'upper_setback':top_depth,'width':8.4,'height':20,'construction':'Connected extruded section; surface panels and reveals use tangent frames'})
bpy.context.view_layer.update();assert cam==[list(v) for v in s.camera.matrix_world] and lens==s.camera.data.lens
assert all(sig(bpy.data.objects[n])==v for n,v in snapshot.items())
(O/'audit.json').write_text(json.dumps({'existing_object_transforms_and_mesh_counts_preserved':True,'camera_preserved':True,'approved_pipe_geometry_unchanged':True,'replaced_front_facade_objects':hidden,'section':json.loads(kit['section_rules'])},indent=2))
K=R/'art/components/facades/v016';K.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(K/'section-building.blend'),{kit},fake_user=True)
(K/'section-rules.json').write_text(kit['section_rules'])
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
print('FRONT_SECTION_COMPLETE')
