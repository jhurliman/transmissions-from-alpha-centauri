"""236 geometry-only rubble tongues joining retained pile to destroyed wall feet."""
import bpy,json,random,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/rubble-extension-236'

def apply(scene):
 assert not bpy.data.collections.get('236 Backward rubble transition'),'Apply236 once'
 C=bpy.data.collections.new('236 Backward rubble transition');scene.collection.children.link(C)
 before={o.name:(o.data,tuple(v for r in o.matrix_world for v in r),tuple(sl.material for sl in o.material_slots))for o in bpy.data.objects if o.type=='MESH'}
 dg=bpy.context.evaluated_depsgraph_get();soil=bpy.data.objects['Street foundation'];ev=soil.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();terrain=BVHTree.FromPolygons([soil.matrix_world@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);ev.to_mesh_clear()
 def height(x,y):
  hit=terrain.ray_cast(Vector((x,y,15)),Vector((0,0,-1)),35);assert hit[0] is not None,(x,y);return hit[0].z
 pools={'masonry':[],'structural':[]};templates={}
 for family in ['077 End rubble depth clusters','075 Scrap integration','078 End rubble tangled structural remnants']:
  for ob in bpy.data.collections[family].all_objects:
   if ob.type!='MESH'or ob.hide_render or(family.startswith('075')and ob.get('zone')!='end'):continue
   ps=[ob.matrix_world@Vector(v)for v in ob.bound_box];center=sum(ps,Vector())/8;span=[max(p[k]for p in ps)-min(p[k]for p in ps)for k in range(3)]
   if not(29<center.y<44)or max(span[:2])<.65:continue
   if 'layered masonry fragment'in ob.name:pools['masonry'].append(ob)
   elif family.startswith('075')or'torn projecting sheet'in ob.name or'hollow severed pipe'in ob.name:pools['structural'].append(ob)
 assert pools['masonry']and pools['structural']
 cache={};materials={};rows=[];rng=random.Random(236)
 def template(src):
  if src.name in cache:return cache[src.name]
  ev=src.evaluated_get(dg);data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);data.transform(src.matrix_world)
  vs=[v.co.copy()for v in data.vertices];center=Vector(((min(v.x for v in vs)+max(v.x for v in vs))/2,(min(v.y for v in vs)+max(v.y for v in vs))/2,min(v.z for v in vs)))
  data.transform(Matrix.Translation(-center));slots=[sl.material for sl in src.material_slots];indices=[p.material_index for p in data.polygons];data.materials.clear()
  for old in slots:
   if old not in materials:
    private=old.copy();private.name='236 Retained rubble palette | '+old.name;private['236 original palette']=old.name;materials[old]=private
   data.materials.append(materials[old])
  for p,i in zip(data.polygons,indices):p.material_index=min(i,len(slots)-1)
  cache[src.name]=data;return data
 # Stagger unequal sections so tongues do not become two neat mirrored rows.
 sections=[(32.7,2.6,14),(35.2,2.9,16),(37.9,2.5,13),(40.5,2.2,11),(43.3,1.8,8),(46.0,1.35,6),(48.0,.85,3)]
 for side in(-1,1):
  for band,(y0,width,count)in enumerate(sections):
   depth=(y0-32.7)/(48-32.7);cx=side*((5.40 if side<0 else 6.05)+(2.20 if side<0 else 2.35)*depth)
   for j in range(count+(1 if side>0 and band in(1,3)else 0)):
    kind='structural'if j%5==0 and band<5 else'masonry';src=rng.choice(pools[kind]);base=template(src);data=base.copy();ob=bpy.data.objects.new('236 '+('Left'if side<0 else'Right')+' rubble tongue '+kind,data);C.objects.link(ob)
    span=max(max(v.co.x for v in data.vertices)-min(v.co.x for v in data.vertices),max(v.co.y for v in data.vertices)-min(v.co.y for v in data.vertices))
    desired=rng.uniform(.70,1.55)*(1-.42*depth)
    if j==0 and band<4:desired*=1.20
    factor=desired/span;angle=rng.uniform(-math.pi,math.pi);data.transform(Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((factor,factor,factor,1)))
    # Keep the extension low enough to expose damaged wall faces; broad source bottoms remain grounded.
    zmax=max(v.co.z for v in data.vertices);cap=.95*(1-.55*depth)
    if zmax>cap:
     scale=cap/zmax
     for v in data.vertices:v.co.z*=scale
    x=cx+rng.uniform(-width*.46,width*.46);y=y0+rng.uniform(-1.0,1.0)+(0.20 if side>0 else-.13)
    if min(abs(x+v.co.x)for v in data.vertices)<2.2:x+=side*(2.3-min(abs(x+v.co.x)for v in data.vertices))
    # Exact terrain seating: minimum vertex clearance is zero; other vertices never penetrate terrain.
    dz=max(height(x+v.co.x,y+v.co.y)-v.co.z for v in data.vertices);ob.location=(x,y,dz)
    clearances=[v.co.z+dz-height(x+v.co.x,y+v.co.y)for v in data.vertices];assert min(clearances)>-1e-5 and min(clearances)<1e-4
    ob['236 extension']=True;ob['236 side']='left'if side<0 else'right';ob['236 world depth']=y;ob['236 depth_m']=y;ob['236 fade fraction']=max(0,min(1,(y-32)/17));ob['236 source']=src.name;ob['zone']='236 midground extension';ob['236 band']=band
    world=[ob.matrix_world@v.co for v in data.vertices] # Update view layer below before final world bounds.
    rows.append({'object':ob.name,'side':ob['236 side'],'source':src.name,'kind':kind,'center':[x,y,dz],'band':band,'desired_footprint_m':desired,'height_cap_m':cap,'minimum_terrain_clearance_m':min(clearances),'minimum_route_abs_x':min(abs(x+v.co.x)for v in data.vertices),'depth_m':y,'vertices':len(data.vertices),'faces':len(data.polygons)})
 bpy.context.view_layer.update()
 for row in rows:
  ob=bpy.data.objects[row['object']];pts=[ob.matrix_world@v.co for v in ob.data.vertices];row['world_min']=[min(p[k]for p in pts)for k in range(3)];row['world_max']=[max(p[k]for p in pts)for k in range(3)]
 for name,(data,M,mats)in before.items():
  ob=bpy.data.objects[name];assert ob.data==data and tuple(v for r in ob.matrix_world for v in r)==M and tuple(sl.material for sl in ob.material_slots)==mats,name
 return {'study':236,'source':'ruin-integration-235','collection':C.name,'objects':len(rows),'masonry':sum(r['kind']=='masonry'for r in rows),'structural':sum(r['kind']=='structural'for r in rows),'rows':rows,'bounds':[[min(r['world_min'][k]for r in rows)for k in range(3)],[max(r['world_max'][k]for r in rows)for k in range(3)]],'all_original_meshes_materials_transforms_exact':True,'source_shapes':'Existing077 angular masonry plus075 casings/channels and078 severed sheets/pipes','private_palette_materials':len(materials),'grounding':'Evaluated native Street foundation raycast; zero minimum vertex clearance','center_route_half_width_m':2.2,'depth_metadata':'236 depth_m and236 fade fraction on every new object; parent owns ink/material transition','references':['UCL-01','DP-03','DP-08'],'status':'CPU native geometry; parent combined actual proof pending'}

if __name__=='__main__':
 O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ruin-integration-235/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('236 RUBBLE READY',a['objects'],a['bounds'],flush=True)
