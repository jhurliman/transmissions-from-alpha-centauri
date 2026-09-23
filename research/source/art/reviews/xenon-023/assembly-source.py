"""Install reviewed facade masters along the accepted alley; preserve rubble and vista."""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];V=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else '023';O=R/('art/reviews/xenon-'+V);O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-022/scene.blend'));s=bpy.context.scene
old_names=['02 Left facade - sloped shell, canopy and services','03 Right facade - interrupted horizontal floors','017 Alley construction and service detail','018 Torn cladding and buckled steel','021 Collapsed service doorway']
old_objects={o for n in old_names for o in bpy.data.collections[n].objects}
preserved=[o for o in s.objects if o not in old_objects]
def fingerprint(obs):
 return hashlib.sha256(json.dumps([(o.name,[list(r) for r in o.matrix_world],len(o.data.vertices) if o.type=='MESH' else 0) for o in obs],sort_keys=True).encode()).hexdigest()
fixed=fingerprint(preserved);camera=[list(r) for r in s.camera.matrix_world];lens=s.camera.data.lens
for name in old_names:
 c=bpy.data.collections[name];c.hide_render=True;c.hide_viewport=True
with bpy.data.libraries.load(str(R/'art/components/facades/v014/facade-kit.blend'),link=False) as (f,t):t.collections=f.collections
assets={c.get('part_id'):c for c in t.collections if c and c.get('part_id')}
with bpy.data.libraries.load(str(R/'art/components/services/v002/service-kit.blend'),link=False) as (f,t):t.collections=[n for n in f.collections if n in ['PIP_housing','PIP_blind','PIP_bend_90']]
for c in t.collections:
 if c:assets[c['part_id']]=c
C=bpy.data.collections.new('023 Reviewed architecture assembly');s.collection.children.link(C)
paint=bpy.data.materials['Cladding | slate enamel'];steel=bpy.data.materials['Structure | charcoal steel'];pale=bpy.data.materials['Cladding | pale mineral blue'];dark=bpy.data.materials['Recess | dark backing']
def box(n,p,d,m):
 x,y,z=p;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);C.objects.link(ob);be=ob.modifiers.new('Edge radius','BEVEL');be.width=.008;be.segments=2;return ob
placements=[]
def instance(key,M):
 ob=bpy.data.objects.new('Architecture | '+key,None);ob.instance_type='COLLECTION';ob.instance_collection=assets[key];ob.matrix_world=M;C.objects.link(ob);placements.append({'part':key,'position':list(M.translation)});return ob

def wallframe(side,y,z=0,x=None):
 # Local -Y outward becomes toward alley center. Local X follows the wall.
 X=(-8.15 if side<0 else 8.15) if x is None else x
 return Matrix.Translation((X,y,z))@Matrix.Rotation(math.pi/2 if side<0 else -math.pi/2,4,'Z')
def place(key,side,y,z=0,x=None):return instance(key,wallframe(side,y,z,x))

# Raise the canopy roof by extending only its vertical stems, preserving all profiles.
old=assets['canopy_y_support'];new=bpy.data.collections.new('FAC | canopy_tall');new.asset_mark();new['part_id']='canopy_tall'
for original in old.objects:
 ob=original.copy();ob.data=original.data.copy();new.objects.link(ob)
 if ob.type!='MESH':continue
 mw=ob.matrix_world.copy();inv=mw.inverted();ps=[mw@v.co for v in ob.data.vertices];lo=min(p.z for p in ps);hi=max(p.z for p in ps)
 if hi<.11:continue
 stem=lo<.01 and .85<hi<.95
 for v,p in zip(ob.data.vertices,ps):
  if not stem or p.z>.5:p.z+=1.30
  v.co=inv@p
assets['canopy_tall']=new
# New deep wall backing stays behind the aperture / service depth.
for side in [-1,1]:
 for i,(start,end,h) in enumerate([(-8,2,20),(2,12,23),(12,22,20),(22,32,16)]):
  box('New structural backing',(side*9.7,(start+end)/2,h/2),(1.0,end-start,h),dark)

