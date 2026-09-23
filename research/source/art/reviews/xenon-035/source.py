import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-035';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-034/scene.blend'));s=bpy.context.scene
camera=s.camera.matrix_world.copy();lens=s.camera.data.lens
paint=bpy.data.materials['Cladding | slate enamel'];pale=bpy.data.materials['Cladding | pale mineral blue'];steel=bpy.data.materials['Structure | charcoal steel'];dark=bpy.data.materials['Recess | dark backing'];concrete=bpy.data.materials['Structure | bare mineral']
assets={c.get('part_id'):c for c in bpy.data.collections if c.get('part_id')};hidden=[]
def hide(o):o.hide_render=True;o.hide_viewport=True;hidden.append(o.name)
def inst(key,p,M=None):
 ob=bpy.data.objects.new('035 | '+key,None);ob.instance_type='COLLECTION';ob.instance_collection=assets[key];kit.objects.link(ob);ob.matrix_world=M or Matrix.Translation(p);return ob
def mesh(n,vs,fs,m,transform=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);ob=bpy.data.objects.new(n,me);kit.objects.link(ob);ob.matrix_world=transform or Matrix.Identity(4);be=ob.modifiers.new('Manufactured edge','BEVEL');be.width=.012;be.segments=2;return ob
F=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
def box(n,p,d,m,transform=None):
 x,y,z=p;a,b,c=[v/2 for v in d];v=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(n,v,F,m,transform)
def prism(n,u0,u1,profile,m):
 N=len(profile);vs=[(u,d,z) for u in [u0,u1] for d,z in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)];return mesh(n,vs,fs,m)
def panel(n,u0,u1,z0,z1,depth,m=paint,transform=None):
 gap=.022;return box(n,((u0+u1)/2,depth+.04,(z0+z1)/2),(u1-u0-gap,.08,z1-z0-gap),m,transform)


kit=assets['right_horizontal_utility']
for ob in list(kit.objects):
 if ob.name.startswith('Utility crown panel'):hide(ob)
for u in [-5.6,-2.8,0,2.8,5.6]:inst('window_broken' if u==-2.8 else 'window_bay',(u,.45,13.32))
for a,b in [(-7.4,-7),(7,7.4)]:panel('Upper ribbon end',a,b,13.32,16.44,.45)
panel('Roof parapet',-7.4,7.4,16.44,17,.45)
box('Utility roof deck',(0,2.2,16.92),(14.8,3.6,.16),paint)
# Restore two selected bays only.
for key,u,d,prefix in [('right_vertical_galleries',4.2,.35,'Gallery base panel'),('right_horizontal_utility',0,.3,'Utility base')]:
 kit=assets[key]
 for ob in list(kit.objects):
  if ob.type=='MESH' and ob.name.startswith(prefix):
   center=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices)
   if abs(center-u)<.02:hide(ob)
 inst('layout_access' if key=='right_vertical_galleries' else 'layout_transition',(u,d,.12))
