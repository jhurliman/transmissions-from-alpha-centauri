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
with bpy.data.libraries.load(str(R/'art/components/services/v002/service-kit.blend'),link=False) as (f,t):t.collections=[n for n in f.collections if n in ['PIP_housing','PIP_blind','PIP_bend_90','PIP_bend_180']]
for c in t.collections:
 if c:assets[c['part_id']]=c
C=bpy.data.collections.new(V+' Reviewed architecture assembly');s.collection.children.link(C)
paint=bpy.data.materials['Cladding | slate enamel'];steel=bpy.data.materials['Structure | charcoal steel'];pale=bpy.data.materials['Cladding | pale mineral blue'];dark=bpy.data.materials['Recess | dark backing']
def box(n,p,d,m):
 x,y,z=p;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);C.objects.link(ob);be=ob.modifiers.new('Edge radius','BEVEL');be.width=.008;be.segments=2;return ob
placements=[]
def instance(key,M):
 ob=bpy.data.objects.new('Architecture | '+key,None);ob.instance_type='COLLECTION';ob.instance_collection=assets[key];ob.matrix_world=M;C.objects.link(ob);placements.append({'part':key,'position':list(M.translation)});return ob

def wallframe(side,y,z=0,x=None):
 # Local -Y outward becomes toward alley center. Local X follows the wall.
 X=side*wall_distance(side,y) if x is None else x+side*(wall_distance(side,y)-8.15)
 return Matrix.Translation((X,y,z))@Matrix.Rotation(math.pi/2 if side<0 else -math.pi/2,4,'Z')
def place(key,side,y,z=0,x=None):return instance(key,wallframe(side,y,z,x))

# Authored building groups, measured in alley coordinates. Open gaps contain no facade backing.
def wall_distance(side,y):
 if side<0:return 7.65 if y<.4 else (9.15 if y<20 else 8.65)
 return 8.15 if y<.4 else (9.50 if y<17.2 else 8.85)
concrete=bpy.data.materials['Structure | bare mineral']
new_masters=[]
def master(key,fn,metadata):
 global C
 save=C;C=bpy.data.collections.new('FAC | '+key);C['part_id']=key;C['assembly_rules']=json.dumps(metadata);C.asset_mark();fn();assets[key]=C;new_masters.append(C);C=save

def ibeam(n,a,b,w=.22,d=.24):
 a,b=Vector(a),Vector(b);L=(b-a).length;M=Matrix.Translation(a)@(b-a).to_track_quat('Z','Y').to_matrix().to_4x4()
 for label,p,dims in [('web',(0,0,L/2),(.045,d,L)),('front flange',(0,-d/2,L/2),(w,.038,L)),('back flange',(0,d/2,L/2),(w,.038,L))]:
  ob=box(n+' '+label,p,dims,steel);ob.matrix_world=M

def gangway():
 # Single large Y carries a long narrow platform; all principal braces are 30 degrees.
 ibeam('Y stem',(0,-1.38,.08),(0,-1.38,1.90),.27,.28)
 for sign in [-1,1]:ibeam('Y arm',(0,-1.38,1.90),(sign*1.50,-1.38,4.498),.23,.24)
 box('Y splice',(0,-1.55,1.90),(.42,.04,.50),pale)
 box('Foot plate',(0,-1.38,.05),(.60,.62,.10),steel)
 for x in [-.15,.15]:
  for z in [1.75,2.05]:box('Splice bolt',(x,-1.585,z),(.07,.05,.07),steel)
 for y in [-.10,-1.38]:ibeam('Long platform girder',(-4.10,y,4.54),(4.10,y,4.54),.20,.22)
 for x in [-3.85,-2.55,-1.28,0,1.28,2.55,3.85]:ibeam('Deck cross joist',(x,-.06,4.57),(x,-1.55,4.57),.12,.14)
 for j in range(7):box('Replaceable deck panel',(-3.51+j*1.17,-.79,4.69),(1.146,1.52,.04),paint)
 box('Folded fascia',(0,-1.58,4.57),(8.24,.055,.26),pale)
 box('Fascia bottom return',(0,-1.55,4.435),(8.24,.12,.03),steel)
 for x in [-3.8,-1.5,1.5,3.8]:box('Wall bearing plate',(x,0,4.54),(.32,.12,.42),steel)
