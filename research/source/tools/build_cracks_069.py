import bpy,bmesh,json,math,random,subprocess,hashlib,textwrap
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-069';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-068/final.blend'));s=bpy.context.scene
for m in bpy.data.materials:
 if m.use_nodes:
  for node in m.node_tree.nodes:
   if 'Depth darkness' in node.label:node.inputs['To Min'].default_value=.45
src=(R/'tools/build_cracks_064.py').read_text();start=src.index('source=target.data.materials[0]');end=src.index('\n for ob in',start)
materialcode=src[start:end];materialcode=' '+materialcode;materialcode=textwrap.dedent(materialcode).replace("m.name='064 Projected surface | '+hostName","m.name='069 Projected fracture | '+target.name")
cutcol=bpy.data.collections.new('069 editable fracture cutters');s.collection.children.link(cutcol)
selected=[];audit=[];skipped=[]
# Explicit brittle architectural candidates; folded metal sheets, services and steel excluded.
prefixes=('Ground plinth','Tapered column structural volume','Forty-five-degree column corbel','Recessed base wall','Recessed column face','Thirty-degree shoulder panel','Upper recessed mass panel','Forty-five-degree upper transition','Gallery base panel','Gallery upper quiet panel','Gallery structural blade','Utility base','Utility broad plate','Utility broad rake','Utility crown panel','Roof parapet','Column structural core','Solid concrete 45 degree support','Inset window jamb return','Inset window head return')
for host in sorted(list(s.objects),key=lambda x:x.name):
 if host.hide_render or not host.instance_collection or not host.name.startswith(('Architecture','Front-left','right_','035 | window')):continue
 candidates=[]
 for target in host.instance_collection.objects:
  if target.type!='MESH' or not target.name.startswith(prefixes) or any(m.name.startswith('059 localized') for m in target.modifiers):continue
  seed=int(hashlib.sha256((host.name+target.name).encode()).hexdigest()[:8],16);rng=random.Random(seed)
  chance=.65 if host.name.startswith(('Front-left','right_')) else .35
  if rng.random()>chance:continue
  world=host.matrix_world @ target.matrix_world;faces=[]
  for f in target.data.polygons:
   if len(f.vertices)<4 or f.area<.12:continue
   n=(world.to_3x3().inverted().transposed() @ f.normal).normalized();c=world @ f.center;screen=world_to_camera_view(s,s.camera,c)
   if not (.015<screen.x<.985 and .04<screen.y<.98 and screen.z>0) or n.dot((s.camera.location-c).normalized())<.25 or abs(n.z)>.95:continue
   faces.append((f.area*n.dot((s.camera.location-c).normalized()),f.index))
  if faces:candidates.append((target,max(faces)[1],seed))
 if not candidates:continue
 old=host.instance_collection;col=bpy.data.collections.new('069 unique | '+host.name);mapping={}
 for oldob in old.objects:
  ob=oldob.copy();col.objects.link(ob);mapping[oldob]=ob
 host.instance_collection=col
 for oldob,faceid,seed in candidates:selected.append((host,mapping[oldob],faceid,seed))
# Direct meshes form the warm side-road elevation, outside the prefab instances.
from types import SimpleNamespace
from mathutils import Matrix
for target in list(s.objects):
 if target.type!='MESH' or target.hide_render or not target.name.startswith(('Road-facing broad panel','Road window surround','Road window upper field','Road elevation structural pilaster','Road portal jamb','Service bay lintel','Side road broad end cladding','End wall upper grouped panel')):continue
 seed=int(hashlib.sha256(target.name.encode()).hexdigest()[:8],16);rng=random.Random(seed)
 if rng.random()>.65:continue
 world=target.matrix_world;faces=[]
 for f in target.data.polygons:
  if len(f.vertices)<4 or f.area<.12:continue
  n=(world.to_3x3().inverted().transposed() @ f.normal).normalized();c=world @ f.center;screen=world_to_camera_view(s,s.camera,c)
  if .005<screen.x<.995 and .02<screen.y<.98 and screen.z>0 and n.dot((s.camera.location-c).normalized())>.25 and abs(n.z)<.95:faces.append((f.area*n.dot((s.camera.location-c).normalized()),f.index))
 if faces:selected.append((SimpleNamespace(name='Warm road elevation',matrix_world=Matrix.Identity(4)),target,max(faces)[1],seed))