ys=[-6.6+i*2.8 for i in range(14)]
for side in [-1,1]:
 for i,y in enumerate(ys):
  h=20 if y<2 else (23 if y<12 else (20 if y<22 else 16))
  # Recessed ground cladding; deliberate variations share matching datums.
  layout=['layout_broad','layout_access','layout_transition'][(i+(side>0))%3]
  place(layout,side,y,.05,x=side*8.50)
  box('Ground bay plinth',(side*8.50,y,.12),(.5,2.8,.24),pale)
  if side>0:
   for row in range(6):
    z=2.75+row*3.12
    if z+3.12>h:break
    state=['window_bay','window_open','window_bay','window_broken'][(i+row*3)%4]
    place(state,side,y,z)
   if i%2==0:place('buttress_30',side,y,0)
  else:
   # Inclined lower shell, then broad upper wall fields with sparse window bays.
   M=wallframe(side,y,2.75)@Matrix.Rotation(-math.radians(15),4,'X');instance('slot_wall',M)
   top=2.75+1.6*math.cos(math.radians(15));setback=1.6*math.sin(math.radians(15))
   for row in range(7):
    z=top+.024+row*2.184
    if z+2.16>h:break
    place(['layout_broad','layout_transition','layout_access'][(i//3+row)%3],side,y,z,x=-8.15-setback)
   place('floor_band',side,y,2.47)
  # Narrow full-height piers own the shared edges, rather than double side seams.
  if i%3==0:box('Long vertical structural pier',(side*8.08,y-1.4,h/2),(.17,.14,h),steel)
 # Rear closure covers the final .8 m remainder without changing the alley endpoint.
 box('Alley end return',(side*8.4,31.6,8),(.60,.80,16),paint)
# Canopies are spaced as groups; they do not repeat at every bay.
for side,locations in [(-1,[-3.1,6.0,18.1]),(1,[.4,12.5,24.5])]:
 for y in locations:place('canopy_tall',side,y,0)

# Continuous native service risers: connect the saved bore interfaces, never stretch parts.
def ports(key):return json.loads(assets[key]['ports_json'])
def frame(p):
 z=Vector(p['outward']);up=Vector(p.get('up',[0,1,0]));up=(up-z*up.dot(z)).normalized();x=up.cross(z)
 return Matrix.Translation(Vector(p['position']))@Matrix((x,up,z)).transposed().to_4x4()
joins=[]
def connect(parent,pk,key):
 a=ports(pk)[1];b=ports(key)[0];assert a['interface']==b['interface'] and abs(a['bore_diameter']-b['bore_diameter'])<1e-6
 M=parent.matrix_world@frame(a)@Matrix.Rotation(math.pi,4,'Y')@frame(b).inverted();ob=instance(key,M);bpy.context.view_layer.update()
 err=(parent.matrix_world@Vector(a['position'])-M@Vector(b['position'])).length;assert err<1e-5;joins.append(err);return ob
for side,y,height in [(-1,.2,18),(-1,1.15,17),(-1,9,20),(-1,9.8,18),(-1,22,13),(1,7,16),(1,20,14)]:
 root=instance('spool',Matrix.Translation((side*7.65,y,.10)));bpy.context.view_layer.update();pk='spool';q=root;length=1.0;n=0
 while length+1.5<height:
  key=['housing','spool','flange_joint','spool'][n%4];q=connect(q,pk,key);length+=ports(key)[1]['position'][2];pk=key;n+=1
 q=connect(q,pk,'blind')
 for z in [1.2+j*2.7 for j in range(int(height/2.7))]:
  box('Riser wall standoff',(side*8.02,y,z),(.35,.16,.12),steel)
  instance('detail_collar',Matrix.Translation((side*7.65,y,z-.12)))
# Explicit audit of the untouched composition and geometry-only rendering.
bpy.context.view_layer.update();assert fixed==fingerprint(preserved);assert camera==[list(r) for r in s.camera.matrix_world] and lens==s.camera.data.lens
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
s.compositing_node_group=None
(O/'audit.json').write_text(json.dumps({'preserved_camera_actor_rubble_vista':True,'preserved_object_count':len(preserved),'baseline_fingerprint':fixed,'alley_extent':[-8,32],'dome_nearest_edge':272,'gap_alley_ratio':6,'placements':len(placements),'service_joins':len(joins),'max_port_error':max(joins),'image_textures':0,'compositor':None},indent=2))
(O/'placements.json').write_text(json.dumps(placements,indent=2))
s.cycles.samples=32;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
print('ALLEY_ASSEMBLY_COMPLETE',V)
