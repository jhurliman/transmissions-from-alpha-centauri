import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'art/studies/coliseum-181';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.hide_render or (ob.type=='MESH' and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes) for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;rows=[]
for x,y in [(2160,628),(2176,628),(1913,580),(2144,612),(2152,620),(1753,596),(1761,596),(1769,596),(1761,604)]:
 q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
 if not ok:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();f=me.polygons[fi];mat=ob.material_slots[f.material_index].material;rows.append({'pixel':[x,y],'object':ob.name,'face':fi,'material_slot':f.material_index,'material':mat.name if mat else None,'world':list(p),'normal':list(n),'face_vertices_world':[list(ob.matrix_world@me.vertices[i].co) for i in f.vertices]});ev.to_mesh_clear()
def sock(v):
 try:return list(v)
 except TypeError:return v
mats={}
for name in ['151 Warm violet exposed masonry core','165 Existing light on exposed masonry core']:
 m=bpy.data.materials[name];nodes=[]
 for n in m.node_tree.nodes:
  nodes.append({'name':n.name,'label':n.label,'type':n.type,'operation':getattr(n,'operation',None),'inputs':[{'index':i,'name':a.name,'default':sock(a.default_value) if hasattr(a,'default_value') else None,'links':[{'node':l.from_node.name,'socket':l.from_socket.name} for l in a.links]} for i,a in enumerate(n.inputs)]})
 mats[name]={'nodes':nodes}
(O/'current-core-routing.json').write_text(json.dumps({'source':'173','rays':rows,'materials':mats,'actual_diffuse_measured':False,'no_scene_mutation_or_render':True},indent=2));print('DONE',[(r['pixel'],r['object'],r['face'],r['material_slot'],r['material'])for r in rows])
