"""Distinct right-side section families; approved services unchanged."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-034';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-033/scene.blend'));s=bpy.context.scene
cam=s.camera.matrix_world.copy();lens=s.camera.data.lens
old=bpy.data.collections['027 Reviewed architecture assembly'];hidden=[]
def signature(o):
 return (tuple(v for row in o.matrix_world for v in row),hashlib.sha256(str([tuple(v.co) for v in o.data.vertices]).encode()).hexdigest() if o.type=='MESH' else None)
original={o.name:signature(o) for o in s.objects}
keys={'layout_broad','layout_access','layout_transition','window_bay','window_open','window_broken','floor_band'}
for ob in old.objects:
 hide=False
 if ob.instance_collection and ob.instance_collection.get('part_id') in keys and ob.location.x>0 and ob.location.y>=6:hide=True
 if ob.type=='MESH' and ob.name.startswith(('Building structural backing','Building side return','Return horizontal joint','Vertical structural pier','Ground bay plinth')):
  pts=[ob.matrix_world@v.co for v in ob.data.vertices]
  if sum(v.x for v in pts)/len(pts)>0 and sum(v.y for v in pts)/len(pts)>=6:hide=True
 if hide:ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
paint=bpy.data.materials['Cladding | slate enamel'];pale=bpy.data.materials['Cladding | pale mineral blue'];steel=bpy.data.materials['Structure | charcoal steel'];dark=bpy.data.materials['Recess | dark backing'];concrete=bpy.data.materials['Structure | bare mineral']
C=bpy.data.collections.new('034 Distinct right buildings');s.collection.children.link(C);masters=[]
assets={c.get('part_id'):c for c in bpy.data.collections if c.get('part_id')}
def start(name,x,y):
 global kit
 kit=bpy.data.collections.new('FAC | '+name);kit['part_id']=name;kit.asset_mark();masters.append(kit)
 ob=bpy.data.objects.new(name,None);ob.instance_type='COLLECTION';ob.instance_collection=kit;C.objects.link(ob);ob.matrix_world=Matrix.Translation((x,y,0))@Matrix.Rotation(-math.pi/2,4,'Z')
def window(u,d,z,key='window_bay'):
 ob=bpy.data.objects.new('Inset slider | '+key,None);ob.instance_type='COLLECTION';ob.instance_collection=assets[key];ob.location=(u,d,z);kit.objects.link(ob)
def mesh(n,vs,fs,m,transform=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);ob=bpy.data.objects.new(n,me);kit.objects.link(ob);ob.matrix_world=transform or Matrix.Identity(4);be=ob.modifiers.new('Manufactured edge','BEVEL');be.width=.012;be.segments=2;return ob
F=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
def box(n,p,d,m,transform=None):
 x,y,z=p;a,b,c=[v/2 for v in d];v=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(n,v,F,m,transform)
def prism(n,u0,u1,profile,m):
 N=len(profile);vs=[(u,d,z) for u in [u0,u1] for d,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];return mesh(n,vs,fs,m)
def panel(n,u0,u1,z0,z1,depth,m=paint,transform=None):
 gap=.022;return box(n,((u0+u1)/2,depth+.04,(z0+z1)/2),(u1-u0-gap,.08,z1-z0-gap),m,transform)

# Middle block: recessed vertical galleries between structural ribs.
start('right_vertical_galleries',9.5,11.6)
profile=[(.35,0),(.35,2.65),(.65,2.95),(.65,15.48),(1.4,16.23),(1.4,23),(4,23),(4,0)]
for a,b in [(-5.6,-5.48),(5.48,5.6)]:prism('Gallery end return',a,b,profile,paint)
box('Gallery closed back',(0,3.9,11.5),(11.2,.2,23),dark)
for u in [-4.2,-1.4,1.4,4.2]:
 for za,zb in [(.12,1.35),(1.35,2.65)]:panel('Gallery base panel',u-1.4,u+1.4,za,zb,.35)
 T=Matrix.Translation((u,.35,2.65))@Matrix.Rotation(-math.pi/4,4,'X');panel('Gallery base bevel',-1.4,1.4,0,.3*math.sqrt(2),0,pale,T)
 for row in range(4):window(u,.65,3+3.12*row,['window_bay','window_open','window_broken','window_bay'][(row+int(u*5))%4])
 # Inset upper mass with broad quiet panels; no endless window grid.
 for za,zb in [(16.23,18.6),(18.6,21),(21,23)]:panel('Gallery upper quiet panel',u-1.4,u+1.4,za,zb,1.4)
 T=Matrix.Translation((u,.65,15.48))@Matrix.Rotation(-math.pi/4,4,'X');panel('Gallery upper chamfer',-1.4,1.4,0,.75*math.sqrt(2),0,pale,T)
# Paired stiles define deep vertical shadow bays, aligned with service mounting datum.
for u in [-5.5,-2.8,0,2.8,5.5]:
 prism('Gallery structural blade',u-.12,u+.12,[(0,2.65),(0,14.8),(.65,15.45),(1.4,16.23),(1.65,16.23),(1.65,2.65)],pale)
 for z in [3,9.24,15.3]:box('Blade bearing cap',(u,-.04,z),(.38,.2,.16),paint)
# Keep existing support heads landing on a solid common bearing.
box('Gallery support bearing',(0,.10,2.45),(11.2,.5,.3),concrete)
kit['rules']='Vertical bays: four aligned slider stacks, deep reveals, quiet upper mass, 45 degree setbacks.'
# Rear block: horizontal, mostly solid utility mass with a broad 30-degree shoulder.
start('right_horizontal_utility',8.85,24.6)
W=14.8;rise=2.4;run=rise*math.tan(math.pi/6)
profile=[(.3,0),(.3,2.65),(-.25,2.65),(-.25,3.0),(run-.25,5.4),(run-.25,10.2),(.45,10.2),(.45,17),(4,17),(4,0)]
for a,b in [(-7.4,-7.28),(7.28,7.4)]:prism('Utility end return',a,b,profile,paint)
box('Utility closed back',(0,3.9,8.5),(14.8,.2,17),dark)
for ua,ub in [(-7.4,-4.2),(-4.2,-1.4),(-1.4,1.4),(1.4,4.2),(4.2,7.4)]:
 for za,zb in [(.15,1.25),(1.25,2.65)]:panel('Utility base',ua,ub,za,zb,.3)
 panel('Utility projecting edge',ua,ub,2.65,3,-.25,pale)
 T=Matrix.Translation((0,-.25,3))@Matrix.Rotation(-math.pi/6,4,'X')
 panel('Utility broad rake',ua,ub,0,rise/math.cos(math.pi/6),0,paint,T)
 for za,zb in [(5.4,7.6),(7.6,10.2)]:panel('Utility broad plate',ua,ub,za,zb,run-.25)
 panel('Utility crown panel',ua,ub,13.32,17,.45)
# One horizontal band of existing two-panel sliders; end margins close the mass.
for u in [-5.6,-2.8,0,2.8,5.6]:window(u,.45,10.2,'window_open' if u==0 else 'window_bay')
for ua,ub in [(-7.4,-7),(7,7.4)]:panel('Ribbon end closure',ua,ub,10.2,13.32,.45)
box('Ribbon underside',(0,.7,10.19),(14.8,.85,.10),pale)
box('Utility support bearing',(0,.1,2.45),(14.8,.5,.3),concrete)
# Two unequal groups of louver hoods, with solid returns into their receiving wall.
for u,width in [(-4.8,2.1),(.5,3.3)]:
 d=run-.25
 box('Vent return',(u,d-.15,7),(width,.34,1.65),dark)
 for uu in [u-width/2,u+width/2]:box('Vent side cheek',(uu,d-.2,7),(.12,.45,1.8),paint)
 for z in [6.12,7.88]:box('Vent head and sill',(u,d-.2,z),(width+.12,.45,.12),pale)
 for j in range(8):box('Vent horizontal vane',(u,d-.38,6.27+j*.21),(width,.19,.075),paint)
kit['rules']='Horizontal utility block: broad 30 degree shoulder, unequal ventilation groups, single high slider ribbon.'
bpy.context.view_layer.update()
assert s.camera.matrix_world==cam and s.camera.data.lens==lens
assert all(signature(bpy.data.objects[n])==v for n,v in original.items())
K=R/'art/components/facades/v017';K.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(K/'right-building-families.blend'),set(masters),fake_user=True)
(O/'audit.json').write_text(json.dumps({'camera_preserved':True,'existing_geometry_hashes_and_transforms_preserved':True,'hidden_old_facade_objects':hidden,'families':[c['part_id'] for c in masters]},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
