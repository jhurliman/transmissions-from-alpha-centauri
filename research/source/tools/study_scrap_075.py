import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; O=R/'art/studies/scrap-075';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-074/scene.blend'));s=bpy.context.scene
s.render.threads_mode='FIXED';s.render.threads=4
random.seed(75031)
K=bpy.data.collections.new('KIT | 075 battered scrap masters'); C=bpy.data.collections.new('075 Scrap integration');s.collection.children.link(C)
def material(name,base):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');dif=n.new('ShaderNodeBsdfDiffuse');dif.inputs['Color'].default_value=(.65,.65,.65,1);rgb=n.new('ShaderNodeShaderToRGB');l.new(dif.outputs[0],rgb.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT'
 stops=[(.0,.26),(.28,.57),(.51,1),(.77,1.38)]
 for j,(pos,mult) in enumerate(stops):
  e=r.color_ramp.elements[j] if j<2 else r.color_ramp.elements.new(pos);e.position=pos;e.color=tuple(min(.9,v*mult) for v in base)+(1,)
 l.new(rgb.outputs[0],r.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=10;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.78
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.40;ramp.color_ramp.elements[0].color=(.42,.42,.42,1);ramp.color_ramp.elements[1].position=.55;ramp.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=.55;l.new(r.outputs[0],mul.inputs[1]);l.new(ramp.outputs[0],mul.inputs[2]);em=n.new('ShaderNodeEmission');l.new(mul.outputs[0],em.inputs[0]);g=n.new('ShaderNodeBsdfGlossy');g.inputs['Color'].default_value=(.64,.50,.42,1);g.inputs['Roughness'].default_value=.24;mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.15;l.new(em.outputs[0],mix.inputs[1]);l.new(g.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0]);return m
steel=material('075 Scrap | unified violet iron',(.055,.049,.069));edge=material('075 Scrap | worn rim',(.24,.19,.19));rust=material('075 Scrap | muted oxidized metal',(.12,.073,.062));stone=material('075 Scrap | mineral dusty slate',(.18,.16,.16))
source=bpy.data.materials.get('DUCT | muted blue-gray sheet')
if source:
 steel=source.copy();steel.name='075 Scrap | accepted service metal darkened'
 nt=steel.node_tree
 for emission in [n for n in nt.nodes if n.type=='EMISSION' and n.inputs['Color'].is_linked]:
  sock=emission.inputs['Color'].links[0].from_socket;grade=nt.nodes.new('ShaderNodeMixRGB');grade.blend_type='MULTIPLY';grade.inputs[0].default_value=1;grade.inputs[2].default_value=(.52,.47,.53,1);nt.links.new(sock,grade.inputs[1]);nt.links.new(grade.outputs[0],emission.inputs['Color'])
def mesh(n,vs,fs,mat=steel):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(n,me);K.objects.link(ob);me.materials.append(mat);return ob
# Bent sheet/channel masters: each has real shell thickness and two physically bent folds.
masters=[]
for j in range(12):
 rng=random.Random(751+j);length=rng.uniform(.9,2.1);w=rng.uniform(.32,.85);vs=[];sections=7
 for i in range(sections):
  y=(i/(sections-1)-.5)*length;z=.06*math.sin(i*1.9+j)+max(0,i-3)*rng.uniform(.045,.11);shift=.07*math.sin(i+j)
  cross=[(-w/2,.13 if j%3 else .04),(-w*.36,0),(w*.32,0),(w/2,.10 if j%3 else .025)]
  for k,(x,dz) in enumerate(cross):vs.append((x+shift,y+rng.uniform(-.06,.06)*(i in [0,6]),z+dz))
 fs=[(i*4+k,i*4+k+1,(i+1)*4+k+1,(i+1)*4+k) for i in range(sections-1) for k in range(3)]
 ob=mesh('075 master folded channel %02d'%j,vs,fs);sol=ob.modifiers.new('Actual folded sheet thickness','SOLIDIFY');sol.thickness=.028;be=ob.modifiers.new('Worn fold chamfer','BEVEL');be.width=.014;be.segments=1;masters.append(ob)
# Hollow deformed pipe/duct fragments; battered rim has varying axial length.
for j in range(7):
 rng=random.Random(830+j);N=12 if j<4 else 4;r=.22 if j<4 else .34;L=rng.uniform(.55,1.2);vs=[]
 for k in range(4):
  rr=r-(.035 if k>=2 else 0);top=k%2
  for i in range(N):
   a=i*math.tau/N;vs.append((rr*math.cos(a)*(1+.1*math.sin(a*3+j)),rr*math.sin(a),top*(L+(.13 if i==2 else -.08 if i==3 else .012*math.sin(i+j)))+(.08*top*math.sin(a))))
 fs=[]
 for i in range(N):
  q=(i+1)%N;fs.extend([(i,q,N+q,N+i),(2*N+i,3*N+i,3*N+q,2*N+q),(N+i,N+q,3*N+q,3*N+i),(i,2*N+i,2*N+q,q)])
 ob=mesh('075 master torn hollow casing %02d'%j,vs,fs);be=ob.modifiers.new('Bent rim light catch','BEVEL');be.width=.012;be.segments=1;masters.append(ob)
