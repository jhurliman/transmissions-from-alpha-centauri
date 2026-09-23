"""Editable recessed facade kit and complete scoped replacement of the far-city family."""
import bpy,math,random,hashlib,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
FAMILY_NAMES=('ribbed bay tower','stepped slab ruin','partial structural frame')
def lin(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def rgba(hex):return tuple(lin(int(hex[i:i+2],16)/255) for i in (0,2,4))+(1,)
def material(name,hex,kind):
 m=bpy.data.materials.new('211 '+name);m.use_nodes=True;nt=m.node_tree;n=nt.nodes;l=nt.links;n.clear()
 def nd(t,label):q=n.new(t);q.label=label;return q
 out=nd('ShaderNodeOutputMaterial','Native material');em=nd('ShaderNodeEmission','211 Lit pigment output');l.new(em.outputs[0],out.inputs[0])
 g=nd('ShaderNodeNewGeometry','Physical surface coordinates');dif=nd('ShaderNodeBsdfDiffuse','211 Actual incident scene light');dif.inputs[0].default_value=(.65,.65,.65,1);rgb=nd('ShaderNodeShaderToRGB','211 Continuous light response');l.new(dif.outputs[0],rgb.inputs[0]);bw=nd('ShaderNodeRGBToBW','211 Light intensity');l.new(rgb.outputs[0],bw.inputs[0])
 r=nd('ShaderNodeMapRange','211 Quiet ambient floor and continuous highlight');r.clamp=True;r.inputs['From Min'].default_value=0;r.inputs['From Max'].default_value=.8;r.inputs['To Min'].default_value=.52 if kind!='recess' else .26;r.inputs['To Max'].default_value=1.16 if kind!='recess' else .58;l.new(bw.outputs[0],r.inputs[0])
 mix=nd('ShaderNodeMixRGB','211 Same mineral palette across structural parts');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[1].default_value=rgba(hex);l.new(r.outputs[0],mix.inputs[2]);color=mix.outputs[0]
 tex=nd('ShaderNodeTexNoise','211 Connected worn finish');tex.inputs['Scale'].default_value=3.8;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.68;l.new(g.outputs['Position'],tex.inputs[0])
 ramp=nd('ShaderNodeValToRGB','211 Restrained unequal coating remnants');ramp.color_ramp.elements[0].position=.38;ramp.color_ramp.elements[0].color=(.76,.78,.82,1);ramp.color_ramp.elements[1].position=.62;ramp.color_ramp.elements[1].color=(1.1,1.05,.99,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);w=nd('ShaderNodeMixRGB','211 Connected small tonal variation');w.blend_type='MULTIPLY';w.inputs[0].default_value=.43;l.new(color,w.inputs[1]);l.new(ramp.outputs[0],w.inputs[2]);color=w.outputs[0]
 vor=nd('ShaderNodeTexVoronoi','211 Fine broken mineral pits');vor.inputs['Scale'].default_value=45;l.new(g.outputs['Position'],vor.inputs[0]);mask=nd('ShaderNodeMath','211 Sparse grain');mask.operation='LESS_THAN';mask.inputs[1].default_value=.19;l.new(vor.outputs['Distance'],mask.inputs[0]);p=nd('ShaderNodeMixRGB','211 Dark granules');p.blend_type='MULTIPLY';p.inputs[2].default_value=(.42,.44,.47,1);l.new(mask.outputs[0],p.inputs[0]);l.new(color,p.inputs[1]);ao=nd('ShaderNodeAmbientOcclusion','211 Real recess contact shading');ao.inputs['Distance'].default_value=.55
 contact=nd('ShaderNodeMixRGB','211 Contact shadow without flat black bays');contact.blend_type='MULTIPLY';contact.inputs[0].default_value=.62;l.new(p.outputs[0],contact.inputs[1]);l.new(ao.outputs['Color'],contact.inputs[2]);l.new(contact.outputs[0],em.inputs[0]);return m

def mesh(C,name,vs,fs,mat,bevel=0):
 me=bpy.data.meshes.new('211 '+name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();o=bpy.data.objects.new('211 '+name,me);C.objects.link(o)
 if bevel:
  b=o.modifiers.new('211 Small physical chipped-edge return','BEVEL');b.width=bevel;b.segments=1;b.affect='EDGES'
 return o

def box(C,name,loc,dim,mat,bevel=.025):
 x,y,z=loc;a,b,c=[v/2 for v in dim];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in ((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))]
 return mesh(C,name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat,bevel)

def crown(C,name,x0,x1,y,thick,z,mat,seed):
 rng=random.Random(seed);w=x1-x0
 xs=[x0,x0+w*.18,x0+w*.24,x0+w*.51,x0+w*.66,x1]
 heights=[z+rng.uniform(-.24,.16) for _ in xs];heights[2]-=.48;profile=[(x0,z-.85),(x1,z-.85)]+list(reversed(list(zip(xs,heights))))
 N=len(profile);vs=[(x,y+d,zz)for d in(0,thick)for x,zz in profile];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
 return mesh(C,name,vs,fs,mat,.018)

def kit(family,variant,stories=3):
 rng=random.Random(211+family*100+variant);C=bpy.data.collections.new(f'211 Prefab {family}.{variant} {stories}stories | '+FAMILY_NAMES[family]);C.use_fake_user=True
 hex=('72788b','7b727c','777583')[variant];m=material(f'{family}.{variant} mineral wall',hex,'wall');rec=material(f'{family}.{variant} sheltered bay',hex,'recess');edge=material(f'{family}.{variant} exposed slabs',('858188','8d7e7b','818187')[variant],'edge')
 #Canonical3m-wide module. Components occupy real physical depths, with an unbroken rear weather shell.
 W=3.;D=3.;H=stories*4.;levels=tuple(i*(H-.5)/stories for i in range(stories+1));front=.10
 backH=H-4.2 if family==2 else (H-4 if family==1 else H-.6)
 box(C,'rear weather shell',(0,2.85,backH/2),(W,.3,backH),m)
 if family==1:box(C,'setback upper rear shell',(-.28,2.85,H-2.05),(2.16,.3,3.9),m)
 for side in(-1,1):
  sideH=H-4 if family==1 else H-.4
  for yy in(.16,2.84):box(C,'true returned corner post',(side*1.37,yy,sideH/2),(.26,.32,sideH),m)
  box(C,'side grouped bay mullion',(side*1.38,1.62,sideH/2),(.22,.13,sideH-.12),m)
  #Broad side panels are separated by real shallow construction joints.
  for row in range(stories-(1 if family in(1,2) else 0)):
   zz=(row+.5)*(H-.6)/stories;hh=(H-.6)/stories-.045
   y0=.43;y1=2.70;z0=zz-hh/2;z1=zz+hh/2
   prof=[(y0,z0),(y1,z0),(y1,z1)]
   if (row+variant)%2==0:prof.extend([(y1-.24,z1),(y1-.42,z1-.24),(y1-.59,z1)])
   prof.append((y0,z1));N=len(prof);vs=[(side*1.23+dd,yy,z)for dd in(-.05,.05)for yy,z in prof];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
   mesh(C,'chipped recessed side bay',vs,fs,rec,.012)
   box(C,'side floor reveal',(side*1.36,1.6,z0+.03),(.30,2.27,.12),edge,.014)
  if family==1:
   for yy in(.55,2.80):box(C,'setback upper corner',(side*.96-.28,yy,H-2.05),(.24,.28,3.9),m)
   box(C,'setback upper side skin',(side*.86-.28,1.8,H-2.1),(.10,2.12,3.8),rec)
 bays=[(-1.20,-.12),(.12,1.20)]
 for j,(z0,z1) in enumerate(zip(levels,levels[1:])):
  setback=.40 if family==1 and j==stories-1 else 0
  front=.10+setback
  for b,(x0,x1) in enumerate(bays):
   if family==1 and j==stories-1:x0=x0*.72-.28;x1=x1*.72-.28
   quiet=(j+b+variant)%3==0
   if family==2 and j==stories-1:quiet=False
   if quiet:
    for seg in range(2):
     zz=z0+(seg+.5)*(z1-z0)/2
     box(C,'quiet jointed wall panel',((x0+x1)/2,front+.14,zz),(x1-x0,.22,(z1-z0)/2-.045),m)
   else:
    #Proper jamb depth, side reveals, shaded rear wall and a broad sill.
    deep=.48 if family!=2 else .75
    if not(family==2 and j==stories-1):box(C,'recess rear panel',((x0+x1)/2,front+deep,(z0+z1)/2),(x1-x0,.14,z1-z0-.28),rec)
    for xx in(x0,x1):box(C,'recess inner jamb',(xx,front+deep/2,(z0+z1)/2),(.10,deep,z1-z0-.2),m,.018)
    for zz in(z0+.22,z1-.20):box(C,'recess slab return',((x0+x1)/2,front+deep/2,zz),(x1-x0,deep,.16),edge,.018)
    #Only one strong architectural divider per group; no miniature illuminated grids.
    if j==1 and b==variant%2:box(C,'single deep bay crossmember',((x0+x1)/2,front+.28,z0+.93),(x1-x0,.14,.12),edge,.012)
  box(C,'central structural rib',(-.28 if family==1 and j==stories-1 else 0,front-.02,(z0+z1)/2),(.24,.32,z1-z0),m)
  #Unequal slab truncation makes structural loss part of the geometry.
  slabw=2.72 if j!=stories-1 else rng.uniform(1.75,2.35);slabx=0 if j!=stories-1 else rng.uniform(-.24,.24)
  box(C,'broken projecting floor slab',(slabx,1.37,z0+.10),(slabw,2.72,.20),edge)
 if family==0:
  for x in(-1.40,1.40):box(C,'interrupted external vertical rib',(x,-.04,(H-1.3)/2),(.18,.24,H-1.3),edge)
 elif family==1:
  box(C,'setback upper side wall',(-.92,1.65,H-.44),(.20,2.4,.75),m)
 else:
  for x in(-.70,.58):box(C,'exposed broken crown post',(x,1.85,H-.32),(.16,.20,rng.uniform(.8,1.35)),edge)
 cx=-.28 if family==1 else 0;cw=1.05 if family==1 else 1.46;cy=.50 if family==1 else .08
 crown(C,'broken front parapet',cx-cw,cx+cw,cy,.22,H-.05,m,variant+family*13)
 crown(C,'broken rear parapet',cx-cw,cx+cw,2.78,.22,H-.12,m,variant+family*13+9)
 for side in(-1,1):
  xedge=(side*.96-.28) if family==1 else side*1.37
  ob=crown(C,'broken side parapet',.55 if family==1 else .16,2.84,-xedge-.1,.20,H-.12,m,variant+family*13+side+23);ob.rotation_euler.z=math.pi/2
 C['211 family']=FAMILY_NAMES[family];C['211 nominal dimensions']=[3,3,H];C['211 stories']=stories
 return C

def apply(scene):
 old=bpy.data.collections['101 Original city layout study'];groups={}
 for o in old.all_objects:
  if o.type=='MESH' and o.get('reference_mass') and not o.hide_render:groups.setdefault(o['reference_mass'],[]).append(o)
 assert len(groups)==23,len(groups)
 out=bpy.data.collections.new('211 Native city prefab scatter');scene.collection.children.link(out);skins=[];prefabs={(f,v):kit(f,v,(2,3,5)[v])for f in range(3)for v in range(3)};rows=[]
 scales=(.72,1.18,.87,1.32,1.04,.65,1.24,.92,1.35)
 for index,(mid,obs) in enumerate(sorted(groups.items())):
  vs=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=Vector(tuple(min(v[i]for v in vs)for i in range(3)));hi=Vector(tuple(max(v[i]for v in vs)for i in range(3)));W=hi.x-lo.x;H=hi.z-lo.z;D=max(hi.y-lo.y,min(3.6,W*1.15));factor=scales[index%len(scales)]
  if mid=='R08':factor=1.35
  if mid=='N_L6':factor=1.32
  if mid=='R03':factor=.65
  family=index%3;variant=0 if H*factor<7.5 else (1 if H*factor<13 else 2);stories=(2,3,5)[variant]
  #Low partial structures remain separate silhouettes without changing the route footprint.
  #Share the kit meshes while preserving each original building's palette identity.
  body=next((o for o in obs if 'measured crown mass' in o.name),obs[0]);oldmat=body.active_material
  ramps=[n for n in oldmat.node_tree.nodes if n.type=='VALTORGB' and n.label=='Two broad painted light families'] if oldmat and oldmat.use_nodes else []
  original_color=tuple(ramps[0].color_ramp.elements[-1].color) if ramps else rgba(('686176','736575','625f76')[variant])
  skin=bpy.data.collections.new('211 Palette '+mid);skin.use_fake_user=True;skins.append(skin);mm={}
  for src in prefabs[(family,variant)].objects:
   q=src.copy();q.name='211 '+mid+' '+src.name;skin.objects.link(q)
   for slot in q.material_slots:
    orig=slot.material
    if orig.name not in mm:
     cm=orig.copy();cm.name='211 '+mid+' '+orig.name;nn=next(n for n in cm.node_tree.nodes if n.label=='211 Same mineral palette across structural parts');base=tuple(nn.inputs[1].default_value);weight=.58 if 'exposed slabs' in orig.name else .75;nn.inputs[1].default_value=tuple(base[i]*(1-weight)+original_color[i]*weight for i in range(3))+(1,);mm[orig.name]=cm
    slot.link='OBJECT';slot.material=mm[orig.name]
  inst=bpy.data.objects.new('211 '+mid+' '+FAMILY_NAMES[family],None);inst.instance_type='COLLECTION';inst.instance_collection=skin;out.objects.link(inst);inst.location=((lo.x+hi.x)/2,lo.y,lo.z);inst.scale=(W/3,D/3,H*factor/(stories*4));inst['reference_mass']=mid;inst['211 replaces native city']=True
  for o in obs:o.hide_render=True
  def project(pt):
   q=world_to_camera_view(scene,scene.camera,Vector(pt));return [q.x*scene.render.resolution_x,(1-q.y)*scene.render.resolution_y]
  oldtop=project(((lo.x+hi.x)/2,lo.y,hi.z));newtop=project(((lo.x+hi.x)/2,lo.y,lo.z+H*factor));foot=project(((lo.x+hi.x)/2,lo.y,lo.z))
  rows.append({'projected_old_top':oldtop,'projected_new_top':newtop,'projected_foot':foot,'id':mid,'source_objects':[o.name for o in obs],'family':FAMILY_NAMES[family],'variant':variant,'stories':stories,'average_story_height_m':H*factor/stories,'original_palette_linear':original_color,'original_palette_weight':.75,'old_bounds':[list(lo),list(hi)],'new_height':H*factor,'height_ratio':factor,'new_depth':D,'street_width_and_front_preserved':True})
 #Keep foreground widths off the new city. Preserve existing exclusions in private unions.
 ink=bpy.data.collections.new('211 Native city ink targets');ink.use_fake_user=True
 for c in skins:
  for o in c.objects:ink.objects.link(o)
 union_cache={}
 for vl in scene.view_layers:
  if not vl.use_freestyle:continue
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    oldfilter=ls.collection
    if oldfilter.name not in union_cache:
     u=bpy.data.collections.new('211 City exclusion union | '+oldfilter.name);u.use_fake_user=True
     for o in set(oldfilter.all_objects)|set(ink.objects):u.objects.link(o)
     union_cache[oldfilter.name]=u
    ls.collection=union_cache[oldfilter.name]
  ls=vl.freestyle_settings.linesets.new('211 Fine city structural contours');ls.select_by_collection=True;ls.collection=ink;ls.collection_negation='INCLUSIVE';ls.select_by_edge_types=True
  for prop in ('select_ridge_valley','select_suggestive_contour','select_material_boundary','select_contour','select_external_contour','select_edge_mark'):setattr(ls,prop,False)
  ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.linestyle.thickness=.26;ls.linestyle.color=(.035,.032,.047);ls.linestyle.alpha=.84
 return {'source_visible_masses':len(groups),'source_objects_hidden':sum(len(x)for x in groups.values()),'prefab_masters':9,'prefab_families':list(FAMILY_NAMES),'prefab_mesh_parts':sum(len(c.objects)for c in prefabs.values()),'instances':rows,'changed_original_objects':'hide_render only on106visible city meshes','no_other_scene_changes':True,'native_geometry_no_reference_projection':True}
