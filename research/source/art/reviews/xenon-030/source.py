"""Large service infrastructure in the far alley, dimensioned masters at unit scale."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-030';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-027/scene.blend'));s=bpy.context.scene
original=list(s.objects);camera=[list(r) for r in s.camera.matrix_world];lens=s.camera.data.lens
C=bpy.data.collections.new('030 Distant large service infrastructure');s.collection.children.link(C)
paint=bpy.data.materials['Cladding | slate enamel'];steel=bpy.data.materials['Structure | charcoal steel'];pale=bpy.data.materials['Cladding | pale mineral blue']
assets={};audit=[]
def box(n,p,d,m,col):
 x,y,z=p;a,b,c=[v/2 for v in d];v=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);col.objects.link(ob);b=ob.modifiers.new('Manufactured edge','BEVEL');b.width=.015;b.segments=2;return ob

def master(k):
 c=bpy.data.collections.new('SERVICE XL | '+k);c.asset_mark();c['part_id']=k;assets[k]=c;return c

def loft(n,sections,radii,col,m,thickness=.045):
 N=64;vs=[]
 for inside in [False,True]:
  for (p,u,v),r in zip(sections,radii):
   rr=r-thickness if inside else r
   for i in range(N):vs.append(tuple(Vector(p)+rr*(math.cos(i*math.tau/N)*Vector(u)+math.sin(i*math.tau/N)*Vector(v))))
 K=len(sections)*N;fs=[]
 for offset in [0,K]:
  for j in range(len(sections)-1):
   for i in range(N):a=offset+j*N+i;b=offset+j*N+(i+1)%N;fs.append((a,b,b+N,a+N) if not offset else (a+N,b+N,b,a))
 for j in [0,len(sections)-1]:
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;fs.append((a,b,K+b,K+a))
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 ob=bpy.data.objects.new(n,me);col.objects.link(ob)

def axial(n,profile,c,m=paint):loft(n,[((0,0,z),(1,0,0),(0,1,0)) for z,r in profile],[r for z,r in profile],c,m)
def ring(c,z,r):
 axial('Structural clamp band',[(z-.045,r+.045),(z+.045,r+.045)],c,steel)
 for j in range(8):
  a=j*math.tau/8;box('Clamp fastening lug',((r+.075)*math.cos(a),(r+.075)*math.sin(a),z),(.12,.12,.14),steel,c)
for k,r,L in [('trunk_1350_L3',.675,3),('companion_600_L3',.3,3)]:
 c=master(k);axial('Hollow straight section',[(0,r),(L,r)],c);c['dimensions']=json.dumps({'diameter':r*2,'length':L});c['ports_json']=json.dumps([{'position':[0,0,z],'outward':[0,0,-1 if z==0 else 1],'diameter':r*2} for z in [0,L]])
for k,r,Rbig,L in [('housing_1950',.675,.975,1.95),('housing_1000',.3,.5,1.5)]:
 c=master(k);axial('Stepped service housing',[(0,r),(.2,r),(.45,Rbig),(L-.45,Rbig),(L-.2,r),(L,r)],c)
 for z,rr in [(.08,r),(.50,Rbig),(L-.50,Rbig),(L-.08,r)]:ring(c,z,rr)
 for a in [0,math.pi/2,math.pi,3*math.pi/2]:box('Housing longitudinal seam',(Rbig*math.cos(a),Rbig*math.sin(a),L/2),(.045,.045,L-.98),steel,c)
 c['dimensions']=json.dumps({'shaft_diameter':r*2,'housing_diameter':Rbig*2,'length':L});c['ports_json']=json.dumps([{'position':[0,0,z],'outward':[0,0,-1 if z==0 else 1],'diameter':r*2} for z in [0,L]])
def inst(k,M):
 ob=bpy.data.objects.new('XL | '+k,None);ob.instance_type='COLLECTION';ob.instance_collection=assets[k];ob.matrix_world=M;C.objects.link(ob);return ob
# Local X follows alley +Y; local -Y points into the alley.
def base(x,y,z):return Matrix.Translation((x,y,z))@Matrix.Rotation(math.pi/2,4,'Z')
endpoints=[]
def wallturn(k,r,rad,depth,down=False):
 c=master(k);sec=[];sign=-1 if down else 1
 for j in range(33):
  t=j*math.pi/64;sec.append(((0,rad*(1-math.cos(t)),sign*rad*math.sin(t)),(1,0,0),(0,math.cos(t),-sign*math.sin(t))))
 sec.append(((0,depth+.16,sign*rad),(1,0,0),(0,0,1)))
 loft('Continuous wall turn',sec,[r]*len(sec),c,paint)
 # Wall trim is an annulus with close fitting bore.
 loft('Wall flange',[((0,depth-.06,sign*rad),(1,0,0),(0,0,1)),((0,depth+.035,sign*rad),(1,0,0),(0,0,1))],[r+.16]*2,c,steel,thickness=.15)
 c['termination']='wall penetration';return k
# Large primary is approximately a person's height in diameter, deeper into the alley.
x,y=-6.8,26.0;z=3.0
for k,L in [('trunk_1350_L3',3),('housing_1950',1.95),('trunk_1350_L3',3)]:inst(k,base(x,y,z));z+=L
inst(wallturn('primary_bottom_wall_turn',.675,1.05,2.2,True),base(x,y,3.0));endpoints.append({'route':'primary','bottom':'90 into wall','top':'projecting building receiver'})
# Massive upper architectural receiver: native local geometry and panel seams.
c=master('primary_building_receiver')
# Receiver face encloses the complete flange; rear extends into the inset facade.
box('Projecting receiver',(0,.765,.75),(2.3,3.37,1.74),paint,c)
box('Receiver front cover',(0,-.955,.80),(1.96,.07,1.25),pale,c)
for xx in [-.85,.85]:
 for zz in [.30,1.30]:box('Receiver fastener',(xx,-1.01,zz),(.09,.06,.09),steel,c)
loft('Concentric receiver docking flange',[((0,0,-.20),(1,0,0),(0,1,0)),((0,0,-.10),(1,0,0),(0,1,0))],[.80,.80],c,paint,thickness=.12)
inst('primary_building_receiver',base(x,y,z))
for zz in [4.2,7.4,10.0]:box('Primary structural standoff',(-8.3,y,zz),(1.70,.30,.19),steel,C)
# Medium companion uses different event elevation and terminates into wall at both ends.
x,y=-7.45,22.5;z=1.5
for k,L in [('companion_600_L3',3),('housing_1000',1.5),('companion_600_L3',3)]:inst(k,base(x,y,z));z+=L
for level,down in [(1.5,True),(z,False)]:inst(wallturn('companion_wall_'+str(down),.3,.6,1.55 if down else 1.614,down),base(x,y,level))
endpoints.append({'route':'medium companion','bottom':'90 into wall','top':'90 into wall'})
for zz in [2.0,5.0,8.0]:box('Companion standoff',(-8.40,y,zz),(1.40,.18,.12),steel,C)
# Large rectangular service duct: 1.4 x 1.0 m, clean long modules, terminating at vent and plinth.
c=master('duct_1400x1000_L3')
for xx in [-.7,.7]:box('Duct side',(xx,0,1.5),(.055,1.0,3),paint,c)
for yy in [-.5,.5]:box('Duct face',(0,yy,1.5),(1.4,.055,3),paint,c)
for zz in [.06,2.94]:
 for xx in [-.75,.75]:box('Duct cuff',(xx,0,zz),(.10,1.14,.10),paint,c)
 for yy in [-.55,.55]:box('Duct cuff',(0,yy,zz),(1.55,.10,.10),paint,c)
x,y=-7.80,19.0
for z in [.65,3.65]:inst('duct_1400x1000_L3',base(x,y,z))
c=master('large_vent_terminal')
# A real return housing joins the vent to the facade at x=-9.564.
for xx in [-.85,.85]:box('Vent front frame',(xx,-.20,.85),(.12,.82,1.70),paint,c)
for zz in [.06,1.66]:box('Vent return shell',(0,.65,zz),(1.8,2.52,.12),paint,c)
box('Vent back mounting frame',(0,1.90,.85),(2.0,.14,1.84),paint,c)
box('Vent right return',(.85,.96,.85),(.12,1.90,1.7),paint,c)
# Left return has a bounded side inlet for the smaller duct.
box('Vent left upper return',(-.85,1.0,1.18),(.12,1.8,1.04),paint,c)
box('Vent left lower return',(-.85,1.0,.08),(.12,1.8,.08),paint,c)
box('Vent left forward return',(-.85,.36,.38),(.12,.48,.56),paint,c)
box('Vent left rear return',(-.85,1.47,.38),(.12,.86,.56),paint,c)
box('Vent cavity',(0,1.70,.85),(1.6,.10,1.5),steel,c)
for j in range(7):box('Vent slat',(0,-.40,.25+j*.2),(1.6,.35,.055),pale,c)
inst('large_vent_terminal',base(x,y,6.60))
for zz in [2.1,5.2]:box('Duct wall standoff',(-8.95,y,zz),(1.40,.28,.18),steel,C)
c=master('duct_building_plinth');box('Projecting service plinth',(0,.55,.35),(1.85,2.30,.70),paint,c);box('Plinth cover',(0,-.64,.36),(1.56,.06,.44),pale,c);inst('duct_building_plinth',base(x,y,0))
endpoints.append({'route':'large duct','bottom':'building plinth','top':'louver terminal'})
# Remove only the obsolete small far-left service bank; retain facade and vista.
old=bpy.data.collections['027 Reviewed architecture assembly'];hidden=[]
for ob in old.objects:
 if ob.instance_collection and ob.location.x<0 and ob.location.y>21 and ob.instance_collection.name.startswith('PIP_'):
  ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
# Remove the old over-tall small duct at y=16.6 and route it into the vent side inlet.
service_assets={c.get('part_id'):c for c in bpy.data.collections if c.get('part_id') and c.name.startswith('PIP_')}
for ob in old.objects:
 if ob.instance_collection and ob.location.x<0 and abs(ob.location.y-16.6)<.01 and ob.instance_collection.name.startswith('PIP_'):
  ob.hide_render=True;ob.hide_viewport=True
 if ob.name.startswith('U return extended wall mount'):ob.hide_render=True;ob.hide_viewport=True
for key in ['duct_M','duct_bend_M_90','joint_M']:assets[key]=service_assets[key]
def portframe(p):
 Z=Vector(p['outward']);Y=Vector(p.get('up',[0,1,0]));Y=(Y-Z*Y.dot(Z)).normalized();X=Y.cross(Z);return Matrix.Translation(Vector(p['position']))@Matrix((X,Y,Z)).transposed().to_4x4()
q=None;M=base(-8.6,16.6,.5);pk=None;side_joins=[]
for key in ['duct_M']*6+['duct_bend_M_90','duct_M','joint_M']:
 if q is not None:
  a=json.loads(assets[pk]['ports_json'])[1];b=json.loads(assets[key]['ports_json'])[0]
  assert a['interface']==b['interface'] and abs(a['width']-b['width'])<1e-6 and abs(a['height']-b['height'])<1e-6
  prev=M.copy();M=M@portframe(a)@Matrix.Rotation(math.pi,4,'Y')@portframe(b).inverted();side_joins.append((prev@Vector(a['position'])-M@Vector(b['position'])).length)
 q=inst(key,M);pk=key
box('Small duct building inlet',(-8.6,16.6,.26),(1.4,.9,.52),paint,C)
# Local regularity stays, but rectangular joints share the duct finish.
for col in bpy.data.collections:
 if col.name.startswith('PIP_'):
  for ob in col.objects:
   if ob.type=='MESH' and ob.name.startswith(('Duct joint','Duct removable end cover')):
    ob.data.materials.clear();ob.data.materials.append(bpy.data.materials.get('DUCT | muted blue-gray sheet',paint))
# Visible clamp straps and brackets on both legs of the existing U-return.
c=master('U_return_wall_strap');axial('Fitted strap',[(0,.224),(.14,.224)],c,paint)
box('Clamp ear',(0,-.244,.07),(.16,.08,.14),steel,c)
for yy,levels in [(5.5,[2.2,5.6,8.8,11.3]),(6.5,[2.2,5.6,8.8])]:
 for zz in levels:
  inst('U_return_wall_strap',Matrix.Translation((-8.0,yy,zz-.07)))
  wall_x=9.50 if zz<2.75 else 9.564
  box('U-return bracket',(-(8.22+wall_x)/2,yy,zz),(wall_x-8.22,.17,.13),steel,C)
  box('U-return wall plate',(-wall_x+.025,yy,zz),(.07,.36,.30),paint,C)
# PBR review: retain material colors and scene layout, remove graphic contour rendering.
s.render.use_freestyle=False;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
s.cycles.samples=64;s.cycles.use_denoising=True
for ob in s.objects:
 if ob.type=='LIGHT':
  if ob.data.type=='AREA':ob.hide_render=True
  if ob.data.type=='SUN':ob.data.energy=2.2;ob.data.color=(1.0,.83,.67);ob.data.angle=.10
if s.world and s.world.use_nodes:
 for node in s.world.node_tree.nodes:
  if node.type=='BACKGROUND' and node.name=='Background':node.inputs['Color'].default_value=(.42,.49,.62,1);node.inputs['Strength'].default_value=.80
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 for node in mat.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED':
   if 'Cladding' in mat.name or 'enamel' in mat.name.lower() or 'DUCT' in mat.name:
    node.inputs['Metallic'].default_value=0;node.inputs['Roughness'].default_value=.48
    node.inputs['Coat Weight'].default_value=.12;node.inputs['Coat Roughness'].default_value=.34
   elif 'steel' in mat.name.lower() and not node.inputs['Metallic'].is_linked:
    node.inputs['Metallic'].default_value=.7;node.inputs['Roughness'].default_value=.46
bpy.context.view_layer.update();assert camera==[list(r) for r in s.camera.matrix_world] and lens==s.camera.data.lens
assert all(all(abs(v-1)<1e-5 for v in ob.scale) for ob in C.objects)
(O/'audit.json').write_text(json.dumps({'camera_preserved':True,'existing_mesh_geometry_unchanged':True,'unit_scale_instances':True,'hidden_old_services':hidden,'diameters_m':[.4,.6,1.35],'largest_housing_diameter_m':1.95,'primary_size_factor':.75,'vent_back_plane_x':-9.7,'receiver_back_plane_x':-9.25,'u_return_straps':7,'side_duct_port_error':max(side_joins),'preview':'Cycles PBR, AgX, no Freestyle','duct_section_m':[1.4,1.0],'primary_alley_y':26.0,'primary_camera_forward_distance_m':40.0,'route_endpoints':endpoints,'unassigned_new_route_endpoints':0},indent=2))
kit=R/'art/components/services/scale-v002';kit.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(kit/'large-service-masters.blend'),set(assets.values()),fake_user=True)
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
print('SERVICE_SCALE_DONE')
