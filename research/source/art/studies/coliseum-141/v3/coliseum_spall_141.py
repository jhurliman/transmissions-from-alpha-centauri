"""141 V3: one broad U9 facing loss; no geometry outside the source perimeter."""
import bpy,bmesh,time
from mathutils import Vector,geometry
from coliseum_crown_repair_123 import topology
TARGETS=[('COL110 U9 sill wall',34,.12,0)]
def apply(C):
 out=[];dg=bpy.context.evaluated_depsgraph_get()
 for name,index,depth,variant in TARGETS:
  t=time.time();ob=C.objects[name]
  if ob.get('141 damage'):raise RuntimeError('Already applied141spall')
  old=ob.data;e=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg);tmp=bpy.data.objects.new('141 before check',me);tmp.matrix_world=ob.matrix_world;before=topology(tmp);bpy.data.objects.remove(tmp);me.update();face=me.polygons[index]
  if len(face.vertices)!=5:raise RuntimeError('Expected measured five-vertex U9 facing '+name)
  oldnormals={tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices)):{tuple(me.vertices[me.loops[li].vertex_index].co):me.corner_normals[li].vector.copy()for li in f.loop_indices}for f in me.polygons if f.index!=index}
  corners=list(face.vertices);p=[me.vertices[i].co.copy()for i in corners];M=ob.matrix_world;iv=M.inverted();N=(M.to_3x3().inverted().transposed()@face.normal).normalized();dv=iv.to_3x3()@N
  center=sum((M@q for q in p),Vector())/len(p);X=Vector((0,0,1)).cross(N).normalized();Y=N.cross(X).normalized();xy=[Vector(((M@q-center).dot(X),(M@q-center).dot(Y)))for q in p];x0=min(q.x for q in xy);x1=max(q.x for q in xy);y0=min(q.y for q in xy);y1=max(q.y for q in xy)
  def pos(u,v):return iv@(center+X*(x0+u*(x1-x0))+Y*(y0+v*(y1-y0)))
  boundary=[Vector(((q.x-x0)/(x1-x0),(q.y-y0)/(y1-y0)))for q in xy];B=len(boundary)
  ring=[(.10,.08),(.30,.12),(.52,.06),(.83,.10),(.90,.30),(.82,.55),(.91,.83),(.70,.90),(.40,.78),(.12,.88),(.07,.61),(.15,.37)]
  uv=boundary+[Vector(q)for q in ring+[(.38,.43),(.67,.58)]];edges=[(i,(i+1)%B)for i in range(B)]+[(B+i,B+(i+1)%len(ring))for i in range(len(ring))]
  vv,ee,ff,vorig,_,_=geometry.delaunay_2d_cdt(uv,edges,[list(range(B))],1,1e-7,True)
  me.calc_loop_triangles();orig=me.attributes['115 Original world position'];origvals=[d.vector.copy()for d in orig.data];bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();f=bm.faces[index];mat=f.material_index;bmesh.ops.delete(bm,geom=[f],context='FACES_ONLY');mask=bm.faces.layers.int.new('141 Spall exposed core');new=[];newcoords={}
  for j,q in enumerate(vv):
   source=vorig[j];corner=next((k for k in source if k<B),None)
   if corner is not None:new.append(bm.verts[corners[corner]]);continue
   u,v=q;D=depth*(.78+.14*u+.08*v);vtx=bm.verts.new(pos(u,v)-dv*D);new.append(vtx);near=min(me.loop_triangles,key=lambda tri:(geometry.closest_point_on_tri(pos(u,v),*[me.vertices[k].co for k in tri.vertices])-pos(u,v)).length_squared);pt=geometry.closest_point_on_tri(pos(u,v),*[me.vertices[k].co for k in near.vertices]);newcoords[tuple(vtx.co)]=geometry.barycentric_transform(pt,*[me.vertices[k].co for k in near.vertices],*[origvals[k]for k in near.vertices])
  for inds in ff:
   f=bm.faces.new([new[i]for i in inds]);f.material_index=mat;f[mask]=1;f.smooth=False
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();a=me.attributes['115 Original world position'];core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE')
  for v in me.vertices:
   if tuple(v.co)in newcoords:a.data[v.index].vector=newcoords[tuple(v.co)]
  for f in me.polygons:
   if me.attributes['141 Spall exposed core'].data[f.index].value:core.data[f.index].value=1.
  # Retained faces keep their original split normals; new surfaces use actual facet normals.
  normals=[x.vector.copy()for x in me.corner_normals]
  for f in me.polygons:
   key=tuple(sorted(tuple(me.vertices[i].co)for i in f.vertices))
   for li in f.loop_indices:
    coord=tuple(me.vertices[me.loops[li].vertex_index].co)
    normals[li]=oldnormals[key][coord] if key in oldnormals else f.normal.copy()
  me.normals_split_custom_set(normals)
  ob.data=me;mods=list(ob.modifiers)
  for m in mods:m.show_viewport=False;m.show_render=False
  check=topology(ob)
  if check['nonmanifold']or check['strict_crossings']or check['volume']<=0:
   ob.data=old
   for m in mods:m.show_viewport=True;m.show_render=True
   raise RuntimeError('Spall rejected '+name+str(check))
  for m in mods:ob.modifiers.remove(m)
  ob['141 damage']='True shallow facing loss in existing ledge; source perimeter unchanged'
  out.append({'object':name,'source_face':index,'inward_depth_world_m':depth,'new_vertices':len(newcoords),'before_evaluated':before,'after_raw':check,'after_evaluated':check,'outer_boundary_vertices_unchanged':True,'unmodified_original_vertices':len(origvals),'original_position_attribute':'retained/interpolated','new_objects':0,'seconds':time.time()-t})
 return {'references':['UCL-01','UCL-02','DP-03'],'source':'140 native scene','targets':out,'scope':'One broad inward-only U9 facing spall above the existing cornice; all other object geometry unchanged','production_integrated':False}
