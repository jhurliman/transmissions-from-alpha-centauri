import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/edge-diagnosis';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=3;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1725/3840;s.render.border_max_x=2330/3840;s.render.border_min_y=1-960/2885;s.render.border_max_y=1-560/2885
gp=bpy.data.objects.get('110 Landmark contact ink');gp.hide_render=True
materials={slot.material for ob in C.all_objects if ob.type=='MESH' for slot in ob.material_slots if slot.material and slot.material.use_nodes};saved=[]
for mat in materials:
 n,l=mat.node_tree.nodes,mat.node_tree.links
 for q in list(n):
  if q.type=='AMBIENT_OCCLUSION':
   val=n.new('ShaderNodeValue');val.outputs[0].default_value=1.
   for link in list(q.outputs['AO'].links):saved.append((l,link.from_socket,link.to_socket));l.new(val.outputs[0],link.to_socket)
s.render.filepath=str(O/'diagnostic-no-ao.png');bpy.ops.render.render(write_still=True)
for l,src,dst in saved:l.new(src,dst)
for mat in materials:
 n,l=mat.node_tree.nodes,mat.node_tree.links
 for q in list(n):
  if q.type=='TEX_NOISE':
   val=n.new('ShaderNodeValue');val.outputs[0].default_value=.5
   for link in list(q.outputs['Fac'].links):l.new(val.outputs[0],link.to_socket)
  if q.type=='MIX_RGB'and q.label.startswith(('134 ','135 ','148 ')):
   for link in list(q.inputs[0].links):l.remove(link)
   q.inputs[0].default_value=0.
s.render.filepath=str(O/'diagnostic-no-procedural-age.png');bpy.ops.render.render(write_still=True)
# Record actual material-space anchors from previously ray-hit native faces.
from mathutils import geometry
D=json.loads((O/'diagnosis-inputs.json').read_text());dg=bpy.context.evaluated_depsgraph_get();anchors=[];cache={}
for r in D['rays']:
 if ('profile'in r['object']and abs(r['normal'][2])<.4)or 'dentil'in r['object']:
  ob=bpy.data.objects[r['object']]
  if ob.name not in cache:
   me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);me.calc_loop_triangles();cache[ob.name]=me
  me=cache[ob.name];at=me.attributes.get('115 Original world position')
  if at:
   p=ob.matrix_world.inverted()@Vector(r['point']);ts=[t for t in me.loop_triangles if t.polygon_index==r['face']];t=min(ts,key=lambda t:(geometry.closest_point_on_tri(p,*[me.vertices[i].co for i in t.vertices])-p).length_squared);pos=geometry.barycentric_transform(p,*[me.vertices[i].co for i in t.vertices],*[at.data[i].vector for i in t.vertices]);anchors.append({**r,'original_world':list(pos),'material':ob.material_slots[me.polygons[r['face']].material_index].material.name})
(O/'receiver-anchors.json').write_text(json.dumps(anchors,indent=2))
