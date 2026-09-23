"""Restricted light-gated highlight A/B for one walkway fascia and pipe bands."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/highlight-refine-077'
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def op(nt,operation,a,b):
 q=nt.nodes.new('ShaderNodeMath');q.operation=operation
 for i,v in enumerate([a,b]):
  if isinstance(v,(float,int)):q.inputs[i].default_value=v
  else:nt.links.new(v,q.inputs[i])
 return q.outputs[0]
def light_gate(nt):
 n=nt.nodes;l=nt.links;d=n.new('ShaderNodeBsdfDiffuse');d.label='077 actual illumination gate';d.inputs[0].default_value=(1,1,1,1);sr=n.new('ShaderNodeShaderToRGB');l.new(d.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.025;r.inputs['From Max'].default_value=.25;l.new(bw.outputs[0],r.inputs[0]);return r.outputs[0]
def apply(scene):
 changes=[]
 for m in bpy.data.materials:
  if not m.use_nodes or m.get('highlight077'):continue
  fascia=m.name=='055 fascia | 042 Street coating | right_front';pipe=m.name.startswith(('PIP | blue-gray enamel','PIP | warm brown metal finish'))
  if not(fascia or pipe):continue
  nt=m.node_tree;n=nt.nodes;l=nt.links;gate=light_gate(nt)
  if pipe:
   for q in list(n):
    if q.type=='MIX_RGB' and not q.inputs[2].is_linked and max(abs(a-b) for a,b in zip(q.inputs[2].default_value,rgb('#b8b5ae')))<.0001 and q.inputs[0].is_linked:
     old=q.inputs[0].links[0].from_socket;g=op(nt,'MULTIPLY',op(nt,'MULTIPLY',old,1.45),op(nt,'ADD',.25,op(nt,'MULTIPLY',gate,.75)));l.new(g,q.inputs[0]);q.inputs[2].default_value=rgb('#c4c1b9');changes.append(m.name+' neutral band')
  if fascia:
   em=next(q for q in n if q.type=='EMISSION' and q.outputs[0].is_linked and q.inputs[0].is_linked);base=em.inputs[0].links[0].from_socket;geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0]);mask=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',sep.outputs['Z'],.65),op(nt,'LESS_THAN',sep.outputs['Z'],.77));noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=13;noise.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],noise.inputs[0]);mask=op(nt,'MULTIPLY',mask,op(nt,'GREATER_THAN',noise.outputs['Fac'],.40));mask=op(nt,'MULTIPLY',op(nt,'MULTIPLY',mask,gate),.24);mix=n.new('ShaderNodeMixRGB');mix.label='077 hero chamfer warm pale sliver';l.new(mask,mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=rgb('#d8c8b3');l.new(mix.outputs[0],em.inputs[0]);changes.append(m.name+' chamfer')
  m['highlight077']=True
 return changes
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;changes=apply(s);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'render.png');(O/'audit.json').write_text(json.dumps(changes,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
