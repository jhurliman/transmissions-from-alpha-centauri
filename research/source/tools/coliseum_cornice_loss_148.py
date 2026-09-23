"""Bounded native inward cornice loss beside Tower7; source147, no detached debris."""
import bpy,bmesh,time
from mathutils import Vector,geometry
from coliseum_crown_repair_123 import topology
NAMES=['COL110 T1 band07 profile'+str(i)for i in [1,2,3]]
def apply(C):
 dg=bpy.context.evaluated_depsgraph_get();out=[]
 for idx,name in enumerate(NAMES):
  ob=C.objects[name];old=ob.data;ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.name='148 '+old.name;M=ob.matrix_world.copy();iv=M.inverted();src=[v.co.copy()for v in me.vertices];me.calc_loop_triangles();tris=[tuple(t.vertices)for t in me.loop_triangles];orig=[v.vector.copy()for v in me.attributes['115 Original world position'].data];norms={tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices)):{tuple(me.vertices[me.loops[k].vertex_index].co):me.corner_normals[k].vector.copy()for k in f.loop_indices}for f in me.polygons}
  tmp=bpy.data.objects.new('148 temporary evaluated',me);C.objects.link(tmp);tmp.matrix_world=M;before=topology(tmp)
  if before['nonmanifold']or before['strict_crossings']:raise RuntimeError('Unsafe source '+name+str(before))
  # Coherent offset corners and uneven fracture shoulders, three neighboring courses.
  cx=-10.55;profile=[(-.79,27.30),(-.91,27.65),(-.67,28.05),(-.30,28.43),(.59,28.38),(.86,28.04),(.68,27.55),(.24,27.28)]
  front=187.0;back=193.15+[-.14,.08,-.04][idx];vs=[]
  for rear in [False,True]:
   for x,z in profile:
    x*=1.32
    w=Vector((cx+x,back+.21*x-.16*(z-27.8) if rear else front,z));vs.append(iv@w)
  n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(k,(k+1)%n,(k+1)%n+n,k+n)for k in range(n)]
  cm=bpy.data.meshes.new('148 convex inward cutter');cm.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();co=bpy.data.objects.new('148 cutter',cm);C.objects.link(co);co.matrix_world=M
  mod=tmp.modifiers.new('148 inward missing cornice facing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;tmp.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True);me=tmp.data;me.update();after=topology(tmp)
  if after['nonmanifold']or after['strict_crossings']or not 0<after['volume']<before['volume']:raise RuntimeError('Rejected cornice cut '+name+str(after))
  attrs=me.attributes;aa=attrs.get('115 Original world position');tag=attrs.get('148 Cornice fracture')or attrs.new('148 Cornice fracture','FLOAT','FACE');retained=set(tuple(v)for v in src);changed=[]
  for v in me.vertices:
   if tuple(v.co)in retained:continue
   tri=min(tris,key=lambda t:(geometry.closest_point_on_tri(v.co,*[src[k]for k in t])-v.co).length_squared);pt=geometry.closest_point_on_tri(v.co,*[src[k]for k in tri]);aa.data[v.index].vector=geometry.barycentric_transform(pt,*[src[k]for k in tri],*[orig[k]for k in tri]);changed.append(list(M@v.co))
  coremat=next((ma for q in C.all_objects if q.type=='MESH'for ma in q.data.materials if ma and ma.name.startswith('117 Exposed masonry core')),None)
  if coremat:me.materials.append(coremat)
  core=attrs.get('117 Exposed core')or attrs.new('117 Exposed core','FLOAT','FACE')
  custom=[x.vector.copy()for x in me.corner_normals]
  for f in me.polygons:
   key=tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices));center=sum((me.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);distance=min((geometry.closest_point_on_tri(center,*[src[k]for k in t])-center).length for t in tris);exposed=distance>1e-4;tag.data[f.index].value=float(exposed);core.data[f.index].value=float(exposed)
   if exposed and coremat:f.material_index=len(me.materials)-1
   for li in f.loop_indices:
    q=tuple(me.vertices[me.loops[li].vertex_index].co);custom[li]=norms[key][q]if key in norms else f.normal.copy()
  me.normals_split_custom_set(custom);ob.data=me
  for mod in list(ob.modifiers):ob.modifiers.remove(mod)
  bpy.data.objects.remove(tmp,do_unlink=True);ob['148 cornice loss']='Three-course connected inward loss; no outward displacement';out.append({'object':name,'before':before,'after':after,'new_vertices_world':changed,'retained_old_vertices':sum(tuple(v.co)in retained for v in me.vertices),'original_vertex_count':len(src),'outward_added_geometry':False,'existing_materials_preserved':True})
 return {'targets':out,'scope':'Three cornice profiles only; arches, columns, platforms, wall and tower unchanged','source':'147 actual','references':['UCL-01','UCL-02','DP-03']}
