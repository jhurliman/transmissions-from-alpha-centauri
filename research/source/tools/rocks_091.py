import bpy,sys,math,random,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from rock_masters_090 import create_rock
O=R/'art/studies/rocks-091';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rocks-090/scene.blend'));s=bpy.context.scene;rng=random.Random(91071)
for o in list(s.objects):
 if o.get('rock_family'):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ground=s.objects['Street foundation'];ev=ground.evaluated_get(deps)
small=bpy.data.collections['090 Small embedded stones'];large=bpy.data.collections['090 Larger fractured debris']
def color(h):
 return tuple((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for v in [int(h[i:i+2],16)/255 for i in (0,2,4)])+(1,)
def material(name,palette):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 def node(t):return n.new(t)
 def mathn(op,a,b):
  q=node('ShaderNodeMath');q.operation=op
  for v,inp in zip([a,b],q.inputs):
   if isinstance(v,(float,int)):inp.default_value=v
   else:l.new(v,inp)
  return q.outputs[0]
 geo=node('ShaderNodeNewGeometry');tex=node('ShaderNodeTexCoord');noise=node('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4.8;noise.inputs['Detail'].default_value=2.1;noise.inputs['Roughness'].default_value=.72;l.new(tex.outputs['Generated'],noise.inputs['Vector'])
 sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN');direction=sun.matrix_world.to_quaternion()@Vector((0,0,1));dot=node('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=direction;l.new(geo.outputs['Normal'],dot.inputs[0])
 # Grain breaks the transitions only slightly, preserving dominant planar faces.
 grain=mathn('MULTIPLY',mathn('SUBTRACT',noise.outputs['Fac'],.5),.22);light=mathn('ADD',dot.outputs['Value'],grain)
 ra=node('ShaderNodeValToRGB');cr=ra.color_ramp;cr.interpolation='CONSTANT';cr.elements.remove(cr.elements[1]);stops=[(-0.0,palette[0]),(.18,palette[1]),(.49,palette[2]),(.78,palette[3])]
 for j,(pos,h) in enumerate(stops):
  e=cr.elements[0] if j==0 else cr.elements.new(pos);e.position=pos;e.color=color(h)
 l.new(light,ra.inputs[0]);mix=node('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.30;l.new(ra.outputs[0],mix.inputs[1]);l.new(noise.outputs['Fac'],mix.inputs[2])
 # Sparse chipped pigment islands, not a full-surface darkening wash.
 chips=mathn('LESS_THAN',noise.outputs['Fac'],.37);chip=node('ShaderNodeMixRGB');l.new(chips,chip.inputs[0]);l.new(mix.outputs[0],chip.inputs[1]);chip.inputs[2].default_value=color(palette[1])
 em=node('ShaderNodeEmission');out=node('ShaderNodeOutputMaterial');l.new(chip.outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs[0]);return m
road=[material('091 road warm fractured rock', ['211b20','403233','795048','a27065']),material('091 road muted fractured rock',['241d21','49393b','795747','a97968'])]
bank=[material('091 bank ochre slab',['272128','554750','827063','a98a73']),material('091 bank violet slab',['242129','4b4656','736777','a38c82']),material('091 bank slate slab',['22212b','414552','737b83','a4a1a0'])]
rim=material('091 selective broken ridge',['211b20','44363b','806052','bb927d'])
# Native, terrain-conforming contact accents, scaled with the individual stones.
sh=bpy.data.materials.new('091 broken contact shadow');sh.use_nodes=True;n=sh.node_tree.nodes;n.clear();l=sh.node_tree.links;tc=n.new('ShaderNodeTexCoord');dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);l.new(tc.outputs['UV'],dist.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.27;r.color_ramp.elements[0].color=(.85,.85,.85,1);r.color_ramp.elements[1].position=.52;r.color_ramp.elements[1].color=(0,0,0,1);l.new(dist.outputs['Value'],r.inputs[0]);em=n.new('ShaderNodeEmission');em.inputs[0].default_value=color('241b1e');tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(r.outputs[0],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);sh.surface_render_method='DITHERED'
# Candidate visibility is checked before adding geometry so dependency updates stay bounded.
records=[];band_counts={'road':[0,0,0],'bank':[0,0,0]};band_quotas={'road':[20,48,52],'bank':[85,147,8]}
def candidate(x,y,w,zone,family=None):
 if abs(x)<.9 and -3.2<y<1.3:return False
 hit,p,no,idx=ev.ray_cast((x,y,2),(0,0,-1))
 if not hit or p.z<-.11:return False
 point=Vector((x,y,p.z+w*.23));q=world_to_camera_view(s,s.camera,point)
 if not (.02<q.x<.98 and .105<q.y<.54 and q.z>0):return False
 band=0 if q.y>.44 else (1 if q.y>.305 else 2)
 if band_counts[zone][band]>=band_quotas[zone][band]:return False
 unit=world_to_camera_view(s,s.camera,point+Vector((1,0,0)));pixels_per_unit=max(1,abs(unit.x-q.x)*1440)
 hero=rng.random() < (.267 if zone=='road' else .188)
 px=rng.uniform(12,22 if zone=='road' else 33) if hero else rng.uniform(4,10)
 w=min(1.0,px/pixels_per_unit)
 if zone=='road':w=min(w,.60)
 point.z=p.z+w*.23
 origin=s.camera.location;d=point-origin;visible,loc,*rest=s.ray_cast(deps,origin,d.normalized(),distance=d.length-.04)
 if visible and (loc-point).length>w*.40:return False
 if any((x-a['x'])**2+(y-a['y'])**2<(w+a['w'])**2*.15 for a in records):return False
 band_counts[zone][band]+=1;records.append(dict(x=x,y=y,z=p.z,w=w,zone=zone,family=family,screen=[q.x,q.y]));return True
# Targets are visible, resolvable stones, separate from subpixel soil grain.
targets=json.loads((O/'generation-targets.json').read_text()) if (O/'generation-targets.json').exists() else {'road':160,'bank':300}
for zone in ['road','bank']:
 start=len(records);attempt=0
 while len(records)-start<targets[zone] and attempt<20000:
  attempt+=1
  if zone=='road':
   x=rng.uniform(-7.0,7.0);y=rng.uniform(-14,29);u=rng.random();w=rng.uniform(.045,.105) if u<.70 else (rng.uniform(.12,.23) if u<.94 else rng.uniform(.24,.38));fam=None
  else:
   side=-1 if rng.random()<.40 else 1;y=(rng.gauss(rng.choice([-4,1.7,7.8,14,22]),1.45) if rng.random()<.63 else rng.uniform(-14,28));u=rng.random();x=side*rng.uniform(7.05,8.65);w=rng.uniform(.045,.14) if u<.66 else (rng.uniform(.15,.32) if u<.91 else rng.uniform(.38,.72));fam=None
  candidate(x,y,w,zone,fam)
# Instantiate the accepted positions; ground-contact accents do not add to stone counts.
for i,a in enumerate(records):
 w=a['w'];zone=a['zone'];family=('slab' if zone=='bank' and w>.65 else a['family']) or rng.choices(['wedge','slab','shard','splinter'],[49,24,20,7])[0];length=w*rng.uniform(.85,1.6);height=w*rng.uniform(.29,.52)
 ob=create_rock('091 '+zone+' '+family,family,91000+i,(w,length,height));co=small if w<.18 else large
 for c in list(ob.users_collection):c.objects.unlink(ob)
 co.objects.link(ob);ob.rotation_euler=(rng.uniform(-.15,.15),rng.uniform(-.18,.18),rng.random()*math.tau);ob.location=(a['x'],a['y'],a['z']-height*.19)
 if zone=='bank' and w>.38:
  ob.rotation_euler.x=rng.uniform(.35,.72)*(-1 if a['x']<0 else 1);ob.rotation_euler.y=rng.uniform(-.32,.32)
  ob.location.z=a['z']-min((ob.rotation_euler.to_matrix()@v.co).z for v in ob.data.vertices)-height*.35
 ob.data.materials.append(rng.choice(road if zone=='road' else bank));ob['scatter_zone']=zone
 if w>.14:
  ob.data.materials.append(rim);be=ob.modifiers.new('091 narrow fractured ridge','BEVEL');be.width=w*.016;be.segments=1;be.affect='EDGES';be.limit_method='ANGLE';be.angle_limit=.45;be.material=1
 if w>.07:
  verts=[];uv=[]
  for k in range(16):
   t=math.tau*k/16;radius=rng.uniform(.90,1.08);dx=math.cos(t)*w*.82*radius;dy=math.sin(t)*length*.69*radius;ang=ob.rotation_euler.z;xx=a['x']+dx*math.cos(ang)-dy*math.sin(ang)-.05*w;yy=a['y']+dx*math.sin(ang)+dy*math.cos(ang);hit,p,_,_=ev.ray_cast((xx,yy,2),(0,0,-1));verts.append((xx,yy,(p.z if hit else a['z'])+.008));uv.append((.5+math.cos(t)*.5,.5+math.sin(t)*.5))
  me=bpy.data.meshes.new('091 contact');me.from_pydata(verts,[],[list(range(16))]);me.uv_layers.new()
  for loop in me.loops:me.uv_layers[0].data[loop.index].uv=uv[loop.vertex_index]
  shadow=bpy.data.objects.new('091 contact accent',me);small.objects.link(shadow);me.materials.append(sh)
(O/'scatter-audit.json').write_text(json.dumps({'target_visible':targets,'accepted_candidates':{z:sum(a['zone']==z for a in records) for z in targets},'screen_band_counts':band_counts,'records':records,'visibility':'camera-frustum and native scene ray test before placement; tiny grain excluded from targets'},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.03;s.render.border_max_x=.43;s.render.border_min_y=.15;s.render.border_max_y=.51;s.render.filepath=str(O/'detail.png');bpy.ops.render.render(write_still=True)
