import bpy,math,random,bmesh
from mathutils import Vector
rng=random.Random(7707)
def apply(s):
 ground=bpy.data.objects['Street foundation'];ma=ground.data.materials[0];nt=ma.node_tree;n=nt.nodes;l=nt.links
 # Disable old cellular seams: feed grain directly into its multiply stage.
 for nd in n:
  if nd.type=='MIX_RGB' and nd.blend_type=='MULTIPLY' and tuple(round(x,2) for x in nd.inputs[2].default_value[:3])==(.42,.4,.44):
   for link in list(nd.inputs[0].links):l.remove(link)
   nd.inputs[0].default_value=0
 # Sparse multiscale pigment grit within the material, not inked point geometry.
 em0=next(x for x in n if x.type=='EMISSION');base0=em0.inputs[0].links[0].from_socket
 co=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeTexVoronoi');v.inputs['Scale'].default_value=18;l.new(co.outputs['Object'],v.inputs[0]);less=n.new('ShaderNodeMath');less.operation='LESS_THAN';less.inputs[1].default_value=.34;l.new(v.outputs['Distance'],less.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';l.new(less.outputs[0],mul.inputs[0]);l.new(base0,mul.inputs[1]);mul.inputs[2].default_value=(.47,.43,.40,1);l.new(mul.outputs[0],em0.inputs[0])
 # Copy complete earth material into the recesses, darkening by real depth.
 inner=ma.copy();inner.name='077 earth fracture interior';ns=inner.node_tree.nodes;lk=inner.node_tree.links
 em=next(x for x in ns if x.type=='EMISSION');base=em.inputs[0].links[0].from_socket
 geo=ns.new('ShaderNodeNewGeometry');sep=ns.new('ShaderNodeSeparateXYZ');lk.new(geo.outputs['Position'],sep.inputs[0]);r=ns.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=-.04;r.inputs['From Max'].default_value=-.10;r.inputs['To Min'].default_value=.38;r.inputs['To Max'].default_value=.08;lk.new(sep.outputs['Z'],r.inputs[0]);mx=ns.new('ShaderNodeMixRGB');mx.blend_type='MULTIPLY';mx.inputs[0].default_value=1;lk.new(base,mx.inputs[1]);lk.new(r.outputs[0],mx.inputs[2]);lk.new(mx.outputs[0],em.inputs[0])
 ground.data.materials.append(inner)
 bpy.context.view_layer.objects.active=ground
 bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free()
 # Sparse light-dependent mineral lip response; not permanent bright outlines.
 for material in []:
  ns=material.node_tree.nodes;lk=material.node_tree.links;em=next(x for x in ns if x.type=='EMISSION');base=em.inputs[0].links[0].from_socket
  gl=ns.new('ShaderNodeBsdfGlossy');gl.inputs['Color'].default_value=(1,1,1,1);gl.inputs['Roughness'].default_value=.32;sr=ns.new('ShaderNodeShaderToRGB');lk.new(gl.outputs[0],sr.inputs[0]);bw=ns.new('ShaderNodeRGBToBW');lk.new(sr.outputs[0],bw.inputs[0]);mp=ns.new('ShaderNodeMapRange');mp.clamp=True;mp.inputs['From Min'].default_value=.20;mp.inputs['From Max'].default_value=.7;mp.inputs['To Max'].default_value=.26;lk.new(bw.outputs[0],mp.inputs[0]);mx=ns.new('ShaderNodeMixRGB');lk.new(mp.outputs[0],mx.inputs[0]);lk.new(base,mx.inputs[1]);mx.inputs[2].default_value=(.28,.17,.105,1);lk.new(mx.outputs[0],em.inputs[0])
 C=bpy.data.collections.new('077 Soil fractures and mineral scatter');s.collection.children.link(C)
 for oldc in list(ground.users_collection):oldc.objects.unlink(ground)
 C.objects.link(ground)
 # Triangular cutters make shallow V openings; direction persists between sparse bends.
 paths=[]
 for i in range(15):
  angle=[-.06,.09,-.1,.04,.12,-.08,.02][i] if i<7 else rng.choice([math.pi/2,math.pi/2,math.pi/4,-math.pi/4]);start=Vector((-6.5,[-8,-4.2,2.1,10.3,14.8,23.9,29][i])) if i<7 else Vector((rng.uniform(-5.8,5.8),rng.uniform(-8,24)));length=rng.uniform(10,13) if i<7 else rng.uniform(3,7);steps=max(4,int(length/.24));pts=[]
  for k in range(steps+1):
   t=k/steps;v=start+Vector((math.cos(angle),math.sin(angle)))*length*t+Vector((-math.sin(angle),math.cos(angle)))*(.18*math.sin(t*5+i)+rng.uniform(-.045,.045));pts.append(v)
  paths.append(pts)
 for j,pts in enumerate(paths):
  verts=[];faces=[];width=rng.uniform(.07,.12)
  for k,p in enumerate(pts):
   d=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)];d.normalize();side=Vector((-d.y,d.x));w=width*rng.uniform(.25,1.4)*(0.4+0.6*abs(math.sin(k*.37+j)))*(min(1,(k+1)/2,(len(pts)-k)/2));depth=rng.uniform(.035,.06)
   for x,y,z in [(p.x-side.x*w,p.y-side.y*w,.035),(p.x+side.x*w,p.y+side.y*w,.035),(p.x,p.y,-.04-depth)]:verts.append((x,y,z))
  faces.append((2,1,0));last=3*(len(pts)-1);faces.append((last,last+1,last+2))
  for k in range(len(pts)-1):
   a=3*k;b=a+3
   for t in range(3):faces.append((a+t,a+(t+1)%3,b+(t+1)%3,b+t))
  mesh=bpy.data.meshes.new('077 fracture cutter');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();ob=bpy.data.objects.new('077 fracture cutter',mesh);C.objects.link(ob)
  mesh.materials.append(ma);mesh.materials.append(inner)
  for p in mesh.polygons:p.material_index=1
  bpy.context.view_layer.objects.active=ground;mod=ground.modifiers.new('077 shallow directional V fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob
  bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free();bpy.data.objects.remove(ob,do_unlink=True)
 # Broken, shallow earth lips create actual normal/light variation along fracture banks.
 for pts in paths:
  for k in range(len(pts)-1):
   if rng.random()<.3:continue
   p=pts[k];q=pts[k+1];d=q-p;d.normalize();side=Vector((-d.y,d.x));w=.045;outer=rng.uniform(.07,.13)
   vs=[]
   for v in [p,q]:
    for offset,z in [(w,-.039),(outer,-.023),(outer+.04,-.04)]:vs.append((v.x+side.x*offset,v.y+side.y*offset,z))
   me=bpy.data.meshes.new('077 broken earth lip');me.from_pydata(vs,[],[(0,3,4,1),(1,4,5,2)]);me.materials.append(ma);ob=bpy.data.objects.new(me.name,me);C.objects.link(ob)
 # Avoid minimum-width ink on subpixel stones; actual shadows describe them.
 for ls in s.view_layers[0].freestyle_settings.linesets:
  ls.select_by_collection=True;ls.collection=C;ls.collection_negation='EXCLUSIVE'
 # Replace 075 mineral scatter only, preserving all scrap and building geometry.
 for ob in list(s.objects):
  if ob.name.startswith('075 irregular embedded mineral'):ob.hide_render=True
 source=bpy.data.materials['075 mineral 0'];families=[]
 def lin(h):
  return tuple(((int(h[i:i+2],16)/255+.055)/1.055)**2.4 for i in (0,2,4))
 for idx,h in enumerate(['634737','71503a','594133','92765b','76665d','a08a70','685c59']):
  m=source.copy();m.name='077 soil stone '+str(idx)
  for nd in m.node_tree.nodes:
   if nd.type=='RGB':nd.outputs[0].default_value=(*lin(h),1)
  families.append(m)
 def stone(x,y,size,light):
  vs=[]
  for j in range(12):
   a=math.tau*(j%6)/6+rng.uniform(-.2,.2);rr=size*rng.uniform(.5,1);vs.append((x+math.cos(a)*rr,y+math.sin(a)*rr*rng.uniform(.7,1.4),-.065 if j<6 else -.04+rng.uniform(.45,.85)*size))
  me=bpy.data.meshes.new('077 embedded stone');bm=bmesh.new();v=[bm.verts.new(p) for p in vs];bmesh.ops.convex_hull(bm,input=v);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);C.objects.link(o)
  family=rng.choice([3,4,5,6]) if light else rng.choice([0,0,1,2]);me.materials.append(families[family]);me.materials.append(families[2 if not light else 4]);me.materials.append(families[1 if not light else 5])
  for face in me.polygons:face.material_index=1 if face.normal.x>.4 else (2 if face.normal.z>.75 and rng.random()<.5 else 0)
 for i in range(1500):
  light=i<1000
  x=rng.choice([-1,1])*rng.uniform(7.25,9.0) if light else rng.uniform(-7.2,7.2);y=rng.uniform(-9,32)
  if abs(x)<.85 and -3<y<1:continue
  size=rng.uniform(.025,.085)
  if light:
   size*=1+max(0,abs(x)-7.5)*1.7
   if rng.random()<.06:size*=1.5
  elif rng.random()<.07:size*=1.5
  stone(x,y,size,light)
 return {'directional_grooves':len(paths),'rock_attempts':1500,'native_boolean_ground':True}
if __name__=='__main__':
 from pathlib import Path
 R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-077';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;apply(s);s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
