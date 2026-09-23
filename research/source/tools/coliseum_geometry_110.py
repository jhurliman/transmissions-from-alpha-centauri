"""Editable front-half coliseum kit. UCL-01 form; DP-03 layered structure; UX-01 distant rhythm.
No reference projection. Uniform clay, role attributes for subsequent look development.
"""
import bpy,bmesh,math,random,json,time,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-110';O.mkdir(parents=True,exist_ok=True)
t0=time.time();bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-109/A/scene.blend'));s=bpy.context.scene
camera=s.camera.matrix_world.copy()
for c in list(bpy.data.collections):
 if c.name.startswith('109 Coliseum'):
  for ob in list(c.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.collections.remove(c)
C=bpy.data.collections.new('110 Coliseum detailed front ruin');s.collection.children.link(C)
m=bpy.data.materials.new('110 Clay masonry');m.diffuse_color=(.34,.29,.27,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.34,.29,.27,1)
m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.88
rad=75.;cy=347.;thick=8.0;H=78.;step=math.tau/36
# Global modest physical lean, anchored at center of foundation. Cornice curvature is not treated as tilt.
lean=Matrix.Rotation(math.radians(2),4,'X')
def point(r,a,z):
 batter=1-.055*z/H
 v=lean@Vector((r*batter*math.cos(a),r*batter*math.sin(a),z));return(v.x,cy+v.y,v.z)
def mesh(name,vs,fs,role='wall',tier=-1,bay=-1):
 me=bpy.data.meshes.new('COL110 '+name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new('COL110 '+name,me);C.objects.link(ob);me.materials.append(m);ob['coliseum_role']=role;ob['tier']=tier;ob['bay']=bay;return ob

def slab(name,ri,ro,z0,z1,a0,a1,n=3,role='wall',tier=-1,bay=-1,profile=None):
 L=n+1;vs=[]
 for top in [False,True]:
  for rr in [ri,ro]:
   for j in range(L):vs.append(point(rr,a0+(a1-a0)*j/n,(profile[j] if profile else z1) if top else z0))
 fs=[]
 for j in range(n):fs += [(j,j+1,L+j+1,L+j),(2*L+j,3*L+j,3*L+j+1,2*L+j+1),(j,2*L+j,2*L+j+1,j+1),(L+j,L+j+1,3*L+j+1,3*L+j)]
 fs += [(0,L,3*L,2*L),(n,2*L+n,3*L+n,L+n)]
 return mesh(name,vs,fs,role,tier,bay)

def wedge(name,a,spring,r0,r1,p0,p1,depthfront,depthback,role,tier,bay):
 # Arch voussoir segment, square radial joint faces, true curved soffit.
 N=3;vs=[]
 for rr in [depthback,depthfront]:
  for ar in [r0,r1]:
   for k in range(N+1):
    t=p0+(p1-p0)*k/N;u=ar*math.cos(t);vs.append(point(rr,a+u/rad,spring+ar*math.sin(t)))
 L=N+1;fs=[]
 for k in range(N):fs.extend([(k,k+1,L+k+1,L+k),(2*L+k,3*L+k,3*L+k+1,2*L+k+1),(k,2*L+k,2*L+k+1,k+1),(L+k,L+k+1,3*L+k+1,3*L+k)])
 fs.extend([(0,L,3*L,2*L),(N,2*L+N,3*L+N,L+N)])
 return mesh(name,vs,fs,role,tier,bay)

start=-math.pi;end=0
slab('half-ring structural foundation',rad-11,rad+1,0,2.73,start,end,144,'band')
pitch=18.33;archhalf=rad*step*.34
for tier in range(3):
 bottom=2.73+tier*pitch;top=bottom+pitch;spring=top-2.184-archhalf
 for j in range(18):
  a=start+(j+.5)*step;name=f'T{tier} B{j:02d}'
  # Main spandrel with real arch cutout, uninterrupted wall above.
  N=24;vs=[]
  for rr in [rad-thick,rad]:
   for k in range(N+1):
    u=-archhalf+2*archhalf*k/N;lo=spring+math.sqrt(max(0,archhalf**2-u**2));vs.extend([point(rr,a+u/rad,lo),point(rr,a+u/rad,top)])
  L=2*(N+1);fs=[]
  for k in range(N):
   p=2*k;fs.extend([(p,p+2,p+3,p+1),(L+p,L+p+1,L+p+3,L+p+2),(p,L+p,L+p+2,p+2),(p+1,p+3,L+p+3,L+p+1)])
  fs.extend([(0,1,L+1,L),(2*N,L+2*N,L+2*N+1,2*N+1)])
  mesh(name+' loadbearing arch tunnel',vs,fs,'wall',tier,j)
  # Two recessed/extruded archivolts; individual voussoirs give masonry radial seams.
  for ring,(inner,outer,front) in enumerate([(archhalf-.03,archhalf+.36,rad+.27),(archhalf+.41,archhalf+.83,rad+.52)]):
   for k in range(13):
    p0=math.pi*k/13+.008;p1=math.pi*(k+1)/13-.008
    wedge(name+f' archivolt{ring} stone{k:02d}',a,spring,inner,outer,p0,p1,front,rad-.12,'arch_molding',tier,j)
  # Jamb lining continues down to plinth, and impost blocks support arch spring.
  for sign in [-1,1]:
   aa=a+sign*(archhalf+.35)/rad
   slab(name+f' jamb {sign}',rad-.15,rad+.29,bottom+.56,spring,aa-.23/rad,aa+.23/rad,1,'pier',tier,j)
   slab(name+f' impost {sign}',rad-.3,rad+.72,spring-.35,spring+.13,aa-.65/rad,aa+.65/rad,2,'band',tier,j)
  # Under-arch sill edge, not a pane or backing.
  slab(name+' sill',rad-thick-.4,rad+.42,bottom,bottom+.35,a-step*.345,a+step*.345,5,'band',tier,j)
  # Piers at bay right boundaries, with jointed shallow facing courses.
  pa=a+step*.5;w=step*.16
  slab(name+' solid pier',rad-thick,rad,bottom,top,pa-w,pa+w,4,'pier',tier,j)
  slab(name+' pier pilaster',rad-.08,rad+.42,bottom+.45,top-.75,pa-w*.54,pa+w*.54,2,'pier',tier,j)
  for z,hh,out,ww in [(bottom,.55,.7,.76),(bottom+.55,.25,.5,.65),(top-.88,.36,.6,.67),(top-.52,.38,.84,.83)]:
   slab(name+' pier plinth capital',rad-.1,rad+out,z,z+hh,pa-w*ww,pa+w*ww,2,'band',tier,j)
  for k in range(1,5):
   z=bottom+(top-bottom)*k/5
   slab(name+f' pier bedding joint{k}',rad+.415,rad+.46,z,z+.065,pa-w*.53,pa+w*.53,2,'detail',tier,j)
 # continuous bands segmented per bay, with stepped profiles and selective losses.
 for j in range(18):
  a0=start+j*step;a1=a0+step-.0006
  for k,(z0,z1,ro) in enumerate([(top-.12,top+.25,rad+.5),(top+.25,top+.63,rad+1.02),(top+.63,top+1.00,rad+.8),(top+1.0,top+1.33,rad+1.3),(top+1.33,top+1.60,rad+.68)]):
   # few broken lengths on upper cornice, not independent uniform random damage.
   if tier==2 and j in [3,12] and k>=3:a1=a0+step*.74
   slab(f'T{tier} band{j:02d} profile{k}',rad-thick*1.3,ro,z0,z1,a0,a1,7,'band',tier,j)
 # close left boundary pier
 slab(f'T{tier} left cut end pier',rad-thick,rad,bottom,top,start,start+step*.16,3,'pier',tier,0)

# Upper wall. A connected uneven fracture profile, retaining substantial intact sections.
base=59.36
crown=[73,73,74,76,76,76,67,65,67,74,74,74,65,66,72,72,70,68,66]
for j in range(18):
 a0=start+j*step;a1=a0+step;ac=(a0+a1)/2;rng=random.Random(110+j)
 h0=crown[j];h1=crown[j+1];slotw=step*.08;slotbottom=base+3.2;slottop=base+5.4
 slab(f'U{j} sill wall',rad-thick,rad,base,slotbottom,a0,a1,8,'wall',3,j)
 for side,aa,bb in [('L',a0,ac-slotw),('R',ac+slotw,a1)]:
  profile=[]
  for k in range(7):
   alpha=((aa+(bb-aa)*k/6)-a0)/step
   transition=max(0,min(1,(alpha-.76)/.24))
   profile.append(max(slottop+.65,h0*(1-transition)+h1*transition+rng.uniform(-.18,.18)))
  slab(f'U{j} fractured upper wall {side}',rad-thick,rad,slotbottom,max(profile),aa,bb,6,'wall',3,j,profile)
 # head includes irregular top, opening remains real.
 profile=[max(slottop+.65,h0+q) for q in [0,.18,-.12,.13]]
 slab(f'U{j} aperture head',rad-thick,rad,slottop,max(profile),ac-slotw,ac+slotw,3,'wall',3,j,profile)
 # sparse shallow framing around apertures, stones not lit windows.
 for sign in [-1,1]:
  aa=ac+sign*(slotw+.0009);slab(f'U{j} slot jamb {sign}',rad-.1,rad+.24,slotbottom,slottop,aa-.002,aa+.002,1,'detail',3,j)
 # surviving coping lengths leave deliberate exposed fractured thickness.
 if j not in [0,4,7,12,13,17]:
  slab(f'U{j} surviving coping',rad-thick-.18,rad+.34,h0+.12,h0+.48,a0+step*.18,a0+step*.68,4,'band',3,j)

# Projecting engaged towers every third bay, substantial contrast against arcade repetition.
for j in [1,4,7,10,13,16]:
 a=start+j*step;w=step*.19;top=[75.5,80,76.5,79,74,71][[1,4,7,10,13,16].index(j)]
 slab(f'Tower{j} core',rad-2,rad+2.8,0,top,a-w,a+w,6,'tower',-1,j)
 for sign in [-1,1]:
  aa=a+sign*w*.73
  slab(f'Tower{j} flanking rib{sign}',rad+2.65,rad+3.18,1.5,top-.55,aa-w*.12,aa+w*.12,2,'tower',-1,j)
 # center inset remains same stone but physical channel formed between projecting ribs.
 for z in [2.7,20.8,39.1,57.5,top-2.1]:
  for k,(dz,hh,rr) in enumerate([(0,.34,3.18),(.34,.52,4.1),(.86,.35,3.6)]):
   slab(f'Tower{j} collar{z:.1f} step{k}',rad-2.15,rad+rr,z+dz,z+dz+hh,a-w*1.11,a+w*1.11,6,'band',-1,j)
 # fractured crown with exposed masonry cap thickness, unequal teeth.
 profile=[top+.4,top+.65,top-.1,top+.1,top+.9,top+.6,top+.3]
 slab(f'Tower{j} broken crown',rad-2,rad+2.8,top-.3,top+.9,a-w,a+w,6,'fracture',-1,j,profile)

# Cut-end buttressing closes the front half without any rear wall.
for a,label in [(start,'left'),(end,'right')]:
 da=.021 if a==start else -.021
 slab(label+' exposed terminal buttress',rad-8,rad+.8,0,60,min(a,a+da),max(a,a+da),2,'tower')
# Physical gallery strips are only against front facade; no rear geometry.
for z in [21.1,39.4,57.7]:slab('inner gallery floor',rad-10,rad-thick,z,z+.48,start,end,90,'band')

# Canonical bay-local meshes share exact repeated intact geometry. Unequal crown fragments hash uniquely.
import hashlib
pool={};linked=0;maxerr=0.
for ob in C.objects:
 bay=int(ob.get('bay',-1))
 if bay<0:continue
 a=start+(bay+.5)*step
 M=Matrix.Translation(Vector((0,cy,0))) @ lean @ Matrix.Rotation(a,4,'Z')
 inv=M.inverted();coords=[inv@v.co for v in ob.data.vertices]
 faces=[tuple(p.vertices) for p in ob.data.polygons]
 key=hashlib.sha256(repr((ob.get('coliseum_role'),[tuple(round(x,3) for x in v) for v in coords],faces)).encode()).hexdigest()
 if key in pool:
  me=pool[key];linked+=1
 else:
  me=bpy.data.meshes.new(ob.name+' reusable local mesh');me.from_pydata(coords,[],faces);me.update();me.materials.append(m);pool[key]=me
 for old,new in zip(ob.data.vertices,me.vertices):maxerr=max(maxerr,((M@new.co)-old.co).length)
 ob.data=me;ob.matrix_world=M;ob['kit_mesh_key']=key[:12]
assert maxerr<.002, maxerr
assert s.camera.matrix_world==camera
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'))
audit={'source':'109A','reference_ids':['UCL-01','DP-03','UX-01'],'objects':len(C.objects),'linked_instances':linked,'unique_bay_meshes':len(pool),'canonicalization_max_error_m':maxerr,'wall_depth_m':thick,'front_half_only':True,'radius':75,'height_nominal':78,'tiers':3,'bays_front_half':18,'lean_degrees':{'toward_camera':2,'right':0,'radial_inward_batter_percent':5.5},'tilt_evidence':'Critic manual UCL-01 tower centers: left leans screen-right3–4deg; middle screen-left3deg; right screen-left6deg. These converge, not uniform roll. Fit uses5.5percent radial inward batter and2deg forward lean; inferred geometry, not exact physical measurement.','camera_preserved':True,'build_seconds':time.time()-t0,'uniform_material':'110 Clay masonry','role_property':'coliseum_role'}
(O/'geometry-audit.json').write_text(json.dumps(audit,indent=2))
if os.environ.get('COL_RENDER')=='1':
 s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.30;s.render.border_max_x=.71;s.render.border_min_y=.48;s.render.border_max_y=.89;s.render.use_freestyle=False;s.render.filepath=str(O/'geometry-clay.png');bpy.ops.render.render(write_still=True)