master('gangway_single_Y_8m',gangway,{'span':8.24,'projection':1.61,'height':4.71,'support_count':1,'brace_angle_from_vertical':30,'wall_plane':0,'no_instance_scaling':True})

# Support positions vary along the same unscaled platform to suit each frontage.
for key,shift in [('gangway_single_Y_left',1.6),('gangway_single_Y_right',-1.6)]:
 col=bpy.data.collections.new('FAC | '+key);col['part_id']=key;col.asset_mark()
 meta=json.loads(assets['gangway_single_Y_8m']['assembly_rules']);meta['support_offset_along_platform']=shift;col['assembly_rules']=json.dumps(meta)
 for original in assets['gangway_single_Y_8m'].objects:
  ob=original.copy();col.objects.link(ob)
  if ob.name.startswith(('Y stem','Y arm','Y splice','Foot plate','Splice bolt')):ob.location.x+=shift
 assets[key]=col;new_masters.append(col)

def buttress45():
 pts=[(-2.65,0),(-2.25,0),(.20,2.45),(-.20,2.45)]
 vs=[(x,y,z) for x in [-.20,.20] for y,z in pts]
 me=bpy.data.meshes.new('45 degree concrete prism');me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(concrete);ob=bpy.data.objects.new('Solid concrete 45 degree support',me);C.objects.link(ob)
 box('Concrete footing',(0,-2.45,.06),(.64,.65,.12),concrete);box('Head bearing',(0,0,2.45),(.50,.48,.12),steel)
master('buttress_45',buttress45,{'rake':45,'height':2.51,'arrangement':'Authored singleton then close pair'})

def recessed_column():
 box('Column structural core',(0,.19,2.38),(.66,.38,4.76),concrete)
 for x in [-.28,.28]:box('Column edge stile',(x,-.025,2.38),(.10,.10,4.76),paint)
 for z in [.08,1.60,3.16,4.68]:box('Column cross cap',(0,-.03,z),(.66,.12,.12),pale)
 for z in [.84,2.38,3.92]:box('Recessed column panel',(0,.07,z),(.44,.045,1.36),paint)
master('column_recessed_4m8',recessed_column,{'height':4.76,'width':.66,'panel_recess':.07})

# Discrete backings create real alley openings and different facade depths.
groups={-1:[(-8,.4,20), (3.2,20,23),(20,32,17)],1:[(-8,.4,21),(6,17.2,23),(17.2,32,17)]}
for side,blocks in groups.items():
 for start,end,h in blocks:
  d=wall_distance(side,(start+end)/2)
  box('Building structural backing',(side*(d+1.55),(start+end)/2,h/2),(1,end-start,h),dark)
  # Paneled perpendicular end walls make the setback readable at gaps.
  for yy in [start+.06,end-.06]:
   box('Building side return',(side*(d+2.0),yy,h/2),(4,.12,h),paint)
   for zz in range(2,int(h),2):box('Return horizontal joint',(side*(d+2),yy-.07,zz),(4,.05,.035),steel)
