"""Pipe detail + compatible rectangular duct components, version 2."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
src=(R/'tools/build_pipe_kit.py').read_text()
exec(src[:src.index('# Catalogue: true')])
exec(src[src.index('def offset_asset():'):src.index("C=bpy.data.collections['Catalogue captions']")])
O=R/'art/components/services/v002';O.mkdir(parents=True,exist_ok=True)
# Reuse prior assets as-is; add a dedicated duct finish and accent materials.
ductmat=mat('DUCT | muted blue-gray sheet',(.22,.29,.34),.35)
accent=mat('SERVICE | ochre identification plate',(.37,.23,.085),.25)
# Pipe embellishments remain optional independent components.
def collar_detail():
 ring(.025,.2,.18,paint,.085)
 for a in [0,math.pi/2,math.pi,math.pi*1.5]:
  x=.255*math.cos(a);y=.255*math.sin(a)
  box('Collar longitudinal lug',(x,y,.12),(.075,.075,.26),steel)
  bolt(x,y,.27,.27)
register('detail_collar','Lugged reinforcing collar',collar_detail,[])
def panel_detail():
 box('Service panel backing',(0,-.23,.28),(.38,.085,.48),steel)
 box('Service panel face',(0,-.28,.28),(.32,.025,.41),paint)
 for x in [-.12,.12]:
  for z in [.12,.44]:
   o=lathe('Panel fastener',[(0,.019),(.023,.019)],rim,6);o.rotation_euler.x=math.pi/2;o.location=(x,-.30,z)
 box('Panel label recess',(0,-.303,.34),(.17,.01,.09),gasket)
 box('Panel identification plate',(0,-.313,.34),(.12,.009,.045),accent)
register('detail_panel','Bolt-on service panel',panel_detail,[])
def service_tap():
 o=lathe('Service neck',[(0,.05),(.19,.05)],steel,32,inner=.025);o.rotation_euler.x=math.pi/2;o.location=(0,-.18,.16)
 o=lathe('Service cap',[(0,.08),(.05,.08)],oxide,8);o.rotation_euler.x=math.pi/2;o.location=(0,-.37,.16)
 ring(.10,.20,.12,steel,.02)
register('detail_tap','Capped service takeoff',service_tap,[])
SIZES={'S':(.32,.22),'M':(.56,.38),'L':(.88,.60)};T=.024

def rectloop(w,h,N=32):
 corners=[(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)];n=N//4
 return [(corners[j][0]+(corners[(j+1)%4][0]-corners[j][0])*i/n,corners[j][1]+(corners[(j+1)%4][1]-corners[j][1])*i/n) for j in range(4) for i in range(n)]
def circleloop(r,N=32):return [(r*math.cos(-math.pi/4+i*math.tau/N),r*math.sin(-math.pi/4+i*math.tau/N)) for i in range(N)]
def hollow_loft(name,sections,m=ductmat):
 # Each section: center, tangent-plane X and Y, outer and inner perimeter arrays.
 N=len(sections[0][3]);K=len(sections)*N;vs=[]
 for inner in [False,True]:
  for center,u,v,outer,hole in sections:
   for a,b in (hole if inner else outer):vs.append(tuple(Vector(center)+Vector(u)*a+Vector(v)*b))
 fs=[]
 for offset in [0,K]:
  for j in range(len(sections)-1):
   for i in range(N):
    face=(offset+j*N+i,offset+j*N+(i+1)%N,offset+(j+1)*N+(i+1)%N,offset+(j+1)*N+i);fs.append(face if offset==0 else tuple(reversed(face)))
 for j in [0,len(sections)-1]:
  for i in range(N):fs.append((j*N+i,j*N+(i+1)%N,K+j*N+(i+1)%N,K+j*N+i))
 return mesh(name,vs,fs,m,False)
def section(z,w,h,dx=0):return ((dx,0,z),(1,0,0),(0,1,0),rectloop(w,h),rectloop(w-2*T,h-2*T))
def duct(w,h,L=1):hollow_loft('Folded hollow duct',[section(0,w,h),section(L,w,h)])
def seam(z,w,h):
 # External four-piece corner frame, leaving terminal bore fully open.
 for x in [-w/2-.017,w/2+.017]:box('Duct joint side',(x,0,z),(.045,h+.1,.06),steel)
 for y in [-h/2-.017,h/2+.017]:box('Duct joint top',(0,y,z),(w+.06,.045,.06),steel)
def dport(pos,normal,size):
 w,h=SIZES[size];return {'position':list(pos),'outward':list(normal),'profile':'rect','up':[0,1,0],'width':round(w-2*T,5),'height':round(h-2*T,5),'interface':'rect_spigot_v2'}
def dp(z,size):return dport((0,0,z),(0,0,1 if z else -1),size)
for size,(w,h) in SIZES.items():
 register('duct_'+size,'Rectangular duct '+size,lambda w=w,h=h:(duct(w,h),seam(.10,w,h),seam(.90,w,h)),[dp(0,size),dp(1,size)])
 register('joint_'+size,'Rectangular sleeve '+size,lambda w=w,h=h:(duct(w,h,.22),seam(.05,w,h),seam(.17,w,h)),[dp(0,size),dp(.22,size)])

def ductbend(size,angle):
 w,h=SIZES[size];R=.72 if size=='L' else .48;tmax=math.radians(angle);sections=[]
 for j in range(17):
  t=tmax*j/16;sections.append(((R*(1-math.cos(t)),0,R*math.sin(t)),(math.cos(t),0,-math.sin(t)),(0,1,0),rectloop(w,h),rectloop(w-2*T,h-2*T)))
 hollow_loft('Swept rectangular elbow',sections)
 return R
for size in ['S','M','L']:
 for angle in [45,90]:
  rad=.72 if size=='L' else .48;t=math.radians(angle)
  register('duct_bend_'+size+'_'+str(angle),str(angle)+' degree duct elbow '+size,lambda size=size,angle=angle:ductbend(size,angle),[dp(0,size),dport((rad*(1-math.cos(t)),0,rad*math.sin(t)),(math.sin(t),0,math.cos(t)),size)])
for small,big in [('S','M'),('M','L')]:
 w,h=SIZES[small];W,H=SIZES[big]
 register('duct_reduce_'+small+big,'Duct transition '+small+' to '+big,lambda w=w,h=h,W=W,H=H:hollow_loft('Rectangular tapered transition',[section(0,w,h),section(.12,w,h),section(.63,W,H),section(.75,W,H)]),[dp(0,small),dp(.75,big)])
# Round-to-rectangular lofts preserve distinct bore shapes at both ends.
for size,r in [('S',.20),('M',.20),('L',.34)]:
 w,h=SIZES[size]
 def adapter(w=w,h=h,r=r):
  sections=[((0,0,0),(1,0,0),(0,1,0),circleloop(r),circleloop(r-.028)),((0,0,.12),(1,0,0),(0,1,0),circleloop(r),circleloop(r-.028)),section(.68,w,h),section(.80,w,h)]
  hollow_loft('Round to rectangular formed transition',sections);ring(.025,r,.06,steel,.035);seam(.73,w,h)
 register('round_rect_'+size,'Round to duct '+size,adapter,[P(0,r),dp(.80,size)])
# Offset is a formed rectangular section, not arbitrary instance scaling.
w,h=SIZES['M']
register('duct_offset','Rectangular offset M',lambda:hollow_loft('Offset box transition',[section(0,w,h),section(.18,w,h),section(.78,w,h,.42),section(.96,w,h,.42)]),[dp(0,'M'),dport((.42,0,.96),(0,0,1),'M')])
# Side branch tee, with an actual cutout into the trunk.
def ducttee():
 w,h=SIZES['M'];duct(w,h,1)
 trunk=next(iter(C.objects));parts_before=set(C.objects);duct(w,h,.72)
 branch=next(o for o in C.objects if o not in parts_before);branch.rotation_euler.y=math.pi/2;branch.location.z=.5
 cutter=box('Branch bore cutter',(.42,0,.5),(.90,h-2*T,w-2*T),steel)
 mod=trunk.modifiers.new('Open side branch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;C.objects.unlink(cutter);utility.objects.link(cutter)
 cutter=box('Trunk bore cutter',(0,0,.5),(w-2*T,h-2*T,1.10),steel)
 mod=branch.modifiers.new('Clear branch interior','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;C.objects.unlink(cutter);utility.objects.link(cutter)
register('duct_tee','Rectangular tee M',ducttee,[dp(0,'M'),dp(1,'M'),dport((.72,0,.5),(1,0,0),'M')])
def endcap():
 w,h=SIZES['M'];duct(w,h,.14);seam(.08,w,h);box('Duct removable end cover',(0,0,.16),(w+.06,h+.06,.055),paint)
 for x in [-w*.4,w*.4]:
  for y in [-h*.36,h*.36]:bolt(x,y,.205,.08)
register('duct_cap','Rectangular end cap M',endcap,[dp(0,'M')])
# More explicit connection schema: rectangular ports additionally constrain clocking.
links=[]
def compatible(a,b,roll=0):
 if a['interface']!=b['interface']:return False
 if a.get('profile')=='rect':
  if abs((roll%180))>1e-5:return False
  return abs(a['width']-b['width'])<1e-5 and abs(a['height']-b['height'])<1e-5
 return abs(a['bore_diameter']-b['bore_diameter'])<1e-5

def frame(p):
 z=Vector(p['outward']).normalized();y=Vector(p.get('up',[0,1,0]));y=y-z*y.dot(z)
 if y.length<1e-6:y=Vector((1,0,0))-z*z.x
 y.normalize();x=y.cross(z).normalized()
 basis=Matrix((x,y,z)).transposed().to_4x4()
 return Matrix.Translation(Vector(p['position']))@basis

def connect(parent,out_idx,key,in_idx=0,roll=0):
 a=assets[parent['part_id']]['ports'][out_idx];b=assets[key]['ports'][in_idx]
 assert compatible(a,b,roll),'Port mismatch: use an adapter or valid rectangular clocking'
 assert all(abs(parent.matrix_world.to_3x3().col[i].length-1)<1e-5 for i in range(3)),'Do not stretch component instances'
 transform=parent.matrix_world@frame(a)@Matrix.Rotation(math.radians(roll),4,'Z')@Matrix.Rotation(math.pi,4,'Y')@frame(b).inverted()
 child=instance(key,'MIXED | '+key,transform);bpy.context.view_layer.update()
 error=(parent.matrix_world@Vector(a['position'])-child.matrix_world@Vector(b['position'])).length
 dot=(parent.matrix_world.to_3x3()@Vector(a['outward'])).dot(child.matrix_world.to_3x3()@Vector(b['outward']));assert error<1e-5 and dot<-.99999
 links.append({'from':parent.name,'to':child.name,'position_error':error,'normal_dot':dot});return child
# Assemble a mixed route, returning to pipe after the rectangular section.
root=instance('spool','MIXED | inlet',Matrix.Identity(4));q=connect(root,1,'housing');q=connect(q,1,'round_rect_M');q=connect(q,1,'duct_M');q=connect(q,1,'joint_M');q=connect(q,1,'duct_reduce_ML');q=connect(q,1,'duct_L');q=connect(q,1,'duct_bend_L_90');q=connect(q,1,'round_rect_L',1);q=connect(q,0,'spool_large')
for key,pos in [('detail_collar',(0,0,.28)),('detail_panel',(0,-.20,1.4)),('detail_tap',(0,0,.64))]:instance(key,'MIXED | '+key,Matrix.Translation(Vector(pos)))
# Additional test chain exercises transition reversal, all port profiles and tee continuation.
testroot=instance('duct_S','TEST | inlet',Matrix.Translation(Vector((20,0,0))))
t=connect(testroot,1,'duct_reduce_SM');t=connect(t,1,'duct_tee');t=connect(t,1,'duct_cap')
otherroot=instance('duct_S','TEST | adapter inlet',Matrix.Translation(Vector((24,0,0))));t2=connect(otherroot,1,'round_rect_S',1)
checks={'round_to_rect_without_adapter_rejected':not compatible(P(1),dp(0,'M')),'wrong_rect_size_rejected':not compatible(dp(1,'S'),dp(0,'L')),'quarter_turn_rect_rejected':not compatible(dp(1,'M'),dp(0,'M'),90),'round_size_mismatch_rejected':not compatible(P(1),P(0,.34))}
assert all(checks.values())
# Hide test-only instances from review output while retaining logged results.
for ob in list(s.objects):
 if ob.location.x>15:bpy.data.objects.remove(ob,do_unlink=True)
# Lighting and cameras. Keep the mixed assembly in its own scene collection.
assembly=bpy.data.collections.new('Mixed service assembly');s.collection.children.link(assembly)
for ob in list(s.collection.objects):s.collection.objects.unlink(ob);assembly.objects.link(ob)
C=bpy.data.collections.new('Workshop studio');s.collection.children.link(C)
s.world=bpy.data.worlds.new('Service studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.20,.26,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
for name,power,pos,size in [('Key',800,(-4,-6,10),7),('Rim',600,(5,1,8),5),('Fill',350,(4,-4,3),5)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,3.8))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Workshop camera');cam=bpy.data.objects.new('Workshop camera',d);C.objects.link(cam);cam.location=(8,-18,10);cam.rotation_euler=(Vector((.9,0,3.8))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=9.4;s.camera=cam
s.render.resolution_x=1200;s.render.resolution_y=1400;s.render.filepath=str(O/'mixed-assembly.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'mixed-assembly.blend'));bpy.ops.render.render(write_still=True)
# Catalogue is a separate collection, switchable without touching component masters.
assembly.hide_render=True;assembly.hide_viewport=True
C=bpy.data.collections.new('Duct and detail catalogue');s.collection.children.link(C)
cat=C
newkeys=[k for k in assets if k.startswith(('detail_','duct_','joint_','round_rect_'))]
captionmat=bpy.data.materials.new('Catalogue lettering');captionmat.use_nodes=True;nd=captionmat.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');em=nd.new('ShaderNodeEmission');em.inputs[0].default_value=(.72,.78,.85,1);em.inputs[1].default_value=.8;captionmat.node_tree.links.new(em.outputs[0],out.inputs[0])
def textlabel(txt,pos):
 cu=bpy.data.curves.new(txt,'FONT');cu.body=txt;cu.size=.115;o=bpy.data.objects.new(txt,cu);cat.objects.link(o);o.location=pos;o.rotation_euler.x=math.pi/2;cu.materials.append(captionmat)
for i,key in enumerate(newkeys):
 x=i%5*2.25;z=6-(i//5)*2.05;ob=instance(key,'CAT | '+key,Matrix.Translation(Vector((x,0,z))));s.collection.objects.unlink(ob);cat.objects.link(ob)
 textlabel(assets[key]['title'],(x-.55,-.5,z-.33))
cam.location=(10,-24,13);cam.rotation_euler=(Vector((4.7,0,2.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13.7
# Reposition studio key for catalogue coverage.
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.location.x+=4
s.render.resolution_x=1800;s.render.resolution_y=1500;s.render.filepath=str(O/'catalogue.png')
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
spec={'version':2,'parts':{k:{'title':v['title'],'ports':v['ports']} for k,v in assets.items()},'validated_links':links,'negative_checks':checks,'limitations':['No automatic routing or collision clearance','Tee interiors use editable Boolean cutouts','Optional details and mounts placed explicitly','No decay applied']}
(O/'ports-and-rules.json').write_text(json.dumps(spec,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(O/'service-kit.blend'));bpy.ops.render.render(write_still=True)
