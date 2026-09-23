import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-064';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-061/scene.blend'));s=bpy.context.scene;proofs=json.loads((R/'art/reviews/xenon-061/validation.json').read_text());records=[]
for hostName,a in zip(['Architecture | buttress_45','Front-left section instance'],proofs):
 host=bpy.data.objects[hostName];target=next(o for o in host.instance_collection.objects if any(m.type=='BOOLEAN' and m.name.startswith('059 localized') for m in o.modifiers));source=target.data.materials[0];m=source.copy();m.name='064 Projected surface | '+hostName;visited={}
 def project_tree(nt):
  # Private copies of nested groups preserve original facade and service materials.
  for node in list(nt.nodes):
   if node.type=='GROUP' and node.node_tree:
    old=node.node_tree
    if old.name not in visited:
     new=old.copy();visited[old.name]=new;project_tree(new)
    node.node_tree=visited[old.name]
  oldgeo=[n for n in nt.nodes if n.type=='NEW_GEOMETRY']
  poslinks=[l for n in oldgeo for l in list(n.outputs['Position'].links)];normlinks=[l for n in oldgeo for key in ['Normal','True Normal'] for l in list(n.outputs[key].links)]
  geo=nt.nodes.new('ShaderNodeNewGeometry');geo.label='064 actual interior geometry';sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],sub.inputs[0]);sub.inputs[1].default_value=a['center'];dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=a['normal'];scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[0].default_value=a['normal'];nt.links.new(dot.outputs['Value'],scale.inputs['Scale']);proj=nt.nodes.new('ShaderNodeVectorMath');proj.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],proj.inputs[0]);nt.links.new(scale.outputs[0],proj.inputs[1])
  def affine(socket,matrix):
   comb=nt.nodes.new('ShaderNodeCombineXYZ')
   for i in range(3):
    row=nt.nodes.new('ShaderNodeVectorMath');row.operation='DOT_PRODUCT';nt.links.new(socket,row.inputs[0]);row.inputs[1].default_value=tuple(matrix[i][j] for j in range(3))
    offset=nt.nodes.new('ShaderNodeMath');offset.operation='ADD';nt.links.new(row.outputs['Value'],offset.inputs[0]);offset.inputs[1].default_value=matrix[i][3];nt.links.new(offset.outputs[0],comb.inputs[i])
   return comb.outputs[0]
  for tex in [n for n in nt.nodes if n.type=='TEX_COORD']:
   for kind in ['Object','Generated']:
    links=list(tex.outputs[kind].links)
    if not links:continue
    transform=tex.object.matrix_world if kind=='Object' and tex.object else host.matrix_world @ target.matrix_world
    local=affine(proj.outputs[0],transform.inverted())
    if kind=='Generated':
     bounds=[v.co for v in target.data.vertices];lo=Vector(tuple(min(v[i] for v in bounds) for i in range(3)));hi=Vector(tuple(max(v[i] for v in bounds) for i in range(3)))
     subtract=nt.nodes.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT';nt.links.new(local,subtract.inputs[0]);subtract.inputs[1].default_value=lo
     divide=nt.nodes.new('ShaderNodeVectorMath');divide.operation='DIVIDE';nt.links.new(subtract.outputs[0],divide.inputs[0]);divide.inputs[1].default_value=hi-lo;local=divide.outputs[0]
    for link in links:nt.links.new(local,link.to_socket)
  for link in poslinks:nt.links.new(proj.outputs[0],link.to_socket)
  for link in normlinks:
   if link.to_node.type not in {'BSDF_DIFFUSE','BSDF_PRINCIPLED','BSDF_GLOSSY'}:
    socket=link.to_socket;nt.links.remove(link);socket.default_value=a['normal']
 project_tree(m.node_tree)
 # The copied surface finish has the same pigment/wear; only a real mouth glint is added.
 nt=m.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);base=out.inputs['Surface'].links[0].from_socket
 geo=nt.nodes.new('ShaderNodeNewGeometry');sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],sub.inputs[0]);sub.inputs[1].default_value=a['center'];dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=tuple(-v for v in a['normal']);mask=nt.nodes.new('ShaderNodeMapRange');mask.clamp=True;nt.links.new(dot.outputs['Value'],mask.inputs['Value']);mask.inputs['From Min'].default_value=.0004;mask.inputs['From Max'].default_value=.004;mask.inputs['To Min'].default_value=.12;mask.inputs['To Max'].default_value=0
 glossy=nt.nodes.new('ShaderNodeBsdfGlossy');glossy.inputs['Color'].default_value=(.3,.3,.3,1);glossy.inputs['Roughness'].default_value=.3
 mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(mask.outputs[0],mix.inputs[0]);nt.links.new(base,mix.inputs[1]);nt.links.new(glossy.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
 for ob in [target]+[mod.object for mod in target.modifiers if mod.type=='BOOLEAN' and mod.name.startswith('059 localized')]:
  for slot in ob.material_slots:
   if slot.material and slot.material.name.startswith('059 exposed mineral lip'):slot.material=m
 records.append({'host':hostName,'surface_material':source.name,'projection':'World position projected to original face plane in copied surface shader and its nested groups','normal':'Actual crack normals retained for shading and mouth glint'})
(O/'materials.json').write_text(json.dumps(records,indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
for j,a in enumerate(proofs):
 center=Vector(a['center']);normal=Vector(a['normal']);s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=a['size']*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/('support.png' if j==0 else 'panel.png'));bpy.ops.render.render(write_still=True)
