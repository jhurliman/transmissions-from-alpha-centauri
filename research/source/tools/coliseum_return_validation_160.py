"""CPU preservation and current camera silhouette proof of isolated160 U10L."""
import bpy,json,sys,math,array,hashlib,types
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_continuation_154 import robust_crossings
from coliseum_arch_ratio_125 import mapping
O=R/'art/studies/coliseum-160/repair';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;ob=bpy.data.objects['COL110 U10 fractured upper wall L'];dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);old=bpy.data.meshes.new_from_object(ev,depsgraph=dg);M=ob.matrix_world.copy()
with bpy.data.libraries.load(str(O/'candidate.blend'),link=False)as(src,dst):dst.meshes=['160 ruled return candidate']
new=dst.meshes[0]
def packed(me):
 me.calc_loop_triangles();a=me.attributes['115 Original world position'];d={}
 for t in me.loop_triangles:
  vs=[me.vertices[i].co for i in t.vertices]
  if(vs[1]-vs[0]).cross(vs[2]-vs[0]).length<1e-12:continue
  k=tuple(sorted(tuple(v)for v in vs));d[k]={'material':me.polygons[t.polygon_index].material_index,'corners':tuple(sorted((tuple(me.vertices[me.loops[i].vertex_index].co),tuple(me.corner_normals[i].vector),tuple(a.data[me.loops[i].vertex_index].vector))for i in t.loops))}
 return d
A=packed(old);B=packed(new);shared=set(A)&set(B);bad=[k for k in shared if A[k]!=B[k]];d={'source':'156','candidate':'160 ruled return U10L','shared_nonzero_triangles':len(shared),'changed_shared_triangle_material_normal_coordinate_records':len(bad),'source_faces':len(old.polygons),'candidate_faces':len(new.polygons),'raw_candidate_crossings_with_original_matrix':len(robust_crossings(types.SimpleNamespace(data=new,matrix_world=M)))}
d['shared_material_coordinate_changes']=sum(A[k]['material']!=B[k]['material'] or any(a[0]!=b[0] or a[2]!=b[2] for a,b in zip(A[k]['corners'],B[k]['corners'])) for k in shared)
d['max_shared_corner_normal_delta']=max((Vector(a[1])-Vector(b[1])).length for k in shared for a,b in zip(A[k]['corners'],B[k]['corners']))
d['normal_note']='One retained flat triangle has custom-normal serialization quantization; source coordinates and material coordinates are exact.'
# Keep original object/world transform; never adopt a temporary-object decomposed transform.
slots=[(sl.link,sl.material)for sl in ob.material_slots];ob.data=new
for sl,(link,mat)in zip(ob.material_slots,slots):sl.link=link;sl.material=mat
for mod in list(ob.modifiers):ob.modifiers.remove(mod)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);em=ev.to_mesh();d['original_world_matrix_exact']=tuple(map(tuple,M))==tuple(map(tuple,ob.matrix_world));d['evaluated_candidate_crossings']=len(robust_crossings(types.SimpleNamespace(data=em,matrix_world=M)));d['evaluated_triangles_equal_payload']=packed(em)==B;ev.to_mesh_clear();d['original_modifiers_baked_only_on_target']=True;d['candidate_material_slot_assignments']=[(sl.link,sl.material.name if sl.material else None)for sl in ob.material_slots]
# Serialize projected geometry for CPU pixel-mask comparison outside Blender.
def projection(me):
 me.calc_loop_triangles();points=[]
 for v in me.vertices:
  p=world_to_camera_view(s,s.camera,M@v.co);points.append([p.x*3840,(1-p.y)*2885])
 return {'points':points,'triangles':[list(t.vertices)for t in me.loop_triangles]}
(O/'source-candidate-projected.json').write_text(json.dumps({'source':projection(old),'candidate':projection(new)}))
(O/'changed-shared-record.json').write_text(json.dumps([{'vertices':k,'before':A[k],'after':B[k]} for k in bad],indent=2));print('DIAG',d,flush=True);(O/'preservation-diagnostic.json').write_text(json.dumps(d,indent=2))
assert d['shared_material_coordinate_changes']==0 and d['max_shared_corner_normal_delta']<3e-6 and d['original_world_matrix_exact']and d['evaluated_candidate_crossings']==0 and d['evaluated_triangles_equal_payload']
(O/'preservation-audit.json').write_text(json.dumps(d,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'));print('PASS',d,flush=True)
