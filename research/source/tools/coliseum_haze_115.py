"""Native world-height dust gradient, user-authorized after114."""
import bpy,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-115/haze';O.mkdir(parents=True,exist_ok=True)
def apply_haze(low=3.,high=19.):
 ob=bpy.data.objects['Distant dust volume - real lighting'];m=ob.active_material.copy();m.name='115 Street haze height falloff';ob.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links
 geo=n.new('ShaderNodeNewGeometry');geo.label='World-space elevation';xyz=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],xyz.inputs[0])
 ramp=n.new('ShaderNodeMapRange');ramp.interpolation_type='SMOOTHERSTEP';ramp.clamp=True
 for k,v in [('From Min',low),('From Max',high),('To Min',1.),('To Max',0.)]:ramp.inputs[k].default_value=v
 l.new(xyz.outputs['Z'],ramp.inputs['Value']);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.0017;l.new(ramp.outputs[0],mul.inputs[0]);l.new(mul.outputs[0],n.get('Volume Scatter').inputs['Density'])
 return {'density_at_street':.0017,'falloff_start_world_z':low,'zero_density_world_z':high,'interpolation':'SMOOTHERSTEP','volume_bounds_unchanged':True}
if __name__=='__main__':
 for label,low,high in [('A',3,19),('B',5,27)]:
  bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-114/scene.blend'));s=bpy.context.scene;settings=apply_haze(low,high)
  s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.use_freestyle=False;s.render.use_border=False;s.render.filepath=str(O/(label+'.png'))
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(label+'.blend')));t=time.time();bpy.ops.render.render(write_still=True);settings['render_seconds']=time.time()-t;(O/(label+'.json')).write_text(json.dumps(settings,indent=2))
