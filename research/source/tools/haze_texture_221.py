"""More visible native atmospheric opacity and restrained warm height color.
Extends selected219V2 density texture in final220 without changing the tunnel kit.
"""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from haze_texture_219 import layer_state
O=R/'art/studies/haze-texture-221'

def apply(scene):
 cfg=json.loads((R/'config/haze-texture-221.json').read_text());ob=scene.objects['Distant dust volume - real lighting'];old=ob.active_material
 assert old.node_tree.nodes.get('219 Unity-centered density multiplier'),'Final220 source needs selected219V2 texture'
 assert not any(n.name.startswith('221 ')for n in old.node_tree.nodes),'Already applied221'
 state={o.name:(o.data.as_pointer()if o.data else None,[list(row)for row in o.matrix_world],o.hide_render,[(sl.material.as_pointer()if sl.material else None)for sl in o.material_slots])for o in scene.objects};layers=layer_state(scene);world=scene.world;comp=scene.compositing_node_group;lights={o.name:(o.data.energy,list(o.data.color),o.data.type)for o in scene.objects if o.type=='LIGHT'}
 old.use_fake_user=True;m=old.copy();m.name='221 Denser orange-to-peach atmosphere';ob.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links;scatter=n['Volume Scatter'];em=n['136 Orange atmospheric radiance'];density=scatter.inputs['Density'].links[0].from_socket
 mul=n.new('ShaderNodeMath');mul.name='221 Real opacity increase';mul.label=mul.name;mul.operation='MULTIPLY';mul.inputs[1].default_value=cfg['scatter_density_multiplier'];l.new(density,mul.inputs[0]);l.new(mul.outputs[0],scatter.inputs['Density'])
 height=n.new('ShaderNodeMapRange');height.name='221 Orange to pale peach height';height.label=height.name;height.clamp=True;height.interpolation_type='SMOOTHERSTEP';l.new(n['Separate XYZ'].outputs['Z'],height.inputs['Value']);height.inputs['From Min'].default_value=cfg['height_gradient_world_z_m'][0];height.inputs['From Max'].default_value=cfg['height_gradient_world_z_m'][1];height.inputs['To Min'].default_value=0;height.inputs['To Max'].default_value=1
 for target,key,title in [(scatter,'scatter_rgb_linear','Scattering warm gradient'),(em,'radiance_rgb_linear','Radiance warm gradient')]:
  mix=n.new('ShaderNodeMixRGB');mix.name='221 '+title;mix.label=mix.name;mix.blend_type='MIX';mix.inputs[1].default_value=(*cfg[key]['bottom'],1);mix.inputs[2].default_value=(*cfg[key]['top'],1);l.new(height.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],target.inputs['Color'])
 for name,(data,matrix,hidden,mats)in state.items():
  o=scene.objects[name];assert (o.data.as_pointer()if o.data else None)==data,name;assert [list(row)for row in o.matrix_world]==matrix,name;assert o.hide_render==hidden,name
  if o!=ob:assert [(sl.material.as_pointer()if sl.material else None)for sl in o.material_slots]==mats,name
 assert layers==layer_state(scene)and scene.world==world and scene.compositing_node_group==comp
 assert lights=={o.name:(o.data.energy,list(o.data.color),o.data.type)for o in scene.objects if o.type=='LIGHT'}
 assert any(k.startswith('215 Distant ink without atmospheric boundary')and k.endswith('/215 Atmosphere beauty and existing ink')and v[0]for k,v in layers.items())
 return {'source':cfg['source'],'source_material':old.name,'private_material':m.name,'scatter_density_multiplier':cfg['scatter_density_multiplier'],'existing_textured_density_source':[density.node.name,density.name],'height_gradient_world_z_m':cfg['height_gradient_world_z_m'],'scatter_rgb_linear':cfg['scatter_rgb_linear'],'radiance_rgb_linear':cfg['radiance_rgb_linear'],'219V2_noise_unchanged':True,'original_depth_and_height_envelopes_unchanged':True,'near_clear_far5x_relative_envelope_preserved':True,'original_object_count':len(state),'all_geometry_transforms_visibility_unchanged':True,'all_nonatmosphere_material_bindings_unchanged':True,'final220_tunnels_unchanged':True,'sky_world_lights_camera_unchanged':True,'217_compositor_unchanged':True,'215_ink_atmosphere_exclusion_preserved':True,'all_view_layer_states_unchanged':True,'actual_render_inspected':False,'approved':False}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/arcade-tunnels-220/scene.blend'));s=bpy.context.scene;a=apply(s);s.render.filepath=str(O/'main-4k.png');(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('221 CPU READY',flush=True)
