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

def window():
 # Rough aperture 1.90 x 2.00. Broad 45-degree reveal leads to slimmer interior frame.
 frame_ring('Folded outer reveal',[(-.065,1.94,2.04,1.76,1.86,1.02),(.015,1.94,2.04,1.60,1.70,1.02),(.24,1.94,2.04,1.60,1.70,1.02)],pale)
 frame_ring('Inner frame',[(.235,1.61,1.71,1.48,1.58,1.02),(.31,1.61,1.71,1.48,1.58,1.02)],steel)
 # Back cavity behind the infill; no full wall crosses the aperture.
 box('Interior shadow backing',(0,.61,1.02),(1.60,.035,1.70),dark)
 for x in [-.40,.40]:
  for z,h in [(.67,.80),(1.48,.72)]:box('Recessed infill pane',(x,.335,z),(.75,.022,h),glass,.002)
 box('Central mullion',(0,.28,1.02),(.048,.065,1.58),edge)
 box('Transom',(0,.28,1.10),(1.48,.065,.041),edge)
 box('Projecting sill',(0,-.105,.015),(2.02,.39,.07),pale)
 box('Sill downturned lip',(0,-.286,-.015),(2.02,.026,.06),steel)
 box('Hood top',(0,-.115,2.075),(2.04,.36,.04),pale)
 box('Hood downturned lip',(0,-.288,2.04),(2.04,.02,.08),paint)
 for x in [-.905,.905]:
  for z in [.18,1.86]:screw(x,-.082,z)
register('window_divided',window,{'kind':'opening','rough_width':1.94,'rough_height':2.04,'depth':.65,'outward':[0,-1,0],'up':[0,0,1],'sill_projection':.30})

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
 box('Exposed base',(0,.18,-.07),(1.67,.55,.18),concrete)

def window_bay():
 # Physical wall surround leaves the full rough aperture clear.
 for x in [-1.19,1.19]:box('Pier backing',(x,.24,1.55),(.43,.48,3.1),dark)
 for z,h in [(.25,.5),(2.855,.49)]:box('Header / sill backing',(0,.24,z),(1.94,.48,h),dark)
 for x in [-1.19,1.19]:
  for z in [.02,1.464]:inst('plate_narrow',(x,0,z))
 inst('plate_sill',(0,0,.02));inst('plate_header',(0,0,2.60));inst('window_divided',(0,0,.54))
 inst('floor_band',(0,0,-.23))
proof('panel_corner',panel_corner);proof('window_bay',window_bay)
# Neutral studio does not contain painted image textures or compositing nodes.
C=bpy.data.collections.new('Studio');s.collection.children.link(C)
box('Studio floor',(0,0,-.36),(200,200,.1),mat('Studio floor',(.075,.082,.095)))
s.world=bpy.data.worlds.new('Facade studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.30,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,pos,power,size in [('Key',(-4,-6,8),1100,5),('Fill',(5,-3,4),500,4),('Rim',(1,4,6),800,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Proof camera');cam=bpy.data.objects.new('Proof camera',d);C.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=4.65
cam.location=(4,-9,4.5);cam.rotation_euler=(Vector((0,.12,1.40))-cam.location).to_track_quat('-Z','Y').to_euler()
# Persist assembly and module contracts alongside editable asset collections.
manifest={k:json.loads(v['interface_json']) for k,v in assets.items()}
(O/'interfaces.json').write_text(json.dumps({'coordinates':'X horizontal, -Y outward, Z up; meters','assets':manifest,'rules':['Generate dimensions before instancing; never stretch instances','Panel face gaps are 0.024 meters','Window aperture must remain free through 0.65 meters','Shared corners and seams have one owner','Services require explicit mounting stand-off; no automatic collision solver']},indent=2))
checks={'all_instances_unit_scale':all(tuple(o.scale)==(1,1,1) for o in bpy.data.objects if o.instance_type=='COLLECTION'),'no_image_textures':not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes),'asset_count':len(assets),'geometry_objects':sum(o.type=='MESH' for o in bpy.data.objects),'compositing_node_group':str(s.compositing_node_group)}
assert checks['all_instances_unit_scale'] and checks['no_image_textures']
(O/'audit.json').write_text(json.dumps(checks,indent=2))
for key,col in proofs.items():
 for k,v in proofs.items():v.hide_render=k!=key;v.hide_viewport=k!=key
 s.render.filepath=str(O/(key+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(key+'.blend')));bpy.ops.render.render(write_still=True)
 s.view_layers[0].material_override=clay;s.render.filepath=str(O/(key+'-clay.png'));bpy.ops.render.render(write_still=True);s.view_layers[0].material_override=None
print('FACADE_PROOFS_COMPLETE',VERSION)