print('CANDIDATES',len(selected),flush=True)
for host,target,faceid,seed in selected:
 rng=random.Random(seed);target.data=target.data.copy();f=target.data.polygons[faceid];world=host.matrix_world @ target.matrix_world;n=f.normal.copy();origin=f.center.copy()
 vs=[target.data.vertices[i].co for i in f.vertices];v=Vector((0,0,1));v-=n*v.dot(n)
 if v.length<.1:continue
 v.normalize();u=v.cross(n).normalized();us=[(p-origin).dot(u) for p in vs];zs=[(p-origin).dot(v) for p in vs];umin,umax=min(us),max(us);vmin,vmax=min(zs),max(zs);W=umax-umin;H=vmax-vmin
 if min(W,H)<.18:continue
 family='pier' if H/W>2.1 else 'panel';support=target.name.startswith('Solid concrete')
 j=(rng.uniform(.3,.7),rng.uniform(.3,.7));routes=[]
 if support:
  z=rng.choice([rng.uniform(.08,.23),rng.uniform(.77,.91)]);routes=[((0,z),(1,min(.98,z+rng.uniform(-.08,.08))))]
 elif family=='pier':
  routes=[((rng.uniform(.2,.8),0),j),(j,(rng.uniform(.2,.8),1))]
  if rng.random()<.65:routes.append((j,(rng.choice([0,1]),rng.uniform(.15,.85))))
 else:
  routes=[((0,rng.uniform(.08,.4)),j),(j,(1,rng.uniform(.6,.95)))]
  if rng.random()<.7:routes.append((j,(rng.uniform(.15,.85),rng.choice([0,1]))))
 payload={'paths':[]}
 for k,(aa,bb) in enumerate(routes):
  delta=Vector(bb)-Vector(aa);side=Vector((-delta.y,delta.x)).normalized();N=max(9,int((Vector((delta.x*W,delta.y*H))).length/.065));N=min(N,45);coords=[];widths=[];walk=0
  for i in range(N+1):
   t=i/N;walk=.3*walk+rng.uniform(-1,1);q=Vector(aa).lerp(Vector(bb),t);offset=(.018*walk+.013*math.sin(t*math.pi*7+seed%20))*math.sin(math.pi*t);q+=Vector((side.x*min(W,H)/W,side.y*min(W,H)/H))*offset;coords.append([q.x*W,q.y*H]);w=rng.uniform(.0035,.007)*(1 if k<2 else .6)
   for endpoint in [aa,bb]:
    if 0 in endpoint or 1 in endpoint:w+=.010*math.exp(-math.dist(coords[-1],[endpoint[0]*W,endpoint[1]*H])/.035)
   widths.append(w)
  for i,other in [(0,1),(-1,-2)]:
   if min(coords[i][0],W-coords[i][0],coords[i][1],H-coords[i][1])<.001:
    d=(Vector(coords[i])-Vector(coords[other])).normalized();coords[i]=list(Vector(coords[i])+d*.022)
  payload['paths'].append({'points':coords,'widths':widths})
 ident=str(len(audit))+ '-' +str(seed);req=O/(ident+'-paths.json');res=O/(ident+'-mesh.json');req.write_text(json.dumps(payload));subprocess.run(['/tmp/crack060-env/bin/python',str(R/'tools/fracture_mesh_061.py'),str(req),str(res)],check=True);data=json.loads(res.read_text())
 # Limit depth by the solid's extent along its local face normal.
 extent=max(p.co.dot(n) for p in target.data.vertices)-min(p.co.dot(n) for p in target.data.vertices);cap=min(.035,extent*.25);depth=max(-p[2] for p in data['vertices']);factor=min(1,cap/max(depth,.00001));depth*=factor
 if depth<.0002:continue
 a={'center':list(world @ origin),'normal':list((world.to_3x3().inverted().transposed() @ n).normalized())};hostName=host.name
 exec(materialcode)
 # Depth-weighted material darkening, leaving mouth reflection alone.
 nt=m.node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry');sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],sub.inputs[0]);sub.inputs[1].default_value=a['center'];dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=tuple(-z for z in a['normal']);ramp=nt.nodes.new('ShaderNodeMapRange');ramp.label='069 Depth darkness';ramp.clamp=True;nt.links.new(dot.outputs['Value'],ramp.inputs[0]);ramp.inputs['From Max'].default_value=depth;ramp.inputs['To Min'].default_value=.45;ramp.inputs['To Max'].default_value=0
 for em in [x for x in nt.nodes if x.type=='EMISSION' and x.outputs[0].is_linked]:
  color=em.inputs['Color'];mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
  if color.is_linked:nt.links.new(color.links[0].from_socket,mul.inputs[1])
  else:mul.inputs[1].default_value=color.default_value
  nt.links.new(ramp.outputs[0],mul.inputs[2]);nt.links.new(mul.outputs[0],color)
 verts=[tuple(origin+u*(umin+x)+v*(vmin+y)+n*(z*factor if z<0 else z)) for x,y,z in data['vertices']];me=bpy.data.meshes.new('069 cutter mesh');me.from_pydata(verts,[],data['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();c=bpy.data.objects.new('069 cutter | '+target.name,me);cutcol.objects.link(c);c.matrix_world=target.matrix_world.copy();c.hide_render=True;c.hide_set(True)
 idx=len(target.data.materials);target.data.materials.append(m)
 for mat in target.data.materials:c.data.materials.append(mat)
 for face in c.data.polygons:face.material_index=idx
 mod=target.modifiers.new('069 localized fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.context.view_layer.update()
 ev=target.evaluated_get(bpy.context.evaluated_depsgraph_get());check=ev.to_mesh();bm=bmesh.new();bm.from_mesh(check);nonman=sum(not e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume());bm.free();ev.to_mesh_clear()
 if nonman or volume<=0:
  target.modifiers.remove(mod);skipped.append({'host':host.name,'part':target.name,'reason':'nonmanifold output','edges':nonman});continue
 audit.append({'host':host.name,'part':target.name,'family':'bearing' if support else family,'routes':len(routes),'depth_m':depth,'nonmanifold':nonman,'center':a['center'],'normal':a['normal'],'seed':seed});print('CUT',len(audit),host.name,target.name,flush=True)
(O/'placements.json').write_text(json.dumps(audit,indent=2));(O/'skipped.json').write_text(json.dumps(skipped,indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
# Higher resolution game-camera crops keep the accepted perspective.
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True
for label,x0,x1,y0,y1 in [('left',0,.36,.27,.91),('right',.62,1,.22,.95)]:
 s.render.border_min_x=x0;s.render.border_max_x=x1;s.render.border_min_y=y0;s.render.border_max_y=y1;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