# Closed battered housing fragments, never smooth cube scatter.
for j in range(5):
 rng=random.Random(950+j);vs=[(-.5,-.35,0),(.5,-.3,0),(.41,.4,0),(-.45,.35,0),(-.35,-.3,.32),(.43,-.2,.22),(.24,.28,.45),(-.4,.24,.36)]
 vs=[(x*rng.uniform(.8,1.2),y*rng.uniform(.8,1.2),z) for x,y,z in vs];ob=mesh('075 master fractured casing %02d'%j,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4),(3,4,7),(4,5,6),(4,6,7)]);be=ob.modifiers.new('Battered edge chamfer','BEVEL');be.width=.025;be.segments=1;masters.append(ob)
# Add reusable stamped ribs and fastening remnants to the twelve folded masters.
def append_shape(vs,fs,adds,faces):
 off=len(vs);vs.extend(adds);fs.extend([tuple(off+i for i in face) for face in faces])
for j,ob in enumerate(masters[:12]):
 original=[v.co.copy() for v in ob.data.vertices]
 # Evaluate shell so ribs/fasteners become part of the editable finished master mesh.
 temp=bpy.data.collections.new('075 temporary evaluation');s.collection.children.link(temp);temp.objects.link(ob)
 bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()));temp.objects.unlink(ob);bpy.data.collections.remove(temp)
 ob.modifiers.clear();vs=[tuple(v.co) for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons]
 for alpha in [.22,.78]:
  pts=[original[i*4+1].lerp(original[i*4+2],alpha)+Vector((0,0,.025)) for i in range(7)]
  adds=[]
  for p in pts:
   adds.extend([tuple(p+Vector((dx,0,dz))) for dx,dz in [(-.027,0),(.027,0),(.018,.036),(-.018,.036)]])
  faces=[(i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k) for i in range(6) for k in range(4)]+[(0,3,2,1),(24,25,26,27)]
  append_shape(vs,fs,adds,faces)
 for row in [1,4]:
  for side in [0,3]:
   p=original[row*4+side]+Vector((0,0,.035));adds=[]
   for z,r in [(0,.05),(.025,.05),(.05,.037)]:
    adds.extend([tuple(p+Vector((r*math.cos(i*math.tau/6),r*math.sin(i*math.tau/6),z))) for i in range(6)])
   faces=[(k*6+i,k*6+(i+1)%6,(k+1)*6+(i+1)%6,(k+1)*6+i) for k in range(2) for i in range(6)]+[tuple(range(12,18)),tuple(range(5,-1,-1))];append_shape(vs,fs,adds,faces)
 out=bpy.data.meshes.new(ob.name+' ribbed shell');out.from_pydata(vs,[],fs);out.materials.append(steel);ob.data=out
 be=ob.modifiers.new('Stamped edges','BEVEL');be.width=.006;be.segments=1
