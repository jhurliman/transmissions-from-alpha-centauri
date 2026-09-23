"""Controlled panel layouts, canopy connections and an attached service chase."""
from pathlib import Path
base=(Path(__file__).parent/'build_facade_assemblies.py').read_text()
exec(base[:base.index("proof('left_inclined_bay'")])
# Fix inherited metadata for equally sized window-state assemblies.
for k in ['window_bay','window_open','window_broken']:
 c=json.loads(assets[k]['interface_json']);c['width']=2.8;assets[k]['interface_json']=json.dumps(c)
layouts={
 'broad':[(0,0,1.82,1.39),(1.844,0,.956,1.39),(0,1.414,1.10,.746),(1.124,1.414,1.676,.746)],
 'access':[(0,0,.42,2.16),(.444,0,1.46,.72),(.444,.744,1.46,1.416),(1.928,0,.872,1.068),(1.928,1.092,.872,1.068)],
 'transition':[(0,0,.42,2.16),(.444,0,.52,2.16),(.988,0,1.812,.52),(.988,.544,1.812,1.616)]}
layout_checks=[]
for name,rects in layouts.items():
 def layout(rects=rects,name=name):
  box('Panel field backing',(0,.10,1.08),(2.8,.04,2.16),dark)
  for i,(x,z,w,h) in enumerate(rects):
   before=set(C.objects);panel(w,h,[paint,pale,paint,warm,paint][i%5])
   for ob in set(C.objects)-before:ob.location=(x+w/2-1.4,0,z)
  if name=='access':inst('access_insert',(-.36,-.014,.88))
 register('layout_'+name,layout,{'kind':'panel_layout','width':2.8,'height':2.16,'gap':.024,'rectangles':rects,'outward':[0,-1,0]})
 for i,(x,z,w,h) in enumerate(rects):
  assert x>=0 and z>=0 and x+w<=2.80001 and z+h<=2.16001
  for X,Z,W,H in rects[i+1:]:assert min(x+w,X+W)-max(x,X)<1e-5 or min(z+h,Z+H)-max(z,Z)<1e-5
 layout_checks.append({'layout':name,'bounded_nonoverlapping_panels':len(rects)})

# Add connection parts to the same native canopy master, preserving its profile.
C=assets['canopy_y_support']
for x in [-1.20,1.20]:
 for dx in [-.52,.52]:
  box('Brace head splice',(x+dx,-1.04,1.78),(.20,.035,.22),edge)
  for sx in [-.06,.06]:
   for z in [1.72,1.84]:screw(x+dx+sx,-1.067,z)
 for dx in [-.095,.095]:
  for dy in [-.095,.095]:
   before=set(C.objects);screw(0,0,0)
   M=Matrix.Translation((x+dx,-.90+dy,.072))@Matrix.Rotation(-math.pi/2,4,'X')
   for ob in set(C.objects)-before:ob.matrix_world=M
for x in [-1.65,-.55,.55,1.65]:
 for y in [-.15,-.90]:
  box('Crossmember seat',(x,y,1.77),(.19,.22,.035),edge)
  box('Seat downstand',(x,y-.1,1.72),(.19,.026,.11),steel)
  for dx in [-.055,.055]:screw(x+dx,y-.117,1.72)
# Folded underside inspection cassette with actual perforations between slats.
box('Underside access frame',(0,-.58,1.77),(.86,.55,.055),steel)
for x in [-.30,-.15,0,.15,.30]:box('Inspection cassette slat',(x,-.58,1.733),(.10,.43,.02),paint)

# Append saved service component masters. Never rebuild their mesh from approximations.
with bpy.data.libraries.load(str(R/'art/components/services/v002/service-kit.blend'),link=False) as (f,t):
 t.collections=[n for n in f.collections if n.startswith('PIP_')]
needed=['spool','round_rect_M','duct_M','duct_cap','flange_joint','sleeve','detail_collar']
service={}
for col in t.collections:
 if col and col.get('part_id') in needed:
  key=col['part_id'];ports=json.loads(col.get('ports_json','[]'));col['interface_json']=json.dumps({'kind':'imported_service','source':'services/v002','ports':ports});assets['service_'+key]=col;service[key]={'collection':col,'ports':ports}
