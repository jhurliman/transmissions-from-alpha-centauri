"""Geometry-driven optional hardware, corrosion and microink for clean panel masters.
Descriptors: id,object,origin,u,v,normal,width,height; optional polygon_uv,holes_uv,candidate_fasteners_uv.
"""
import bpy,math,random,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def inside(p,poly):
 x,y=p;c=False
 for (a,b),(d,e) in zip(poly,poly[1:]+poly[:1]):
  if (b>y)!=(e>y) and x<(d-a)*(y-b)/(e-b)+a:c=not c
 return c

def valid(p,s,margin=0):
 poly=s.get('polygon_uv',[(0,0),(s['width'],0),(s['width'],s['height']),(0,s['height'])])
 if not inside(p,poly):return False
 return not any(inside(p,h)for h in s.get('holes_uv',[])) and (s['_support'](p) if '_support' in s else True)

def node_group(spec,anchors,seed):
 g=bpy.data.node_groups.new('145 Corrosion '+spec['id'],'ShaderNodeTree');g.interface.new_socket(name='Position',in_out='INPUT',socket_type='NodeSocketVector');g.interface.new_socket(name='Strength',in_out='INPUT',socket_type='NodeSocketFloat').default_value=1;g.interface.new_socket(name='Mask',in_out='OUTPUT',socket_type='NodeSocketFloat');g.interface.new_socket(name='Tint multiplier',in_out='OUTPUT',socket_type='NodeSocketColor');g.interface.new_socket(name='Wash strength',in_out='INPUT',socket_type='NodeSocketFloat').default_value=1;g.interface.new_socket(name='Wash length multiplier',in_out='INPUT',socket_type='NodeSocketFloat').default_value=1.5;g.interface.new_socket(name='Wash mask',in_out='OUTPUT',socket_type='NodeSocketFloat');g.interface.new_socket(name='Wash tint multiplier',in_out='OUTPUT',socket_type='NodeSocketColor');n,l=g.nodes,g.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
 def calc(op,*args):
  q=n.new('ShaderNodeMath');q.operation=op
  for i,x in enumerate(args):
   if isinstance(x,(int,float)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def dot(a,b):
  q=n.new('ShaderNodeVectorMath');q.operation='DOT_PRODUCT';l.new(a,q.inputs[0]);q.inputs[1].default_value=b;return q.outputs['Value']
 rel=n.new('ShaderNodeVectorMath');rel.operation='SUBTRACT';l.new(gi.outputs['Position'],rel.inputs[0]);rel.inputs[1].default_value=spec['origin'];pos=rel.outputs[0];U=dot(pos,spec['u']);V=dot(pos,spec['v']);depth=dot(pos,spec['normal'])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=115;noise.inputs['Detail'].default_value=2;l.new(pos,noise.inputs['Vector'])
 coarse=n.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=43;coarse.inputs['Detail'].default_value=1;l.new(pos,coarse.inputs['Vector'])
 edge=calc('ADD',calc('MULTIPLY',calc('SUBTRACT',coarse.outputs['Fac'],.5),.70),calc('MULTIPLY',calc('SUBTRACT',noise.outputs['Fac'],.5),.24));field=0;contact=0;opacity=0;wash_field=0
 for a in anchors:
  du=calc('SUBTRACT',U,a['uv'][0]);down=calc('SUBTRACT',a['uv'][1],V)
  if a['kind']=='bolt':
   # Unequal oxide contact footprint: irregular broken stain, no concentric palette rings.
   skew=calc('ADD',du,calc('MULTIPLY',down,a.get('skew',.15)))
   dist=calc('SQRT',calc('ADD',calc('POWER',calc('DIVIDE',skew,a['radius']),2),calc('POWER',calc('DIVIDE',down,a['radius']*a.get('aspect',1.12)),2)))
   patch=calc('MULTIPLY',calc('LESS_THAN',calc('ADD',dist,edge),1),calc('SUBTRACT',.92,calc('MULTIPLY',coarse.outputs['Fac'],.20)))
   field=calc('MAXIMUM',field,patch);contact=calc('MAXIMUM',contact,patch);opacity=calc('MAXIMUM',opacity,calc('MINIMUM',1,calc('MULTIPLY',patch,1.3)))
  for trail in a.get('trails',[]):
   tx=calc('SUBTRACT',du,trail['offset']);along=calc('DIVIDE',down,trail['length']);is_broad=trail.get('role')=='broad tapered contact run'
   progress=calc('DIVIDE',calc('MAXIMUM',0,calc('SUBTRACT',along,.10 if is_broad else 0)),.90 if is_broad else 1)
   decay=calc('POWER',calc('MAXIMUM',0,calc('SUBTRACT',1,progress)),trail.get('taper_power',.8));width=calc('ADD',trail.get('tail_width',trail['width']),calc('MULTIPLY',decay,trail['width']-trail.get('tail_width',trail['width'])))
   drift=calc('MULTIPLY',calc('SUBTRACT',coarse.outputs['Fac'],.5),trail['width']*.30)
   if is_broad:
    kink=calc('MULTIPLY',calc('MINIMUM',1,calc('MAXIMUM',0,calc('DIVIDE',calc('SUBTRACT',along,.25),.22))),trail['width']*.30)
    drift=calc('ADD',drift,kink)
   cross=calc('DIVIDE',calc('ABSOLUTE',calc('ADD',tx,drift)),width)
   if is_broad:
    # Continuous translucent rain body; finite edge turbulence, no confetti cutouts.
    edgefade=calc('MINIMUM',1,calc('MAXIMUM',0,calc('MULTIPLY',calc('SUBTRACT',1,calc('ADD',cross,calc('MULTIPLY',edge,.32))),4)))
    shape=calc('MULTIPLY',edgefade,calc('MULTIPLY',calc('GREATER_THAN',down,0),calc('LESS_THAN',along,1)))
    tailbreak=calc('MAXIMUM',calc('LESS_THAN',along,.74),calc('GREATER_THAN',coarse.outputs['Fac'],.48))
    strength=calc('MULTIPLY',calc('MULTIPLY',shape,tailbreak),calc('MULTIPLY',trail['strength'],calc('SUBTRACT',1,calc('MULTIPLY',along,.50))))
   else:
    shape=calc('SUBTRACT',1,calc('MAXIMUM',calc('ADD',cross,edge),along));shape=calc('MULTIPLY',calc('MAXIMUM',0,shape),calc('GREATER_THAN',down,0));broken=calc('GREATER_THAN',noise.outputs['Fac'],trail.get('break_threshold',.45));strength=calc('MULTIPLY',calc('MULTIPLY',shape,broken),trail['strength'])
   field=calc('MAXIMUM',field,strength);opacity=calc('MAXIMUM',opacity,calc('MINIMUM',1,calc('MULTIPLY',strength,1.6 if is_broad else 4.2)))
   # Independent, continuous diluted oxide wash extends the same gravity run50%.
   wash_along=calc('DIVIDE',down,calc('MULTIPLY',trail['length'],gi.outputs['Wash length multiplier']))
   wash_progress=calc('DIVIDE',calc('MAXIMUM',0,calc('SUBTRACT',wash_along,.10)),.90)
   wash_decay=calc('POWER',calc('MAXIMUM',0,calc('SUBTRACT',1,wash_progress)),trail.get('taper_power',.8))
   wash_width=calc('ADD',trail.get('tail_width',trail['width']*.25),calc('MULTIPLY',wash_decay,trail['width']-trail.get('tail_width',trail['width']*.25)))
   wash_cross=calc('DIVIDE',calc('ABSOLUTE',calc('ADD',tx,drift)),wash_width)
   wash_edge=calc('MINIMUM',1,calc('MAXIMUM',0,calc('MULTIPLY',calc('SUBTRACT',1,calc('ADD',wash_cross,calc('MULTIPLY',edge,.22))),4)))
   wash_fade=calc('POWER',calc('MAXIMUM',0,calc('SUBTRACT',1,wash_along)),.75)
   near_origin=calc('MINIMUM',1,calc('MAXIMUM',0,calc('MULTIPLY',along,5)))
   wash_tail=calc('MAXIMUM',calc('LESS_THAN',wash_along,.90),calc('GREATER_THAN',coarse.outputs['Fac'],.47))
   wash=calc('MULTIPLY',calc('MULTIPLY',wash_edge,wash_fade),calc('MULTIPLY',near_origin,wash_tail))
   wash=calc('MULTIPLY',wash,calc('MULTIPLY',.56 if is_broad else .43,calc('GREATER_THAN',down,0)))
   wash_field=calc('MAXIMUM',wash_field,wash)

 gate=calc('LESS_THAN',calc('ABSOLUTE',depth),.045);mask=calc('MULTIPLY',calc('MULTIPLY',opacity,gate),gi.outputs['Strength']);l.new(mask,go.inputs['Mask'])
 wash_mask=calc('MULTIPLY',calc('MULTIPLY',wash_field,gate),calc('MULTIPLY',gi.outputs['Wash strength'],gi.outputs['Strength']));l.new(wash_mask,go.inputs['Wash mask']);go.inputs['Wash tint multiplier'].default_value=(.62,.49,.46,1)
 # Color depends on irregular mineral patches, not distance rings around hardware.
 ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.interpolation='CONSTANT';r.elements[0].position=.0;r.elements[0].color=(.56,.35,.30,1);r.elements[1].position=.78;r.elements[1].color=(.20,.13,.17,1);r.elements.new(.43).color=(.38,.25,.26,1);l.new(coarse.outputs['Fac'],ramp.inputs[0])
 tint=n.new('ShaderNodeMixRGB');tint.blend_type='MIX';l.new(ramp.outputs[0],tint.inputs[1]);tint.inputs[2].default_value=(.80,.43,.26,1)
 warm=calc('MULTIPLY',calc('LESS_THAN',field,.45),calc('GREATER_THAN',noise.outputs['Fac'],.59));l.new(warm,tint.inputs[0]);l.new(tint.outputs[0],go.inputs['Tint multiplier']);g['145 anchors_json']=json.dumps(anchors);g['145 seed']=seed;return g

def attach_overlay(material,group):
 m=material.copy();m.name='145 Attached details | '+material.name;n,l=m.node_tree.nodes,m.node_tree.links;em=next((q for q in n if q.type=='EMISSION'),None);bs=next((q for q in n if q.type=='BSDF_PRINCIPLED'),None);target=em.inputs['Color']if em else bs.inputs['Base Color']if bs else None
 if target is None:raise ValueError('Provide emission or Principled base-color material')
 if target.is_linked:base=target.links[0].from_socket
 else:q=n.new('ShaderNodeRGB');q.outputs[0].default_value=target.default_value;base=q.outputs[0]
 g=n.new('ShaderNodeGroup');g.node_tree=group;g.label='145 Disable corrosion with Strength0';geo=n.new('ShaderNodeNewGeometry');l.new(geo.outputs['Position'],g.inputs['Position']);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';l.new(g.outputs['Mask'],mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(g.outputs['Tint multiplier'],mix.inputs[2]);mix.label='145 Layer1 contact oxide and original run';wash=n.new('ShaderNodeMixRGB');wash.name='145 Layer2 translucent extended rainwash';wash.label='145 Layer2 diluted oxide,1.5x length, fading down';wash.blend_type='MULTIPLY';l.new(g.outputs['Wash mask'],wash.inputs[0]);l.new(mix.outputs[0],wash.inputs[1]);l.new(g.outputs['Wash tint multiplier'],wash.inputs[2]);l.new(wash.outputs[0],target);m['145 detail_layer']=True;m['145 second_wash_layer']='Disable Wash strength; Wash length multiplier=1.5';return m

def apply_panels(specs,parent_collection=None,seed=145,occupancy=.70,add_nicks=False,install_material=True):
 rng=random.Random(seed);dg=bpy.context.evaluated_depsgraph_get()
 for spec in specs:
  ob=spec['object'].evaluated_get(dg);me=ob.to_mesh();mw=ob.matrix_world.copy();tree=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices)for p in me.polygons]);ob.to_mesh_clear()
  def support(p,spec=spec,tree=tree):
   nn=Vector(spec['normal']);world=Vector(spec['origin'])+Vector(spec['u'])*p[0]+Vector(spec['v'])*p[1]+nn*.05;loc,no,fi,dist=tree.ray_cast(world,-nn,.056)
   return bool(loc is not None and no.dot(nn)>.75)
  spec['_support']=support
 parent=parent_collection or bpy.context.scene.collection;root=bpy.data.collections.new('145 Panel detail layers');parent.children.link(root);hardware=bpy.data.collections.new('145 Fasteners');micro=bpy.data.collections.new('145 Microink');cutters=bpy.data.collections.new('145 Optional nick cutters')
 for c in [hardware,micro,cutters]:root.children.link(c)
 def mat(name,col,metal=0):
  m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=.55;return m
 steel=mat('145 Dark fastener steel',(.055,.062,.075),.65);ink=mat('145 Plum microink',(.009,.008,.016));candidates=[]
 for s in specs:
  inset=min(.06,.10*min(s['width'],s['height']));cs=s.get('candidate_fasteners_uv',[(inset,inset),(s['width']-inset,inset),(s['width']-inset,s['height']-inset),(inset,s['height']-inset)])
  for p in cs:
   if valid(p,s) and all(s['_support']((p[0]+dx,p[1]+dy)) for dx,dy in [(.024,0),(-.024,0),(0,.024),(0,-.024)]):candidates.append((s['id'],tuple(p)))
 chosen=set(rng.sample(range(len(candidates)),round(len(candidates)*occupancy)));rows=[]
 def mesh(name,vs,fs,col,material):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob
 for panel_index,s in enumerate(specs):
  origin=Vector(s['origin']);u=Vector(s['u']);v=Vector(s['v']);normal=Vector(s['normal'])
  def world(p,z=0):return origin+u*p[0]+v*p[1]+normal*z
  anchors=[];bolts=[]
  for i,(sid,p)in enumerate(candidates):
   if sid!=s['id']or i not in chosen:continue
   for typ,r,z0,z1,N in [('washer',.020,.0005,.0035,16),('hex head',.014,.0035,.014,6)]:
    vs=[world((p[0]+r*math.cos(k*math.tau/N),p[1]+r*math.sin(k*math.tau/N)),z)for z in [z0,z1]for k in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)];ob=mesh('145 '+s['id']+' '+typ+str(i),vs,fs,hardware,steel);ob['145 panel']=s['id'];ob['145 anchor_uv']=p
   a={'kind':'bolt','uv':p,'world':list(world(p)),'radius':rng.uniform(.025,.035),'aspect':rng.uniform(.82,1.45),'skew':rng.uniform(-.35,.35),'width':rng.uniform(.007,.015),'length':rng.uniform(.16,.60)};anchors.append(a);bolts.append(p)
  top_origins=s.get('top_origins_uv',[(s['width']*rng.uniform(.12,.86),s['height']) for _ in range(rng.choice([0,1,1,2]))])
  for p in top_origins:
   p=list(p)
   for step in range(100):
    q=(p[0],s['height']-.008-step*s['height']*.007)
    if valid(q,s):p=q;break
   else:continue
   anchors.append({'kind':'top edge','uv':p,'world':list(world(p)),'radius':0,'width':rng.uniform(.005,.012),'length':rng.uniform(.16,.52)})
  for a in anchors:
   trail_count=rng.choices([0,1,3,4],[.32,.28,.29,.11])[0] if a['kind']=='bolt' else rng.choice([1,2,3])
   a['trails']=[]
   for k in range(trail_count):
    broad=rng.random()<.17
    a['trails'].append({'offset':rng.uniform(-.017,.017),'width':rng.uniform(.009,.017)if broad else rng.uniform(.0016,.0045),'length':rng.uniform(.025,.085)if broad else rng.uniform(.08,.42),'strength':rng.uniform(.30,.72),'break_threshold':rng.uniform(.45,.57)})
  # A few broad-headed contact runs, with true width decay rather than a constant-width stem.
  if 'broad_run_anchors' not in s and panel_index%4 in [0,2,3] and anchors:
   a=max(anchors,key=lambda q:q['uv'][1]);ww,ll,pp={0:(.028,.56,.8),2:(.039,.33,1.6),3:(.032,.47,1.05)}[panel_index%4];a['trails'].append({'offset':rng.uniform(-.010,.010),'width':ww,'tail_width':.0018,'taper_power':pp,'length':ll,'strength':.52,'break_threshold':.38,'role':'broad tapered contact run'})
  for authored in s.get('broad_run_anchors',[]):
   p=tuple(authored['uv'])
   if not valid(p,s):raise ValueError('Unsupported authored rain anchor '+s['id']+str(p))
   trail={'offset':0,'width':authored.get('half_width',.045),'tail_width':authored.get('tail_half_width',.0018),'taper_power':authored.get('taper_power',1.05),'length':authored.get('length',.45),'strength':authored.get('strength',.60),'break_threshold':.38,'role':'broad tapered contact run'}
   anchors.append({'kind':'authored supported edge','uv':p,'world':list(world(p)),'radius':0,'width':trail['width'],'length':trail['length'],'trails':[trail],'145 source_note':authored.get('source_note','Supported visible upper edge')})
  group=node_group(s,anchors,seed);modified=[]
  if install_material:
   for slot in s['object'].material_slots:
    if slot.material:
     old=slot.material;slot.link='OBJECT';slot.material=attach_overlay(old,group);modified.append(slot.material.name)
  vs=[];fs=[];count=0;area=s['width']*s['height'];limit=round(area*21)
  for i in range(limit*12):
   if count>=limit:break
   mode=rng.random();damage=s.get('damage_footprints_uv',[])
   if mode<.50 and damage:
    poly=rng.choice(damage);q=rng.choice(poly);p=(q[0]*s['width']+rng.gauss(0,.065),q[1]*s['height']+rng.gauss(0,.065))
   elif mode<.82:
    side=rng.choice([.035,s['width']-.035]);p=(side+rng.gauss(0,.045),rng.uniform(.02,s['height']-.02))
   else:p=(rng.uniform(.025,s['width']-.025),rng.uniform(.025,s['height']-.025))
   if not valid(p,s)or any(math.dist(p,b)<.075 for b in bolts):continue
   radius=.0007+(rng.random()**3)*.0055;ry=radius*rng.uniform(.55,1.7);start=len(vs);vs.extend(world((p[0]+radius*math.cos(k*math.tau/5),p[1]+ry*math.sin(k*math.tau/5)),.0006)for k in range(5));fs.append(tuple(range(start,start+5)));count+=1
  dots=mesh('145 '+s['id']+' tiny ink dots',vs,fs,micro,ink)
  for k in range(2):
   p=(rng.uniform(.10,s['width']-.10),rng.uniform(.10,s['height']-.10))
   if not valid(p,s):continue
   rx=rng.uniform(.011,.025);ry=rng.uniform(.003,.008)
   if not all(valid((p[0]+rx*math.cos(j*math.tau/12),p[1]+ry*math.sin(j*math.tau/12)),s)for j in range(12)):continue
   ell=[world((p[0]+rx*math.cos(j*math.tau/12),p[1]+ry*math.sin(j*math.tau/12)),.0008)for j in range(12)];mesh('145 '+s['id']+' elliptic nick ink',ell,[tuple(range(12))],micro,ink)
  for k in range(2):
   p=(rng.uniform(.12,s['width']-.12),rng.uniform(.12,s['height']-.12))
   if not all(valid((p[0]+j*.009,p[1]+math.sin(j*.8)*.005),s)for j in range(6)):continue
   cu=bpy.data.curves.new('145 Short curved gash','CURVE');cu.dimensions='3D';cu.bevel_depth=.0015;cu.bevel_resolution=0;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(5)
   for j,q in enumerate(sp.points):q.co=(*world((p[0]+j*.009,p[1]+math.sin(j*.8)*.005),.001),1)
   ob=bpy.data.objects.new('145 '+s['id']+' short ink gash',cu);micro.objects.link(ob);cu.materials.append(ink)
  nick_count=0
  if add_nicks:
   p=(s['width']*.63,s['height']*.46)
   if valid(p,s):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=world(p,.001));c=bpy.context.object;c.name='145 '+s['id']+' ellipsoid nick cutter';c.scale=(.040,.013,.009);c.rotation_mode='QUATERNION';c.rotation_quaternion=normal.to_track_quat('Z','Y')
    for co in list(c.users_collection):co.objects.unlink(c)
    cutters.objects.link(c);c.hide_render=True;c.display_type='WIRE';mod=s['object'].modifiers.new('145 Optional physical shallow nick','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;nick_count=1
  rows.append({'id':s['id'],'occupied':len(bolts),'anchors':anchors,'ink_dots':count,'physical_nicks':nick_count,'materials':modified,'node_group':group.name})
 return {'panels':rows,'candidate_count':len(candidates),'occupied_count':len(chosen),'occupancy':len(chosen)/len(candidates)if candidates else 0,'seed':seed,'layer_collection':root.name,'disable_layers':{'hardware':hardware.name,'microink':micro.name,'corrosion':'Group Strength=0','physical_nicks':'Modifier show_viewport/show_render False'},'clean_mesh_data_modified':False,'microink_note':'Tiny dots and shortgashes are native surface ink marks, not claimed physical recesses; optional ellipsoid Boolean is true shallow geometry.'}
