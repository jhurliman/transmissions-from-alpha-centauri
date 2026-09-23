"""Broaden low distant-street atmosphere while preserving upper136E behavior."""
import bpy

def apply(scene):
 ob=scene.objects['Distant dust volume - real lighting'];old=ob.active_material;m=old.copy();m.name='202 Continuous low street atmosphere';ob.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links
 xyz=n.get('Separate XYZ');original=n.get('136 Orange source depth').outputs[0];old_finite=n.get('136 Finite source depth');rear=n.get('136 Rear source cutoff').outputs[0]
 def mathn(op,a,b,name):
  q=n.new('ShaderNodeMath');q.operation=op;q.name=name
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(value,lo,hi,a,b,name):
  q=n.new('ShaderNodeMapRange');q.name=name;q.clamp=True;q.interpolation_type='SMOOTHERSTEP';l.new(value,q.inputs['Value'])
  for k,v in [('From Min',lo),('From Max',hi),('To Min',a),('To Max',b)]:q.inputs[k].default_value=v
  return q.outputs[0]
 low=ramp(xyz.outputs['Z'],.5,8.5,1,0,'202 Ground layer falloff')
 rise=ramp(xyz.outputs['Y'],48,105,0,.95,'202 Broad ground source depth')
 early=mathn('MULTIPLY',rise,ramp(xyz.outputs['Y'],130,200,1,0,'202 Low terminal taper'),'202 Finite low luminous bank')
 mix=mathn('ADD',mathn('MULTIPLY',original,mathn('SUBTRACT',1,low,'202 Upper preserved'),'202 Upper source'),mathn('MULTIPLY',early,low,'202 Earlier low source'),'202 Blended low source')
 l.new(mix,old_finite.inputs[0])
 scatter=n.get('Volume Scatter');field=scatter.inputs['Density'].links[0].from_socket
 # A finite low layer adds optical depth only after the nearest city begins.
 dep=ramp(xyz.outputs['Y'],48,150,0,1,'202 Low scattering depth')
 extra=mathn('MULTIPLY',low,dep,'202 Low scatter envelope')
 l.new(mathn('MULTIPLY',field,mathn('ADD',1,extra,'202 Low scatter multiplier'),'202 Distributed low scattering'),scatter.inputs['Density'])
 return {'old_material':old.name,'new_material':m.name,'upper_haze_preserved_above_m':8.5,'low_source_rise_m':[48,105],'low_source_fall_m':[130,200],'low_source_peak_relative':.95,'low_source_terminal_relative':0,'low_scatter_max_multiplier':2,'nearest_city_start_m':48,'rear_cutoff_m':[205,225],'geometry_sky_lights_camera_unchanged':True}
