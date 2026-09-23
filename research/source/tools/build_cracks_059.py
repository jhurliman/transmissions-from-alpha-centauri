import bpy,random,math,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-059'
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs[0]);return m
import os
for variant in os.environ.get('CRACK_VARIANTS','density,network').split(','):
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-058/scene.blend'));s=bpy.context.scene
 dark=mat('059 fracture depth',(.014,.011,.015));lip=mat('059 exposed mineral lip',(.25,.17,.12));cutcol=bpy.data.collections.new('059 hidden editable cutters');s.collection.children.link(cutcol);proofs=[];audit=[]
 for hostName,partName in [('Architecture | buttress_45','Solid concrete'),('Front-left section instance','Tapered column structural volume')]:
  host=bpy.data.objects[hostName];old=host.instance_collection;kit=bpy.data.collections.new('059 '+variant+' | '+hostName)
  for ob in old.objects:
   if ob.type=='CURVE' and ob.name.startswith('Recessed anchored fracture'):continue
   q=ob.copy();kit.objects.link(q)
   if ob.name.startswith(partName) and (partName=='Solid concrete' or ob.name==partName):target=q;q.data=ob.data.copy()
  host.instance_collection=kit
  for m in list(target.modifiers):
   if m.type=='BOOLEAN' and 'crack' in m.name:target.modifiers.remove(m)
  # Select a large original planar face facing the unchanged game camera.
  world=host.matrix_world @ target.matrix_world
  candidates=[]
  for f in target.data.polygons:
   if partName=='Solid concrete' and not (f.normal.y < -.5 and f.normal.z > .5):continue
   normal=(world.to_3x3() @ f.normal).normalized();center=world @ f.center
   score=f.area*max(0,normal.dot((s.camera.location-center).normalized()))
   if partName=='Tapered column structural volume':score=center.x if abs(f.normal.y)>.5 and f.area>.7 else -999
   candidates.append((score,f))
  f=max(candidates,key=lambda a:a[0])[1];n=f.normal.copy();
  if (world.to_3x3() @ n).dot(s.camera.location-world @ f.center)<0:n=-n
  vs=[target.data.vertices[i].co.copy() for i in f.vertices]
  v=Vector((0,0,1));v=(v-n*v.dot(n)).normalized();u=v.cross(n).normalized();origin=f.center.copy();us=[(p-origin).dot(u) for p in vs];zs=[(p-origin).dot(v) for p in vs];umin,umax=min(us),max(us);vmin,vmax=min(zs),max(zs);
  W=umax-umin;H=vmax-vmin
  def point(p,depth=0):return origin+u*(umin+p[0]*W)+v*(vmin+p[1]*H)+n*depth
  def mesh_obj(name,verts,faces,col,material):
   me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(material);return ob
  def boolean(c):
   c.hide_render=True;c.hide_set(True);mod=target.modifiers.new('059 localized fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
  def path(a,b,seed,improved):
   rng=random.Random(seed);N=30 if improved else 24;pts=[];delta=Vector((b[0]-a[0],b[1]-a[1]));side=Vector((0,1)) if abs(delta.x*W)>=abs(delta.y*H) else Vector((1,0));walk=0
   for j in range(N+1):
    t=j/N;walk=.48*walk+rng.uniform(-1,1);offset=(.023*walk+(.035*math.sin(t*math.pi*5+seed) if improved else 0))*math.sin(math.pi*t);offset*=min(W,H)/(H if side.y else W);p=Vector(a).lerp(Vector(b),t)+side*offset;pts.append(tuple(p))
   return pts
  if variant=='density':paths=[path((0,z),(1,min(.95,z+.13)),701+j,False) for j,z in enumerate([.15,.28,.41,.54,.67,.80])]
  else:
   # Main network routes meet exactly at two interior junctions and connect edges.
   A=(.38,.38);B=(.62,.68)
   routes=[((0,.21),A),(A,B),(B,(1,.86)),(A,(.28,0)),(B,(.49,1)),(A,(1,.34))]
   paths=[path(a,b,701+j,True) for j,(a,b) in enumerate(routes)]
  for k,pts in enumerate(paths):
   rng=random.Random(500+k);widths=[]
   for j in range(len(pts)):
    # Width measured in meters, not normalized panel size.
    widths.append(.004 if variant=='density' else (.0025+.0035*(.5+.5*math.sin(j*.7+k)))* (1 if k<3 else .65))
   left=[];right=[]
   for j,p in enumerate(pts):
    a=Vector(pts[max(0,j-1)]);b=Vector(pts[min(len(pts)-1,j+1)]);d=Vector(((b.x-a.x)*W,(b.y-a.y)*H));side=Vector((0,1)) if abs((pts[-1][0]-pts[0][0])*W)>=abs((pts[-1][1]-pts[0][1])*H) else Vector((1,0));center=point(p);off=(u*side.x+v*side.y)*widths[j];left.append(center-off);right.append(center+off)
   verts=[tuple(p+n*d) for d in [.012,-.014] for pair in zip(left,right) for p in pair];N=len(pts)*2;faces=[]
   for j in range(len(pts)-1):
    a=2*j;b=a+2;faces.extend([(a,b,b+1,a+1),(a+N+1,b+N+1,b+N,a+N),(a,a+N,b+N,b),(a+1,b+1,b+N+1,a+N+1)])
   faces.extend([(0,1,N+1,N),(N-2,2*N-2,2*N-1,N-1)])
   c=mesh_obj('059 groove cutter',verts,faces,cutcol,lip);boolean(c)
   # Dark recessed floor; actual Boolean groove provides the mouth and walls.
   floorverts=[tuple(p-n*.012) for pair in zip(left,right) for p in pair];floorfaces=[(2*j,2*j+2,2*j+3,2*j+1) for j in range(len(pts)-1)];ob=mesh_obj('059 recessed dark core',floorverts,floorfaces,kit,dark)
  if variant=='network':
   for j,p in enumerate([A,B,(.28,0)]):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=point(p,-.003));c=bpy.context.object
    for col in list(c.users_collection):col.objects.unlink(c)
    cutcol.objects.link(c);c.name='059 junction breakout';c.scale=(.025,.025,.025)
    # Shape in the face basis, with an elongated surface footprint.
    for vv in c.data.vertices:vv.co=u*vv.co.x*1.2+v*vv.co.z*2+n*vv.co.y*.6
    bm=bmesh.new();bm.from_mesh(c.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(c.data);bm.free();c.data.materials.append(lip);boolean(c)
  
  if variant=='network':
   weld=target.modifiers.new('059 weld fracture junctions','WELD');weld.merge_threshold=.00001
  for mod in target.modifiers:mod.show_viewport=False
  for mod in target.modifiers:
   mod.show_viewport=True;bpy.context.view_layer.update();print('CHECK',partName,mod.name,len(target.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons),flush=True)
  evaluated=target.evaluated_get(bpy.context.evaluated_depsgraph_get());assert len(evaluated.data.polygons)>0
  center=world @ point((.5,.5));normal=(world.to_3x3() @ n).normalized();proofs.append((partName,center,normal,max(W,H)))
  audit.append({'host':hostName,'part':partName,'face_dimensions':[W,H],'paths':len(paths),'variant':variant,'center':list(center),'normal':list(normal)})
 (O/(variant+'-audit.json')).write_text(json.dumps(audit,indent=2));s.render.filepath=str(O/(variant+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(variant+'.blend')));bpy.ops.render.render(write_still=True)
 for j,(name,center,normal,size) in enumerate(proofs):
  s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=size*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/(variant+('-support.png' if j==0 else '-panel.png')));bpy.ops.render.render(write_still=True)
