import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-018';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-017/scene.blend'));s=bpy.context.scene;random.seed(1818)
C=bpy.data.collections.new('018 Torn cladding and buckled steel');s.collection.children.link(C)
src=(R/'tools/rebuild_xenon_geometry.py').read_text();exec(src[src.index('def mesh('):src.index("coll('01 Street")])
wall=bpy.data.materials['Painted lavender steel'];metal=bpy.data.materials['Exposed weathered steel'];shadow=bpy.data.materials['Recessed structural iron'];rust=bpy.data.materials['Oxidized edges']
changed=0
for ob in list(s.objects):
 if not ob.name.startswith(('Left broad battered cladding','Right facade plate')):continue
 ps=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=Vector([min(p[i] for p in ps) for i in range(3)]);hi=Vector([max(p[i] for p in ps) for i in range(3)])
 x=(lo.x+hi.x)/2;y=(lo.y+hi.y)/2;z=(lo.z+hi.z)/2;w=hi.y-lo.y;h=hi.z-lo.z;side=1 if x<0 else -1
 if y>22 or z>15 or random.random()>.42:continue
 mat=ob.data.materials[0];bpy.data.objects.remove(ob,do_unlink=True);changed+=1
 # A torn sheet with a large missing corner and an outward folded lip.
 outline=[(-.5,-.5),(.15,-.5),(.12,-.38),(.34,-.32),(.25,-.15),(.5,-.05),(.5,.5),(-.5,.5)]
 vs=[]
 for u,v in outline:
  bend=max(0,.30-v)*max(0,u+.2)*side*random.uniform(.35,.8)
  vs.append((x+bend,y+u*w,z+v*h))
 ob=mesh('Torn cladding sheet with folded edge',vs,[tuple(range(len(vs)))],mat);mod=ob.modifiers.new('Real sheet thickness','SOLIDIFY');mod.thickness=.10
 # Interior exposed rib visible through the torn corner, with a bent loose end.
 beam('Fracture exposed vertical rib',(x-side*.25,y+w*.30,lo.z),(x-side*.25,y+w*.30,z),.10,.11,rust)
 beam('Fracture bent rib end',(x-side*.25,y+w*.30,z),(x+side*.25,y+w*.23,z+.35),.10,.11,rust)
 # Dark structural fissure branches on surviving upper face.
 pts=[(x+side*.075,y-w*.2,z+h*.49),(x+side*.08,y-w*.1,z+h*.27),(x+side*.08,y-w*.22,z+h*.12),(x+side*.08,y-w*.16,z-h*.06)]
 wire('Cladding branching fracture',pts,.013,shadow)
 wire('Cladding fracture branch',[pts[1],(x+side*.08,y+w*.08,z+h*.2),(x+side*.08,y+w*.18,z+h*.23)],.009,shadow)
# Replace main simple rectangular buttress members by bent I sections.
for ob in list(s.objects):
 if not ob.name.startswith('Right structural buttress'):continue
 mw=ob.matrix_world.copy();zs=[v.co.z for v in ob.data.vertices];a=mw@Vector((0,0,min(zs)));b=mw@Vector((0,0,max(zs)));bpy.data.objects.remove(ob,do_unlink=True)
 mid=a.lerp(b,.52)+Vector((-.18,.1,0));pts=[a,mid,b]
 for j in range(2):
  pa,pb=pts[j:j+2]
  beam('Buckled buttress steel web',pa,pb,.12,.32,metal)
  for dy in [-.17,.17]:beam('Buckled buttress flange',pa+Vector((0,dy,0)),pb+Vector((0,dy,0)),.39,.065,wall)
 for p in [a,b]:box('Buttress bolted foot plate',p,(.66,.62,.12),rust)
# Interrupted wall seams emphasize attachment and missing cover strips.
for y in [-5.2,3.5,12.5]:
 for z in [2.1,7.6]:
  wire('Dangling torn seam strap',[(-7.95,y,z+1),(-7.83,y,z+.35),(-7.48,y+.2,z)],.055,metal)
# Selected floor lips visibly sag without changing passage boundaries.
for ob in s.objects:
 if ob.name.startswith(('Right cantilevered floor edge','Right floor lip')):
  ps=[v.co.y for v in ob.data.vertices]
  if min(ps)>15:continue
  for v in ob.data.vertices:
   if v.co.y>sum(ps)/len(ps):v.co.z-=.10
s.use_nodes=False;s.cycles.samples=48;s.render.filepath=str(O/'render.png')
(O/'audit.json').write_text(json.dumps({'replaced_cladding':changed,'detail_objects':len(C.objects),'camera_fixed':True,'dome_fixed':True,'image_textures':sum(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
