import bpy,random,math,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-060'
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs[0]);return m
import os
for variant in ['network']:
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
  import subprocess
  payload={'paths':[]}
  for k,pts in enumerate(paths):
   coords=[[p[0]*W,p[1]*H] for p in pts];widths=[]
   for j,p in enumerate(coords):
    w=(.006+.004*(.5+.5*math.sin(j*.7+k)))*(1 if k<3 else .65)
    for endpoint in [coords[0],coords[-1]]:
     boundary=min(endpoint[0],W-endpoint[0],endpoint[1],H-endpoint[1])<.0001
     distance=math.dist(p,endpoint)
     w+=(.027 if boundary else .009)*math.exp(-distance/.055)
    widths.append(w)
   for j,other in [(0,1),(-1,-2)]:
    if min(coords[j][0],W-coords[j][0],coords[j][1],H-coords[j][1])<.0001:
     d=Vector(coords[j])-Vector(coords[other]);d.normalize();coords[j]=list(Vector(coords[j])+d*.025)
   payload['paths'].append({'points':coords,'widths':widths})
  req=O/(str(len(audit))+'-paths.json');res=O/(str(len(audit))+'-cutter.json');req.write_text(json.dumps(payload))
  subprocess.run(['/tmp/crack060-env/bin/python',str(R/'tools/fracture_mesh_060.py'),str(req),str(res)],check=True)
  mesh=json.loads(res.read_text());verts=[tuple(origin+u*(umin+x)+v*(vmin+y)+n*z) for x,y,z in mesh['vertices']]
  c=mesh_obj('060 unified chamfer cutter',verts,mesh['faces'],cutcol,lip)
  # Match cutter material slots to target; cut faces retain exposed-lip/depth IDs.
  basecount=len(target.data.materials);target.data.materials.append(lip);target.data.materials.append(dark);c.data.materials.clear()
  for material in target.data.materials:c.data.materials.append(material)
  for f,idx in zip(c.data.polygons,mesh['materials']):f.material_index=basecount+idx
  boolean(c)
  bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(target.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me)
  nonman=sum(not e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume());bm.free();assert nonman==0 and volume>0,(partName,nonman,volume)
  center=world @ point((.5,.5));normal=(world.to_3x3() @ n).normalized();proofs.append((partName,center,normal,max(W,H)))
  audit.append({'part':partName,'nonmanifold_edges':nonman,'volume':volume,'center':list(center),'normal':list(normal),'size':max(W,H)})
 (O/'validation.json').write_text(json.dumps(audit,indent=2))
 # Give real fracture lips directional highlights using their actual normals.
 nt=lip.node_tree;e=next(n for n in nt.nodes if n.type=='EMISSION');g=nt.nodes.new('ShaderNodeNewGeometry');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(g.outputs['Normal'],dot.inputs[0]);dot.inputs[1].default_value=(.4,-.6,.7);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(.055,.037,.03,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.48,.35,.24,1);nt.links.new(dot.outputs['Value'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],e.inputs[0])
 s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
 for j,(name,center,normal,size) in enumerate(proofs):
  s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=size*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/('support.png' if j==0 else 'panel.png'));bpy.ops.render.render(write_still=True)
 # Untextured, lit proof: remove pigment, dark floor coloring, and line rendering.
 host=bpy.data.objects['Front-left section instance'];target=next(o for o in host.instance_collection.objects if o.name.startswith('Tapered column structural volume') and any(m.name.startswith('059 localized fracture') for m in o.modifiers));me=bpy.data.meshes.new_from_object(target.evaluated_get(bpy.context.evaluated_depsgraph_get()));transform=host.matrix_world @ target.matrix_world
 for ob in s.objects:
  if ob!=s.camera:ob.hide_render=True
 proof=bpy.data.objects.new('060 actual cut column geometry',me);s.collection.objects.link(proof);proof.matrix_world=transform
 s.world=bpy.data.worlds.new('060 neutral world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1)
 clay=bpy.data.materials.new('060 neutral geometry proof');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.35,.35,1);bs.inputs['Roughness'].default_value=.7;s.view_layers[0].material_override=clay;s.render.use_freestyle=False
 bpy.ops.object.light_add(type='AREA',location=s.camera.location+Vector((-.5,-2,2)));light=bpy.context.object;light.data.energy=900;light.data.shape='DISK';light.data.size=2;light.rotation_euler=(proofs[-1][1]-light.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'panel-clay.png');bpy.ops.render.render(write_still=True)
