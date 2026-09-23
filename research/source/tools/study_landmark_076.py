import bpy,bmesh,math,json,random,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/landmark-076';O.mkdir(parents=True,exist_ok=True)
BASE=O/'environment-075.blend';CY=376.3887;RAD=104.3887
specs=[('A','Terraced arena'),('B','Open-ring citadel'),('C','Broken docking crown')]
for label,title in specs:
 if label < os.environ.get('LANDMARK_START','A'):continue
 if os.environ.get('LANDMARK_ONLY') and label!=os.environ['LANDMARK_ONLY']:continue
 bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;camera=s.camera.matrix_world.copy();s.render.threads_mode='FIXED';s.render.threads=2
 hidden=[]
 for o in s.objects:
  if o.name.startswith(('Dome ','Fine secondary dome','Crown broken spar')):o.hide_render=True;hidden.append(o.name)
 C=bpy.data.collections.new('076 '+label+' '+title);s.collection.children.link(C)
 mats=[bpy.data.materials.get('Dome oxidized plate '+str(i)) for i in range(4)];mats=[m for m in mats if m];base=mats[1];dark=bpy.data.materials['Dome deep frame']
 def mesh(n,vs,fs,m=base):
  me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('076 '+label+' '+n,me);C.objects.link(ob);me.materials.append(m);return ob
 def pt(r,a,z):return (r*math.cos(a),CY+r*math.sin(a),z)
 def arc(n,ro,ri,z0,z1,a0,a1,m=base,N=6):
  vs=[]
  for z in [z0,z1]:
   for r in [ri,ro]:vs.extend([pt(r,a0+(a1-a0)*j/N,z) for j in range(N+1)])
  L=N+1;fs=[]
  for j in range(N):fs.extend([(j,j+1,L+j+1,L+j),(2*L+j,3*L+j,3*L+j+1,2*L+j+1),(j,2*L+j,2*L+j+1,j+1),(L+j,L+j+1,3*L+j+1,3*L+j)])
  fs.extend([(0,L,3*L,2*L),(N,2*L+N,3*L+N,L+N)]);return mesh(n,vs,fs,m)
 def arcade(r,z,h,count=36,skip=None,phase=0):
  step=math.tau/count
  for j in range(count):
   a=-math.pi/2+phase+j*step
   if skip and skip(a,j):continue
   # Structural pier and curved spandrel leave an actual arch void.
   arc('arcade pier',r,r-8,z,z+h,a-step*.66,a-step*.34,mats[j%len(mats)],2)
   width=step*.68;half=r*width/2;spring=z+h-3-half;vs=[];N=8
   for rr in [r-8,r]:
    for k in range(N+1):
     aa=a-width/2+width*k/N;u=(2*k/N-1)*half;lo=(z+h-3-min(3,max(0,abs(u)-(half-3)))) if label=='B' or (label=='C' and z>50) else spring+math.sqrt(max(0,half*half-u*u));vs.extend([pt(rr,aa,lo),pt(rr,aa,z+h)])
   L=(N+1)*2;fs=[]
   for k in range(N):
    p=k*2;fs.extend([(p,p+2,p+3,p+1),(L+p,L+p+1,L+p+3,L+p+2),(p,L+p,L+p+2,p+2),(p+1,p+3,L+p+3,L+p+1)])
   fs.extend([(0,1,L+1,L),(2*N,L+2*N,L+2*N+1,2*N+1)]);mesh('arched opening head',vs,fs,mats[j%len(mats)])
   if label=='B' and z>25 or label=='C' and z>50:arc('recessed docking bay back',RAD,RAD-1,z+1,z+h-1,a-width*.48,a+width*.48,dark,4)
 def buttress(a,r,z,wide=4):
  # Face against each terrace is sloped; all feet remain within approved footprint.
  vs=[]
  for da in [-wide/RAD/2,wide/RAD/2]:vs.extend([pt(RAD,a+da,0),pt(RAD-8,a+da,0),pt(r-5,a+da,z),pt(r,a+da,z)])
  mesh('radial buttress',vs,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],mats[2%len(mats)])
 # Footprint ring fixes the nearest edge at 272m in every option.
 arc('foundation ring',RAD,RAD-16,0,5,-math.pi/2,3*math.pi/2,base,72)
 if label=='A':
  for tier in range(4):
   r=RAD-tier*3.5;z=5+tier*21;arcade(r,z,19,36);arc('terrace band',min(RAD,r+1),r-12,z+19,z+21,-math.pi/2,3*math.pi/2,mats[2],72)
  for j in range(18):buttress(-math.pi/2+j*math.tau/18,RAD-10.5,89)
  # Rear top dock bays give a service crown instead of a roof pyramid.
  for j in range(9):
   a=math.pi/6+j*math.pi/12;arc('upper dock pier',93,78,89,103,a,a+.025,base,1);arc('upper dock canopy',95,77,101,103,a,a+math.pi/12,base,3)
 elif label=='B':
  def front_gap(a,j):return math.sin(a)<-.60
  for tier in range(4):
   z=5+tier*23;arcade(101,z,21,24,front_gap if tier>0 else None); 
   for j in range(32):
    a=-math.pi/2+j*math.tau/32
    if tier>0 and front_gap(a,j):continue
    arc('heavy ring entablature',103,87,z+21,z+23,a-math.pi/32,a+math.pi/32,base,3)
  for j in range(16):
   a=-math.pi/2+j*math.tau/16
   if not front_gap(a,j):buttress(a,101,97,5)
  # Broad paired docking terraces project inward through the court.
  for side in [-1,1]:
   a=math.pi if side<0 else 0
   arc('inward docking deck',91,55,65,69,a-.22,a+.22,base,7)
   arc('dock roof wing',95,66,95,103,a-.21,a+.21,base,7)
 else:
  # Irregularly surviving tiers produce a clear low-left/high-right silhouette.
  for tier in range(4):
   def missing(a,j,t=tier):
    if t==0:return False
    if t==1:return math.cos(a)<-.25 and math.sin(a)<-.30
    if t==2:return math.sin(a)<-.28 or (math.cos(a)<-.4)
    return math.cos(a)<.32 or math.sin(a)<-.28
   r=RAD-tier*2;z=5+tier*23;arcade(r,z,20,34,missing)
   for j in range(34):
    a=-math.pi/2+j*math.tau/34
    if not missing(a,j):arc('surviving terrace cap',min(RAD,r+1),r-13,z+20,z+23,a-math.pi/34,a+math.pi/34,base,3)
  for j in range(17):
   a=-math.pi/2+j*math.tau/17;h=26 if math.sin(a)<-.3 else 95 if math.cos(a)>.32 else 70;buttress(a,97,h,5)
  for j in range(4):
   a=-.20+j*.20;arc('docking crown roof',100,65,101,103.4,a,a+.17,base,4);arc('docking crown blade',98,72,85,103.4,a,a+.035,dark,1)
 # Three concentric interior steps imply bowl construction without micro-detail.
 for j in range(3):arc('interior stepped bowl',78-j*11,67-j*11,4+j*3,7+j*3,-math.pi/2,3*math.pi/2,mats[j%len(mats)],72)
 assert s.camera.matrix_world==camera
 s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100
 s.render.filepath=str(O/(label+'.png'));bpy.data.libraries.write(str(O/(label+'-kit.blend')),{C},fake_user=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/(label+'-scene.blend')));bpy.ops.render.render(write_still=True)
 (O/(label+'.json')).write_text(json.dumps({'title':title,'collection':C.name,'hidden_dome_objects':len(hidden),'center_y':CY,'nearest_footprint_y':272,'width':RAD*2,'height_max':103.4,'stage':'original architectural massing, not finished design','camera_preserved':True},indent=2))
