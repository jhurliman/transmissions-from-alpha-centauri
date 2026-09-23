"""Native directional sky. Import apply_sky(scene, variant) for integration."""
import bpy, math, json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri'); O=R/'art/studies/sky-075'
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def apply_sky(s,variant='B'):
 s.world=s.world.copy(); nt=s.world.node_tree;n=nt.nodes;l=nt.links
 out=next(q for q in n if q.type=='OUTPUT_WORLD'); original=out.inputs['Surface'].links[0].from_socket
 def node(t,label):
  q=n.new(t);q.label='075 '+label;return q
 def mathn(op,a,b):
  q=node('ShaderNodeMath',op);q.operation=op
  for i,v in enumerate((a,b)):
   if isinstance(v,(float,int)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 tc=node('ShaderNodeTexCoord','World directions');sep=node('ShaderNodeSeparateXYZ','Elevation');l.new(tc.outputs['Normal'],sep.inputs[0]);elev=mathn('ABSOLUTE',sep.outputs['Z'],0)
 base=node('ShaderNodeValToRGB','Amber horizon to vermilion zenith');ra=base.color_ramp;ra.elements[0].position=.05;ra.elements[0].color=rgb('#ee8b35');ra.elements[1].position=.65;ra.elements[1].color=rgb('#c83c16');q=ra.elements.new(.3);q.color=rgb('#ee5724');l.new(elev,base.inputs[0])
 mapping=node('ShaderNodeVectorMath','Horizontally stretched cloud field');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(5.5,3.7,24);l.new(tc.outputs['Normal'],mapping.inputs[0]);noise=node('ShaderNodeTexNoise','Multi-scale wind-sheared cloud mass');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.64;l.new(mapping.outputs[0],noise.inputs['Vector'])
 mask=node('ShaderNodeValToRGB','Graphic cloud boundary');mask.color_ramp.interpolation='LINEAR';threshold={'A':.60,'B':.56,'C':.52}[variant];mask.color_ramp.elements[0].position=threshold;mask.color_ramp.elements[1].position=threshold+.022;l.new(noise.outputs['Fac'],mask.inputs[0]);cloud=node('ShaderNodeMixRGB','Cloud oxide red');cloud.blend_type='MIX';cloud.inputs[2].default_value=rgb({'A':'#b94e33','B':'#b64930','C':'#9e432f'}[variant]);l.new(mask.outputs[0],cloud.inputs[0]);l.new(base.outputs[0],cloud.inputs[1])
 sun=node('ShaderNodeVectorMath','Sun angular distance');sun.operation='DOT_PRODUCT';sun.inputs[1].default_value=tuple(v/math.sqrt(.109375**2+.950317**2+.291504**2) for v in (-.109375,-.950317,-.291504));l.new(tc.outputs['Normal'],sun.inputs[0]);disc=mathn('GREATER_THAN',sun.outputs['Value'],.99985);sm=node('ShaderNodeMixRGB','Low pale amber sun');l.new(disc,sm.inputs[0]);l.new(cloud.outputs[0],sm.inputs[1]);sm.inputs[2].default_value=rgb('#ffd07a');bg=node('ShaderNodeBackground','Camera sky only');l.new(sm.outputs[0],bg.inputs['Color']);bg.inputs['Strength'].default_value=.9
 lp=node('ShaderNodeLightPath','Preserve approved illumination');mix=node('ShaderNodeMixShader','Camera-only sky switch');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(original,mix.inputs[1]);l.new(bg.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface']);return s.world
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True)
 for variant in ['A','B','C']:
  bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-074/scene.blend'));s=bpy.context.scene;apply_sky(s,variant);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/(variant+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(variant+'.blend')));bpy.ops.render.render(write_still=True)