assert len(service)==len(needed)
joins=[]
def portframe(p):
 z=Vector(p['outward']).normalized();y=Vector(p.get('up',[0,1,0]));y-=z*y.dot(z)
 if y.length<1e-6:y=Vector((1,0,0))-z*z.x
 y.normalize();x=y.cross(z);return Matrix.Translation(Vector(p['position']))@Matrix((x,y,z)).transposed().to_4x4()
def connect(parent,parentkey,out,key,inp=0):
 a=service[parentkey]['ports'][out];b=service[key]['ports'][inp]
 assert a['interface']==b['interface']
 if a.get('profile')=='rect':assert abs(a['width']-b['width'])<1e-6 and abs(a['height']-b['height'])<1e-6
 else:assert abs(a['bore_diameter']-b['bore_diameter'])<1e-6
 ob=inst('service_'+key);ob.matrix_world=parent.matrix_world@portframe(a)@Matrix.Rotation(math.pi,4,'Y')@portframe(b).inverted()
 bpy.context.view_layer.update();err=(parent.matrix_world@Vector(a['position'])-ob.matrix_world@Vector(b['position'])).length
 dot=(parent.matrix_world.to_3x3()@Vector(a['outward'])).dot(ob.matrix_world.to_3x3()@Vector(b['outward']))
 assert err<1e-5 and dot<-.9999
 joins.append({'from':parentkey,'to':key,'error':err,'normal_dot':dot});return ob

def service_bay():
 # Clear width 1.60m beside the unchanged 2.80m window bay.
 inst('window_bay',(.65,0,0))
 box('Chase recessed back',(-1.57,.76,1.56),(1.60,.05,3.12),dark)
 for x in [-2.37,-.77]:
  box('Chase side return',(x,.36,1.56),(.035,.80,3.12),paint)
  box('Chase edge strip',(x,0,1.56),(.065,.04,3.12),pale)
 for z in [.03,3.09]:box('Chase end closure',(-1.57,.36,z),(1.6,.80,.055),steel)
 root=inst('service_spool',(-1.86,.22,.10));bpy.context.view_layer.update()
 q=connect(root,'spool',1,'round_rect_M');q=connect(q,'round_rect_M',1,'duct_M');q=connect(q,'duct_M',1,'duct_cap')
 q=inst('service_spool',(-1.14,.22,.10));bpy.context.view_layer.update()
 q=connect(q,'spool',1,'flange_joint');q=connect(q,'flange_joint',1,'spool');q=connect(q,'spool',1,'sleeve')
 for x in [-1.86,-1.14]:
  for z in [.32,.80]:
   inst('service_detail_collar',(x,.22,z))
   box('Wall bracket foot',(x,.71,z+.12),(.22,.06,.24),edge)
   box('Bracket stand-off',(x,.60,z+.12),(.10,.26,.08),steel)
 for z in [2.13,2.63]:
  # Rectangular retaining strap around the duct, attached to wall stand-offs.
  x=-1.86
  for X in [x-.305,x+.305]:box('Duct strap side',(X,.22,z),(.025,.44,.045),edge)
  for y in [0,.44]:box('Duct strap front/back',(x,y,z),(.635,.025,.045),edge)
  for X in [x-.23,x+.23]:box('Duct bracket stand-off',(X,.60,z),(.045,.31,.045),steel)
 box('Service chase plinth',(-1.57,.40,-.15),(1.68,.85,.30),concrete)

proof('panel_layouts',lambda:[inst('layout_'+name,((i-1)*3.05,0,0)) for i,name in enumerate(layouts)])
proof('canopy_underside',lambda:inst('canopy_y_support',(0,0,-.30)))
proof('service_window_bay',service_bay)
(O/'assembly-audit.json').write_text(json.dumps({'layout_checks':layout_checks,'service_joins':joins,'scope':'Port alignment and panel bounds verified. Mounts visually reviewed; not a general collision solver.'},indent=2))
tail=src[src.index('# Neutral studio'):]
tail=tail.replace("for key,col in proofs.items():\n",'''for key,col in proofs.items():
 if key=='panel_layouts':
  target=Vector((0,0,1.05));delta=Vector((2,-15,3));d.ortho_scale=10.2
 elif key=='canopy_underside':
  target=Vector((0,-.6,1.0));delta=Vector((4,-7,-.35));d.ortho_scale=5.4
 else:
  target=Vector((-.12,.1,1.40));delta=Vector((4,-9,3.1));d.ortho_scale=7.1
 cam.location=target+delta;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
''')
exec(tail)