kit=bpy.data.collections.new('035 Service destinations and side architecture');s.collection.children.link(kit)
# Replace only requested caps; all lower assemblies stay in place.
for n in ['Architecture | blind.003','Architecture | blind.004','Architecture | duct_cap.002']:hide(bpy.data.objects[n])
def tube(name,points,r=.2):
 vs=[];N=32
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])).normalized();u=Vector((0,1,0));v=t.cross(u).normalized()
  for j in range(N):vs.append(tuple(p+r*(u*math.cos(j*math.tau/N)+v*math.sin(j*math.tau/N))))
 fs=[]
 for i in range(len(points)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;fs.append((a,b,b+N,a+N))
 ob=mesh(name,vs,fs,paint)
 for f in ob.data.polygons:f.use_smooth=True
 ob.modifiers.clear()
# Rear round pipe: extension, broad U bend above roof, descending into flashed curb.
x=7.8;y=23;z=17.55;rr=1.1
pts=[(x,y,13.42),(x,y,z)]+[(x+rr*(1-math.cos(t*math.pi/32)),y,z+rr*math.sin(t*math.pi/32)) for t in range(1,33)]+[(x+2*rr,y,16.8)]
tube('Roof return continuous pipe',pts)
box('Roof penetration flashing',(10,23,17.02),(.75,.75,.2),pale)
for zc in [14.6,16.5]:
 inst('detail_collar',(7.8,23,zc));box('Roof riser wall bracket',(8.6,23,zc+.1),(1.65,.16,.12),steel)
# Near round riser bends into a projecting wall receiver.
pts=[(9,8,14.92)]+[(9+.55*(1-math.cos(t*math.pi/32)),8,14.92+.55*math.sin(t*math.pi/32)) for t in range(1,17)]+[(10.3,8,15.47)]
tube('Round riser wall elbow',pts)
box('Round wall receiver',(10.25,8,15.47),(.48,.72,.72),paint)
# Rectangular duct uses its authored bend; oriented width across world Y.
vs=[]
for i in range(25):
 t=i*math.pi/48;p=Vector((8.95+.48*(1-math.cos(t)),15.8,12.9+.48*math.sin(t)));a=Vector((0,.28,0));b=Vector((math.cos(t)*.19,0,-math.sin(t)*.19))
 for aa,bb in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append(tuple(p+aa*a+bb*b))
fs=[]
for i in range(24):
 for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
mesh('Duct fitted quarter bend',vs,fs,paint)
# Bend exits +X at 9.43, 15.8, 13.38. Native rectangular run docks into wall box.
box('Duct wall run',(9.93,15.8,13.38),(1.04,.56,.38),paint)
box('Duct wall receiver',(10.40,15.8,13.38),(.55,.65,.82),pale)
# Remove protruding legacy narrow structural strips beyond rear roof height.
for ob in list(s.objects):
 if ob.hide_render or ob.type!='MESH' or ob.name in kit.objects:continue
 pts=[ob.matrix_world@v.co for v in ob.data.vertices]
 if not pts:continue
 lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if lo[0]>7 and lo[1]>17 and hi[2]>17.15 and hi[0]-lo[0]<.4 and hi[1]-lo[1]<.4:hide(ob)
# Replace the repetitive visible end-of-road wall; create large grouped fields with a loading portal.
for ob in list(s.objects):
 if ob.name.startswith(('Side road far facade','Side road vertical seam','Side road floor joint','Side road recessed service panel','Side road north floor band','Side road north vertical seam')):hide(ob)
# End facade at X=19, local horizontal axis along Y.
T=Matrix.Translation((18.7,3.2,0))@Matrix.Rotation(-math.pi/2,4,'Z')
for a,b in [(-2.8,-1.4),(1.4,2.8)]:
 for za,zb in [(0,3.6),(3.6,7.2),(7.2,12.2),(12.2,17),(17,21)]:panel('Side road broad end cladding',a,b,za,zb,0,paint,T)
box('Loading entrance shadow',(0,.55,1.8),(2.8,.2,3.6),dark,T)
for u in [-1.38,1.38]:box('Loading portal jamb',(u,-.08,1.85),(.18,.32,3.7),pale,T)
box('Loading portal lintel',(0,-.12,3.65),(3.05,.55,.25),pale,T)
for zc in [.5,1.4,2.3,3.2]:box('Door broad panel',(0,.35,zc),(2.5,.09,.85),paint,T)
for zc in [4.0,7.12]:inst('window_open' if zc==4 else 'window_bay',(0,0,0),T@Matrix.Translation((0,0,zc)))
for za,zb in [(10.24,13.8),(13.8,17.4),(17.4,21)]:panel('End wall upper grouped panel',-1.4,1.4,za,zb,0,paint,T)
# Side of the middle building facing road: broad structural bays and a recessed service door.
for x0,x1 in [(9.6,13.5),(13.5,18),(18,23),(23,29.5)]:
 for za,zb in [(4.3,8.6),(8.6,14.5),(14.5,21)]:
  if x1<=18 and za<14.5:
   cx=(x0+x1)/2
   for a,b in [(x0,cx-1.4),(cx+1.4,x1)]:box('Road window surround',((a+b)/2,5.90,(za+zb)/2),(b-a-.025,.15,zb-za-.025),paint)
   inst('window_bay' if za==4.3 else 'window_open',(cx,6.04,za))
   box('Road window upper field',(cx,5.90,(za+3.12+zb)/2),(2.78,.15,zb-za-3.12-.025),paint)
  else:box('Road-facing broad panel',((x0+x1)/2,5.94,(za+zb)/2),(x1-x0-.035,.10,zb-za-.035),paint)
for x0 in [13.5,23]:box('Road elevation structural pilaster',(x0,5.77,6.8),(.30,.42,13.6),pale)
box('Road-facing service portal',(12,5.82,1.85),(2.6,.22,3.7),dark)
for x0 in [10.65,13.35]:box('Road portal jamb',(x0,5.62,1.9),(.15,.32,3.8),pale)
box('Road portal hood',(12,5.45,3.9),(3,.95,.20),paint)
assert s.camera.matrix_world==camera and s.camera.data.lens==lens
K=R/'art/components/facades/v018';K.mkdir(parents=True,exist_ok=True)
bpy.data.libraries.write(str(K/'right-refinements.blend'),{assets['right_horizontal_utility'],assets['right_vertical_galleries'],kit},fake_user=True)
(O/'audit.json').write_text(json.dumps({'camera_preserved':True,'hidden_objects':hidden,'endpoints':['Rear round: roof penetration at (10,23,17)','Near round: projecting wall receiver','Rectangular: 90 degree turn into wall receiver'],'window_rows':2,'restored_ground_bays':2},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
