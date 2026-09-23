"""One bounded U10L return-patch reconstruction study; never edits primary."""
import bpy,bmesh,json,sys,types,math
from pathlib import Path
from mathutils import Vector,geometry
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
from coliseum_crown_continuation_154 import robust_crossings
NAME='COL110 U10 fractured upper wall L'
def study(C):
 ob=C.objects[NAME];dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);src=bpy.data.meshes.new_from_object(ev,depsgraph=dg);M=ev.matrix_world.copy();_,_,unpack=mapping();cc=[unpack(M@v.co)for v in src.vertices];amin=min(c[1]for c in cc);amax=max(c[1]for c in cc);floor=min(c[2]for c in cc);src.calc_loop_triangles();before=len(robust_crossings(types.SimpleNamespace(data=src,matrix_world=M)))
 bm=bmesh.new();bm.from_mesh(src);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();cut=[];retained=[]
 for f in bm.faces:
  c=[cc[v.index]for v in f.verts]
  protected=all(p[0]>=74.85 for p in c)or all(p[0]<=67.15 for p in c)or all(p[1]<amin+.0003 for p in c)or all(p[1]>amax-.0003 for p in c)or all(p[2]<floor+.05 for p in c)
  protected=protected and f.calc_area()>=1e-10
  if protected:retained.append(f.index)
  else:cut.append(f)
 d={'object':NAME,'source':'156','before_float64_pairs':before,'candidate':'Constrained cap/return retriangulation, retaining original front/back/end/bottom faces exactly','protected_face_count':len(retained),'replaced_return_face_count':len(cut),'front_threshold_r':74.85,'back_threshold_r':67.15,'source_bounds':[amin,amax,floor],'accepted':False}
 bmesh.ops.delete(bm,geom=cut,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 edges=[e for e in bm.edges if e.is_boundary];degrees={v:sum(e.is_boundary for e in v.link_edges)for e in edges for v in e.verts};d['boundary_edges']=len(edges);d['nonloop_boundary_vertices']=sum(x!=2 for x in degrees.values());loops=[];pending=set(edges)
 while pending:
  e=pending.pop();loop=[e.verts[0],e.verts[1]];v=loop[-1]
  while v!=loop[0]:
   candidates=[e for e in v.link_edges if e in pending]
   if len(candidates)!=1:break
   e=candidates[0];pending.remove(e);v=e.other_vert(v)
   if v!=loop[0]:loop.append(v)
  loops.append(loop)
 d['boundary_loop_lengths']=[len(l)for l in loops]
 d['boundary_junctions']=[{'local':list(v.co),'authored':list(unpack(M@v.co)),'degree':degree}for v,degree in degrees.items()if degree!=2]
 d['loop_authored_bounds']=[[[min(unpack(M@v.co)[i]for v in loop),max(unpack(M@v.co)[i]for v in loop)]for i in range(3)]for loop in loops]
 if d['nonloop_boundary_vertices']or len(loops)!=1:
  d['reason']='The geometrically classified return patch is not one disk: retained protected planes produce multiple loops/junctions. A single boundary fill would invent connections or remove protected surfaces.';bm.free();bpy.data.meshes.remove(src);return d
 loop=loops[0];uv=[Vector(((unpack(M@v.co)[1]-amin)*75,unpack(M@v.co)[0]))for v in loop];d['projected_duplicate_boundary_pairs']=[(i,j)for i in range(len(uv))for j in range(i)if(uv[i]-uv[j]).length<1e-6 and(loop[i].co-loop[j].co).length>1e-5]
 if d['projected_duplicate_boundary_pairs']:
  d['reason']='The cap boundary is not a single-valued heightfield: vertically separated protected edge vertices occupy identical radial/angular coordinates. Simple radial/angular CDT would collapse their masonry step and violate preserved boundaries.';bm.free();bpy.data.meshes.remove(src);return d
 verts,edges2,faces,vorig,_,_=geometry.delaunay_2d_cdt(uv,[(i,(i+1)%len(uv))for i in range(len(uv))],[list(range(len(uv)))],1,1e-8,True);maps={i:loop[ids[0]]for i,ids in enumerate(vorig)if len(ids)==1};d['cdt_new_vertices']=len(verts)-len(maps)
 if len(maps)!=len(verts):d['reason']='Projected boundary self-intersection requires new vertices; cannot retain exact protected loop with this reconstruction.';bm.free();bpy.data.meshes.remove(src);return d
 for face in faces:
  try:bm.faces.new([maps[i]for i in face])
  except ValueError:pass
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));out=bpy.data.meshes.new('160 U10L return reconstruction candidate');bm.to_mesh(out);bm.free();out.update();bm=bmesh.new();bm.from_mesh(out);d['after_nonmanifold']=sum(not e.is_manifold for e in bm.edges);d['after_zero_faces']=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();d['after_float64_pairs']=len(robust_crossings(types.SimpleNamespace(data=out,matrix_world=M)));d['accepted']=False;d['reason']='Geometry-only candidate pending exact retained attributes/normals and unchanged surface verification.'if d['after_float64_pairs']==0 and d['after_nonmanifold']==0 else'Constrained reconstruction fails closure/crossing gates; do not integrate.'
 bpy.data.meshes.remove(out);bpy.data.meshes.remove(src);return d
if __name__=='__main__':
 O=R/'art/studies/coliseum-160/repair';O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));d=study(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'candidate-audit.json').write_text(json.dumps(d,indent=2));print(json.dumps(d),flush=True)
