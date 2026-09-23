"""Original modular pipe kit. Native geometry; ports are geometry-independent local frames."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/components/pipes/v001';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
def mat(name,rgb,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=.42;return m
paint=mat('PIP | blue-gray enamel',(.19,.26,.36),.25);steel=mat('PIP | dark machined steel',(.085,.11,.14),.65);rim=mat('PIP | worn edge steel',(.34,.38,.41),.65);oxide=mat('PIP | warm brown metal finish',(.25,.13,.075),.4);gasket=mat('PIP | dark gasket',(.017,.022,.026));wallmat=mat('Display wall',(.075,.08,.095))
assets={};C=None;utility=bpy.data.collections.new('Pipe internal bore cutters');utility.use_fake_user=True

def mesh(name,vs,fs,m,smooth=True,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);me.materials.append(m)
 for p in me.polygons:p.use_smooth=smooth
 if bevel:
  mod=o.modifiers.new('Manufactured edge radius','BEVEL');mod.width=bevel;mod.segments=2
 return o

def box(name,p,dim,m):
 x,y,z=p;a,b,c=[v/2 for v in dim];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m,False,.012)

def lathe(name,profile,m,N=48,inner=None):
 # Closed radial section, optional hollow bore. Input profile is z/r outer contour.
 section=list(profile)
 if inner is None:section += [(profile[-1][0],0),(profile[0][0],0)]
 else:section += [(profile[-1][0],inner),(profile[0][0],inner)]
 vs=[(rr*math.cos(i*math.tau/N),rr*math.sin(i*math.tau/N),z) for z,rr in section for i in range(N)]
 fs=[(j*N+i,j*N+(i+1)%N,((j+1)%len(section))*N+(i+1)%N,((j+1)%len(section))*N+i) for j in range(len(section)) for i in range(N)]
 ob=mesh(name,vs,fs,m,True)
 for j in range(len(section)):
  if abs(section[j][0]-section[(j+1)%len(section)][0])<1e-8:
   for poly in ob.data.polygons[j*N:(j+1)*N]:poly.use_smooth=False
 return ob

def ring(z,r,width,m=steel,extra=.07):
 return lathe('Machined collar',[(z,r),(z+.012,r+extra),(z+width-.012,r+extra),(z+width,r)],m,inner=r-.016)

def bolt(x,y,z,length=.18):
 o=lathe('Hex head',[(0,.033),(.038,.033)],rim,6);o.location=(x,y,z)
 o=lathe('Bolt shank',[(0,.017),(length,.017)],steel,16);o.location=(x,y,z-length)
 o=lathe('Washer',[(0,.048),(.012,.048)],rim,32,inner=.019);o.location=(x,y,z-.014)

def flange(z,r):
 lathe('Raised flange plate',[(z,r),(z+.018,r+.12),(z+.105,r+.12),(z+.12,r+.055)],steel,inner=r-.028)
 ring(z+.026,r+.115,.032,rim,.008)
 for i in range(8):
  a=math.tau*i/8;bolt((r+.075)*math.cos(a),(r+.075)*math.sin(a),z+.13)

def spool(r=.20,L=1.0):
 lathe('Hollow pipe barrel',[(0,r),(L,r)],paint,inner=r-.028)

def elbow(r=.20,angle=90,Rb=.50):
 angle=math.radians(angle);steps=max(8,int(angle*24));N=40;vs=[]
 for rr in [r,r-.028]:
  for j in range(steps+1):
   t=angle*j/steps;center=Vector((Rb*(1-math.cos(t)),0,Rb*math.sin(t)));u=Vector((math.cos(t),0,-math.sin(t)));v=Vector((0,1,0))
   for i in range(N):vs.append(tuple(center+rr*(math.cos(i*math.tau/N)*u+math.sin(i*math.tau/N)*v)))
 K=(steps+1)*N;fs=[]
 for offset in [0,K]:
  for j in range(steps):
   for i in range(N):fs.append((offset+j*N+i,offset+j*N+(i+1)%N,offset+(j+1)*N+(i+1)%N,offset+(j+1)*N+i))
 for j in [0,steps]:
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,K+j*N+(i+1)%N,K+j*N+i))
 ob=mesh('Continuous hollow swept bend',vs,fs,paint)
 for poly in ob.data.polygons[-2*N:]:poly.use_smooth=False
 return (Rb*(1-math.cos(angle)),0,Rb*math.sin(angle)),(math.sin(angle),0,math.cos(angle))

def port(pos,normal,r):return {'position':list(pos),'outward':list(normal),'bore_diameter':round(2*(r-.028),5),'interface':'plain_spigot_v1'}
def register(key,title,fn,ports):
 global C
 C=bpy.data.collections.new('PIP_'+key);fn();C.asset_mark();C.asset_data.description=title+' | Native editable geometry. Connection frames stored in ports_json.';C['ports_json']=json.dumps(ports);C['part_id']=key;C['finish_slots']='enamel, steel, edge, oxide, gasket';assets[key]={'collection':C,'ports':ports,'title':title};return C
P=lambda z,r=.2:port((0,0,z),(0,0,1 if z else -1),r)
register('spool','Straight spool',lambda:spool(),[P(0),P(1)])
register('sleeve','Overlapping sleeve',lambda:(spool(L=.30),ring(.01,.20,.28,paint,.055)),[P(0),P(.30)])
def joint():
 spool(L=.33);flange(0,.20);flange(.19,.20);lathe('Compressed gasket',[(.145,.30),(.18,.30)],gasket,inner=.172)
register('flange_joint','Bolted flange pair',joint,[P(0),P(.33)])
def reducer():
 lathe('Tapered hollow reducer',[(0,.20),(.08,.20),(.39,.34),(.49,.34)],paint,inner=.172);ring(.02,.20,.055);ring(.42,.34,.055)
 # Replace simplified inner wall with a matching tapered bore.
 ob=next(o for o in C.objects if o.name.startswith('Tapered hollow reducer'));bpy.data.objects.remove(ob,do_unlink=True)
 section=[(0,.20),(.08,.20),(.39,.34),(.49,.34),(.49,.312),(.39,.312),(.08,.172),(0,.172)]
 N=48;vs=[(rr*math.cos(i*math.tau/N),rr*math.sin(i*math.tau/N),z) for z,rr in section for i in range(N)];fs=[(j*N+i,j*N+(i+1)%N,((j+1)%8)*N+(i+1)%N,((j+1)%8)*N+i) for j in range(8) for i in range(N)];mesh('Tapered bore and shell',vs,fs,paint)
register('reducer','Conical diameter transition',reducer,[P(0),P(.49,.34)])
def step():
 section=[(0,.20),(.10,.20),(.14,.28),(.32,.28),(.32,.252),(.15,.252),(.09,.172),(0,.172)]
 N=48;vs=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z) for z,r in section for i in range(N)]
 fs=[(j*N+i,j*N+(i+1)%N,((j+1)%8)*N+(i+1)%N,((j+1)%8)*N+i) for j in range(8) for i in range(N)]
 ob=mesh('Stepped shell and matching bore',vs,fs,paint)
 for j in [3,7]:
  for poly in ob.data.polygons[j*N:(j+1)*N]:poly.use_smooth=False
 ring(.15,.28,.13)
register('step','Stepped adapter',step,[P(0),P(.32,.28)])

for ang in [22.5,45,90,180]:
 t=math.radians(ang);end=(.5*(1-math.cos(t)),0,.5*math.sin(t));register('bend_'+str(ang).replace('.','_'),str(ang)+' degree swept bend',lambda ang=ang:elbow(angle=ang),[P(0),port(end,(math.sin(t),0,math.cos(t)),.2)])
def housing():
 lathe('Enlarged jacket and necks',[(0,.20),(.15,.20),(.30,.34),(.38,.39),(1.12,.39),(1.20,.34),(1.35,.20),(1.50,.20)],paint,inner=.172)
 for z in [.01,1.36]:ring(z,.20,.10,steel,.06)
 for z in [.34,1.08]:ring(z,.39,.075,steel,.045)
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:
  x=.405*math.cos(a);y=.405*math.sin(a);box('Jacket seam rail',(x,y,.75),(.032,.032,.57),steel)
register('housing','Collared inline chamber',housing,[P(0),P(1.50)])
def plenum():
 box('Plenum shell',(0,0,.55),(.85,.68,.78),paint)
 spool(L=.18);ob=lathe('Plenum outlet neck',[(.92,.20),(1.10,.20)],paint,inner=.172)
 box('Removable plenum cover',(0,-.355,.55),(.69,.045,.60),steel)
 for x in [-.27,.27]:
  for z in [.33,.77]:
   ob=lathe('Cover screw',[(0,.027),(.018,.027)],rim,6);ob.rotation_euler.x=math.pi/2;ob.location=(x,-.39,z)
 shell=next(o for o in C.objects if o.name=='Plenum shell')
 cutter=lathe('Temporary plenum bore',[(-.05,.172),(1.15,.172)],steel)
 mod=shell.modifiers.new('Open neck bore','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
 # Source collections are not in the scene yet; apply via evaluated mesh later instead.
 mod.show_viewport=True;mod.show_render=True;cutter.hide_render=True
 # Boolean operand is kept in an unlinked utility collection, not rendered as part of asset.
 C.objects.unlink(cutter);utility.objects.link(cutter)
register('plenum','Box plenum (design extension)',plenum,[P(0),P(1.10)])
def cap():
 flange(0,.20);lathe('Blind service cover',[(.13,.30),(.17,.30),(.20,.23)],paint)
register('blind','Blind flange / inspection cap',cap,[P(0)])
def clamp():
 lathe('Split wrap band',[(.02,.23),(.12,.23)],steel,inner=.205)
 for x in [-.26,.26]:box('Clamp ear',(x,0,.07),(.16,.12,.08),steel);bolt(x,0,.15,.15)
 box('Wall standoff',(0,.38,.07),(.13,.42,.10),steel);box('Wall anchor plate',(0,.60,.07),(.48,.07,.38),paint)
register('clamp','Wall saddle and band',clamp,[])
def bundle():
 for x in [-.24,0,.24]:
  ob=lathe('Secondary service conduit',[(0,.055),(1.2,.055)],oxide,32,inner=.042);ob.location.x=x
  for z in [.15,1.0]:
   ob=ring(z,.055,.06,steel,.024);ob.location.x=x
 for z in [.18,1.03]:box('Bundle wall bridge',(0,.09,z),(.70,.10,.08),steel)
register('bundle','Three secondary service conduits',bundle,[])
# Tee uses a boolean to open the actual branch into the hollow trunk.
def tee():
 spool(L=.8)
 ob=lathe('Branch neck',[(0,.20),(.45,.20)],paint,inner=.172);ob.rotation_euler.y=math.pi/2;ob.location=(0,0,.4)
 trunk=next(o for o in C.objects if o.name.startswith('Hollow pipe barrel'))
 c=lathe('Temporary tee branch bore',[(0,.172),(.52,.172)],steel);c.rotation_euler.y=math.pi/2;c.location=(0,0,.4)
 mod=trunk.modifiers.new('Open branch into trunk','BOOLEAN');mod.operation='DIFFERENCE';mod.object=c;C.objects.unlink(c);utility.objects.link(c)
 c=lathe('Temporary tee trunk bore',[(-.04,.172),(.84,.172)],steel)
 mod=ob.modifiers.new('Open trunk through branch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=c;C.objects.unlink(c);utility.objects.link(c)
register('tee','Tee branch (design extension)',tee,[P(0),P(.8),port((.45,0,.4),(1,0,0),.2)])

def instance(key,name,transform=None):
 ob=bpy.data.objects.new(name,None);s.collection.objects.link(ob);ob.instance_type='COLLECTION';ob.instance_collection=assets[key]['collection'];ob['part_id']=key
 if transform is not None:ob.matrix_world=transform
 return ob

def frame(p):
 q=Vector(p['outward']).to_track_quat('Z','Y');return Matrix.Translation(Vector(p['position']))@q.to_matrix().to_4x4()
links=[]
def connect(parent,out_idx,key,in_idx=0,roll=0):
 src=assets[parent['part_id']]['ports'][out_idx];dst=assets[key]['ports'][in_idx]
 assert src['interface']==dst['interface'] and abs(src['bore_diameter']-dst['bore_diameter'])<1e-5,'Connector mismatch requires adapter'
 t=parent.matrix_world@frame(src)@Matrix.Rotation(math.radians(roll),4,'Z')@Matrix.Rotation(math.pi,4,'Y')@frame(dst).inverted()
 child=instance(key,'ASSEMBLY | '+key,t);bpy.context.view_layer.update()
 a=parent.matrix_world@Vector(src['position']);b=child.matrix_world@Vector(dst['position']);na=parent.matrix_world.to_3x3()@Vector(src['outward']);nb=child.matrix_world.to_3x3()@Vector(dst['outward']);assert (a-b).length<1e-5;assert na.dot(nb)<-.9999
 links.append({'from':parent.name,'to':child.name,'position_error':(a-b).length,'normal_dot':na.dot(nb)})
 return child
# Catalogue: true collection instances arranged on a labeled presentation plane.
C=bpy.data.collections.new('Catalogue captions');s.collection.children.link(C)
def label(text,pos,size=.15):
 cu=bpy.data.curves.new(text,'FONT');cu.body=text;cu.size=size;cu.extrude=0;o=bpy.data.objects.new(text,cu);C.objects.link(o);o.location=pos;o.rotation_euler.x=math.pi/2;cu.materials.append(rim)
def offset_asset():
 global C
 offset_collection=C
 a=instance('bend_45','Offset prefab entry',Matrix.Identity(4));b=connect(a,1,'spool');c=connect(b,1,'bend_45',roll=180)
 for ob in [a,b,c]:s.collection.objects.unlink(ob);offset_collection.objects.link(ob)
 endpoint=c.matrix_world@Vector(assets['bend_45']['ports'][1]['position']);normal=c.matrix_world.to_3x3()@Vector(assets['bend_45']['ports'][1]['outward'])
 offset_asset.ports=[P(0),port(endpoint,normal,.2)]
register('offset','Two-bend offset assembly',offset_asset,[])
assets['offset']['ports']=offset_asset.ports;assets['offset']['collection']['ports_json']=json.dumps(offset_asset.ports)
register('spool_large','Large-bore spool',lambda:spool(r=.34),[P(0,.34),P(1,.34)])
register('spool_small','Secondary conduit spool',lambda:spool(r=.055),[P(0,.055),P(1,.055)])
C=bpy.data.collections['Catalogue captions']
keys=list(assets)
for i,key in enumerate(keys):
 col=i%5;row=i//5;x=col*2.15;z=(2-row)*2.45
 ob=instance(key,'KIT | '+key,Matrix.Translation(Vector((x,0,z))))
 label(f'{i+1:02}  '+assets[key]['title'],(x-.50,-.48,z-.32),.115)
# Offset assembled from two bends; retain in library as an asset using instances of existing parts.
start=instance('bend_45','ASSEMBLY | offset entry',Matrix.Translation(Vector((11.8,0,.0))))
mid=connect(start,1,'spool');end=connect(mid,1,'bend_45',roll=180)
# Separate vertical service riser, fully snapped via interface frames.
root=instance('spool','ASSEMBLY | service inlet',Matrix.Translation(Vector((11.4,0,1.0))))
p=connect(root,1,'flange_joint');p=connect(p,1,'housing');p=connect(p,1,'reducer');p=connect(p,1,'spool_large');p=connect(p,1,'reducer',1);p=connect(p,0,'bend_90');p=connect(p,1,'spool')
# Supports are explicit mounts rather than fluid ports.
for z in [1.5,3.0]:instance('clamp','ASSEMBLY | wall support',Matrix.Translation(Vector((11.4,0,z))))
label('CONNECTED SERVICE ASSEMBLY',(10.7,-.45,.58),.15);label('TWO-BEND OFFSET',(11.1,-.45,-.4),.15)
# Backing plane shows contact and rounded section without weathering.
box('Display backing',(5.9,.95,2.0),(15,.10,11),wallmat)
# Save port specification and rule validation.
spec={'units':'meters; invented art dimensions, not measured reference dimensions','version':1,'port_convention':'Local position and outward normal, bore diameter, interface family. Mate coincident positions and opposing normals; roll around mating axis.','parts':{k:{'title':v['title'],'ports':v['ports']} for k,v in assets.items()},'validated_links':links,'limitations':['Tee and plenum use nondestructive bore cutouts; pressure / watertight certification is out of scope','No collision routing or pressure-system validation','Damage and customization intentionally deferred']}
(O/'ports-and-rules.json').write_text(json.dumps(spec,indent=2)+'\n')
# Reject incompatible connection as a meaningful negative test.
try:connect(root,1,'reducer',1)
except AssertionError:spec['mismatched_bore_rejected']=True
else:raise RuntimeError('Mismatch was accepted')
(O/'ports-and-rules.json').write_text(json.dumps(spec,indent=2)+'\n')
s.world=bpy.data.worlds.new('Studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.23,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.25
for name,power,pos,size,color in [('Key',900,(2,-6,10),8,(.84,.91,1)),('Warm edge',500,(12,-2,7),6,(1,.75,.49)),('Fill',350,(-4,-2,1),5,(.66,.77,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((6,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Catalogue camera');cam=bpy.data.objects.new('Catalogue camera',d);s.collection.objects.link(cam);cam.location=(8,-22,10);cam.rotation_euler=(Vector((6,0,2))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=16.8;s.camera=cam
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
s.render.filepath=str(O/'catalogue.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'pipe-kit.blend'));bpy.ops.render.render(write_still=True)
# Close-up on the connected sample, same native geometry and light rig.
cam.location=(14,-14,7);cam.rotation_euler=(Vector((11.9,0,3.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=7.9;s.render.resolution_x=1100;s.render.resolution_y=1400;s.render.filepath=str(O/'assembly.png');bpy.ops.render.render(write_still=True)
