"""Real shallow V-joints between arch crowns and their supported cornice undersides."""
import bpy,bmesh,math,time
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping

def apply(C,bays=None,tiers=None,width=.19,depth=.16,ink_radius=.027):
 if any(o.get('131 crown masonry joints')for o in C.objects):raise RuntimeError('Crown joints already applied')
 original,world,unpack=mapping();records=[];skipped=[];started=time.time();inkpaths=[]
 for tier in (range(3)if tiers is None else tiers):
  wall=C.objects.get(f'COL127 T{tier} continuous arcade wall')
  if wall is None:continue
  old=wall.data;coords=[wall.matrix_world@v.co for v in old.vertices];tree=BVHTree.FromPolygons(coords,[tuple(p.vertices)for p in old.polygons]);specs=[]
  for bay in (range(18)if bays is None else bays):
   stones=[o for o in C.objects if o.type=='MESH'and o.name.startswith(f'COL110 T{tier} B{bay:02d} archivolt1 stone')]
   band=C.objects.get(f'COL110 T{tier} band{bay:02d} profile0')
   if not stones or band is None:continue
   ac=-math.pi+(bay+.5)*math.tau/36
   crown=max(unpack(o.matrix_world@v.co)[2]for o in stones for v in o.data.vertices);top=min(unpack(band.matrix_world@v.co)[2]for v in band.data.vertices)
   if top-crown<.2:skipped.append({'tier':tier,'bay':bay,'reason':'No intact crown-to-band interval'});continue
   supported=True
   for t in [0,.2,.4,.6,.8,1]:
    z=crown+(top-crown)*t;p=world(76,ac,z);d=(world(74,ac,z)-p).normalized();hit=tree.ray_cast(p,d)
    if hit[0]is None or abs(unpack(hit[0])[0]-75)>.06:supported=False;break
   if not supported:skipped.append({'tier':tier,'bay':bay,'reason':'Existing missing wall along proposed joint'});continue
   specs.append({'tier':tier,'bay':bay,'angle':ac,'bottom':crown-.025,'top':top+.025,'visible_bottom':crown,'visible_top':top})
  if not specs:continue
  # Disjoint cutters in one boolean avoid repeated re-triangulation of the wall.
  vs=[];fs=[];outside=.3;half=width/2*(outside+depth)/depth
  for q in specs:
   n=len(vs)
   for z in [q['bottom'],q['top']]:
    vs.extend(world(r,q['angle']+u/75,z)for r,u in [(75+outside,-half),(75+outside,half),(75-depth,0)])
   fs.extend(tuple(n+i for i in f)for f in [(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
  cm=bpy.data.meshes.new('131 Crown joint cutters');cm.from_pydata(vs,[],fs);cm.update();bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();cut=bpy.data.objects.new(cm.name,cm);C.objects.link(cut)
  temporary=wall.copy();temporary.data=old.copy();temporary.modifiers.clear();C.objects.link(temporary);mod=temporary.modifiers.new('131 Shallow centered masonry joints','BOOLEAN');mod.object=cut;mod.operation='DIFFERENCE';mod.solver='EXACT';bpy.context.view_layer.objects.active=temporary;bpy.ops.object.modifier_apply(modifier=mod.name)
  me=temporary.data;bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.free()
  if bad or volume<=0:raise RuntimeError(f'Invalid crown joint topology tier{tier}: {bad} / {volume}')
  # Preserve material and split normals on unchanged polygons exactly.
  def key(v):return tuple(round(float(x),5)for x in v)
  prior={tuple(sorted(key(old.vertices[i].co)for i in p.vertices)):{key(old.vertices[old.loops[li].vertex_index].co):old.corner_normals[li].vector.copy()for li in p.loop_indices}for p in old.polygons}
  # Exact Boolean may rotate unchanged n-gon loops, altering Blender's tessellation.
  # Restore source cyclic order to prevent numerical folds at inherited pier feet.
  prior_order={tuple(sorted(key(old.vertices[i].co)for i in p.vertices)):[key(old.vertices[i].co)for i in p.vertices]for p in old.polygons}
  edge_index={tuple(sorted(e.vertices)):e.index for e in me.edges};rotated=0
  for p in me.polygons:
   pk=tuple(sorted(key(me.vertices[i].co)for i in p.vertices))
   if pk not in prior_order:continue
   current={key(me.vertices[me.loops[li].vertex_index].co):(me.loops[li].vertex_index,li)for li in p.loop_indices};order=prior_order[pk]
   if [key(me.vertices[i].co)for i in p.vertices]==order:continue
   corner=[]
   for attribute in me.attributes:
    if attribute.domain!='CORNER' or attribute.name.startswith('.'):continue
    prop=next((q for q in ('vector','color','value')if len(attribute.data)and hasattr(attribute.data[0],q)),None)
    if prop:
     vals={k:getattr(attribute.data[li],prop) for k,(vi,li)in current.items()}
     vals={k:v.copy()if hasattr(v,'copy')else v for k,v in vals.items()};corner.append((attribute,prop,vals))
   ids=[current[k][0]for k in order]
   for j,li in enumerate(p.loop_indices):
    me.loops[li].vertex_index=ids[j];me.loops[li].edge_index=edge_index[tuple(sorted((ids[j],ids[(j+1)%len(ids)])))]
    for attribute,prop,vals in corner:setattr(attribute.data[li],prop,vals[order[j]])
   rotated+=1
  me.update()
  at=me.attributes.get('131 Crown joint interior')or me.attributes.new('131 Crown joint interior','FLOAT','FACE');normals=[];groovefaces=0;unchanged=0
  auth={v.index:unpack(wall.matrix_world@v.co)for v in me.vertices}
  for p in me.polygons:
   pk=tuple(sorted(key(me.vertices[i].co)for i in p.vertices));existing=prior.get(pk)
   if existing is not None:unchanged+=1
   rr=[auth[i][0]for i in p.vertices];aa=sum(auth[i][1]for i in p.vertices)/len(p.vertices);zz=sum(auth[i][2]for i in p.vertices)/len(p.vertices)
   inside=any(abs((aa-q['angle'])*75)<half+.03 and q['bottom']-.01<zz<q['top']+.01 for q in specs)and min(rr)<75-depth*.4 and max(rr)>74.95
   if inside:at.data[p.index].value=1;groovefaces+=1;p.use_smooth=False
   for li in p.loop_indices:
    vi=me.loops[li].vertex_index
    if existing is not None:n=existing[key(me.vertices[vi].co)]
    elif not inside and min(rr)>74.93:
     r,a,z=auth[vi];n=(world(r,a+.0001,z)-world(r,a-.0001,z)).cross(world(r,a,z+.01)-world(r,a,z-.01)).normalized()
     if n.dot(p.normal)<0:n=-n
     p.use_smooth=True
    else:n=p.normal.copy()
    normals.append(n)
  me.normals_split_custom_set(normals)
  pos=me.attributes.get('115 Original world position');dep=me.attributes.get('120 Actual arch tunnel depth')
  oldkeys={key(v.co)for v in old.vertices}
  for v in me.vertices:
   if key(v.co)in oldkeys:continue
   r,a,z=auth[v.index]
   if pos:pos.data[v.index].vector=original(r,a,z)
   if dep:dep.data[v.index].value=max(0,min(1,(75-r)/8))
  wall.data=me;bpy.data.objects.remove(temporary,do_unlink=True);bpy.data.objects.remove(cut,do_unlink=True);wall['131 crown masonry joints']=True
  # Tiny physical ink core follows the real recessed seam; evaluated layout stays exact.
  raw=[]
  for q in specs:
   for z in [q['visible_bottom'],q['visible_top']]:raw.append(wall.matrix_world.inverted()@world(74.998,q['angle'],z))
  probe=wall.copy();pm=bpy.data.meshes.new('131 Ink coordinate probe');pm.from_pydata(raw,[],[]);probe.data=pm;C.objects.link(probe);bpy.context.view_layer.update();ev=probe.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();pworld=[ev.matrix_world@v.co for v in em.vertices];ev.to_mesh_clear();bpy.data.objects.remove(probe,do_unlink=True)
  for i,q in enumerate(specs):inkpaths.append((pworld[2*i],pworld[2*i+1]));q['evaluated_path_world']=[list(pworld[2*i]),list(pworld[2*i+1])]
  records.append({'tier':tier,'object':wall.name,'paths':specs,'vertices_before':len(old.vertices),'vertices_after':len(me.vertices),'unchanged_polygon_normals_restored':unchanged,'source_polygon_orders_restored':rotated,'joint_faces':groovefaces,'nonmanifold_edges':bad,'volume':volume})
 if inkpaths and ink_radius:
  cu=bpy.data.curves.new('131 Recessed crown joint ink','CURVE');cu.dimensions='3D';cu.bevel_depth=ink_radius;cu.bevel_resolution=1;cu.use_fill_caps=True
  for a,b in inkpaths:
   sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  ob=bpy.data.objects.new(cu.name,cu);C.objects.link(ob);mat=next(m for m in bpy.data.materials if m.library is None and m.name=='130 Dark plum physical rim line');cu.materials.append(mat);ob['131 crown masonry joints']=True;ob['feature']='Physical ink inside genuine shallow V-joints'
 return {'references':['UCL-01','UCL-11','DP-03'],'width_authored_m':width,'depth_authored_m':depth,'ink_radius_world_m':ink_radius,'joint_count':len(inkpaths),'operations':records,'skipped':skipped,'geometry':'Shallow negative V-grooves; no through-wall holes. Existing missing wall intervals skipped.','seconds':time.time()-started}
