"""Camera-prioritized native far facade spalls; private nested instance paths only."""
import bpy,bmesh,math,json,random,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.geometry import delaunay_2d_cdt
from bpy_extras.object_utils import world_to_camera_view
from colosseum_crumbling_190 import point_in,readvalue,writevalue,interpolate
R=Path(__file__).resolve().parents[1]

def coremat(base,kind):
 m=base.copy();m.name='234 '+kind+' core | '+base.name;m['234 damage core']=kind
 if not m.use_nodes:return m
 n=m.node_tree.nodes;l=m.node_tree.links;em=next((x for x in n if x.type=='EMISSION'),None)
 if not em:return m
 old=em.inputs[0].links[0].from_socket if em.inputs[0].is_linked else None
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY'if kind=='crack'else'MIX';mix.inputs[0].default_value=.68 if kind=='crack'else .13
 if old:l.new(old,mix.inputs[1])
 else:mix.inputs[1].default_value=em.inputs[0].default_value
 mix.inputs[2].default_value=(.18,.17,.22,1)if kind=='crack'else(.30,.29,.31,1)
 # Fine aggregate modulates the inherited lit palette; it is subordinate to geometry.
 geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],noise.inputs[0]);ramp=n.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.30;ramp.inputs['From Max'].default_value=.7;ramp.inputs['To Min'].default_value=.76;ramp.inputs['To Max'].default_value=1.07;l.new(noise.outputs['Fac'],ramp.inputs[0]);grain=n.new('ShaderNodeMixRGB');grain.blend_type='MULTIPLY';grain.inputs[0].default_value=.55;l.new(mix.outputs[0],grain.inputs[1]);l.new(ramp.outputs[0],grain.inputs[2]);l.new(grain.outputs[0],em.inputs[0]);return m

