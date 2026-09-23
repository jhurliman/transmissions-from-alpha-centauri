"""Restrained editable 3D density variation in the existing atmosphere volume.
No surfaces, new volume boxes, camera overlays or compositor changes.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/haze-texture-219'

def layer_state(scene):
 out={}
 def walk(v,lc,path):
  path+='/'+lc.name;out[v+path]=[lc.exclude,lc.hide_viewport,lc.holdout,lc.indirect_only]
  for c in lc.children:walk(v,c,path)
 for v in scene.view_layers:walk(v.name,v.layer_collection,'')
 return out

def apply(scene):
 cfg=json.loads((R/'config/haze-texture-219.json').read_text());ob=scene.objects['Distant dust volume - real lighting'];old=ob.active_material
 if any(n.name.startswith('219 ')for n in old.node_tree.nodes):raise RuntimeError('219 requires baseline haze; already applied')
 matrices={o.name:[list(row)for row in o.matrix_world]for o in scene.objects};layers=layer_state(scene);world=scene.world;compositor=scene.compositing_node_group;lights={o.name:(list(o.data.color),o.data.energy)for o in scene.objects if o.type=='LIGHT'}
 old.use_fake_user=True;m=old.copy();m.name='219 Subtle spatial street atmosphere';ob.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links;scatter=n['Volume Scatter'];em=n['136 Orange atmospheric radiance'];density=scatter.inputs['Density'].links[0].from_socket;radiance=em.inputs['Strength'].links[0].from_socket;xyz=n['Separate XYZ'];position=xyz.inputs[0].links[0].from_socket
 def node(kind,name):
  q=n.new(kind);q.name='219 '+name;q.label=q.name;return q
 def mathn(op,a,b,name):
  q=node('ShaderNodeMath',name);q.operation=op
  for i,x in enumerate((a,b)):
   if isinstance(x,(int,float)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def noise(name,p,offset):
  add=node('ShaderNodeVectorMath',name+' stable seed');add.operation='ADD';l.new(position,add.inputs[0]);add.inputs[1].default_value=offset
  scale=node('ShaderNodeVectorMath',name+' world metres');scale.operation='MULTIPLY';l.new(add.outputs['Vector'],scale.inputs[0]);scale.inputs[1].default_value=tuple(1/v for v in p['spatial_scales_m'])
  tex=node('ShaderNodeTexNoise',name+' density');tex.noise_dimensions='3D';l.new(scale.outputs['Vector'],tex.inputs['Vector']);tex.inputs['Scale'].default_value=1;tex.inputs['Detail'].default_value=p['detail'];tex.inputs['Roughness'].default_value=p['roughness'];tex.inputs['Distortion'].default_value=0
  if hasattr(tex,'normalize'):tex.normalize=True
  return mathn('MULTIPLY',mathn('SUBTRACT',tex.outputs['Fac'],.5,name+' centered'),p['centered_amplitude'],name+' faint amplitude')
 broad=noise('Broad billow',cfg['broad_noise'],(19.7,-33.1,7.9));fine=noise('Fine variation',cfg['fine_noise'],(-11.3,47.2,19.1));field=mathn('ADD',broad,fine,'Two spatial scales')
 gate=node('ShaderNodeMapRange','Preserve near-clear entrance');gate.interpolation_type='SMOOTHERSTEP';gate.clamp=True;l.new(xyz.outputs['Y'],gate.inputs['Value']);gate.inputs['From Min'].default_value=48;gate.inputs['From Max'].default_value=78;gate.inputs['To Min'].default_value=0;gate.inputs['To Max'].default_value=1
 factor=mathn('ADD',1,mathn('MULTIPLY',field,gate.outputs[0],'Depth-gated variation'),'Unity-centered density multiplier')
 l.new(mathn('MULTIPLY',density,factor,'Textured existing scattering'),scatter.inputs['Density']);l.new(mathn('MULTIPLY',radiance,factor,'Textured existing orange radiance'),em.inputs['Strength'])
 assert matrices=={o.name:[list(row)for row in o.matrix_world]for o in scene.objects}
 assert layers==layer_state(scene);assert scene.world==world and scene.compositing_node_group==compositor
 assert lights=={o.name:(list(o.data.color),o.data.energy)for o in scene.objects if o.type=='LIGHT'}
 assert list(scatter.inputs['Color'].default_value)==list(old.node_tree.nodes['Volume Scatter'].inputs['Color'].default_value)
 assert list(em.inputs['Color'].default_value)==list(old.node_tree.nodes['136 Orange atmospheric radiance'].inputs['Color'].default_value)
 isolated=[p for p,v in layers.items()if p.startswith('215 Distant ink without atmospheric boundary')and p.endswith('/215 Atmosphere beauty and existing ink')and v[0]];assert isolated,'215 atmosphere ink exclusion missing'
 return {'source_material':old.name,'new_private_material':m.name,'original_density_input':[density.node.name,density.name],'original_radiance_input':[radiance.node.name,radiance.name],'source_position_socket':[position.node.name,position.name],'source_gradient_controls_preserved':['132 Near-clear to far-dense','202 Ground layer falloff','202 Broad ground source depth','202 Low terminal taper','136 Rear source cutoff'],'same_multiplier_for_scattering_and_radiance':True,'nominal_factor_mean':1.0,'theoretical_factor_bounds':cfg['density_multiplier']['theoretical_bounds'],'near_y_below48_unchanged':True,'noise_config':{k:cfg[k]for k in ['broad_noise','fine_noise']},'no_color_change':True,'all_object_transforms_unchanged':True,'all_scene_lights_unchanged':True,'sky_world_unchanged':True,'compositor_and217_unchanged':True,'all_view_layer_exclusions_unchanged':True,'215_atmosphere_exclusion_verified':isolated,'source_graph_preserved':True,'actual_render_inspected':False,'rendered_mean_pending_native_comparison':True,'approved':False}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);source=R/'art/studies/scene-direction-218/current-sun/scene.blend';bpy.ops.wm.open_mainfile(filepath=str(source));a=apply(bpy.context.scene);bpy.context.scene.render.filepath=str(O/'main-4k.png');(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('219 CPU READY',flush=True)
