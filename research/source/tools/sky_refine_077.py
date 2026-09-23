"""Secondary cloud-boundary octave; preserves approved sky direction and sun."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/sky-refine-077'
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def apply(scene):
 if scene.world.get('sky_refine077'):return
 scene.world=scene.world.copy();nt=scene.world.node_tree;n=nt.nodes;l=nt.links
 base=next(q for q in n if q.label=='075 Multi-scale wind-sheared cloud mass');mask=next(q for q in n if q.label=='075 Graphic cloud boundary');tc=next(q for q in n if q.label=='075 World directions');cloud=next(q for q in n if q.label=='075 Cloud oxide red')
 fine=n.new('ShaderNodeTexNoise');fine.label='077 Scalloped small cloud boundary';fine.inputs['Scale'].default_value=76;fine.inputs['Detail'].default_value=2;fine.inputs['Roughness'].default_value=.68;l.new(tc.outputs['Normal'],fine.inputs['Vector'])
 bias=n.new('ShaderNodeMath');bias.operation='MULTIPLY_ADD';bias.inputs[1].default_value=.18;bias.inputs[2].default_value=-.09;l.new(fine.outputs['Fac'],bias.inputs[0]);add=n.new('ShaderNodeMath');add.operation='ADD';l.new(base.outputs['Fac'],add.inputs[0]);l.new(bias.outputs[0],add.inputs[1]);l.new(add.outputs[0],mask.inputs[0]);mask.color_ramp.elements[1].position=mask.color_ramp.elements[0].position+.012
 cloud.inputs[2].default_value=rgb('#b9412d');scene.world['sky_refine077']=True
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;apply(s);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
