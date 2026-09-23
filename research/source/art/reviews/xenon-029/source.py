"""Large service infrastructure in the far alley, dimensioned masters at unit scale."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-029';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-027/scene.blend'));s=bpy.context.scene
original=list(s.objects);camera=[list(r) for r in s.camera.matrix_world];lens=s.camera.data.lens
C=bpy.data.collections.new('029 Distant large service infrastructure');s.collection.children.link(C)
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
for k,r,L in [('trunk_1800_L4',.9,4),('companion_600_L3',.3,3)]:
 c=master(k);axial('Hollow straight section',[(0,r),(L,r)],c);c['dimensions']=json.dumps({'diameter':r*2,'length':L});c['ports_json']=json.dumps([{'position':[0,0,z],'outward':[0,0,-1 if z==0 else 1],'diameter':r*2} for z in [0,L]])
for k,r,Rbig,L in [('housing_2600',.9,1.3,2.6),('housing_1000',.3,.5,1.5)]:
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
x,y=-6.45,26.0;z=3.0
for k,L in [('trunk_1800_L4',4),('housing_2600',2.6),('trunk_1800_L4',4)]:inst(k,base(x,y,z));z+=L
inst(wallturn('primary_bottom_wall_turn',.9,1.4,2.55,True),base(x,y,3.0));endpoints.append({'route':'primary','bottom':'90 into wall','top':'projecting building receiver'})
# Massive upper architectural receiver: native local geometry and panel seams.
c=master('primary_building_receiver');box('Projecting receiver',(0,.80,1.03),(3.0,3.0,2.16),paint,c)
box('Receiver front cover',(0,-.735,1.10),(2.60,.07,1.65),pale,c)
for xx in [-1.12,1.12]:
 for zz in [.40,1.80]:box('Receiver fastener',(xx,-.79,zz),(.12,.06,.12),steel,c)
axial('Receiver docking collar',[(-.05,1.06),(.06,1.06)],c,steel)
inst('primary_building_receiver',base(x,y,z-.04))
for zz in [4.2,8.2,12.1]:
 box('Primary structural standoff',(-8.15,y,zz),(2.0,.35,.22),steel,C)
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
 for xx in [-.75,.75]:box('Duct cuff',(xx,0,zz),(.10,1.14,.10),steel,c)
 for yy in [-.55,.55]:box('Duct cuff',(0,yy,zz),(1.55,.10,.10),steel,c)
x,y=-7.80,19.0
for z in [.65,3.65,6.65]:inst('duct_1400x1000_L3',base(x,y,z))
c=master('large_vent_terminal')
for xx in [-.85,.85]:box('Vent frame',(xx,0,.85),(.12,1.22,1.70),paint,c)
for zz in [.06,1.66]:box('Vent frame',(0,0,zz),(1.8,1.22,.12),paint,c)
box('Vent cavity',(0,.50,.85),(1.6,.10,1.5),steel,c)
for j in range(7):box('Vent slat',(0,-.40,.25+j*.2),(1.6,.35,.055),pale,c)
inst('large_vent_terminal',base(x,y,9.60))
for zz in [2.1,5.2,8.2]:box('Duct wall standoff',(-8.95,y,zz),(1.40,.28,.18),steel,C)
c=master('duct_building_plinth');box('Projecting service plinth',(0,.55,.35),(1.85,2.30,.70),paint,c);box('Plinth cover',(0,-.64,.36),(1.56,.06,.44),pale,c);inst('duct_building_plinth',base(x,y,0))
endpoints.append({'route':'large duct','bottom':'building plinth','top':'louver terminal'})
# Remove only the obsolete small far-left service bank; retain facade and vista.
old=bpy.data.collections['027 Reviewed architecture assembly'];hidden=[]
for ob in old.objects:
 if ob.instance_collection and ob.location.x<0 and ob.location.y>21 and ob.instance_collection.name.startswith('PIP_'):
  ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
bpy.context.view_layer.update();assert camera==[list(r) for r in s.camera.matrix_world] and lens==s.camera.data.lens
assert all(all(abs(v-1)<1e-5 for v in ob.scale) for ob in C.objects)
(O/'audit.json').write_text(json.dumps({'camera_preserved':True,'existing_mesh_geometry_unchanged':True,'unit_scale_instances':True,'hidden_old_services':hidden,'diameters_m':[.4,.6,1.8],'largest_housing_diameter_m':2.6,'duct_section_m':[1.4,1.0],'primary_alley_y':26.0,'primary_camera_forward_distance_m':40.0,'route_endpoints':endpoints,'unassigned_new_route_endpoints':0},indent=2))
kit=R/'art/components/services/scale-v001';kit.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(kit/'large-service-masters.blend'),set(assets.values()),fake_user=True)
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
print('SERVICE_SCALE_DONE')