def inset(ob,face,outer,inner,depth,kind,cache):
 src=ob.data;src.calc_loop_triangles();p=src.polygons[face];normal=p.normal.copy();center=p.center.copy();v=Vector((0,0,1));v-=normal*v.dot(normal)
 if v.length<.01:v=Vector((0,1,0));v-=normal*v.dot(normal)
 v.normalize();u=v.cross(normal).normalized();ids=list(p.vertices);xy=[Vector(((src.vertices[i].co-center).dot(u),(src.vertices[i].co-center).dot(v)))for i in ids];N=len(xy);edges=[]
 for loop in(outer,inner):
  off=len(xy);xy.extend(Vector(q)for q in loop);edges.extend((off+i,off+(i+1)%len(loop))for i in range(len(loop)))
 out,_,faces,_,_,parents=delaunay_2d_cdt(xy,edges,[tuple(range(N))],1,1e-7,True)
 verts=[q.co.copy()for q in src.vertices];mapping={};weights=[[(i,1.)]for i in range(len(verts))];tri=[t for t in src.loop_triangles if t.polygon_index==face]
 for i,q in enumerate(out):
  old=next((j for j,a in enumerate(xy[:N])if(a-q).length<1e-6),None)
  if old is not None:mapping[i]=ids[old];continue
  pp=center+u*q.x+v*q.y;dep=depth if point_in(q,inner)else 0.
  # CDT vertices on the inner boundary require explicit positive depth.
  if any((q-Vector(a)).length<1e-6 for a in inner):dep=depth
  mapping[i]=len(verts);verts.append(pp-normal*dep)
  winner=None;best=1e9
  for t in tri:
   a,b,c=[src.vertices[j].co for j in t.vertices];v0=b-a;v1=c-a;v2=pp-a;den=v0.dot(v0)*v1.dot(v1)-v0.dot(v1)**2
   if abs(den)<1e-15:continue
   wb=(v1.dot(v1)*v2.dot(v0)-v0.dot(v1)*v2.dot(v1))/den;wc=(v0.dot(v0)*v2.dot(v1)-v0.dot(v1)*v2.dot(v0))/den;ww=[1-wb-wc,wb,wc];score=sum(max(0,-w)for w in ww)
   if score<best:best=score;winner=list(zip(t.vertices,ww))
  weights.append(winner)
 ff=[];srcfaces=[];slots=[];corners=[];coreflags=[];base_slots=[sl.material for sl in ob.material_slots];base=base_slots[p.material_index];key=(base.name,kind)
 if key not in cache:cache[key]=coremat(base,kind)
 base_slots.append(cache[key]);coreslot=len(base_slots)-1
 for old in src.polygons:
  if old.index==face:continue
  ff.append(list(old.vertices));srcfaces.append(old.index);slots.append(old.material_index);corners.extend([[(li,1.)]for li in old.loop_indices]);coreflags.append(False)
 for f,pa in zip(faces,parents):
  if 0 not in pa:continue
  fi=[mapping[i]for i in f];q=sum((out[i]for i in f),Vector((0,0)))/len(f);iscore=point_in(q,inner);rim=point_in(q,outer)
  ff.append(fi);srcfaces.append(face);slots.append(coreslot if iscore else p.material_index);coreflags.append(rim)
  for index in fi:
   ww=weights[index];cw=[]
   for vi,w in ww:
    li=next(k for k in p.loop_indices if src.loops[k].vertex_index==vi);cw.append((li,w))
   corners.append(cw)
 me=bpy.data.meshes.new('234 physically recessed '+src.name);me.from_pydata(verts,[],ff);me.update()
 for m in base_slots:me.materials.append(m)
 for attr in src.attributes:
  if attr.is_internal or attr.name in('position','custom_normal','material_index')or attr.domain not in('POINT','FACE','CORNER'):continue
  if attr.data_type not in('FLOAT','INT','BOOLEAN','FLOAT_VECTOR','FLOAT2','FLOAT_COLOR','BYTE_COLOR'):continue
  dest=me.attributes.get(attr.name)or me.attributes.new(attr.name,attr.data_type,attr.domain)
  if attr.domain=='FACE':
   for i,j in enumerate(srcfaces):writevalue(dest.data[i],attr.data_type,readvalue(attr.data[j],attr.data_type))
  else:
   for i,ww in enumerate(weights if attr.domain=='POINT'else corners):writevalue(dest.data[i],attr.data_type,interpolate([readvalue(attr.data[j],attr.data_type)for j,w in ww],[w for j,w in ww],attr.data_type))
 normals=[];oldnorm=[tuple(n.vector)for n in src.corner_normals]
 for p,pi,slot,core in zip(me.polygons,srcfaces,slots,coreflags):
  p.material_index=slot;p.use_smooth=src.polygons[pi].use_smooth
  for li in p.loop_indices:
   normals.append(tuple(p.normal)if core else tuple(Vector(interpolate([oldnorm[j]for j,w in corners[li]],[w for j,w in corners[li]],'FLOAT_VECTOR')).normalized()))
 me.normals_split_custom_set(normals);bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);bm.free();assert bad==0,(ob.name,bad)
 # Thin native ink only along the recessed floor/lip boundary, not its triangulation.
 ea=me.attributes.get('freestyle_edge')or me.attributes.new('freestyle_edge','BOOLEAN','EDGE');links={}
 for p in me.polygons:
  for i,a in enumerate(p.vertices):links.setdefault(tuple(sorted((a,p.vertices[(i+1)%len(p.vertices)]))),[]).append(p.material_index)
 count=0
 for e in me.edges:
  mi=links.get(tuple(sorted(e.vertices)),[])
  if len(mi)==2 and(mi[0]==coreslot)!=(mi[1]==coreslot):ea.data[e.index].value=True;count+=1
 ob.data=me
 for sl in ob.material_slots:sl.link='DATA'
 ob['234 native facade damage']=kind
 return {'source_vertices':len(src.vertices),'new_vertices':len(me.vertices),'source_boundary_vertices_exact':all((me.vertices[i].co-src.vertices[i].co).length==0 for i in range(len(src.vertices))),'nonmanifold_edges':bad,'core_material':cache[key].name,'native_inner_boundary_edges':count,'depth_local_m':depth}

