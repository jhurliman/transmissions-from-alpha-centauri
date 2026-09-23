"""Bounded native inward cornice loss beside Tower7; source147, no detached debris."""
import bpy,bmesh,time
from mathutils import Vector,geometry
from coliseum_crown_repair_123 import topology
NAMES=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L']
TARGETS=NAMES
from coliseum_arch_ratio_125 import mapping
from mathutils.bvhtree import BVHTree
def apply(C):
 dg=bpy.context.evaluated_depsgraph_get();out=[]
 for idx,name in enumerate(NAMES):
  ob=C.objects[name];old=ob.data;ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.name='149 '+old.name;M=ob.matrix_world.copy();iv=M.inverted();src=[v.co.copy()for v in me.vertices];me.calc_loop_triangles();tris=[tuple(t.vertices)for t in me.loop_triangles];orig=[v.vector.copy()for v in me.attributes['115 Original world position'].data];norms={tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices)):{tuple(me.vertices[me.loops[k].vertex_index].co):me.corner_normals[k].vector.copy()for k in f.loop_indices}for f in me.polygons}
  tmp=bpy.data.objects.new('149 temporary evaluated',me);C.objects.link(tmp);tmp.matrix_world=M;before=topology(tmp)
  if before['nonmanifold']or before['strict_crossings']:raise RuntimeError('Unsafe source '+name+str(before))
  original,world,unpack=mapping()
  def cut(profile,rear):
   # Closed native cutter entirely outside/inside existing wall; DIFFERENCE only.
   vv=[iv@world(rr,-2.3194+u/75,z)for rr in [rear,79.]for u,z in profile];nn=len(profile)
   ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,nn*2))]+[(k,(k+1)%nn,(k+1)%nn+nn,k+nn)for k in range(nn)]
   cm=bpy.data.meshes.new('151 subtractive stepped cutter');cm.from_pydata(vv,[],ff);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();co=bpy.data.objects.new('151 temporary cutter',cm);C.objects.link(co);co.matrix_world=M
   mod=tmp.modifiers.new('151 existing crown loss','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;tmp.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True)
  cut([(.45,71.35),(.72,70.55),(2.8,70.80),(3.8,72.20),(4.35,73.75),(5.50,73.75),(6.2,71.55),(7.0,69.4),(8.7,69.6),(9.10,70.2),(9.10,79),(.45,79)],73.0)
  # Unequal short deeper course losses, open through the same existing crest.
  cut([(1.10,72.5),(1.32,72.05),(3.2,72.20),(3.55,72.65),(3.55,79),(1.10,79)],71.85)
  cut([(6.30,72.10),(6.60,71.60),(8.25,71.80),(8.25,79),(6.30,79)],72.05)
  me=tmp.data;me.update();after=topology(tmp)
  if after['nonmanifold']or after['strict_crossings']or not 0<after['volume']<before['volume']:raise RuntimeError('Rejected cornice cut '+name+str(after))
  source_tree=BVHTree.FromPolygons(src,tris,all_triangles=True);me.calc_loop_triangles();envelope_samples=[v.co.copy()for v in me.vertices]+[sum((me.vertices[i].co for i in t.vertices),Vector())/3 for t in me.loop_triangles];positive=[]
  for p in envelope_samples:
   near,normal,face,distance=source_tree.find_nearest(p)
   if distance>1e-5 and (p-near).dot(normal)>1e-5:positive.append(float((p-near).dot(normal)))
  if max(positive,default=0)>1e-4:raise RuntimeError('Source envelope tolerance exceeded '+name+str(max(positive)))
  result_tree=BVHTree.FromPolygons([v.co.copy()for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True);lower_errors=[result_tree.find_nearest(p)[3]for p in src if unpack(M@p)[2]<67.8]
  attrs=me.attributes;aa=attrs.get('115 Original world position');tag=attrs.get('151 Exposed crown core')or attrs.new('151 Exposed crown core','FLOAT','FACE');retained=set(tuple(v)for v in src);changed=[]
  for v in me.vertices:
   if tuple(v.co)in retained:continue
   tri=min(tris,key=lambda t:(geometry.closest_point_on_tri(v.co,*[src[k]for k in t])-v.co).length_squared);pt=geometry.closest_point_on_tri(v.co,*[src[k]for k in tri]);aa.data[v.index].vector=geometry.barycentric_transform(pt,*[src[k]for k in tri],*[orig[k]for k in tri]);changed.append(list(M@v.co))
  coremat=next((ma for q in C.all_objects if q.type=='MESH'for ma in q.data.materials if ma and ma.name.startswith('117 Exposed masonry core')),None)
  if coremat:me.materials.append(coremat)
  core=attrs.get('117 Exposed core')or attrs.new('117 Exposed core','FLOAT','FACE')
  custom=[x.vector.copy()for x in me.corner_normals]
  for f in me.polygons:
   key=tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices));center=sum((me.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);distance=min((geometry.closest_point_on_tri(center,*[src[k]for k in t])-center).length for t in tris);exposed=distance>1e-4;tag.data[f.index].value=float(exposed);core.data[f.index].value=1. if exposed else core.data[f.index].value
   if exposed and coremat:f.material_index=len(me.materials)-1
   for li in f.loop_indices:
    q=tuple(me.vertices[me.loops[li].vertex_index].co);custom[li]=norms[key][q]if key in norms else f.normal.copy()
  me.normals_split_custom_set(custom);ob.data=me
  for mod in list(ob.modifiers):ob.modifiers.remove(mod)
  bpy.data.objects.remove(tmp,do_unlink=True);ob['151 crown loss']='Subtractive front skin and two short course returns; no raised rear mass';out.append({'object':name,'before':before,'after':after,'new_vertices_world':changed,'retained_old_vertices':sum(tuple(v.co)in retained for v in me.vertices),'original_vertex_count':len(src),'constructive_additions':0,'boolean_operation':'DIFFERENCE only','source_envelope_max_outward_local':max(positive,default=0),'source_envelope_tolerance_local':1e-4,'source_envelope_samples':len(envelope_samples),'removed_volume':before['volume']-after['volume'],'lower_source_vertex_surface_max_error':max(lower_errors,default=0),'existing_materials_preserved':True,'new_core_original_bounds':[[min(aa.data[v.index].vector[k]for v in me.vertices if tuple(v.co)not in retained),max(aa.data[v.index].vector[k]for v in me.vertices if tuple(v.co)not in retained)]for k in range(3)]})
 return {'targets':out,'scope':'Two existing U4R/U5L crown skins, subtractive only; no added mass or remeshed heightfield','source':'149 accepted working baseline','references':['UCL-01','UCL-02','DP-03']}
