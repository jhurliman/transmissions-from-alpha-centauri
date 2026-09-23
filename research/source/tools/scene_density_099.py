"""099: denser foundation debris and layered city; accepted foreground road unchanged."""
import bpy,sys,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/density-099';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rocks-098/scene.blend'));s=bpy.context.scene;rng=random.Random(9919)
source=[o for o in s.objects if o.get('rock_family') and o.get('scatter_zone')=='bank' and o.dimensions.x>=.10]
new=[]
for i,old in enumerate(sorted(source,key=lambda o:o.name)):
 ob=old.copy();ob.data=old.data.copy();s.collection.objects.link(ob);ob.name='099 foundation '+old.name;ob['added_099']=True
 side=1 if old.location.x>0 else -1
 ob.location.x-=side*rng.uniform(.18,.68);ob.location.y+=rng.choice([-1,1])*rng.uniform(.22,.85)
 ob.rotation_euler.z+=rng.uniform(-.65,.65)
 new.append(ob)
# Additional companions concentrate into loose, visibly overlapping groups.
# Larger source fragments furnish the middle-right wall pockets highlighted by user.
large=sorted(new,key=lambda o:o.dimensions.x,reverse=True)[:24]
for i,ob in enumerate(large):
 cluster=i//4;j=i%4
 anchor=[6.9,8.9,11.0,13.0,15.1,16.3][cluster]
 ob.location.y=anchor+[-.28,.06,.38,.62][j]
 wall=9.85;ob.location.x=wall-ob.dimensions.x*.5-[.06,.34,.13,.60][j]
# Seat only new rocks using the same accepted broad-base terrain fit.
import foundation_contact_092
src=Path(foundation_contact_092.__file__).read_text().replace("if o.get('scatter_zone') in ('road', 'bank')","if o.get('rock_family') and o.get('scatter_zone') in ('road', 'bank')")
src=src.replace("banks = [o for o in stones if o.get('scatter_zone') == 'bank']","banks = [o for o in stones if o.get('added_099')]")
src=src.replace('for accent in scene.objects:', 'for accent in []:');ns={};exec(compile(src,'seating099','exec'),ns);seating=ns['apply'](s)
from city_density_099 import apply
city=apply(s)
for name in ['096 contacts ink','096 damage ink']:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
bpy.context.view_layer.update()
# Re-occlude approved soil fragments against added rock silhouettes.
from mathutils.bvhtree import BVHTree
vv=[];ff=[];deps=bpy.context.evaluated_depsgraph_get()
for rock in new:
 ob=rock.evaluated_get(deps);me=ob.to_mesh();me.calc_loop_triangles();off=len(vv)
 vv.extend(ob.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in t.vertices) for t in me.loop_triangles);ob.to_mesh_clear()
tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);ink=s.objects['097 Broken soil ink'];clipped=0
for frame in ink.data.layers[0].frames:
 dr=frame.drawing;runs=[]
 for st in dr.strokes:
  run=[]
  for p in st.points:
   origin=s.camera.matrix_world.translation;v=Vector(p.position)-origin;hit,_,_,_=tree.ray_cast(origin,v.normalized(),v.length-.018)
   if hit is not None:
    clipped+=1
    if len(run)>1:runs.append(run)
    run=[]
   else:run.append((tuple(p.position),p.radius,p.opacity))
  if len(run)>1:runs.append(run)
 dr.remove_strokes(indices=list(range(len(dr.strokes))));dr.add_strokes(sizes=[len(r) for r in runs])
 for st,run in zip(dr.strokes,runs):
  for p,(pos,r,op) in zip(st.points,run):p.position=pos;p.radius=r;p.opacity=op
(O/'audit.json').write_text(json.dumps({'foundation_sources_at_least_10cm':len(source),'foundation_added':len(new),'city':city,'seating':seating,'occluded_soil_points':clipped},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(O/'placement.blend'))
s.render.use_freestyle=False;s.render.resolution_percentage=75;s.render.filepath=str(O/'preview.png');bpy.ops.render.render(write_still=True)
