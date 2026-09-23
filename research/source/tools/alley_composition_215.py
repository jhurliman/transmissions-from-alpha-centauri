"""Short native-size accepted-component buildings; no stretched alley strips."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
PLACEMENTS=[(-1,48,11.8,'service'),(-1,64,12.6,'gallery'),(-1,83,11.4,'step'),(-1,103,13.0,'service'),(-1,123,11.8,'gallery'),(-1,144,13.2,'service'),(1,51,12.4,'gallery'),(1,70,11.8,'service'),(1,89,15.5,'step'),(1,111,11.7,'gallery'),(1,131,12.7,'service'),(1,149,12.3,'gallery')]
SOURCE_NAMES=['Architecture | layout_access.007','Architecture | layout_broad.007','Architecture | layout_transition.010','Architecture | slot_wall.003','Architecture | floor_band.003','Architecture | layout_broad.032','Architecture | layout_transition.036','Architecture | window_bay','Architecture | window_open.001','XL | companion_600_L3','XL | housing_1000','XL | companion_wall_True','XL | companion_wall_False','073 bolted wall shoe.037']

def apply(scene):
 from alley_repeat_212 import private_copy,verts
 assert not bpy.data.collections.get('215 Short alley composition'),'Already applied215'
 roots={n:bpy.data.objects[n]for n in SOURCE_NAMES};state={};visited=set()
 def collect(c):
  if c in visited:return
  visited.add(c)
  for ob in c.objects:
   state[ob]=(ob.matrix_world.copy(),ob.data)
   if ob.instance_collection:collect(ob.instance_collection)
  for child in c.children:collect(child)
 for ob in roots.values():
  state[ob]=(ob.matrix_world.copy(),ob.data)
  if ob.instance_collection:collect(ob.instance_collection)
 bounds={}
 for n,o in roots.items():
  p=list(verts(o));bounds[n]=([min(v[k]for v in p)for k in range(3)],[max(v[k]for v in p)for k in range(3)])
 C=bpy.data.collections.new('215 Short alley composition');scene.collection.children.link(C)
 allnew=set();source_maps=[];kit_cache={};masters={};metrics=[];components=[]
 def kit(name):
  if name not in kit_cache:
   original=roots[name];col,mapping=private_copy(original.instance_collection,'215 Kit '+name,state);kit_cache[name]=col;allnew.update(o for o in mapping.values()if o.type in('MESH','CURVE'));source_maps.append({o.name:q.name for o,q in mapping.items()})
  return kit_cache[name]
 def part(master,name,y,z,face='street'):
  src=roots[name];lo,hi=bounds[name];cx=8.55 if lo[0]>0 else -9.5641107559;cy=(lo[1]+hi[1])/2
  Q=Matrix.Rotation(math.pi,4,'Z')if lo[0]>0 else Matrix.Identity(4)
  # Keep complete source geometry dimensions and assemble at a new native-size origin.
  M=Matrix.Translation((0,y,z))@Q@Matrix.Translation((-cx,-cy,-lo[2]))@state[src][0]
  if face=='rear':M=Matrix.Translation((-y,master['length']/2,z))@Matrix.Rotation(math.pi/2,4,'Z')@Q@Matrix.Translation((-cx,-cy,-lo[2]))@state[src][0]
  if face=='front':M=Matrix.Translation((-y,-master['length']/2,z))@Matrix.Rotation(-math.pi/2,4,'Z')@Q@Matrix.Translation((-cx,-cy,-lo[2]))@state[src][0]
  ob=bpy.data.objects.new('215 component '+name,None);ob.instance_type='COLLECTION';ob.instance_collection=kit(name);ob.matrix_world=M;master['collection'].objects.link(ob);components.append({'source':name,'object':ob.name,'dimensions_preserved':True,'placement_only':True});return ob
 def paintmat(name):
  for o in roots[name].instance_collection.all_objects:
   if o.type=='MESH':
    for sl in o.material_slots:
     if sl.material and any(t in sl.material.name.lower()for t in('coating','wall','face','facade')):return sl.material
  return next(sl.material for o in roots[name].instance_collection.all_objects for sl in o.material_slots if sl.material)
 def box(master,name,center,size,mat):
  x,y,z=center;a,b,c=(v/2 for v in size);vs=[(x+i*a,y+j*b,z+k*c)for i,j,k in[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]];fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);ob=bpy.data.objects.new(name,me);master['collection'].objects.link(ob);bev=ob.modifiers.new('Small structural edge bevel','BEVEL');bev.width=.025;bev.segments=1;allnew.add(ob);return ob
 def pipe(master,y,with_housing):
  # Existing600mm route: bottom wall entry,3m straight, optional housing, top wall entry.
  routes=[('XL | companion_wall_True',0),('XL | companion_600_L3',0)]
  delta=-3.0
  if with_housing:routes.append(('XL | housing_1000',0))
  else:delta-=1.5
  routes.append(('XL | companion_wall_False',delta))
  for name,dz in routes:
   src=roots[name];ob=bpy.data.objects.new('215 closed service '+name,None);ob.instance_type='COLLECTION';ob.instance_collection=kit(name);ob.matrix_world=Matrix.Translation((9.22,y-22.5,dz-.44))@state[src][0];master['collection'].objects.link(ob)
  # Attached mounting shoes reused at their exact dimensions.
  for z in (1.6,3.9):
   src=roots['073 bolted wall shoe.037'];ob=bpy.data.objects.new('215 service mounting shoe',None);ob.instance_type='COLLECTION';ob.instance_collection=kit(src.name);ob.matrix_world=Matrix.Translation((9.07,y-22.5,z-2))@state[src][0];master['collection'].objects.link(ob)
  steel=next(sl.material for ob in roots['XL | companion_600_L3'].instance_collection.all_objects for sl in ob.material_slots if sl.material)
  for z in(1.6,3.9):box(master,'215 service shoe continuation',(.81,y,z),(1.38,.12,.14),steel)
  master['service_endpoints']=['Lower fitted90degree wallentry','Upper fitted90degree wallentry'];master['pipe_height']=6.62 if with_housing else 5.12
 def make(kind,warm):
  key=(kind,warm)
  if key in masters:return masters[key]
  col=bpy.data.collections.new('215 Prefab '+kind+(' warm'if warm else' cool'));col.use_fake_user=True
  n=3 if kind=='step'else 2;L=2.8*n;master={'collection':col,'length':L,'kind':kind,'warm':warm};masters[key]=master
  base='Architecture | layout_transition.036'if warm else'Architecture | layout_access.007';broad='Architecture | layout_broad.032'if warm else'Architecture | layout_broad.007';mat=paintmat(base)
  heights=[]
  for j in range(n):
   y=-L/2+1.4+2.8*j
   part(master,base if j%2==0 else broad,y,.05)
   if kind=='gallery':
    part(master,'Architecture | window_bay'if j==0 else'Architecture | window_open.001',y,2.22);h=5.63
   else:
    part(master,'Architecture | floor_band.003',y,2.37);part(master,'Architecture | slot_wall.003',y,2.72);part(master,'Architecture | layout_transition.010',y,4.30);h=6.46
    if kind=='step'and j!=0:part(master,broad,y,6.48);h=8.64
   heights.append(h)
   box(master,'215 quiet inner wall',(-.88,y,h/2),(.20,2.8,h),mat)
   box(master,'215 real roof slab',(-2.7875,y,h+.0825),(6.075,2.84,.205),mat)
   part(master,'Architecture | floor_band.003',y,h+.17)
  # Leading side has actual accepted panel bays, not a featureless square slab.
  front_h=heights[0]
  for face,H in(('front',heights[0]),('rear',heights[-1])):
   for off in(1.4,4.2):
    for z in(.05,2.23,4.41,6.59):
     if z+2.16<=H+.03:part(master,broad,off,z,face)
  box(master,'215 leading interior return',(-2.85,-L/2+.14,front_h/2),(5.7,.20,front_h),mat)
  box(master,'215 rear wall return',(-2.85,L/2-.1,heights[-1]/2),(5.7,.20,heights[-1]),mat)
  box(master,'215 outer rear wall',(-5.62,0,max(heights)/2),(.18,L,max(heights)),mat)
  if kind!='gallery':pipe(master,-L/2+1.38,kind=='step')
  master['heights']=heights;return master
 placements=[]
 for side,y,x,kind in PLACEMENTS:
  master=make(kind,side>0);root=bpy.data.objects.new('215 '+('left'if side<0 else'right')+' '+kind+' '+str(y),None);root.instance_type='COLLECTION';root.instance_collection=master['collection'];root.matrix_world=Matrix.Translation((side*x,y,0))@(Matrix.Rotation(math.pi,4,'Z')if side>0 else Matrix.Identity(4));C.objects.link(root);placements.append({'object':root.name,'side':side,'y':y,'frontage_x':side*x,'kind':kind,'roof_heights_m':master['heights'],'native_size':True})
 hidden=[]
 for ob in list(bpy.data.collections['101 Original city layout study'].all_objects):
  if ob.get('reference_mass')and not ob.hide_render:ob.hide_render=True;hidden.append(ob.name)
 gp=bpy.data.objects.get('101 A city contacts')
 if gp:gp.hide_render=True
 # New native IDs receive only their own thinner distant line set, never near style changes.
 ink=bpy.data.collections.new('215 Distant accepted component ink');ink.use_fake_user=True
 for o in allnew:ink.objects.link(o)
 for vl in scene.view_layers:
  if not vl.use_freestyle:continue
  for ls in list(vl.freestyle_settings.linesets):
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    u=bpy.data.collections.new('215 union '+ls.collection.name);u.use_fake_user=True
    for ob in set(ls.collection.all_objects)|allnew:u.objects.link(ob)
    ls.collection=u
  ls=vl.freestyle_settings.linesets.new('215 Distant component architecture');ls.select_by_collection=True;ls.collection=ink;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_edge_mark=True;ls.linestyle.thickness=.42;ls.linestyle.color=(.027,.024,.035);ls.linestyle.alpha=.86
 scene['212 source name groups']=json.dumps(source_maps)
 from alley_ink_atmosphere_215 import apply as isolate_atmosphere
 atmosphere_ink=isolate_atmosphere(scene)
 return {'atmosphere_ink':atmosphere_ink,'source':'210/70','placements':placements,'prefabs':[{'name':m['collection'].name,'kind':m['kind'],'heights':m['heights'],'length':m['length'],'service_endpoints':m.get('service_endpoints')}for m in masters.values()],'source_components':SOURCE_NAMES,'component_instances':len(components),'private_geometry_objects':len(allnew),'hidden_oldcity':hidden,'native_dimensions_preserved':True,'no_original_geometry_or_material_edits':True,'fixed_near_alley':True}


def prepare_guard_pairs(scene):
 from alley_repeat_212 import repeat_guard_pairs
 repeat_guard_pairs(scene)

def install_far_guards(scene):
 import parameter_editor
 from types import SimpleNamespace
 original=list(parameter_editor.callbacks_modifiers_post)
 guards=[f for f in original if any(getattr(f,'_guard'+str(n),False)for n in(192,205,207))]
 def callback(scene,layer,ls):
  if ls.name!='215 Distant component architecture':return[]
  return[shader for f in guards for shader in f(scene,layer,SimpleNamespace(name='Selective geometry contours'))]
 callback._guard215=True
 parameter_editor.callbacks_modifiers_post[:]=[f for f in original if not getattr(f,'_guard215',False)]
 parameter_editor.callbacks_modifiers_post.append(callback)
 return {'style':'215 Distant component architecture','existing_rules':[192,205,207],'near_unchanged':True}