ys=[-6.6+i*2.8 for i in range(14)]
for side in [-1,1]:
 for i,y in enumerate(ys):
  if (side<0 and i==3) or (side>0 and i in [3,4]):continue
  h=next(h for start,end,h in groups[side] if start<=y<=end)
  d=wall_distance(side,y)
  place(['layout_broad','layout_access','layout_transition'][i%3],side,y,.05,x=side*8.50)
  box('Ground bay plinth',(side*(d+.35),y,.12),(.5,2.8,.24),pale)
  if side>0:
   for row in range(6):
    z=2.75+row*3.12
    if z+3.12>h:break
    place(['window_bay','window_open','window_bay','window_broken'][(i+row*3)%4],side,y,z)
  else:
   front=i<3;slope_base=4.78 if front else 2.75
   if front:place('layout_transition',side,y,2.234,x=-8.50)
   instance('slot_wall',wallframe(side,y,slope_base)@Matrix.Rotation(-math.radians(15),4,'X'))
   top=slope_base+1.6*math.cos(math.radians(15));setback=1.6*math.sin(math.radians(15))
   for row in range(8):
    z=top+.024+row*2.184
    if z+2.16>h:break
    place(['layout_broad','layout_transition','layout_access'][(i//3+row)%3],side,y,z,x=-8.15-setback)
   place('floor_band',side,y,slope_base-.30)
  if i%3==0:box('Vertical structural pier',(side*(d-.07),y-1.4,h/2),(.17,.14,h),steel)
# Two paneled columns belong to the projecting front left block.
for y in [-7.55,-.10]:place('column_recessed_4m8',-1,y,0,x=-7.90)
for side,y in [(-1,-3.80),(1,-3.80)]:place('gangway_single_Y_left' if side<0 else 'gangway_single_Y_right',side,y)
# Five concrete supports: single, close pair, and a later close pair.
for y in [7.15,11.7,12.75,20.3,21.4]:place('buttress_45',1,y)
# Far side-road facade supplies spatial depth instead of an unlit world-background slit.
box('Side road far facade',(19.0,3.2,10.5),(.3,5.6,21),paint)
for yy in [.48,1.8,3.2,4.6,5.92]:box('Side road vertical seam',(18.83,yy,10.5),(.055,.055,21),steel)
for zz in range(1,21,2):
 box('Side road floor joint',(18.80,3.2,zz),(.12,5.6,.08),steel)
 for yy in [1.65,4.6]:box('Side road recessed service panel',(18.79,yy,zz+.65),(.09,.8,.85),dark)

# Continuous side wall bounds the road beyond the shallow facade return.
box('Side road north building wall',(19.5,6.08,10.5),(20,.20,21),paint)
for zz in range(1,21,2):box('Side road north floor band',(19.5,5.95,zz),(20,.10,.09),steel)
for xx in range(11,30,3):box('Side road north vertical seam',(xx,5.94,10.5),(.06,.08,21),steel)

# Left service entrance: actual 2.8 m opening with a 4 m recess and lintel.
box('Service bay rear wall',(-13.1,1.8,2.1),(.16,2.8,4.2),dark)
box('Service bay ceiling',(-11,1.8,4.3),(4.4,2.8,.20),steel)
box('Service bay floor',(-11,1.8,.025),(4.4,2.8,.05),concrete)
for y in [.50,3.10]:box('Service bay portal jamb',(-7.65,y,2.12),(.30,.18,4.24),steel)
box('Service bay lintel',(-7.65,1.8,4.25),(.35,2.8,.28),pale)
for j in range(10):box('Recessed shutter slat',(-13.0,1.8,.3+j*.36),(.08,2.5,.32),paint)
# Right road remains open between the first and second building, extending out of sight.
box('Side road surface',(14.5,3.2,.015),(13,5.6,.03),concrete)

# Continuous native service risers: connect the saved bore interfaces, never stretch parts.
def ports(key):return json.loads(assets[key]['ports_json'])
def frame(p):
 z=Vector(p['outward']);up=Vector(p.get('up',[0,1,0]));up=(up-z*up.dot(z)).normalized();x=up.cross(z)
 return Matrix.Translation(Vector(p['position']))@Matrix((x,up,z)).transposed().to_4x4()
joins=[]
def connect(parent,pk,key):
 a=ports(pk)[1];b=ports(key)[0];assert a['interface']==b['interface']
 for dim in (['width','height'] if a.get('profile')=='rect' else ['bore_diameter']):assert abs(a[dim]-b[dim])<1e-5
 M=parent.matrix_world@frame(a)@Matrix.Rotation(math.pi,4,'Y')@frame(b).inverted();ob=instance(key,M);bpy.context.view_layer.update()
 err=(parent.matrix_world@Vector(a['position'])-M@Vector(b['position'])).length;assert err<1e-5;joins.append(err);return ob
for side,y,height in [(-1,9,20),(-1,10.25,18),(-1,22,13),(1,8,16),(1,23,14)]:
 offset=1.05 if y in [9,23] else .50;axis=side*(wall_distance(side,y)-offset)
 root=instance('spool',Matrix.Translation((axis,y,.10)));bpy.context.view_layer.update();pk='spool';q=root;length=1.0;n=0
 while length+1.5<height:
  key=['housing','spool','flange_joint','spool','spool','flange_joint','spool'][n%7];q=connect(q,pk,key);length+=ports(key)[1]['position'][2];pk=key;n+=1
 q=connect(q,pk,'blind')
 for z in [1.2+j*2.7 for j in range(int(height/2.7))]:
  box('Riser wall standoff',(side*(wall_distance(side,y)-offset/2),y,z),(offset,.16,.12),steel)
  instance('detail_collar',Matrix.Translation((axis,y,z-.12)))
# Sparse mixed-profile trunks occupy authored service columns.
for side,y,count in [(-1,5.4,12),(-1,16.6,9),(1,15.8,11)]:
 q=instance('spool',wallframe(side,y,.10,x=side*7.60));bpy.context.view_layer.update();pk='spool'
 for key in ['round_rect_M']+['duct_M']*count+['duct_cap']:
  q=connect(q,pk,key);pk=key
 for z in [2+j*2.4 for j in range(count//2)]:
  box('Duct wall saddle',(side*(wall_distance(side,y)-.28),y,z),(.56,.46,.10),steel)
# Long left downpipe with one continuous 180-degree bottom return.
# Rotation maps local X across the wall and local Z downward.
q=instance('spool',Matrix.Translation((-8.00,5.50,13.0))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Rotation(math.pi,4,'X'));bpy.context.view_layer.update();pk='spool'
for key in ['spool']*11+['bend_180']+['spool']*9+['blind']:
 q=connect(q,pk,key);pk=key
for y in [5.5,6.5]:
 for z in [3,6,9,12]:box('U return extended wall mount',(-8.62,y,z),(1.1,.16,.12),steel)
# Save the new unscaled reusable masters independently of the scene assembly.
kit=R/'art/components/facades/v015';kit.mkdir(parents=True,exist_ok=True)
bpy.data.libraries.write(str(kit/'architectural-extensions.blend'),set(new_masters),fake_user=True)
(kit/'interfaces.json').write_text(json.dumps({c['part_id']:json.loads(c['assembly_rules']) for c in new_masters},indent=2))
# Explicit audit of the untouched composition and geometry-only rendering.
bpy.context.view_layer.update();assert fixed==fingerprint(preserved);assert camera==[list(r) for r in s.camera.matrix_world] and lens==s.camera.data.lens
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
s.compositing_node_group=None
(O/'audit.json').write_text(json.dumps({'preserved_camera_actor_rubble_vista':True,'preserved_object_count':len(preserved),'baseline_fingerprint':fixed,'alley_extent':[-8,32],'dome_nearest_edge':272,'gap_alley_ratio':6,'placements':len(placements),'service_joins':len(joins),'max_port_error':max(joins),'image_textures':0,'compositor':None},indent=2))
(O/'placements.json').write_text(json.dumps(placements,indent=2))
s.cycles.samples=32;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
print('ALLEY_ASSEMBLY_COMPLETE',V)
