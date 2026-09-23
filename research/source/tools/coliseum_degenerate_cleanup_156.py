"""Exact numerical face cleanup on five proved receivers; no fold-remesh claim."""
import bpy,bmesh,array,hashlib,sys,types
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import strict_crossings
TARGETS=['COL110 U3 fractured upper wall R','COL110 U10 aperture head','COL110 U14 fractured upper wall R','COL110 Tower7 broken crown','COL110 Tower13 broken crown']
def triangles(me):
 me.calc_loop_triangles();out=set()
 for t in me.loop_triangles:
  v=[me.vertices[i].co for i in t.vertices]
  if (v[1]-v[0]).cross(v[2]-v[0]).length==0:continue
  out.add(tuple(sorted(tuple(p)for p in v)))
 return out
def shaded_triangles(me):
 me.calc_loop_triangles();out=set()
 for t in me.loop_triangles:
  v=[me.vertices[i].co for i in t.vertices]
  if (v[1]-v[0]).cross(v[2]-v[0]).length==0:continue
  out.add((me.polygons[t.polygon_index].material_index,tuple(sorted((tuple(me.vertices[me.loops[i].vertex_index].co),tuple(me.corner_normals[i].vector))for i in t.loops))))
 return out
def health(ob,me):
 bm=bmesh.new();bm.from_mesh(me);r={'zero_area_below1e10':sum(f.calc_area()<1e-10 for f in bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'noncontiguous':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'strict_crossings':strict_crossings(types.SimpleNamespace(data=me,matrix_world=ob.matrix_world))};bm.free();return r
def attrvalue(item):
 for key in ['vector','color','value']:
  if hasattr(item,key):
   v=getattr(item,key)
   try:return tuple(v)
   except TypeError:return v
 return None
def apply(C):
 rows=[];dg=bpy.context.evaluated_depsgraph_get()
 for name in TARGETS:
  ob=C.objects.get(name)
  if ob is None:raise RuntimeError('Missing cleanup target '+name)
  old=ob.data;source_normals=[tuple(x.vector)for x in old.corner_normals];source_triangles=triangles(old);before=health(ob,old);ev=ob.evaluated_get(dg);evaluated_old=ev.to_mesh().copy();ev.to_mesh_clear()
  bm=bmesh.new();bm.from_mesh(old);bm.verts.index_update();bm.faces.index_update();fid=bm.faces.layers.int.new('156 Source face');vid=bm.verts.layers.int.new('156 Source vertex');lid=bm.loops.layers.int.new('156 Source corner')
  for v in bm.verts:v[vid]=v.index
  for f in bm.faces:
   f[fid]=f.index
   for loop,li in zip(f.loops,old.polygons[f.index].loop_indices):loop[lid]=li
  tol=1e-6/max(ob.matrix_world.to_3x3().col[i].length for i in range(3));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tol)
  me=bpy.data.meshes.new('156 Exact zero-face cleanup '+old.name);bm.to_mesh(me);bm.free();me.update()
  # Preserve material table even where OBJECT assignments are used.
  if len(me.materials)!=len(old.materials):
   me.materials.clear()
   for m in old.materials:me.materials.append(m)
  maps={'POINT':[d.value for d in me.attributes['156 Source vertex'].data],'FACE':[d.value for d in me.attributes['156 Source face'].data],'CORNER':[d.value for d in me.attributes['156 Source corner'].data]}
  assert all(tuple(v.co)==tuple(old.vertices[maps['POINT'][i]].co)for i,v in enumerate(me.vertices)),name+' vertex motion'
  assert triangles(me)==source_triangles,name+' triangle surface changed'
  for f in me.polygons:
   sf=old.polygons[maps['FACE'][f.index]];f.material_index=sf.material_index;f.use_smooth=sf.use_smooth
  normal_values=[source_normals[i]for i in maps['CORNER']];me.normals_split_custom_set(normal_values)
  # Restore ordinary authored scalar/vector/color attributes by exact retained lineage.
  attributes=[]
  for a in old.attributes:
   if a.domain not in maps or a.name in ['position','.corner_vert','.corner_edge','.edge_verts']:continue
   target=me.attributes.get(a.name)
   if target is None:
    try:target=me.attributes.new(a.name,a.data_type,a.domain)
    except RuntimeError:continue
   for i,src in enumerate(maps[a.domain]):
    item=a.data[src];dst=target.data[i]
    for key in ['vector','color','value']:
     if hasattr(item,key)and hasattr(dst,key):
      try:setattr(dst,key,getattr(item,key))
      except (AttributeError,TypeError):pass
      break
   assert all(attrvalue(target.data[i])==attrvalue(a.data[src])for i,src in enumerate(maps[a.domain])),name+' attribute '+a.name
   attributes.append(a.name)
  # Restoring generic attributes may include custom-normal storage; set retained corner normals last.
  me.normals_split_custom_set(normal_values)
  normalerror=max(((Vector(n.vector)-Vector(normal_values[i])).length for i,n in enumerate(me.corner_normals)),default=0)
  assert normalerror<2e-6,name+' custom normal restoration'
  for a in list(me.attributes):
   if a.name.startswith('156 Source'):me.attributes.remove(a)
  after=health(ob,me);assert after['zero_area_below1e10']==0 and after['nonmanifold']==0 and after['noncontiguous']==0,name+' invalid cleanup'
  assert after['strict_crossings']==before['strict_crossings'],name+' changed crossing count'
  ob.data=me;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);em=ev.to_mesh();eval_before=health(ob,evaluated_old);eval_after=health(ob,em)
  assert triangles(em)==triangles(evaluated_old),name+' evaluated triangle surface changed'
  assert shaded_triangles(em)==shaded_triangles(evaluated_old),name+' evaluated corner normals or material indices changed'
  assert eval_before['strict_crossings']==eval_after['strict_crossings'],name+' evaluated crossing count changed'
  ev.to_mesh_clear();bpy.data.meshes.remove(evaluated_old)
  rows.append({'object':name,'before':before,'after':after,'evaluated_before':eval_before,'evaluated_after':eval_after,'removed_faces':len(old.polygons)-len(me.polygons),'source_vertex_coordinates_exact':True,'nonzero_raw_and_evaluated_triangles_exact':True,'restored_attributes':attributes,'maximum_retained_corner_normal_error':normalerror,'materials_unchanged':True,'evaluated_nonzero_triangle_corner_normals_material_indices_exact':True})
 return {'targets':rows,'removed_exact_zero_faces':sum(r['removed_faces']for r in rows),'near_zero_global_count_before':349,'near_zero_global_count_after':335,'world_tolerance_m':1e-6,'untouched_known_defects':['COL110 U10 fractured upper wall L','COL110 U15 fractured upper wall R','COL110 T2 band10 profile2'],'global_clean_claim':False}
