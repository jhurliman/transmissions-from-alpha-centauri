"""Increase low atmospheric spatial variance without a uniform opacity gain.
Only the existing native volume's private material is changed.
"""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from haze_texture_219 import layer_state
O=R/'art/studies/haze-variance-240'

def apply(scene):
 cfg=json.loads((R/'config/haze-variance-240.json').read_text())
 ob=scene.objects['Distant dust volume - real lighting'];old=ob.active_material
 assert '219 Unity-centered density multiplier' in old.node_tree.nodes
 assert not any(n.name.startswith('240 ')for n in old.node_tree.nodes),'240 already applied'
 state={o.name:((o.data.as_pointer()if o.data else None),[list(r)for r in o.matrix_world],o.hide_render,[(x.material.as_pointer()if x.material else None)for x in o.material_slots])for o in scene.objects}
 layers=layer_state(scene);world=scene.world;comp=scene.compositing_node_group
 lights={o.name:(tuple(o.data.color),o.data.energy,[list(r)for r in o.matrix_world])for o in scene.objects if o.type=='LIGHT'}
 old.use_fake_user=True;m=old.copy();m.name='240 Lower-bank high-variance warm atmosphere';ob.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links
 def node(kind,title):
  q=n.new(kind);q.name='240 '+title;q.label=q.name;return q
 def math(op,a,b,title):
  q=node('ShaderNodeMath',title);q.operation=op
  for i,x in enumerate((a,b)):
   if isinstance(x,(float,int)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def range_node(socket,lo,hi,a,b,title):
  q=node('ShaderNodeMapRange',title);q.clamp=True;q.interpolation_type='SMOOTHERSTEP';l.new(socket,q.inputs['Value'])
  for key,val in [('From Min',lo),('From Max',hi),('To Min',a),('To Max',b)]:q.inputs[key].default_value=val
  return q.outputs[0]
 # Symmetric saturation preserves a unity expectation for a symmetric noise field;
 # no extra constant opacity multiplier, and no claim of exact finite-view mean.
 centered=n['219 Two spatial scales'].outputs[0]
 high=math('MULTIPLY',centered,cfg['centered_contrast'],'Amplify centered variation')
 bounded=math('MINIMUM',math('MAXIMUM',high,-cfg['symmetric_amplitude'],'Thin pocket limit'),cfg['symmetric_amplitude'],'Dense pocket limit')
 gate=n['219 Preserve near-clear entrance'].outputs[0]
 heightened=math('ADD',1,math('MULTIPLY',bounded,gate,'Keep existing near-clear onset'),'High-variance unity field')
 z=n['Separate XYZ'].outputs['Z'];low=range_node(z,*cfg['upper_fade_world_z_m'],1,0,'Preserve upper landmark atmosphere')
 oldfactor=n['219 Unity-centered density multiplier'].outputs[0]
 blend=node('ShaderNodeMixRGB','Lower arcade density only');l.new(low,blend.inputs[0]);l.new(oldfactor,blend.inputs[1]);l.new(heightened,blend.inputs[2])
 l.new(blend.outputs[0],n['219 Textured existing scattering'].inputs[1])
 # Radiance remains driven by the old restrained field. Dense pockets extinguish
 # facade contrast rather than creating higher emission / pale white clouds.
 dense=range_node(bounded,0,cfg['symmetric_amplitude'],0,1,'Dense pocket pigment weight')
 weight=math('MULTIPLY',math('MULTIPLY',dense,low,'Low-bank pigment only'),cfg['dense_pigment_blend'],'Restrained orange pigment')
 scatter=n['Volume Scatter'];color=scatter.inputs['Color'].links[0].from_socket
 mix=node('ShaderNodeMixRGB','Dense warm pigment');l.new(weight,mix.inputs[0]);l.new(color,mix.inputs[1]);mix.inputs[2].default_value=(*cfg['dense_pigment_linear'],1);l.new(mix.outputs[0],scatter.inputs['Color'])
 for name,(data,matrix,hidden,mats)in state.items():
  o=scene.objects[name];assert (o.data.as_pointer()if o.data else None)==data;assert [list(r)for r in o.matrix_world]==matrix;assert o.hide_render==hidden
  if o!=ob:assert [(x.material.as_pointer()if x.material else None)for x in o.material_slots]==mats,name
 assert layers==layer_state(scene)and world==scene.world and comp==scene.compositing_node_group
 assert lights=={o.name:(tuple(o.data.color),o.data.energy,[list(r)for r in o.matrix_world])for o in scene.objects if o.type=='LIGHT'}
 assert n['221 Real opacity increase'].inputs[1].default_value==old.node_tree.nodes['221 Real opacity increase'].inputs[1].default_value
 return {'source':cfg['source'],'source_material':old.name,'material':m.name,'contrast':cfg['centered_contrast'],'field_bounds':[1-cfg['symmetric_amplitude'],1+cfg['symmetric_amplitude']],'expected_multiplier_mean':1,'mean_caveat':'Symmetric theoretical noise expectation only; finite rendered-view density/brightness mean needs native proof. No uniform opacity gain added.','upper_fade_world_z_m':cfg['upper_fade_world_z_m'],'radiance_field_unchanged':True,'global_scatter_density_multiplier_unchanged':2.8,'noise_scales_and_seeds_unchanged':True,'all_original_geometry_transforms_other_materials_unchanged':True,'239_world_sun_lights_compositor_preserved':True,'view_layers_ink_unchanged':True,'landmark_ink_owners':['ViewLayer/110 Landmark contours','ViewLayer/110 Landmark fine creases','192 Architecture ink without pigment films/110 Landmark contours','192 Architecture ink without pigment films/110 Landmark fine creases'],'ink_review_note':'If dense pockets retain overlay contour detail, parent must review scoped landmark-only attenuation.215 atmosphere-free pass contains distant components and broken walls, not landmark lines.','actual_render_inspected':False,'approved':False}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);cfg=json.loads((R/'config/haze-variance-240.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('240 CPU READY',flush=True)
