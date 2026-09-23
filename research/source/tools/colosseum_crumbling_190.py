"""190 v2: connected camera-visible native shallow wall-face losses.
Constrained face-local triangulation; no whole-wall Boolean regularization.
Original vertices/boundaries, untouched faces, attributes and material lineage remain.
"""
import bpy,math,random,json,sys,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-190'

def basis(n):
 v=Vector((0,0,1));v=(v-n*v.dot(n)).normalized();return v.cross(n).normalized(),v

def substrate(base,label,gain):
 m=base.copy();m.name='190 '+label+' '+base.name
 em=next((n for n in m.node_tree.nodes if n.type=='EMISSION'),None)
 if em and em.inputs[0].is_linked:
  old=em.inputs[0].links[0].from_socket;mix=m.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(gain,gain*.985,gain*.98,1)
  m.node_tree.links.new(old,mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],em.inputs[0])
 m['190 role']=label;m['190 only native recess faces']=True;return m

def inventory(C):
 dg=bpy.context.evaluated_depsgraph_get();vs=[];tris=[];walls=[]
 for ob in C.all_objects:
  if ob.type!='MESH' or ob.hide_render or ob.name.startswith('190 '):continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(vs);vs.extend(ob.matrix_world@v.co for v in me.vertices);tris.extend(tuple(base+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
  if 'continuous arcade wall'in ob.name or ob.get('coliseum_role')=='wall'and ob.get('tier')==3 and ('fractured upper wall'in ob.name or 'aperture head'in ob.name):walls.append(ob)
 return BVHTree.FromPolygons(vs,tris,all_triangles=True),sorted(walls,key=lambda x:x.name)

def visible(p,tree,s,dg):
 camera=s.camera.matrix_world.translation;d=p-camera;hit=tree.ray_cast(camera,d.normalized(),d.length+.1)
 if hit[0] is None or (hit[0]-p).length>.06:return False
 # Verify actual scene visibility too, while treating atmospheric volumes as transparent.
 start=camera.copy();direction=d.normalized()
 for _ in range(20):
  ok,loc,n,face,ob,matrix=s.ray_cast(dg,start,direction,distance=(p-start).length+.05)
  if not ok:return True
  if (loc-p).length<.07:return True
  name=ob.name.lower()
  if any(t in name for t in ['haze','cloud','sky','fog','dust','ink']):start=loc+direction*.10;continue
  return False
 return False

def point_in(p,poly):
 x,y=p;inside=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside

def dist_edge(p,poly):
 p=Vector(p);best=1e10
 for aa,bb in zip(poly,poly[1:]+poly[:1]):
  a,b=Vector(aa),Vector(bb);d=b-a;t=max(0,min(1,(p-a).dot(d)/max(d.length_squared,1e-12)));best=min(best,(p-a-t*d).length)
 return best

def lobes(p,n,rng,cfg):
 u,v=basis(n);ru=rng.uniform(*cfg['lobe_radius_horizontal_m']);rv=rng.uniform(*cfg['lobe_radius_vertical_m']);orientation=rng.choice([0,0,0,math.pi/2]);a=u*math.cos(orientation)+v*math.sin(orientation);b=-u*math.sin(orientation)+v*math.cos(orientation)
 loops=[]
 for j in range(rng.choice([2,3,3])):
  center=p+a*(j-(1 if j else 0))*ru*.64+b*rng.uniform(-.24,.24)
  sx=ru*rng.uniform(.7,1.0);sy=rv*rng.uniform(.65,1.05);coords=[]
  for k in range(15):
   t=math.tau*k/15;f=rng.uniform(.57,1.18);coords.append((math.cos(t)*sx*f,math.sin(t)*sy*f))
  loops.append({'center':center,'u':a,'v':b,'outer':coords,'inner':[(x*.64,y*.64)for x,y in coords],'depth':rng.uniform(*cfg['v2_recess_depth_m'])})
 return loops

def bary(p,a,b,c):
 v0=b-a;v1=c-a;v2=p-a;den=v0.x*v1.y-v1.x*v0.y
 if abs(den)<1e-15:return None
 w1=(v2.x*v1.y-v1.x*v2.y)/den;w2=(v0.x*v2.y-v2.x*v0.y)/den;return (1-w1-w2,w1,w2)

def readvalue(item,typ):
 if typ in ['FLOAT_VECTOR']:return tuple(item.vector)
 if typ in ['FLOAT_COLOR','BYTE_COLOR']:return tuple(item.color)
 if typ=='FLOAT2':return tuple(item.vector)
 if typ in ['INT','FLOAT','BOOLEAN']:return item.value
 return None

def writevalue(item,typ,val):
 if typ in ['FLOAT_VECTOR','FLOAT2']:item.vector=val
 elif typ in ['FLOAT_COLOR','BYTE_COLOR']:item.color=val
 elif typ in ['INT','FLOAT','BOOLEAN']:item.value=val

def interpolate(values,weights,typ):
 if typ in ['INT','BOOLEAN']:return values[max(range(len(weights)),key=lambda i:weights[i])]
 if isinstance(values[0],tuple):return tuple(sum(v[k]*w for v,w in zip(values,weights))for k in range(len(values[0])))
 return sum(v*w for v,w in zip(values,weights))

def rebuild(ob,groups,cfg,material_cache):
 src=ob.data;src.calc_loop_triangles();matrix=ob.matrix_world;inverse=matrix.inverted();normalmatrix=matrix.to_3x3().inverted().transposed();verts=[v.co.copy()for v in src.vertices];wverts=[matrix@v.co for v in src.vertices]
 edge_vertex_cache={};source_edge_lookup={tuple(sorted(e.vertices)):e.index for e in src.edges}
 faces=[];parents=[];mi=[];weights=[[(i,1.)]for i in range(len(verts))];corner_weights=[];depths=[0.]*len(verts);matlist=[sl.material for sl in ob.material_slots];newslots={};face_records=[]
 for poly in src.polygons:
  source_indices=list(poly.vertices);wn=(normalmatrix@poly.normal).normalized();center=matrix@poly.center;u,v=basis(wn) if abs(wn.z)<.9 else (Vector((1,0,0)),Vector((0,1,0)))
  relevant=[]
  if abs(wn.z)<.28:
   for group in groups:
    if wn.dot(group['normal'])>.985:
     for lobe in group['lobes']:
      if (lobe['center']-center).length<max((p-center).length for p in [wverts[i]for i in source_indices])+5.5 and abs((lobe['center']-center).dot(wn))<.12:relevant.append(lobe)
  if not relevant:
   faces.append(source_indices);parents.append(poly.index);mi.append(poly.material_index);corner_weights.extend([[(li,1.)]for li in poly.loop_indices]);continue
  origin=wverts[source_indices[0]];xy=[Vector(((wverts[i]-origin).dot(u),(wverts[i]-origin).dot(v)))for i in source_indices];edges=[];base_count=len(xy);projected=[]
  for lobe in relevant:
   polys=[]
   for key in ['outer','inner']:
    coords=[Vector(((lobe['center']+lobe['u']*x+lobe['v']*y-origin).dot(u),(lobe['center']+lobe['u']*x+lobe['v']*y-origin).dot(v)))for x,y in lobe[key]];start=len(xy);xy.extend(coords);edges.extend((start+j,start+(j+1)%len(coords))for j in range(len(coords)));polys.append([tuple(q)for q in coords])
   projected.append((polys[0],polys[1],lobe['depth']))
  try:out,oe,of,ov,_,ofids=delaunay_2d_cdt(xy,edges,[tuple(range(base_count))],1,1e-6,True)
  except Exception as ex:raise RuntimeError('CDT '+ob.name+' '+str(poly.index))from ex
  triang=[t for t in src.loop_triangles if t.polygon_index==poly.index];localmap={};localweights={};newdepth={};boundary=[tuple(x)for x in xy[:base_count]]
  for oi,q in enumerate(out):
   originals=[i for i in ov[oi]if i<base_count]
   if originals:idx=source_indices[originals[0]];localmap[oi]=idx;localweights[oi]=[(poly.loop_start+originals[0],1.)];newdepth[oi]=0.;continue
   winner=None;penalty=1e10
   for tri in triang:
    txy=[Vector(((wverts[i]-origin).dot(u),(wverts[i]-origin).dot(v)))for i in tri.vertices];ww=bary(q,*txy)
    if ww is not None:
     score=sum(max(0,-w)for w in ww)
     if score<penalty:penalty=score;winner=(tri,ww)
   if winner is None:continue
   tri,ww=winner;ww=[max(0,w)for w in ww];total=sum(ww);ww=[w/total for w in ww]
   wp=sum((wverts[i]*w for i,w in zip(tri.vertices,ww)),Vector());depth=0.
   # Keep all original face boundaries exact. Only interior native surface is recessed.
   edgefade=min(1,dist_edge(q,boundary)/.08)
   for outer,inner,dep in projected:
    if point_in(q,inner):depth=max(depth,dep*edgefade)
    elif point_in(q,outer):depth=max(depth,dep*min(1,dist_edge(q,outer)/.22)*edgefade)
   nonzero=[(i,w)for i,w in zip(tri.vertices,ww)if w>1e-6];key=None
   if depth<1e-8 and len(nonzero)==2 and tuple(sorted(i for i,w in nonzero))in source_edge_lookup:
    pair=sorted(nonzero);key=(pair[0][0],pair[1][0],round(pair[1][1],6))
   idx=edge_vertex_cache.get(key)if key else None
   if idx is None:
    idx=len(verts);verts.append(inverse@(wp-wn*depth));weights.append(list(zip(tri.vertices,ww)));depths.append(depth)
    if key:edge_vertex_cache[key]=idx
   localmap[oi]=idx;localweights[oi]=list(zip(tri.loops,ww));newdepth[oi]=depth
  count=0;cutarea=0.
  for f,ids in zip(of,ofids):
   if 0 not in ids or any(i not in localmap for i in f):continue
   pts=[localmap[i]for i in f]
   if len(set(pts))<3:continue
   dep=sum(newdepth[i]for i in f)/len(f);slot=poly.material_index
   if dep>.018:
    base=matlist[slot];key=base.name
    if key not in newslots:
     if key not in material_cache:material_cache[key]=[substrate(base,'fractured rim v2',cfg['rim_gain']),substrate(base,'crumbled substrate v2',cfg['substrate_gain'])]
     newslots[key]=[len(matlist),len(matlist)+1];matlist.extend(material_cache[key])
    slot=newslots[key][1 if dep>.07 else 0];count+=1
   faces.append(pts);parents.append(poly.index);mi.append(slot);corner_weights.extend(localweights[i]for i in f)
  face_records.append({'source_face':poly.index,'cut_triangles':count})
 me=bpy.data.meshes.new('190 Local recessed surface '+ob.name);me.from_pydata(verts,[],faces);me.update()
 for mat in matlist:me.materials.append(mat)
 for f,p,m in zip(me.polygons,parents,mi):f.material_index=m;f.use_smooth=src.polygons[p].use_smooth
 # Copy all supported named mesh attributes with explicit parent/barycentric provenance.
 for attr in src.attributes:
  if attr.name in ['position','.edge_verts','.corner_vert','.corner_edge'] or attr.is_internal:continue
  typ=attr.data_type;dom=attr.domain
  if typ not in ['FLOAT_VECTOR','FLOAT_COLOR','BYTE_COLOR','FLOAT2','INT','FLOAT','BOOLEAN']or dom not in ['POINT','FACE','CORNER']:continue
  dest=me.attributes.get(attr.name)or me.attributes.new(attr.name,typ,dom)
  if dom=='FACE':
   for i,p in enumerate(parents):writevalue(dest.data[i],typ,readvalue(attr.data[p],typ))
  else:
   sourceweights=weights if dom=='POINT'else corner_weights
   for i,wts in enumerate(sourceweights):writevalue(dest.data[i],typ,interpolate([readvalue(attr.data[k],typ)for k,w in wts],[w for k,w in wts],typ))
 # Preserve original edge attributes/ink marks, including subdivided old boundaries.
 edgeparents=[]
 for edge in me.edges:
  key=tuple(sorted(edge.vertices));old=source_edge_lookup.get(key)
  if old is None:
   ids={i for vi in edge.vertices for i,w in weights[vi]if w>1e-6}
   if len(ids)==2:old=source_edge_lookup.get(tuple(sorted(ids)))
  edgeparents.append(old)
  if old is not None:edge.use_freestyle_mark=src.edges[old].use_freestyle_mark
 for attr in src.attributes:
  if attr.domain!='EDGE' or attr.is_internal or attr.data_type not in ['FLOAT','INT','BOOLEAN','FLOAT_VECTOR']:continue
  dest=me.attributes.get(attr.name)or me.attributes.new(attr.name,attr.data_type,'EDGE')
  for i,old in enumerate(edgeparents):
   if old is not None:writevalue(dest.data[i],attr.data_type,readvalue(attr.data[old],attr.data_type))
 oldnormals=[tuple(n.vector)for n in src.corner_normals];newnormals=[]
 for f,p,m in zip(me.polygons,parents,mi):
  for li in f.loop_indices:
   if m>=len(ob.material_slots):newnormals.append(tuple(f.normal))
   else:newnormals.append(tuple(Vector(interpolate([oldnormals[k]for k,w in corner_weights[li]],[w for k,w in corner_weights[li]],'FLOAT_VECTOR')).normalized()))
 me.normals_split_custom_set(newnormals)
 provenance=me.attributes.new('190 Source face identity','INT','FACE')
 for i,p in enumerate(parents):provenance.data[i].value=p
 # Reassign explicit material indices after named attributes, which include material_index.
 for f,m in zip(me.polygons,mi):f.material_index=m
 archive=src.copy();archive.name='190 SOURCE '+ob.name;archive.use_fake_user=True
 source_indices=[f.material_index for f in archive.polygons];archive.materials.clear()
 for mat in matlist[:len(ob.material_slots)]:archive.materials.append(mat)
 for f,slot in zip(archive.polygons,source_indices):f.material_index=slot
 ob.data=me
 for sl in ob.material_slots:sl.link='DATA'
 ob['190 source mesh']=archive.name;ob['190 local face method']=True
 return {'object':ob.name,'before':[len(src.vertices),len(src.polygons)],'after':[len(me.vertices),len(me.polygons)],'affected_source_faces':face_records,'original_vertex_positions_exact':all((me.vertices[i].co-src.vertices[i].co).length==0 for i in range(len(src.vertices))),'original_boundary_vertices_preserved':True,'material_names':[m.name if m else None for m in matlist]}

def apply(C,config=None):
 cfg=config or json.loads((R/'config/colosseum-crumbling-190.json').read_text())
 if any(o.get('190 local face method')for o in C.all_objects):raise RuntimeError('Apply to fresh source only')
 tree,walls=inventory(C);rng=random.Random(cfg['seed']);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();camera=s.camera.matrix_world.translation;groups=[];bywall={};checks=0
 for ob in walls:
  src=ob.data;src.calc_loop_triangles();normalmatrix=ob.matrix_world.to_3x3().inverted().transposed();ts=[];areas=[]
  for t in src.loop_triangles:
   poly=src.polygons[t.polygon_index];mat=ob.material_slots[poly.material_index].material if poly.material_index<len(ob.material_slots)else None;n=(normalmatrix@poly.normal).normalized();ps=[ob.matrix_world@src.vertices[i].co for i in t.vertices];p=sum(ps,Vector())/3
   if not mat or any(z in mat.name.lower()for z in ['depth','shade','joint','core'])or abs(n.z)>.28 or n.dot((camera-p).normalized())<.3:continue
   area=(ps[1]-ps[0]).cross(ps[2]-ps[0]).length/2
   if area>.08:ts.append((ps,n,poly.index));areas.append(area)
  if not ts:continue
  arcade='continuous arcade wall'in ob.name;desired=cfg.get('visible_arcade_groups',7)if arcade else 1;accepted=[]
  for attempt in range(desired*240):
   if len(accepted)>=desired:break
   (a,b,c),n,fi=rng.choices(ts,weights=areas,k=1)[0];f=math.sqrt(rng.random());g=rng.random();p=a*(1-f)+b*f*(1-g)+c*f*g
   if any((p-q['center']).length<4.3 for q in accepted):continue
   checks+=1
   if not visible(p,tree,s,dg):continue
   nd=world_to_camera_view(s,s.camera,p)
   if not(0<nd.x<1 and 0<nd.y<1):continue
   group={'center':p,'normal':n,'lobes':lobes(p,n,rng,cfg),'owner':ob.name,'tier':int(ob.get('tier',3)),'bay':int(ob.get('bay',-1)),'source_face':fi,'projected_pixel_4k':[nd.x*3840,(1-nd.y)*2885]};accepted.append(group);groups.append(group)
  if accepted:bywall[ob.name]=accepted
 print('190 V2 VISIBLE GROUPS',len(groups),'CHECKS',checks,flush=True)
 materials={};audit=[]
 for ob in walls:
  if ob.name not in bywall:continue
  row=rebuild(ob,bywall[ob.name],cfg,materials);audit.append(row);print('190 V2 WALL',ob.name,len(bywall[ob.name]),row['after'],flush=True)
 serial=[{k:([list(vv)for vv in v]if k=='unused'else list(v)if isinstance(v,Vector)else v)for k,v in g.items()if k!='lobes'}|{'lobes':[{'center':list(l['center']),'u':list(l['u']),'v':list(l['v']),'outer':l['outer'],'inner':l['inner'],'depth':l['depth']}for l in g['lobes']]}for g in groups]
 return {'version':2,'source':'188','method':'Face-local constrained triangulation with actual recessed interiors and exact unchanged original vertices/boundaries. No global Boolean.','groups':serial,'group_count':len(groups),'changed_walls':audit,'camera_verified_visibility':True,'material_provenance':'Every output face carries its exact original face identity; undamaged faces use the exact effective source material.','review_status':'CPU build; native visual proof pending','user_approved':False}


def replay(C):
 """Apply the frozen v2 meshes after visual review; no camera-dependent re-placement.
 Intended for root integration into192 while preserving its ink/compositing setup.
 """
 import array,hashlib
 def meshhash(me):
  a=array.array('f',[0.])*(len(me.vertices)*3);me.vertices.foreach_get('co',a);b=array.array('i',[0])*len(me.loops);me.loops.foreach_get('vertex_index',b);c=array.array('i',[0])*len(me.polygons);me.polygons.foreach_get('loop_total',c);return hashlib.sha256(a.tobytes()+b.tobytes()+c.tobytes()).hexdigest()
 meta=json.loads((O/'payload-v2.json').read_text());targets={name:C.all_objects.get(name)for name in meta}
 for name,ob in targets.items():
  assert ob and not ob.get('190 local face method'),'190 requires untouched source '+name
  assert meshhash(ob.data)==meta[name]['source_hash'],'190 source geometry mismatch '+name
  assert [list(r)for r in ob.matrix_world]==meta[name]['matrix'],'190 transform mismatch '+name
  assert [sl.material.name if sl.material else None for sl in ob.material_slots]==meta[name]['source_materials'],'190 source materials mismatch '+name
 mesh_names=[meta[n]['mesh_name']for n in meta];archive_names=[meta[n]['archive_mesh']for n in meta]
 with bpy.data.libraries.load(str(O/'payload-v2.blend'),link=False)as(src,dst):dst.meshes=mesh_names+archive_names
 meshes=dst.meshes[:len(meta)];archives=dst.meshes[len(meta):]
 for (name,row),me,archive in zip(meta.items(),meshes,archives):
  ob=targets[name];actual=list(me.materials);face_slots=[f.material_index for f in me.polygons];materials=[]
  for expected,imported in zip(row['materials'],actual):materials.append(imported if expected and expected.startswith('190 ')else bpy.data.materials[expected]if expected else None)
  me.materials.clear()
  for mat in materials:me.materials.append(mat)
  for f,slot in zip(me.polygons,face_slots):f.material_index=slot
  ob.data=me
  for sl in ob.material_slots:sl.link='DATA'
  archive.use_fake_user=True;ob['190 source mesh']=archive.name;ob['190 local face method']=True
  assert meshhash(me)==row['candidate_hash'],'190 replay mismatch '+name
 return {'version':2,'fixed_payload':True,'targets':list(meta),'camera_lights_render_layers_compositor_unchanged':True,'source':'190/candidate-v2.blend','material_provenance':'native-audit-v2.json'}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));t=time.time();audit=apply(bpy.data.collections['110 Coliseum detailed front ruin']);audit['build_seconds']=time.time()-t;(O/'build-audit-v2.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate-v2.blend'))