# Three severed service remnants retain flanged mouths and bolt remnants.
for ob in masters[12:15]:
 vs=[tuple(v.co) for v in ob.data.vertices];fs=[tuple(p.vertices) for p in ob.data.polygons];N=24;adds=[]
 for z,r in [(0,.31),(.075,.31),(0,.185),(.075,.185)]:
  adds.extend([(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for i in range(N)])
 faces=[]
 for i in range(N):
  k=(i+1)%N;faces.extend([(i,k,N+k,N+i),(N+i,N+k,3*N+k,3*N+i),(2*N+i,3*N+i,3*N+k,2*N+k),(i,2*N+i,2*N+k,k)])
 append_shape(vs,fs,adds,faces)
 for j in range(6):
  x=.26*math.cos(j*math.tau/6);y=.26*math.sin(j*math.tau/6);adds=[(x+.036*math.cos(i*math.tau/6),y+.036*math.sin(i*math.tau/6),z) for z in [-.03,0] for i in range(6)];faces=[(i,(i+1)%6,6+(i+1)%6,6+i) for i in range(6)]+[tuple(range(5,-1,-1)),tuple(range(6,12))];append_shape(vs,fs,adds,faces)
 me=bpy.data.meshes.new(ob.name+' flanged mouth');me.from_pydata(vs,[],fs);me.materials.append(steel);ob.data=me
rim=bpy.data.materials.new('075 Scrap | exposed rim physical specular');rim.use_nodes=True
pr=rim.node_tree.nodes.get('Principled BSDF');pr.inputs['Base Color'].default_value=(.18,.15,.16,1);pr.inputs['Metallic'].default_value=.72;pr.inputs['Roughness'].default_value=.24
for o in masters:
 o.data.materials.append(rim)
 for mod in o.modifiers:
  if mod.type=='BEVEL':mod.material=len(o.data.materials)-1;mod.width=max(mod.width,.014)
 o.asset_mark()
def instance(m,p,rot,scale=1,mat=None):
 o=m.copy();o.name='075 assembled '+m.name;C.objects.link(o);o.location=p;o.rotation_euler=rot;o.scale=(scale,scale,scale)
 if mat:o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(mat)
 return o
# Three interlocking lobes; no evenly distributed wall of rocks.
for cx,cy,span,num in [(-3.7,-8.65,2.1,44),(0,-8.95,2.1,32),(3.7,-8.55,2.1,44)]:
 for j in range(num):
  x=cx+random.uniform(-span,span);y=cy+random.uniform(-.45,.48);z=.12+random.uniform(0,.6)*(1-abs(x-cx)/span)
  m=masters[j%len(masters)];scale=random.uniform(.55,1.05);o=instance(m,(x,y,z),(random.uniform(-.25,.8),random.uniform(-.5,.5),random.uniform(-math.pi,math.pi)),scale)
  
  if 12<=j%len(masters)<19:o.rotation_euler.x=random.uniform(1.0,1.75)
  o['zone']='near';o['family']='sheet_metal_scrap'
# Deliberately composed large anchors interrupt the medium-size distribution.
for idx,p,rot,scale in [(4,(-4.9,-8.45,.30),(.38,.22,.8),1.75),(12,(-4.1,-8.05,.80),(-1.8,.08,.30),1.65),(8,(2.7,-8.7,.27),(.45,-.22,-.8),1.65),(13,(4.2,-8.10,.65),(-2.4,.08,-.30),1.2375),(14,(-.5,-8.50,.40),(-2.6,0,0),.87)]:
 ob=instance(masters[idx],p,rot,scale);ob['zone']='near';ob['family']='hero anchor'
for cx,cy in [(-4.2,29),(3.8,30.8),(-1.8,33.5),(5.4,34)]:
 for j in range(22):
  m=random.choice(masters);o=instance(m,(cx+random.uniform(-1.8,1.8),cy+random.uniform(-1.1,1.1),random.uniform(.02,.25)),(random.uniform(-.3,.6),random.uniform(-.4,.4),random.uniform(-math.pi,math.pi)),random.uniform(.6,1.3),random.choice([steel,steel,rust,stone]));o['zone']='end'
  if 'torn hollow casing' in o.name:o.rotation_euler.x=1.35
hide=['Broken thin steel web','Girder parallel flange','Torn foreground cladding','Foreground broken structure','Broken foreground hollow pipe','Fallen I girder web','Fallen girder flange','Midground rubble pile','Midground overlapping rubble','Foreground concrete fragment','Foreground broken girder','Hollow foreground pipe']
hidden=[]
for ob in s.objects:
 if ob.name.startswith(tuple(hide)):ob.hide_render=True;hidden.append(ob.name)
bpy.data.libraries.write(str(O/'kit.blend'),{K,C},fake_user=True)
(O/'integration.json').write_text(json.dumps({'collection':C.name,'masters':K.name,'hide_old_prefixes':hide,'hidden_objects':len(hidden),'near_instances':125,'end_instances':88,'ground_datum':0,'preserved':'074 buildings, camera, service materials; only designated rubble prefixes hidden'},indent=2))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2160;s.render.resolution_y=1620;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=0;s.render.border_max_y=.25;s.render.filepath=str(O/'near.png');bpy.ops.render.render(write_still=True)
s.render.border_min_x=.25;s.render.border_max_x=.75;s.render.border_min_y=.42;s.render.border_max_y=.66;s.render.filepath=str(O/'end.png');bpy.ops.render.render(write_still=True)
# Isolated six masters, same native materials and lighting; integration collection hidden for catalogue.
for ob in list(s.objects):
 if ob.type!='LIGHT' and ob!=s.camera:ob.hide_render=True
P=bpy.data.collections.new('075 six component proof');s.collection.children.link(P)
for j,idx in enumerate([0,4,8,12,16,20]):
 ob=masters[idx].copy();P.objects.link(ob);ob.location=((j%3-1)*2.5,(j//3)*2.7,0);ob.rotation_euler=(.1,.05,.3);ob.hide_render=False
 if idx==12:ob.rotation_euler.x=-1.9;ob.location.z=.4
s.render.film_transparent=True;s.camera.location=(5,-8,7);s.camera.rotation_euler=(Vector((0,1.1,.25))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=9;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'components.png');bpy.ops.render.render(write_still=True)
