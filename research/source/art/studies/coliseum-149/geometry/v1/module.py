"""Bounded native inward cornice loss beside Tower7; source147, no detached debris."""
import bpy,bmesh,time
from mathutils import Vector,geometry
from coliseum_crown_repair_123 import topology
NAMES=['COL110 U9 fractured upper wall L']
def apply(C):
 dg=bpy.context.evaluated_depsgraph_get();out=[]
 for idx,name in enumerate(NAMES):
  ob=C.objects[name];old=ob.data;ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.name='149 '+old.name;M=ob.matrix_world.copy();iv=M.inverted();src=[v.co.copy()for v in me.vertices];me.calc_loop_triangles();tris=[tuple(t.vertices)for t in me.loop_triangles];orig=[v.vector.copy()for v in me.attributes['115 Original world position'].data];norms={tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices)):{tuple(me.vertices[me.loops[k].vertex_index].co):me.corner_normals[k].vector.copy()for k in f.loop_indices}for f in me.polygons}
  tmp=bpy.data.objects.new('149 temporary evaluated',me);C.objects.link(tmp);tmp.matrix_world=M;before=topology(tmp)
  if before['nonmanifold']or before['strict_crossings']:raise RuntimeError('Unsafe source '+name+str(before))
  # Broad under-crown strip with one longer shoulder beside the retained niche.
  profile=[(3.66,47.93),(3.70,50.56),(4.28,50.62),(5.20,50.56),(5.43,50.62),(6.79,50.58),(6.76,49.89),(5.10,49.94),(4.76,49.62),(4.60,48.04),(4.03,47.84)]
  vs=[]
  for rear in [False,True]:
   for x,z in profile:
    back=195.95+.465*x+.09*(z-49.5)+.48
    w=Vector((x,back if rear else 194,z));vs.append(iv@w)
  n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(k,(k+1)%n,(k+1)%n+n,k+n)for k in range(n)]
  cm=bpy.data.meshes.new('149 convex inward cutter');cm.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();co=bpy.data.objects.new('149 cutter',cm);C.objects.link(co);co.matrix_world=M
  mod=tmp.modifiers.new('149 inward missing cornice facing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;tmp.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True)
  # One shallow irregular secondary ledge inside the broad exposed plane.
  step=[(4.69,50.08),(4.80,50.43),(5.48,50.45),(6.42,50.36),(6.46,50.14),(5.71,50.03)]
  vv=[iv@Vector((x,195.95+.465*x+.09*(z-49.5)+(.62 if rear else -.5),z))for rear in [False,True]for x,z in step];nn=len(step);ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,nn*2))]+[(k,(k+1)%nn,(k+1)%nn+nn,k+nn)for k in range(nn)];sm=bpy.data.meshes.new('149 shallow step cutter');sm.from_pydata(vv,[],ff);bb=bmesh.new();bb.from_mesh(sm);bmesh.ops.recalc_face_normals(bb,faces=list(bb.faces));bb.to_mesh(sm);bb.free();cc=bpy.data.objects.new('149 step cutter',sm);C.objects.link(cc);cc.matrix_world=M;mm=tmp.modifiers.new('149 single shallow fracture step','BOOLEAN');mm.operation='DIFFERENCE';mm.solver='EXACT';mm.object=cc;bpy.ops.object.modifier_apply(modifier=mm.name);bpy.data.objects.remove(cc,do_unlink=True);me=tmp.data;me.update();after=topology(tmp)
  if after['nonmanifold']or after['strict_crossings']or not 0<after['volume']<before['volume']:raise RuntimeError('Rejected cornice cut '+name+str(after))
  attrs=me.attributes;aa=attrs.get('115 Original world position');tag=attrs.get('149 Exposed crown core')or attrs.new('149 Exposed crown core','FLOAT','FACE');retained=set(tuple(v)for v in src);changed=[]
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
  bpy.data.objects.remove(tmp,do_unlink=True);ob['149 crown loss']='Under-crown inward loss; outer boundary unchanged';out.append({'object':name,'before':before,'after':after,'new_vertices_world':changed,'retained_old_vertices':sum(tuple(v.co)in retained for v in me.vertices),'original_vertex_count':len(src),'outward_added_geometry':False,'existing_materials_preserved':True,'new_core_original_bounds':[[min(aa.data[v.index].vector[k]for v in me.vertices if tuple(v.co)not in retained),max(aa.data[v.index].vector[k]for v in me.vertices if tuple(v.co)not in retained)]for k in range(3)]})
 return {'targets':out,'scope':'One U9L existing crown face; silhouette, openings, niche trim and other objects unchanged','source':'148 accepted working baseline','references':['UCL-01','UCL-02','DP-03']}
