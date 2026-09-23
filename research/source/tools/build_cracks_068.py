import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-068';O.mkdir(exist_ok=True)
proofs=json.loads((R/'art/reviews/xenon-061/validation.json').read_text())
for label,opening in [('final',.45)]:
 maximum=1.0
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-064/scene.blend'));s=bpy.context.scene;records=[]
 for hostName,a in zip(['Architecture | buttress_45','Front-left section instance'],proofs):
  host=bpy.data.objects[hostName];target=next(o for o in host.instance_collection.objects if any(m.type=='BOOLEAN' and m.name.startswith('059 localized') for m in o.modifiers));m=bpy.data.materials['064 Projected surface | '+hostName];nt=m.node_tree
  world=host.matrix_world @ target.matrix_world;n=Vector(a['normal']);center=Vector(a['center'])
  evaluated=target.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();idx=list(target.data.materials).index(m)
  vertices={i for f in mesh.polygons if f.material_index==idx for i in f.vertices};depth=max(0.0001,max(-(world @ mesh.vertices[i].co-center).dot(n) for i in vertices));evaluated.to_mesh_clear()
  geo=nt.nodes.new('ShaderNodeNewGeometry');sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],sub.inputs[0]);sub.inputs[1].default_value=center
  dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=-n
  ramp=nt.nodes.new('ShaderNodeMapRange');ramp.label='068 Depth darkness | '+label;ramp.clamp=True;nt.links.new(dot.outputs['Value'],ramp.inputs['Value']);ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=depth;ramp.inputs['To Min'].default_value=1-opening;ramp.inputs['To Max'].default_value=1-maximum
  # Attenuate final matte surface color, preserving the independent physical lip reflection.
  for em in [x for x in nt.nodes if x.type=='EMISSION' and x.outputs[0].is_linked]:
   color=em.inputs['Color'];mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
   if color.is_linked:nt.links.new(color.links[0].from_socket,mul.inputs[1])
   else:mul.inputs[1].default_value=color.default_value
   nt.links.new(ramp.outputs[0],mul.inputs[2]);nt.links.new(mul.outputs[0],color)
  records.append({'host':hostName,'depth_max_m':depth,'opening_darkening':opening,'maximum_darkening':maximum,'space':'linear scene color','reflection':'unchanged'})
 (O/(label+'-settings.json')).write_text(json.dumps(records,indent=2));s.render.filepath=str(O/(label+'-render.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(label+'.blend')));bpy.ops.render.render(write_still=True)
 for j,a in enumerate(proofs):
  center=Vector(a['center']);normal=Vector(a['normal']);s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=a['size']*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/(label+('-support.png' if j==0 else '-panel.png')));bpy.ops.render.render(write_still=True)

items=[]
for host in s.objects:
 if host.instance_collection:
  items.append({'host':host.name,'position':list(host.location),'parts':[{'name':o.name,'materials':[m.name for m in o.data.materials if m]} for o in host.instance_collection.objects if o.type=='MESH']})
(O/'scene-components.json').write_text(json.dumps(items,indent=2))