def apply(scene):
 from landmark_contact_visibility_210 import external_tree
 assert not scene.get('facade_damage234_applied');roots=sorted([o for o in bpy.data.collections['215 Short alley composition'].objects if o.instance_collection],key=lambda o:(o.location.y,o.name));assert len(roots)==18
 records=[];allstate={};rootleaves={}
 def walk(c,M,path,root):
  for ob in c.objects:
   if ob.hide_render:continue
   allstate.setdefault(ob,(ob.matrix_world.copy(),ob.data));T=M@ob.matrix_world
   if ob.instance_collection:walk(ob.instance_collection,T@Matrix.Translation(-ob.instance_collection.instance_offset),path+[ob],root)
   elif ob.type=='MESH':
    rootleaves.setdefault(root,[]).append(ob)
    if len(ob.data.vertices)!=8 or not any(t in ob.name for t in('Folded sheet face','Gallery base panel','receiver left','receiver right','receiver below','receiver lintel')):continue
    ps=[T@v.co for v in ob.data.vertices];normalM=T.to_3x3().inverted().transposed();cam=scene.camera.matrix_world.translation
    for face in ob.data.polygons:
     if len(face.vertices)!=4:continue
     n=(normalM@face.normal).normalized();center=T@face.center
     if abs(n.z)>.2 or n.dot((cam-center).normalized())<.20:continue
     v=Vector((0,0,1));v-=face.normal*v.dot(face.normal)
     if v.length<.1:continue
     v.normalize();u=v.cross(face.normal).normalized();coords=[((ob.data.vertices[i].co-face.center).dot(u),(ob.data.vertices[i].co-face.center).dot(v))for i in face.vertices];lo=[min(q[k]for q in coords)for k in(0,1)];hi=[max(q[k]for q in coords)for k in(0,1)];W,H=hi[0]-lo[0],hi[1]-lo[1]
     if W<.50 or H<.60:continue
     pro=[world_to_camera_view(scene,scene.camera,T@ob.data.vertices[i].co)for i in face.vertices];pw=(max(q.x for q in pro)-min(q.x for q in pro))*3840;ph=(max(q.y for q in pro)-min(q.y for q in pro))*2885
     if max(pw,ph)<16 or min(pw,ph)<5:continue
     records.append({'root':root,'path':path,'object':ob,'matrix':T.copy(),'face':face.index,'center':center,'u':u,'v':v,'lo':lo,'hi':hi,'W':W,'H':H,'pixels':[pw,ph],'normal':n})
 for root in roots:walk(root.instance_collection,root.matrix_world@Matrix.Translation(-root.instance_collection.instance_offset),[],root)
 print('234 candidates',len(records),flush=True);tree,owners,info=external_tree(scene);cam=scene.camera.matrix_world.translation;visible=[]
 for r in records:
  ob=r['object'];face=ob.data.polygons[r['face']];good=[]
  for fx,fy in[(.50,.5),(.38,.42),(.62,.64)]:
   p=face.center+r['u']*(r['lo'][0]+r['W']*fx)+r['v']*(r['lo'][1]+r['H']*fy);world=r['matrix']@p;d=world-cam;hit=tree.ray_cast(cam,d.normalized(),d.length+.05)
   if hit[0]is not None and(hit[0]-world).length<.025:good.append((fx,fy))
  if good:r['options']=good;visible.append(r)
 print('234 visible',len(visible),flush=True);chosen=[];perroot=[]
 for root in roots:
  options=[r for r in visible if r['root']==root];options.sort(key=lambda r:r['pixels'][0]*r['pixels'][1],reverse=True);picked=[]
  for r in options:
   if any((r['center']-q['center']).length<1.2 for q in picked):continue
   picked.append(r)
   if len(picked)>=(3 if'step'in root.name else 2):break
  chosen.extend(picked);perroot.append({'root':root.name,'visible_candidates':len(options),'events':len(picked)})
 assert all(any(r['root']==o for r in chosen)for o in roots if'step'in o.name),'Both tall steps need real visible damage'
 print('234 SELECTED',perroot,flush=True)
 # Collection path copies are shallow and scoped; unaffected meshes/IDs stay shared.
 privatecols={};copied=[];aliases=[];newobjects=[];materials={};audit=[]
 def colcopy(old,name):
  c=bpy.data.collections.new(name);c.use_fake_user=True;c.instance_offset=old.instance_offset
  for q in old.objects:c.objects.link(q)
  for q in old.children:c.children.link(q)
  return c
 for index,r in enumerate(chosen):
  root=r['root'];key=(root.name,)
  if key not in privatecols:privatecols[key]=colcopy(root.instance_collection,'234 Private facade '+root.name);root.instance_collection=privatecols[key]
  c=privatecols[key]
  for old in r['path']:
   key=key+(old.name,)
   if key not in privatecols:
    q=old.copy();q.name='234 '+old.name;q.parent=None;q.matrix_world=allstate[old][0];q.instance_collection=colcopy(old.instance_collection,'234 Private component '+old.name);c.objects.unlink(old);c.objects.link(q);privatecols[key]=q.instance_collection;copied.append(q.name)
   c=privatecols[key]
  old=r['object'];q=old.copy();q.name='234 '+root.name+' | '+old.name;q.parent=None;q.matrix_world=allstate[old][0];q.data=old.data.copy();c.objects.unlink(old);c.objects.link(q);newobjects.append(q)
  # Geometry works in actual receiver local coordinates, retaining source materials.
  face=q.data.polygons[r['face']];rng=random.Random(int(hashlib.sha256((root.name+str(index)+old.name).encode()).hexdigest()[:12],16));fx,fy=r['options'][0];cx=r['lo'][0]+r['W']*fx;cy=r['lo'][1]+r['H']*fy;kind='crack'if index%3==1 else'spall'
  thickness=max(v.co.dot(face.normal)for v in q.data.vertices)-min(v.co.dot(face.normal)for v in q.data.vertices);depth=min(thickness*.65,.085)
  if kind=='spall':
   rx=min(r['W']*.34,(cx-r['lo'][0])*.85,(r['hi'][0]-cx)*.85);ry=min(r['H']*.35,(cy-r['lo'][1])*.85,(r['hi'][1]-cy)*.85);outer=[]
   for j in range(15):
    angle=math.tau*j/15;f=rng.uniform(.66,1.07);outer.append((cx+math.cos(angle)*rx*f,cy+math.sin(angle)*ry*f))
   inner=[(cx+(x-cx)*.78,cy+(y-cy)*.79)for x,y in outer]
  else:
   pts=[]
   half=min(r['H']*.39,(cy-r['lo'][1])*.86,(r['hi'][1]-cy)*.86)
   for j in range(8):pts.append((cx+rng.uniform(-.15,.15)*r['W'],cy+half*(1-2*j/7)))
   def ribbon(extra):
    left=[];right=[]
    for j,(x,y)in enumerate(pts):
     w=min(r['W']*.10,.075)*(.65+.35*math.sin(j*1.7))+extra;left.append((x-w,y));right.append((x+w,y))
    return left+right[::-1]
   outer=ribbon(min(r['W']*.035,.035));inner=ribbon(0)
  metrics=inset(q,r['face'],outer,inner,depth,kind,materials);qp=[world_to_camera_view(scene,scene.camera,r['matrix']@(face.center+r['u']*x+r['v']*y))for x,y in outer];pb=[min(p.x for p in qp)*3840,(1-max(p.y for p in qp))*2885,max(p.x for p in qp)*3840,(1-min(p.y for p in qp))*2885]
  mapping={o.name:o.name for o in rootleaves[root]};mapping[old.name]=q.name;aliases.append(mapping);audit.append({'root':root.name,'object':q.name,'source':old.name,'kind':kind,'world_center':list(r['center']),'verified_visible':True,'feature_native_4k_bbox':pb,'feature_pixels':[pb[2]-pb[0],pb[3]-pb[1]],**metrics})
 ink=bpy.data.collections['215 Distant accepted component ink']
 for q in newobjects:
  if q.name not in ink.objects:ink.objects.link(q)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for q in newobjects:
     if q.name not in ls.collection.objects:ls.collection.objects.link(q)
 groups=json.loads(scene.get('212 source name groups','[]'));groups.extend(aliases);scene['212 source name groups']=json.dumps(groups);scene['facade_damage234_applied']=True
 return {'source':'233','method':'Private inward-only native face recesses preserving every source boundary vertex. Spall floors retain source lit paint plus restrained pale aggregate; cracks have deeper-value native floors.','buildings':perroot,'events':audit,'event_count':len(audit),'visible_buildings':sum(x['events']>0 for x in perroot),'private_collections':len(privatecols),'private_objects':len(newobjects),'original_meshes_material_graphs_unchanged':True,'windows_doors_services_roofs_unchanged':True,'standing_ruins_untouched':True,'native_ink':'Existing215inclusive and all near EXCLUSIVE unions; actual inner edges marked.','visual_status':'CPU candidate; parent combined native render pending'}
