import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-021';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-020/scene.blend'));s=bpy.context.scene;random.seed(2121)
# Suppress heavy outline strokes on tiny ground fragments only.
for vl in s.view_layers:
 for ls in vl.freestyle_settings.linesets:
  ls.select_by_collection=True;ls.collection=bpy.data.collections['020 Fine broken surface and weather seams'];ls.collection_negation='EXCLUSIVE'
C=bpy.data.collections.new('021 Collapsed service doorway');s.collection.children.link(C)
src=(R/'tools/rebuild_xenon_geometry.py').read_text();exec(src[src.index('def mesh('):src.index("coll('01 Street")])
wall=bpy.data.materials['Painted lavender steel'];metal=bpy.data.materials['Exposed weathered steel'];rust=bpy.data.materials['Oxidized edges'];shadow=bpy.data.materials['Recessed structural iron']
# One composed assembly replaces a full lower wall bay.
for o in list(s.objects):
 if not o.name.startswith(('Right facade plate','Torn cladding sheet')):continue
 ps=[o.matrix_world@Vector(v) for v in o.bound_box];x=sum(p.x for p in ps)/8;y=sum(p.y for p in ps)/8;z=sum(p.z for p in ps)/8
 if x>0 and -5.5<y<-.5 and z<4:bpy.data.objects.remove(o,do_unlink=True)
x=7.65;y=-3.0
# Distinct double-channel jambs, skewed lintel, folded shutter.
for yy in [y-1.55,y+1.55]:
 beam('Doorway upright channel web',(x,yy,.12),(x,yy,3.8),.12,.35,metal)
 for xx in [x-.18,x+.18]:beam('Doorway upright channel flange',(xx,yy,.12),(xx,yy,3.8),.07,.42,rust)
beam('Doorway displaced upper header',(x,y-1.65,3.9),(x-.32,y+1.6,3.65),.40,.26,metal)
for j in range(9):
 z=3.6-j*.13;yy=y+.28*j/9
 box('Remaining rolling shutter slat',(x+.14,yy,z),(.13,2.85,.105),wall)
# A partly unrolled steel shutter is one curved ribbed surface of real slats.
for j in range(10):
 z=2.45-j*.15;xx=x+.1-.045*j*j/10;yy=y+.48
 if j>6:yy+=.10*(j-6)
 box('Bent hanging shutter slat',(xx,yy,z),(.12,1.70-j*.055,.105),metal)
# Hardware connected to the surviving header.
pipe('Shutter roller axle',(x+.14,y-1.38,3.83),(x+.14,y+1.38,3.83),.16,.035,shadow)
for yy in [y-1.38,y+1.38]:box('Roller bearing block',(x,yy,3.83),(.38,.26,.42),rust)
wire('Doorway snapped lift cable',[(x-.2,y-1.42,3.8),(x-.43,y-1.5,2.5),(x-.66,y-1.32,1.7)],.025,shadow)
# Dropped folded access panel at doorway foot; angular sheet with internal rails.
vs=[(6.6,y-.6,.05),(7.7,y-.8,.08),(7.65,y+.7,1.0),(7.2,y+.85,.7),(6.65,y+.7,.15)]
o=mesh('Doorway dropped folded sheet',vs,[(0,1,2,3,4)],wall);o.modifiers.new('Folded sheet thickness','SOLIDIFY').thickness=.07
for yy in [y-.5,y+.4]:beam('Dropped panel stiffener',(6.7,yy,.12),(7.55,yy,.58),.05,.08,rust)
s.use_nodes=False;s.cycles.samples=48;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
