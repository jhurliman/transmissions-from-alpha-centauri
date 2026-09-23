import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-041';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-040/scene.blend'));s=bpy.context.scene
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
for m in bpy.data.materials:
 if not m.name.startswith('039 Layered coating'):continue
 nt=m.node_tree;n=nt.nodes;l=nt.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
 existing=bs.inputs['Base Color'].links[0].from_node
 ramp=next(x for x in n if x.type=='VALTORGB' and len(x.color_ramp.elements)==3 and any(abs(e.position-.507)<.002 for e in x.color_ramp.elements))
 field=ramp.inputs[0].links[0].from_node
 # Restore most of 039's fine breakup, retaining 040's separately gated angular changes.
 fine=next(x for x in n if x.type=='MATH' and x.operation=='MULTIPLY_ADD' and abs(x.inputs[1].default_value-.028)<.001)
 fine.inputs[1].default_value=.080;fine.inputs[2].default_value=-.040
 for e in ramp.color_ramp.elements:
  if abs(e.position-.507)<.002:e.position=.493;e.color=rgb('#968270')
 # Restore a visible brown intermediate layer beneath the warm tan field.
 ramp.color_ramp.elements[-1].color=rgb('#b29a81')
 tex=next(x for x in n if x.type=='TEX_COORD' and x.object and x.object.name=='039 Building coating coordinates')
 def mathnode(op,a=None,b=None):
  q=n.new('ShaderNodeMath');q.operation=op
  if a is not None:
   if isinstance(a,(int,float)):q.inputs[0].default_value=a
   else:l.new(a,q.inputs[0])
  if b is not None:
   if isinstance(b,(int,float)):q.inputs[1].default_value=b
   else:l.new(b,q.inputs[1])
  return q.outputs[0]
 # Select only portions of the coating edge for dark substrate, rather than ringing every patch.
 local=n.new('ShaderNodeTexNoise');local.inputs['Scale'].default_value=2.4;local.inputs['Detail'].default_value=2;l.new(tex.outputs['Object'],local.inputs['Vector'])
 gate=mathnode('GREATER_THAN',local.outputs['Fac'],.57)
 dist=mathnode('ABSOLUTE',mathnode('SUBTRACT',field.outputs[0],.495))
 edge=mathnode('LESS_THAN',dist,.0045);mask=mathnode('MULTIPLY',edge,gate)
 dark=n.new('ShaderNodeMixRGB');l.new(mask,dark.inputs[0]);l.new(existing.outputs[0],dark.inputs[1]);dark.inputs[2].default_value=rgb('#423735')
 # A second, thinner band on selected adjacent edges suggests exposed primer/light catching a lip.
 rimdist=mathnode('ABSOLUTE',mathnode('SUBTRACT',field.outputs[0],.501))
 rim=mathnode('MULTIPLY',mathnode('LESS_THAN',rimdist,.002),gate)
 highlight=n.new('ShaderNodeMixRGB');l.new(rim,highlight.inputs[0]);l.new(dark.outputs[0],highlight.inputs[1]);highlight.inputs[2].default_value=rgb('#b5a393');l.new(highlight.outputs[0],bs.inputs['Base Color'])
 # Drive coating relief from coating membership, not the brightness of its paint color.
 height=mathnode('LESS_THAN',field.outputs[0],.493)
 bump=next(x for x in n if x.type=='BUMP');l.new(height,bump.inputs['Height']);bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.002
 m['coating_revision']='041: fine amplitude .080, retained coarse variation, two brown layers and sparse substrate/lip accents'
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
(O/'settings.json').write_text(json.dumps({'fine_edge_amplitude':.080,'039_amplitude':.1,'040_amplitude':.028,'intermediate_threshold':.493,'top_threshold':.515,'brown_layers':['#968270','#b29a81'],'substrate':'#423735','lip':'#b5a393','relief_m':.002,'scope':'Front-left coatings; other geometry/materials/lighting unchanged'},indent=2))

exec(compile((R/"art/reviews/xenon-041/line-pass.py").read_text(),"line-pass.py","exec"))
