import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-017';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-016/scene.blend'));s=bpy.context.scene;random.seed(1717)
C=bpy.data.collections.new('017 Alley construction and service detail');s.collection.children.link(C)
# Reuse native mesh constructors, not previous scene setup.
src=(R/'tools/rebuild_xenon_geometry.py').read_text();exec(src[src.index('def mesh('):src.index("coll('01 Street")])
wall=bpy.data.materials['Painted lavender steel'];metal=bpy.data.materials['Exposed weathered steel'];shadow=bpy.data.materials['Recessed structural iron'];rust=bpy.data.materials['Oxidized edges'];light=bpy.data.materials['Sun-worn warm cladding'];warm=bpy.data.materials['Sun-worn warm cladding']
# Scale about the grounded nearest edge, preserving approved depth spacing.
pivot=Vector((0,272,0));xf=Matrix.Translation(pivot)@Matrix.Scale(1.5,4)@Matrix.Translation(-pivot)
for o in list(s.objects):
 if o.name.startswith(('Dome ','Fine secondary dome','Crown broken spar')):o.matrix_world=xf@o.matrix_world
# Replace selected whole cladding panels with openings; the deep wall core remains behind.
selected=[]
for o in list(s.objects):
 if not o.name.startswith(('Left broad battered cladding','Right facade plate')):continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=Vector([min(p[i] for p in ps) for i in range(3)]);hi=Vector([max(p[i] for p in ps) for i in range(3)]);mid=(lo+hi)/2
 if mid.y<23 and mid.z<13 and random.random()<.20:selected.append((o,lo,hi))
for n,(o,lo,hi) in enumerate(selected):
 x=(lo.x+hi.x)/2;side=1 if x<0 else -1;face=x+side*.16;y=(lo.y+hi.y)/2;z=(lo.z+hi.z)/2;w=hi.y-lo.y;h=hi.z-lo.z
 bpy.data.objects.remove(o,do_unlink=True)
 for yy in [lo.y+.09,hi.y-.09]:box('Recess vertical channel',(face,yy,z),(.25,.16,h),metal)
 for zz in [lo.z+.12,hi.z-.12]:box('Recess sill and lintel',(face,y,zz),(.42,w,.18),rust)
 if n%3==0:
  for j in range(9):
   zz=lo.z+.3+j*(h-.6)/9
   ob=box('Bent ventilation louver',(x-side*.2,y,zz),(.25,w-.3,.13),metal);ob.rotation_euler.y=.15
 else:
  # Exposed wall studs and partial backing strips within actual opening.
  for yy in [y-w*.25,y+w*.23]:beam('Exposed wall stud',(x-side*.23,yy,lo.z),(x-side*.23,yy,hi.z),.10,.12,rust)
  for j in range(3):
   zz=lo.z+.4+j*(h-.6)/3
   box('Broken inner wall course',(x-side*.36,y,zz),(.12,w*.75,.21),warm)
  wire('Loose hanging cavity cable',[(face,y-.4,hi.z),(face+side*.12,y-.3,z),(face+side*.18,y+.2,lo.z+.2)],.033,shadow)
# Thin fastener heads and seams attached to surviving wall skin.
for o in list(s.objects):
 if not o.name.startswith(('Left broad battered cladding','Right facade plate')):continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];lo=Vector([min(p[i] for p in ps) for i in range(3)]);hi=Vector([max(p[i] for p in ps) for i in range(3)])
 if lo.y>22 or lo.z>13:continue
 side=1 if hi.x<0 else -1;x=(hi.x if side==1 else lo.x)+side*.015
 for yy in [lo.y+.16,hi.y-.16]:
  for zz in [lo.z+.18,hi.z-.22]:pipe('Panel hex fastener',(x,yy,zz),(x+side*.035,yy,zz),.044,.01,rust,6)
# Build actual I profiles around surviving canopy members and lower floor edges.
for yy in [-3.5,1.7]:
 for z in [5.20,5.47]:beam('Canopy I beam flange',(-8.1,yy,z+.2),(-5.86,yy,z),.34,.055,metal)
 for x in [-7.9,-6.15]:
  box('Canopy bolted gusset',(x,yy,5.35),(.32,.10,.55),rust)
  for dz in [-.16,.16]:pipe('Gusset bolt',(x,yy-.07,5.35+dz),(x,yy-.13,5.35+dz),.06,.015,light,6)
# Steel angle supports and beam-end plates along right floor ledges.
for y in [-5,0,5,10,16]:
 for z in [4.2,8.5]:
  beam('Floor triangulated bracket',(8.05,y,z-.85),(7.45,y,z-.1),.12,.14,rust)
  box('Ledger attachment plate',(7.98,y,z-.5),(.08,.4,1.0),metal)
  for zz in [z-.85,z-.2]:pipe('Ledger bolt',(7.92,y,zz),(7.84,y,zz),.055,.01,light,6)
# Routed service pipes with elbows, unions and valves, organized into two banks.
for j in range(4):
 y=1.0+j*.48;x=-7.45+j*.08
 pts=[(x,y,.3),(x,y,6.1+j*.35),(x+.18,y+.18,6.45+j*.35),(x+.18,y+2.1,6.45+j*.35),(x,y+2.4,6.8+j*.35),(x,y+2.4,17)]
 wire('Bent service riser',pts,.065+j*.018,metal)
 for z in [1.2,3.3,5.2]:
  pipe('Riser coupling',(x,y,z),(x,y,z+.15),.11+j*.018,.02,rust)
  box('Riser retaining clip',(x-.08,y,z+.06),(.22,.31,.08),metal)
 pipe('Service valve stem',(x,y,2.1),(x+.28,y,2.1),.05,.015,metal)
 pipe('Service valve wheel',(x+.26,y,2.1),(x+.31,y,2.1),.20,.038,rust,16)
 for a in [0,math.pi/2]:beam('Valve spoke',(x+.29,y-math.cos(a)*.18,2.1-math.sin(a)*.18),(x+.29,y+math.cos(a)*.18,2.1+math.sin(a)*.18),.025,.025,metal)
# Weather shields and junction cabinets as recognizable service assemblies.
for x,y,z in [(-7.65,7.5,2.0),(-7.65,16,3.4),(7.75,3.5,2.0)]:
 side=1 if x<0 else -1
 box('Electrical cabinet body',(x,y,z),(.55,1.15,1.5),shadow)
 box('Electrical cabinet inset door',(x+side*.30,y,z),(.08,1.01,1.34),wall)
 box('Cabinet drip hood',(x+side*.06,y,z+.83),(.8,1.34,.085),rust)
 for zz in [z-.35,z+.35]:box('Cabinet hinge',(x+side*.37,y-.4,zz),(.08,.09,.22),metal)
 box('Cabinet latch',(x+side*.37,y+.32,z),(.1,.08,.27),light)
 wire('Cabinet conduit',[(x,y,z-.75),(x,y,.3),(x,y+1,.2)],.045,shadow)
assert not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
s.use_nodes=False;s.cycles.samples=48;s.render.filepath=str(O/'render.png')
(O/'detail-audit.json').write_text(json.dumps({'new_detail_objects':len(C.objects),'opened_panels':len(selected),'dome_scale':1.5,'dome_nearest_edge':272,'alley_gap':240,'image_textures':0},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
