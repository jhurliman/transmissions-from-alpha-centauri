"""Bounded metal highlight polish. Integration: apply_polish(bpy.context.scene)."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scrap-polish-075'
def apply_polish(scene):
 records=[]
 for m in bpy.data.materials:
  if not m.name.startswith('075 Scrap |') or 'mineral' in m.name or not m.use_nodes:continue
  if m.get('polish075'):continue
  nt=m.node_tree;n=nt.nodes;l=nt.links;out=next((q for q in n if q.type=='OUTPUT_MATERIAL'),None)
  if not out:continue
  rim='exposed rim physical' in m.name
  if rim:
   old=n.new('ShaderNodeBsdfDiffuse');old.inputs['Color'].default_value=(.095,.084,.10,1);rgb=n.new('ShaderNodeShaderToRGB');l.new(old.outputs[0],rgb.inputs[0]);base=rgb.outputs[0]
  else:
   em=next((q for q in n if q.type=='EMISSION' and q.outputs[0].is_linked and q.inputs['Color'].is_linked),None)
   if not em:continue
   base=em.inputs['Color'].links[0].from_socket
  # Glossy response is computed by EEVEE, then bounded into the painted palette.
  g=n.new('ShaderNodeBsdfGlossy');g.label='075 Physical broad reflection';g.inputs['Color'].default_value=(.72,.65,.61,1);g.inputs['Roughness'].default_value=.32 if rim else .29
  sr=n.new('ShaderNodeShaderToRGB');sr.label='075 Reflection into painted values';l.new(g.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);r=n.new('ShaderNodeValToRGB');r.label='075 restrained metal glints';r.color_ramp.elements[0].position=.035;r.color_ramp.elements[0].color=(0,0,0,1);r.color_ramp.elements[1].position=.36;r.color_ramp.elements[1].color=(1,1,1,1);l.new(bw.outputs[0],r.inputs[0])
  geom=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.label='075 fractured reflective islands';noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=2.8;noise.inputs['Roughness'].default_value=.72;l.new(geom.outputs['Position'],noise.inputs[0]);mask=n.new('ShaderNodeValToRGB');mask.color_ramp.elements[0].position=.48;mask.color_ramp.elements[0].color=(0,0,0,1);mask.color_ramp.elements[1].position=.61;mask.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],mask.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(r.outputs[0],mul.inputs[0]);l.new(mask.outputs[0],mul.inputs[1]);fac=n.new('ShaderNodeMath');fac.operation='MULTIPLY';fac.inputs[1].default_value=.46 if rim else .35
  dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';l.new(geom.outputs['Normal'],dot.inputs[0]);dot.inputs[1].default_value=(.40,-.65,.65)
  lo=n.new('ShaderNodeMath');lo.operation='GREATER_THAN';l.new(dot.outputs['Value'],lo.inputs[0]);lo.inputs[1].default_value=.20 if rim else .58
  hi=n.new('ShaderNodeMath');hi.operation='LESS_THAN';l.new(dot.outputs['Value'],hi.inputs[0]);hi.inputs[1].default_value=.88 if rim else .76
  window=n.new('ShaderNodeMath');window.operation='MULTIPLY';l.new(lo.outputs[0],window.inputs[0]);l.new(hi.outputs[0],window.inputs[1]);gated=n.new('ShaderNodeMath');gated.operation='MULTIPLY';l.new(window.outputs[0],gated.inputs[0]);l.new(mul.outputs[0],gated.inputs[1]);l.new(gated.outputs[0],fac.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.label='075 bounded warm-gray reflection';l.new(fac.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=(.32,.285,.29,1)
  final=n.new('ShaderNodeEmission');l.new(mix.outputs[0],final.inputs[0]);l.new(final.outputs[0],out.inputs['Surface']);m['polish075']=True;records.append(m.name)
 return records
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;records=apply_polish(s);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'render.png');(O/'audit.json').write_text(json.dumps(records,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
