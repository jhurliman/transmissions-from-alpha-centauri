import bpy,sys,random,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from rock_masters_090 import create_rock
O=R/'art/studies/rocks-090';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-089/scene.blend'));s=bpy.context.scene;rng=random.Random(9017)
small=bpy.data.collections.new('090 Small embedded stones');large=bpy.data.collections.new('090 Larger fractured debris');s.collection.children.link(small);s.collection.children.link(large)
# The same soil exclusion prevents oversized ink outlines on subpixel grains.
for ls in s.view_layers[0].freestyle_settings.linesets:
 if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
  if small.name not in ls.collection.children:ls.collection.children.link(small)
def lin(h):
 return tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))
def mat(name,h):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;base=lin(h);df=n.new('ShaderNodeBsdfDiffuse');sr=n.new('ShaderNodeShaderToRGB');bw=n.new('ShaderNodeRGBToBW');ra=n.new('ShaderNodeValToRGB');em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(df.outputs[0],sr.inputs[0]);l.new(sr.outputs[0],bw.inputs[0]);l.new(bw.outputs[0],ra.inputs[0]);ra.color_ramp.interpolation='LINEAR'
 for e,pos,f in zip([ra.color_ramp.elements[0],ra.color_ramp.elements[1],ra.color_ramp.elements.new(.45)],[.08,.90,.45],[.40,1.3,.88]):e.position=pos;e.color=(*(min(1,c*f) for c in base),1)
 l.new(ra.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0]);return m
road=[mat('090 earth stone '+str(i),h) for i,h in enumerate(['634737','71513d','5d4638'])];bank=[mat('090 bank fragment '+str(i),h) for i,h in enumerate(['89765f','716a70','625e69','9b8267'])]
ground=bpy.data.objects['Street foundation'];deps=bpy.context.evaluated_depsgraph_get();ev=ground.evaluated_get(deps)
# Reject overlap with low architectural solids using their world-space bounds.
obstacles=[]
for ob in s.objects:
 if ob.type!='MESH' or ob.hide_render or ob==ground:continue
 if any(k in ob.name.lower() for k in ('soil','earth','scrap','rubble','stone','grain','fracture','lip')):continue
 pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];mn=np.min([v[:] for v in pts],axis=0);mx=np.max([v[:] for v in pts],axis=0)
 if mn[2]<.35 and mx[2]>.12 and mx[0]-mn[0]<5 and mx[1]-mn[1]<12:obstacles.append((mn,mx))
placed=[];counts={};families=['wedge','slab','shard','chunk','splinter']
def put(x,y,w,zone):
 if abs(x)<.85 and -3<y<1:return
 if any(mn[0]-w*.3<x<mx[0]+w*.3 and mn[1]-w*.3<y<mx[1]+w*.3 for mn,mx in obstacles):return
 hit,p,n,idx=ev.ray_cast((x,y,2),(0,0,-1))
 if not hit or p.z<-.11:return
 if w>.23 and any((x-a)**2+(y-b)**2<(w+c)**2*.16 for a,b,c in placed):return
 family=rng.choices(families,[40,25,17,10,8] if zone=='road' else [22,38,17,15,8])[0];length=w*rng.uniform(.65,1.65);height=w*rng.uniform(.22,.48) if family!='splinter' else w*.24
 ob=create_rock('090 '+zone+' '+family,family,rng.randrange(999999),(w,length,height));target=large if w>.24 else small
 for co in list(ob.users_collection):co.objects.unlink(ob)
 target.objects.link(ob);ob.rotation_euler=(rng.uniform(-.12,.12),rng.uniform(-.16,.16),rng.random()*math.tau);ob.location=(x,y,p.z-height*rng.uniform(.12,.28));ob.data.materials.clear();ob.data.materials.append(rng.choice(road if zone=='road' else bank));placed.append((x,y,w));counts[zone]=counts.get(zone,0)+1
for j in range(210):
 x=rng.uniform(-7.15,7.15);y=rng.uniform(-8,33);w=rng.uniform(.045,.14) if j>23 else rng.uniform(.17,.34);put(x,y,w,'road')
 if rng.random()<.32:
  for k in range(rng.randint(2,4)):put(x+rng.uniform(-.3,.3),y+rng.uniform(-.35,.35),rng.uniform(.025,.065),'road')
for j in range(650):
 side=rng.choice([-1,1]);x=side*rng.uniform(7.45,9.15);y=rng.uniform(-7,33);w=rng.uniform(.04,.19);put(x,y,w,'bank')
for side in [-1,1]:
 for y0 in [-4.8,1.4,7.5,15,23.5,30]:
  for j in range(rng.randint(3,6)):
   x=side*rng.uniform(8.4,9.15);y=y0+rng.uniform(-1,1);put(x,y,rng.uniform(.25,.75),'bank')
(O/'scatter-audit.json').write_text(json.dumps({'counts':counts,'total':len(placed),'seed':9017,'soil_unchanged':True,'contact':'native road raycast, partial burial, architecture exclusion'},indent=2));s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.03;s.render.border_max_x=.42;s.render.border_min_y=.14;s.render.border_max_y=.52;s.render.filepath=str(O/'road-detail.png');bpy.ops.render.render(write_still=True)
