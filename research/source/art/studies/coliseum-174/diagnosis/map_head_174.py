import bpy,json,sys,types
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-174/diagnosis'
from coliseum_crown_continuation_154 import robust_crossings
from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH'and(ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ob=bpy.data.objects['COL110 U4 aperture head'];ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);M=ev.matrix_world.copy();me.calc_loop_triangles();_,_,unpack=mapping();cross=robust_crossings(types.SimpleNamespace(data=me,matrix_world=M),True);ids=set(k for c in cross for k in c['pair']);verts=set(v for i in ids for v in me.loop_triangles[i].vertices);faces=set(me.loop_triangles[i].polygon_index for i in ids);ring=set(p.index for p in me.polygons if verts.intersection(p.vertices));origin=s.camera.matrix_world.translation
rows=[]
for i in sorted(ring):
 p=me.polygons[i];points=[M@me.vertices[v].co for v in p.vertices];center=sum(points,Vector())/len(points);uv=world_to_camera_view(s,s.camera,center);di=center-origin;ok,h,n,fi,owner,_=s.ray_cast(dg,origin,di.normalized());rows.append({'face':i,'in_crossing':i in faces,'vertices':list(p.vertices),'material_slot':p.material_index,'normal_local':list(p.normal),'world':list(map(list,points)),'authored':[list(unpack(v))for v in points],'center_pixel':[uv.x*3840,(1-uv.y)*2885],'center_first_hit':{'object':owner.name if ok else None,'face':fi,'depth_behind_first_surface_m':di.length-(h-origin).length if ok else None},'face_attributes':{a.name:a.data[i].value for a in me.attributes if a.domain=='FACE'and a.data_type=='FLOAT'}})
out={'source':'168','object':ob.name,'matrix_world':list(map(list,M)),'mesh_vertices_local':[list(v.co)for v in me.vertices],'mesh_faces':[list(p.vertices)for p in me.polygons],'render_triangles':[{'vertices':list(t.vertices),'face':t.polygon_index}for t in me.loop_triangles],'crossings':cross,'crossing_face_ids':sorted(faces),'one_ring_face_ids':sorted(ring),'face_records':rows,'materials':[sl.material.name if sl.material else None for sl in ob.material_slots],'modifiers':[{'name':q.name,'type':q.type}for q in ob.modifiers]};(O/'head-domain.json').write_text(json.dumps(out,indent=2));print('crossings',len(cross),'faces',faces,'ring',len(ring),flush=True)
