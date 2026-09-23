"""Redistribute approved foundation fragments relative to real facade footprints."""
import bpy,sys,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/rocks-098';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-097/scene.blend'));s=bpy.context.scene
rng=random.Random(98017)
rocks=[o for o in s.objects if o.get('rock_family') and o.get('scatter_zone')=='bank']
road=[o for o in s.objects if o.get('rock_family') and o.get('scatter_zone')=='road']
road_before={o.name:[list(row) for row in o.matrix_world] for o in road}
bounds=json.loads((O/'facade-bounds.json').read_text());walls=[]
for n,a,b in bounds:
 if any(t in n.lower() for t in ['panel field backing','recessed base wall','gallery base panel','utility base','tapered column structural volume','vertical structural pier']):walls.append((n,a,b))
def face(side,y):
 choices=[]
 for n,a,b in walls:
  if (a[0]+b[0])*side>0 and a[1]-.01<=y<=b[1]+.01:choices.append(min(abs(a[0]),abs(b[0])))
 return min(choices) if choices else None
# Static architecture occlusion tree: reveals visible foundation pockets.
from mathutils.bvhtree import BVHTree
av=[];af=[]
for ins in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=ins.object;n=ob.name.lower()
 if ob.type!='MESH' or ob.hide_render or ob.get('rock_family') or any(t in n for t in ['street foundation','contact accent','contact shadow','broken earth lip','dust','fog','cloud','sky','dome']):continue
 me=ob.to_mesh();me.calc_loop_triangles();off=len(av);av.extend(ins.matrix_world@v.co for v in me.vertices);af.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);ob.to_mesh_clear()
architecture=BVHTree.FromPolygons(av,af,all_triangles=True)
old={o.name:o.location.copy() for o in rocks};reports=[]
for rank,o in enumerate(sorted(rocks,key=lambda o:o.dimensions.x*o.dimensions.y,reverse=True)):
 side=1 if o.location.x>0 else -1;y=o.location.y
 # Bring a limited set of hidden, distant medium slabs into visible foreground
 # foundation pockets; each pocket has four unevenly spaced companions.
 if 10<=rank<34:
  j=rank-10;side=-1 if j<12 else 1
  anchor=[-7.55,-4.65,-1.55][(j%12)//4]
  y=anchor+[-.24,.04,.31,.57][j%4]
 wall=face(side,y)
 if wall is None:
  # Fill real facade areas, leaving the cross-alley and service bay open.
  ranges=[(-7.5,-.2),(3.4,19.7),(20.3,28)] if side<0 else [(-7.7,.1),(6.3,16.8),(17.5,28)]
  ya,yb=min(ranges,key=lambda ab:min(abs(y-ab[0]),abs(y-ab[1])));y=max(ya,min(yb,y))+rng.uniform(-.12,.12);wall=face(side,y)
 if wall is None:wall=8.4 if side<0 else 9.2
 half=o.dimensions.x*.5
 near=rank<len(rocks)*.68
 gap=rng.uniform(.005,.10) if near else rng.uniform(.22,max(.35,wall-7.2-half))
 x=side*(wall-half-gap)
 # Avoid a new continuous wall necklace: preserve irregular longitudinal gaps,
 # and move colliding pieces into a second shallow row.
 for prev in reports:
  if (x-prev['x'])**2+(y-prev['y'])**2 < ((half+prev['half'])*.70)**2:x-=side*half*.8
 # Pull hidden stones only far enough forward to clear projecting plinths.
 origin=s.camera.matrix_world.translation
 for attempt in range(14):
  target=Vector((x,y,max(.12,o.location.z+o.dimensions.z*.78)))
  ray=target-origin;hit,_,_,_=architecture.ray_cast(origin,ray.normalized(),ray.length-.03)
  if hit is None:break
  x-=side*.10
 o.location.x=x;o.location.y=y;o['placement_098']='wall accumulation' if near else 'light-soil fan';reports.append(dict(name=o.name,x=x,y=y,wall=wall,half=half,group=o['placement_098']))
bpy.context.view_layer.update()
# Reuse accepted broad-base seating without shrinking contact shades a second time.
import foundation_contact_092 as seating
src=Path(seating.__file__).read_text().replace("if o.get('scatter_zone') in ('road', 'bank')","if o.get('rock_family') and o.get('scatter_zone') in ('road', 'bank')")
src=src.replace('for accent in scene.objects:', 'for accent in []:')
ns={};exec(compile(src,'foundation_contact_092', 'exec'),ns);seat=ns['apply'](s)
terrain=s.objects['Street foundation'].evaluated_get(bpy.context.evaluated_depsgraph_get());inv=terrain.matrix_world.inverted()
for accent in s.objects:
 owner=accent.get('contact_owner')
 if owner not in old:continue
 delta=s.objects[owner].location-old[owner]
 for v in accent.data.vertices:
  p=accent.matrix_world@v.co;p.x+=delta.x;p.y+=delta.y
  ok,hit,_,_=terrain.ray_cast(inv@Vector((p.x,p.y,4)),Vector((0,0,-1)))
  if ok:p.z=(terrain.matrix_world@hit).z+.001
  v.co=accent.matrix_world.inverted()@p
 accent.data.update()
assert road_before=={o.name:[list(row) for row in o.matrix_world] for o in road}
# Remove old scene-contact bake, which belongs to old stone locations.
for name in ['096 contacts ink','096 damage ink']:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.context.view_layer.update()
# Clip approved soil strokes against newly moved rocks; retain their original style.
deps=bpy.context.evaluated_depsgraph_get();ink=s.objects['097 Broken soil ink'];clipped=0
from mathutils.bvhtree import BVHTree
vv=[];ff=[]
for rock in rocks:
 ob=rock.evaluated_get(deps);me=ob.to_mesh();me.calc_loop_triangles();offset=len(vv)
 vv.extend(ob.matrix_world@v.co for v in me.vertices);ff.extend(tuple(offset+i for i in t.vertices) for t in me.loop_triangles);ob.to_mesh_clear()
rocktree=BVHTree.FromPolygons(vv,ff,all_triangles=True)
for frame in ink.data.layers[0].frames:
 drawing=frame.drawing;runs=[]
 for st in drawing.strokes:
  run=[]
  for p in st.points:
   pos=ink.matrix_world@Vector(p.position);origin=s.camera.matrix_world.translation;v=pos-origin;loc,_,_,_=rocktree.ray_cast(origin,v.normalized(),v.length-.018)
   hidden=loc is not None
   if hidden:
    clipped+=1
    if len(run)>1:runs.append(run)
    run=[]
   else:run.append((tuple(p.position),p.radius,p.opacity))
  if len(run)>1:runs.append(run)
 drawing.remove_strokes(indices=list(range(len(drawing.strokes))))
 drawing.add_strokes(sizes=[len(r) for r in runs])
 for st,run in zip(drawing.strokes,runs):
  for p,(pos,r,op) in zip(st.points,run):p.position=pos;p.radius=r;p.opacity=op
(O/'placement.json').write_text(json.dumps(dict(count=len(rocks),road_unchanged=len(road),rocks=reports,seating=seat,soil_points_occluded=clipped),indent=2))
s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(O/'placement.blend'))
