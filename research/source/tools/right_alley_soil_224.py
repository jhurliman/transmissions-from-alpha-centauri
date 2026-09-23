"""224: expose native earth in the right cross-alley; sparse accepted small stones.
Apply before bank dust223. No rendering, main-road geometry change or gatefloor edit.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
BOX=(8.0,21.0,.4,6.0)
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]
def apply(scene):
 if scene.get('soil224_applied'):raise RuntimeError('224 already applied')
 plate=scene.objects['Side road surface'];ground=scene.objects['Street foundation'];original=ground.data.materials[0]
 assert all(abs(a-b)<.001 for a,b in zip(sum(bounds(plate),[]),[8,.4,0,21,6,.03]))
 old=original;old.use_fake_user=True;m=old.copy();m.name='224 Existing painted earth | right cross-alley pale branch';ground.data.materials[0]=m
 ns=m.node_tree.nodes;ls=m.node_tree.links;mix=ns['Mix (Legacy).008'];assert mix.inputs[2].links[0].from_node.name=='Mix (Legacy).006'
 oldmask=mix.inputs[0].links[0].from_socket
 geo=ns.new('ShaderNodeNewGeometry');geo.name='224 Native world position';sep=ns.new('ShaderNodeSeparateXYZ');ls.new(geo.outputs['Position'],sep.inputs[0])
 def mathnode(op,a,b,name):
  n=ns.new('ShaderNodeMath');n.operation=op;n.name='224 '+name
  for inp,val in zip(n.inputs,[a,b]):
   if isinstance(val,(float,int)):inp.default_value=val
   else:ls.new(val,inp)
  return n.outputs[0]
 xm=mathnode('GREATER_THAN',sep.outputs['X'],8.0,'inside X low');xx=mathnode('LESS_THAN',sep.outputs['X'],21.,'inside X high')
 ym=mathnode('GREATER_THAN',sep.outputs['Y'],.4,'inside Y low');yy=mathnode('LESS_THAN',sep.outputs['Y'],6.,'inside Y high')
 rect=mathnode('MULTIPLY',mathnode('MULTIPLY',xm,xx,'X range'),mathnode('MULTIPLY',ym,yy,'Y range'),'cross alley rectangle')
 mask=mathnode('MAXIMUM',oldmask,rect,'preserve old bank and add cross alley');ls.new(mask,mix.inputs[0])
 plate.hide_render=True;plate.hide_set(True);plate['hidden_by224']='User removes raised brown cross-alley floor plate; native soil below retained'
 hidden=[]
 for o in list(scene.objects):
  if not(o.get('rock_family') and o.get('scatter_zone')=='bank'):continue
  a,b=bounds(o)
  if min(b[0],21)-max(a[0],8)>.04 and min(b[1],6)-max(a[1],.4)>.04:
   o.hide_render=True;o.hide_set(True);hidden.append(o.name)
 accents=[]
 for o in scene.objects:
  if o.get('contact_owner') in hidden:o.hide_render=True;o.hide_set(True);accents.append(o.name)
 sources=[o for o in scene.objects if o.get('rock_family') and o.get('scatter_zone')=='bank' and o.location.x<0 and 5<o.location.y<22 and max(o.dimensions.x,o.dimensions.y)<.30 and not o.hide_render]
 assert len(sources)>5
 sources.sort(key=lambda o:o.name);rng=random.Random(224031);created=[];occupied=[];inv=ground.matrix_world.inverted()
 # Unequal loose groups mixed with isolated grains; independent coordinates, no grid.
 anchors=[(8.65,1.0,.50),(10.7,4.9,.7),(13.9,2.25,.8),(18.6,4.7,.7)]
 trials=0
 while len(created)<44 and trials<1000:
  trials+=1;i=len(created)
  if i<26:
   ax,ay,spread=anchors[rng.randrange(len(anchors))];x=rng.gauss(ax,spread);y=rng.gauss(ay,spread*.55)
  else:x=rng.uniform(8.25,20.7);y=rng.uniform(.65,5.73)
  if not(8.2<x<20.75 and .62<y<5.78):continue
  if any((x-a)**2+(y-b)**2<.22**2 for a,b in occupied):continue
  src=rng.choice(sources);o=src.copy();o.data=src.data.copy();o.name=f'224 Right cross-alley small {src.get("rock_family")} {i:02}'
  src.users_collection[0].objects.link(o);o.rotation_euler.z+=rng.uniform(-math.pi,math.pi);o.scale*=rng.uniform(.78,1.04);o.location=(x,y,0);bpy.context.view_layer.update()
  # Seat every native broad-base support vertex against actual retained terrain.
  zmin=min(v.co.z for v in o.data.vertices);base=[v.co for v in o.data.vertices if v.co.z<zmin+.008];shifts=[]
  for v in base:
   p=o.matrix_world@v;ok,hit,_,_=ground.ray_cast(inv@Vector((p.x,p.y,2)),Vector((0,0,-1)))
   if ok:shifts.append((ground.matrix_world@hit).z-p.z)
  if not shifts:bpy.data.objects.remove(o,do_unlink=True);continue
  o.location.z=max(shifts)-.003;o['study224']=True;o['rock_family']=src['rock_family'];o['scatter_zone']='bank';o['source224']=src.name;o['contact_method_092']='224 Native support vertices seated in existing terrain';o['contact_owner']=''
  occupied.append((x,y));created.append({'name':o.name,'source':src.name,'xyz':list(o.location),'dimensions':list(o.dimensions),'support_vertices':len(base),'embed_m':.003})
 scene['soil224_applied']=True
 return {'iteration':224,'source':'final221 before222/223 integration','hidden_plate':plate.name,'plate_bounds':bounds(plate),'soil_object':ground.name,'original_soil_material':old.name,'new_soil_material':m.name,'soil_geometry_unchanged':True,'pale_branch':'Mix (Legacy).006','rectangle_world_xy':list(BOX),'outside_rectangle_mask_unchanged':True,'hidden_existing_bank_rocks':hidden,'hidden_owned_contact_accents':accents,'added_small_stones':created,'count':len(created),'main_road_rocks_unchanged':True,'gatefloor222_untouched':True,'review':'CPU construction only; await combined native render'}
if __name__=='__main__':
 O=R/'art/studies/right-alley-soil-224';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/haze-texture-221/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
