"""Three bounded true inset facing losses; no geometry added outside the source envelope."""
import bpy,bmesh,time
from mathutils import Vector,geometry
from coliseum_crown_repair_123 import topology
TARGETS=[('COL110 T2 band08 profile1',3,.11,0),('COL110 T2 band08 profile2',3,.075,1),('COL110 T2 band09 profile2',3,.10,2)]
def apply(C):
 out=[];dg=bpy.context.evaluated_depsgraph_get()
 for name,index,depth,variant in TARGETS:
  t=time.time();ob=C.objects[name];old=ob.data;e=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg);tmp=bpy.data.objects.new('141 before check',me);tmp.matrix_world=ob.matrix_world;before=topology(tmp);bpy.data.objects.remove(tmp);me.update();face=me.polygons[index]
  if len(face.vertices)!=4:raise RuntimeError('Expected clean quad '+name)
  corners=list(face.vertices);p=[me.vertices[i].co.copy()for i in corners];M=ob.matrix_world;iv=M.inverted();N=(M.to_3x3().inverted().transposed()@face.normal).normalized();dv=iv.to_3x3()@N
  # Choose the long edge as the horizontal course direction, independently of polygon ordering.
  if (M.to_3x3()@(p[1]-p[0])).length<(M.to_3x3()@(p[3]-p[0])).length:corners=corners[1:]+corners[:1];p=p[1:]+p[:1]
  def pos(u,v):return p[0]*(1-u)*(1-v)+p[1]*u*(1-v)+p[2]*u*v+p[3]*(1-u)*v
  ring=[(.12,.15),(.36,.12),(.55,.23),(.85,.14),(.91,.43),(.81,.77),(.62,.84),(.43,.74),(.17,.88),(.08,.59)]
  if variant==1:ring=[(.13+.76*u,.08+.83*v)for u,v in ring]
  if variant==2:ring=[(1-u,v)for u,v in ring[::-1]]
  uv=[Vector(x)for x in [(0,0),(1,0),(1,1),(0,1)]+ring+[(.38,.43),(.67,.58)]];edges=[(i,(i+1)%4)for i in range(4)]+[(4+i,4+(i+1)%len(ring))for i in range(len(ring))]
  vv,ee,ff,vorig,_,_=geometry.delaunay_2d_cdt(uv,edges,[list(range(4))],1,1e-7,True)
  orig=me.attributes['115 Original world position'];origvals=[d.vector.copy()for d in orig.data];bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();f=bm.faces[index];mat=f.material_index;bmesh.ops.delete(bm,geom=[f],context='FACES_ONLY');mask=bm.faces.layers.int.new('141 Spall exposed core');new=[];newcoords={}
  for j,q in enumerate(vv):
   source=vorig[j];corner=next((k for k in source if k<4),None)
   if corner is not None:new.append(bm.verts[corners[corner]]);continue
   u,v=q;D=depth*(.78+.14*u+.08*v);vtx=bm.verts.new(pos(u,v)-dv*D);new.append(vtx);newcoords[tuple(vtx.co)]=origvals[corners[0]]*(1-u)*(1-v)+origvals[corners[1]]*u*(1-v)+origvals[corners[2]]*u*v+origvals[corners[3]]*(1-u)*v
  for inds in ff:
   f=bm.faces.new([new[i]for i in inds]);f.material_index=mat;f[mask]=1;f.smooth=False
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();a=me.attributes['115 Original world position'];core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE')
  for v in me.vertices:
   if tuple(v.co)in newcoords:a.data[v.index].vector=newcoords[tuple(v.co)]
  for f in me.polygons:
   if me.attributes['141 Spall exposed core'].data[f.index].value:core.data[f.index].value=1.
  # Retained faces keep their original split normals; new surfaces use actual facet normals.
  original_normals={tuple(me.vertices[i].co for i in []):None} if False else None
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
 return {'references':['UCL-01','UCL-02','DP-03'],'source':'140 native scene','targets':out,'scope':'Three inward-only front-facing spalls on one existing cornice run; all other object geometry unchanged','production_integrated':False}
