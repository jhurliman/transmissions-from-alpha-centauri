"""Facade proofs: native editable components, local X horizontal / -Y outward / Z up."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
VERSION=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
O=R/'art/components/facades'/VERSION;O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1800;s.render.resolution_y=1200;s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
def mat(n,c,metal=0,rough=.55):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
paint=mat('Cladding | slate enamel',(.23,.29,.37),.25)
pale=mat('Cladding | pale mineral blue',(.32,.38,.45),.18)
warm=mat('Cladding | warm neutral insert',(.33,.29,.25),.12)
steel=mat('Structure | charcoal steel',(.085,.105,.125),.6)
edge=mat('Connections | zinc steel',(.28,.32,.35),.65)
dark=mat('Recess | dark backing',(.023,.032,.044))
glass=mat('Infill | smoked blue opaque study',(.07,.13,.20),.35,.27)
concrete=mat('Structure | bare mineral',(.28,.27,.25))
clay=mat('Review | neutral clay',(.38,.38,.38))
assets={};C=None

def mesh(n,vs,fs,m,bevel=.003):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);C.objects.link(o);me.materials.append(m)
 if bevel:
  b=o.modifiers.new('Manufactured edge', 'BEVEL');b.width=bevel;b.segments=2
 return o

def box(n,p,d,m,bev=.003):
 x,y,z=p;a,b,c=[v/2 for v in d]
 return mesh(n,[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m,bev)

def screw(x,y,z):
 N=12;r=.013;vs=[(x+r*math.cos(i*math.tau/N),y+j*.011,z+r*math.sin(i*math.tau/N)) for j in [0,1] for i in range(N)]
 mesh('Captive panel screw',vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],edge,.001)
 box('Screw slot',(x,y-.001,z),(.014,.002,.003),dark,0)

def panel(w,h,m=paint):
 box('Folded sheet face',(0,0,h/2),(w,.024,h),m)
 # Thin returns at all four edges; face rear at +.012.
 for x in [-w/2+.009,w/2-.009]:box('Side folded return',(x,.035,h/2),(.018,.07,h-.025),m)
 for z in [.009,h-.009]:box('Top / bottom return',(0,.035,z),(w-.036,.07,.018),m)
 for x in [-w/2+.045,w/2-.045]:
  for z in [.05,h-.05]:screw(x,-.025,z)

def register(key,fn,contract):
 global C
 C=bpy.data.collections.new('FAC | '+key);fn();C.asset_mark();C.asset_data.description='Editable clean facade component. Local -Y faces outward; Z up.';C['interface_json']=json.dumps(contract);C['part_id']=key;assets[key]=C;return C

def inst(key,p=(0,0,0),rot=0):
 o=bpy.data.objects.new(key,None);o.instance_type='COLLECTION';o.instance_collection=assets[key];o.location=p;o.rotation_euler.z=rot;C.objects.link(o);return o

def frame_ring(n,sections,m):
 # A continuous closed annulus; sections = (depth, outerW, outerH, innerW, innerH, centerZ).
 vs=[]
 for y,w,h,iw,ih,z in sections:
  for W,H in [(w,h),(iw,ih)]:vs += [(-W/2,y,z-H/2),(W/2,y,z-H/2),(W/2,y,z+H/2),(-W/2,y,z+H/2)]
 fs=[]
 for j in range(len(sections)-1):
  for offset in [0,4]:
   for i in range(4):fs.append((j*8+offset+i,j*8+offset+(i+1)%4,(j+1)*8+offset+(i+1)%4,(j+1)*8+offset+i))
 for j in [0,len(sections)-1]:
  for i in range(4):fs.append((j*8+i,j*8+(i+1)%4,j*8+4+(i+1)%4,j*8+4+i))
 o=mesh(n,vs,fs,m)
 # Recalculate normals for the closed annulus.
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
 return o

for key,w,h,m in [('plate_broad',1.12,1.42,paint),('plate_narrow',.40,1.42,pale),('plate_square',1.12,.68,warm),('plate_sill',1.86,.48,paint),('plate_header',1.86,.52,pale)]:
 register(key,lambda w=w,h=h,m=m:panel(w,h,m),{'kind':'panel','width':w,'height':h,'gap':.024,'outward':[0,-1,0],'up':[0,0,1],'face_depth':0,'rear_depth':.07})

def sloped_kick():
 # 15 degrees from vertical; top at Y=0, bottom projects toward the alley.
 rise=.52;angle=math.radians(15);run=rise*math.tan(angle)
 before=set(C.objects);panel(1.86,rise/math.cos(angle),paint)
 M=Matrix.Translation((0,-run,0))@Matrix.Rotation(-angle,4,'X')
 for ob in set(C.objects)-before:ob.matrix_world=M
 # Wedge-shaped end closures terminate at the facade backing plane.
 for x in [-.93,.914]:
  pts=[(-run,0),(.07,0),(.07,rise),(0,rise)]
  vs=[(X,y,z) for X in [x,x+.016] for y,z in pts]
  mesh('Kick panel side closure',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],paint)
 box('Kick panel folded drip edge',(0,-run-.008,-.014),(1.86,.024,.038),steel)
register('kick_sloped_15',sloped_kick,{'kind':'kick_panel','width':1.86,'vertical_rise':.52,'rake_from_vertical':15,'top_y':0,'bottom_y':-.52*math.tan(math.radians(15)),'outward':[0,-1,0],'top_z':.52,'bottom_z':0})

def corner():
 # L section with small diagonal nose: fixed 45-degree folded edge, not a giant bevel.
 pts=[(-.055,.01),(-.055,-.025),(.018,-.025),(.055,.012),(.055,.18),(.025,.18),(.025,.025),(0,.01)]
 vs=[(x,y,z) for z in [0,1.42] for x,y in pts];N=len(pts)
 mesh('Folded corner cap',vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],pale)
register('corner_cap',corner,{'kind':'corner','angle':90,'height':1.42,'edge_chamfer':45})

def access():
 frame_ring('Access surround',[(0,.46,.39,.39,.32,.195),(-.022,.46,.39,.39,.32,.195)],steel)
 box('Removable access insert',(0,-.018,.195),(.38,.023,.31),pale)
 for x in [-.155,.155]:
  for z in [.075,.315]:screw(x,-.043,z)
 box('Recessed latch',(0,-.031,.195),(.10,.012,.034),dark)
 box('Latch pull',(0,-.044,.195),(.067,.019,.015),edge)
register('access_insert',access,{'kind':'surface_access','width':.46,'height':.39,'mount_depth':0})

def glass_fragment(n,coords,y):
 vs=[(x,Y,z) for Y in [y,y+.006] for x,z in coords];N=len(coords)
 return mesh(n,vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],glass,0)

def window(state='closed'):
 # Thin flush industrial frame: two full-height sliders on parallel tracks.
 frame_ring('Flush perimeter frame',[(0,1.94,2.04,1.82,1.92,1.02),(.065,1.94,2.04,1.82,1.92,1.02)],steel)
 frame_ring('Straight aperture liner',[(.06,1.94,2.04,1.82,1.92,1.02),(.30,1.94,2.04,1.82,1.92,1.02)],paint)
 box('Interior shadow backing',(0,.84,1.02),(1.94,.035,2.04),dark)
 for y in [.115,.19]:
  for z in [.062,1.978]:
   box('Continuous sliding track',(0,y,z),(1.82,.065,.027),edge)
   box('Track groove',(0,y-.017,z+.014),(1.80,.018,.009),dark,0)
 for i in [0,1]:
  cx=-.443 if i==0 else .443
  if state=='open' and i==1:cx-=.82
  y=.115 if i==0 else .19
  w=.934;h=1.886;z=1.02
  # Thin rectangular metal sash with no horizontal divider.
  before=set(C.objects)
  frame_ring('Sliding leaf frame',[(y,w,h,w-.052,h-.052,z),(y+.037,w,h,w-.052,h-.052,z)],edge)
  for ob in set(C.objects)-before:ob.location.x=cx
  xmin=cx-w/2+.027;xmax=cx+w/2-.027;zmin=z-h/2+.027;zmax=z+h/2-.027
  if state=='broken' and i==0:
   # Glass remains in its own replaceable variant; intact master stays clean.
   glass_fragment('Broken pane lower remnant',[(xmin,zmin),(xmax,zmin),(xmax,zmin+.30),(cx+.19,zmin+.19),(cx+.07,zmin+.46),(cx-.15,zmin+.12),(xmin,zmin+.37)],y+.039)
   glass_fragment('Broken pane upper corner',[(xmin,zmax),(xmin+.20,zmax),(xmin+.055,zmax-.35),(xmin,zmax-.44)],y+.039)
   glass_fragment('Broken pane side shard',[(xmax,zmax-.20),(xmax,zmax-.78),(xmax-.13,zmax-.52)],y+.039)
  else:box('Full-height blue glass',(cx,y+.042,z),(xmax-xmin,.006,zmax-zmin),glass,.001)
  # Small stamped pull at the meeting edge, subordinate to the frame.
  hx=cx+(.934/2-.045 if i==0 else -.934/2+.045)
  box('Sliding leaf pull',(hx,y-.019,.96),(.020,.045,.15),steel)
 for x in [-.94,.94]:
  for z in [.12,1.92]:screw(x,-.014,z)
for state in ['closed','open','broken']:
 register('window_slider_'+state,lambda state=state:window(state),{'kind':'opening','rough_width':1.94,'rough_height':2.04,'depth':.88,'outward':[0,-1,0],'up':[0,0,1],'sash_count':2,'track_depths':[.115,.19],'sash_travel':.82,'state':state,'no_transom':True,'broken_glass_is_variant':state=='broken'})

def channel(L=2.6):
 box('Channel web',(0,0,L/2),(.12,.016,L),steel)
 for x in [-.052,.052]:box('Channel flange',(x,-.055,L/2),(.016,.11,L),steel)
register('channel',channel,{'kind':'steel_section','length':2.6,'width':.12,'depth':.118})

def band():
 box('Floor band core',(0,.07,.12),(2.8,.35,.24),steel)
 for x in [-.705,.705]:
  box('Floor fascia panel',(x,-.13,.12),(1.386,.027,.23),paint)
 box('Soffit underside',(0,.02,-.015),(2.8,.50,.025),pale)
 box('Band lower edge',(0,-.229,-.02),(2.8,.026,.075),steel)
 box('Band top cap',(0,.02,.26),(2.8,.5,.025),pale)
register('floor_band',band,{'kind':'floor_band','width':2.8,'height':.30,'projection':.24})

# First proofs are deliberately isolated, kept out of the accepted alley scene.
proofs={}
def proof(key,fn):
 global C
 C=bpy.data.collections.new('PROOF | '+key);s.collection.children.link(C);fn();proofs[key]=C

def panel_corner():
 # Visible black support joints under a regular thin folded skin.
 box('Backplane',(0,.115,1.48),(1.58,.08,2.96),dark)
 for z in [.74,2.184]:
  inst('plate_broad',(-.212,0,z-.71));inst('plate_narrow',(.572,0,z-.71))
 # Side wall is perpendicular with panel fronts outward +X.
 for z in [.03,1.474]:
  ob=inst('plate_broad',(.802,.59,z),math.pi/2)
  inst('corner_cap',(.777,0,z))
 inst('access_insert',(-.24,-.018,.97))
 for z in [.03,2.93]:box('Edge termination',(0,-.025,z),(1.58,.09,.035),steel)
 box('Exposed base',(0,.18,-.145),(1.67,.55,.33),concrete)

def window_bay(state='closed'):
 # Physical wall surround leaves the full rough aperture clear.
 for x in [-1.19,1.19]:box('Pier backing',(x,.24,1.55),(.43,.48,3.1),dark)
 for z,h in [(.25,.5),(2.855,.49)]:box('Header / sill backing',(0,.24,z),(1.94,.48,h),dark)
 for x in [-1.19,1.19]:
  for z in [.02,1.464]:inst('plate_narrow',(x,0,z))
 inst('kick_sloped_15',(0,0,.02));inst('plate_header',(0,0,2.60));inst('window_slider_'+state,(0,0,.54))
 for x in [-1.19,1.19]:
  box('Top pier closure',(x,0,3.007),(.40,.024,.204),pale)
 # Return cladding, generated at correct depth rather than stretched from a front panel.
 for x,rot in [(1.415,math.pi/2),(-1.415,-math.pi/2)]:
  for z in [.02,1.464]:
   before=set(C.objects);panel(.45,1.42,paint)
   for ob in set(C.objects)-before:ob.matrix_world=Matrix.Translation((x,.24,z))@Matrix.Rotation(rot,4,'Z')
 inst('floor_band',(0,0,-.23))
proof('panel_corner',panel_corner);proof('window_bay',window_bay)
proof('window_open',lambda:window_bay('open'));proof('window_broken',lambda:window_bay('broken'))
# Neutral studio does not contain painted image textures or compositing nodes.
C=bpy.data.collections.new('Studio');s.collection.children.link(C)
box('Studio floor',(0,0,-.36),(200,200,.1),mat('Studio floor',(.075,.082,.095)))
s.world=bpy.data.worlds.new('Facade studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,pos,power,size in [('Key',(-4,-6,8),1100,5),('Fill',(5,-3,4),500,4),('Rim',(1,4,6),800,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Proof camera');cam=bpy.data.objects.new('Proof camera',d);C.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=6.0
cam.location=(4,-9,4.5);cam.rotation_euler=(Vector((0,.12,1.40))-cam.location).to_track_quat('-Z','Y').to_euler()
# Persist assembly and module contracts alongside editable asset collections.
manifest={k:json.loads(v['interface_json']) for k,v in assets.items()}
(O/'interfaces.json').write_text(json.dumps({'coordinates':'X horizontal, -Y outward, Z up; meters','assets':manifest,'rules':['Generate dimensions before instancing; never stretch instances','Panel face gaps are 0.024 meters','Window aperture must remain free through 0.88 meters','Shared corners and seams have one owner','Services require explicit mounting stand-off; no automatic collision solver']},indent=2))
checks={'all_instances_unit_scale':all(tuple(o.scale)==(1,1,1) for o in bpy.data.objects if o.instance_type=='COLLECTION'),'no_image_textures':not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes),'asset_count':len(assets),'geometry_objects':sum(o.type=='MESH' for o in bpy.data.objects),'compositing_node_group':str(s.compositing_node_group)}
assert checks['all_instances_unit_scale'] and checks['no_image_textures']
(O/'audit.json').write_text(json.dumps(checks,indent=2))
for key,col in proofs.items():
 for k,v in proofs.items():v.hide_render=k!=key;v.hide_viewport=k!=key
 s.render.filepath=str(O/(key+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(key+'.blend')));bpy.ops.render.render(write_still=True)
 if key in ['window_open','window_broken']:continue
 s.view_layers[0].material_override=clay;s.render.filepath=str(O/(key+'-clay.png'));bpy.ops.render.render(write_still=True);s.view_layers[0].material_override=None
print('FACADE_PROOFS_COMPLETE',VERSION)
