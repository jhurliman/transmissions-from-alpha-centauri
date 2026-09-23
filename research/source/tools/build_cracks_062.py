import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-062'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-061/scene.blend'));s=bpy.context.scene
proofs=json.loads((R/'art/reviews/xenon-061/validation.json').read_text());controls=[];records=[]
for hostName,a in zip(['Architecture | buttress_45','Front-left section instance'],proofs):
 host=bpy.data.objects[hostName];target=next(o for o in host.instance_collection.objects if any(m.type=='BOOLEAN' and m.name.startswith('059 localized') for m in o.modifiers))
 m=bpy.data.materials.new('062 Mineral fracture | '+hostName);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();geo=nt.nodes.new('ShaderNodeNewGeometry');sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';nt.links.new(geo.outputs['Position'],sub.inputs[0]);sub.inputs[1].default_value=a['center'];dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=tuple(-v for v in a['normal'])
 ramp=nt.nodes.new('ShaderNodeMapRange');ramp.clamp=True;nt.links.new(dot.outputs['Value'],ramp.inputs['Value']);ramp.inputs['From Min'].default_value=.00015;ramp.inputs['From Max'].default_value=.0012;ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0
 bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(.045,.041,.043,1);bs.inputs['Metallic'].default_value=0;bs.inputs['IOR'].default_value=1.48
 rough=nt.nodes.new('ShaderNodeMapRange');nt.links.new(ramp.outputs[0],rough.inputs['Value']);rough.inputs['To Min'].default_value=.93;rough.inputs['To Max'].default_value=.28;nt.links.new(rough.outputs[0],bs.inputs['Roughness'])
 gain=nt.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';nt.links.new(ramp.outputs[0],gain.inputs[0]);gain.inputs[1].default_value=.5;nt.links.new(gain.outputs[0],bs.inputs['Specular IOR Level']);controls.append(gain)
 out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs['Surface'])
 for ob in [target]+[mod.object for mod in target.modifiers if mod.type=='BOOLEAN' and mod.name.startswith('059 localized')]:
  for slot in ob.material_slots:
   if slot.material and slot.material.name.startswith('059 exposed mineral lip'):slot.material=m
 records.append({'host':hostName,'mouth_specular_fade_m':[.00015,.0012],'interior_roughness':.93,'mouth_roughness':.28,'ior':1.48})
(O/'settings.json').write_text(json.dumps(records,indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
for j,a in enumerate(proofs):
 center=Vector(a['center']);normal=Vector(a['normal']);s.camera.location=center+normal*4+Vector((0,-.4,.25));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=a['size']*1.25;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(O/('support.png' if j==0 else 'panel.png'));bpy.ops.render.render(write_still=True)
for gain in controls:gain.inputs[1].default_value=0
s.render.filepath=str(O/'panel-no-spec.png');bpy.ops.render.render(write_still=True)
