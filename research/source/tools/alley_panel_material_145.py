"""Native panel pigment/roughness variation with real diffuse+specular light response."""
import bpy

def make_panel_material(name='145 Sun-responsive slate panel',origin=(0,0,0),across=(1,0,0),up=(0,0,1),span=(4.546,1.42)):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 def node(t,label=''):q=n.new(t);q.label=label;return q
 def math(op,*vs):
  q=node('ShaderNodeMath');q.operation=op
  for i,v in enumerate(vs):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def vec(op,a,b):
  q=node('ShaderNodeVectorMath');q.operation=op
  for i,v in enumerate([a,b]):
   if isinstance(v,(tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs['Value']if op=='DOT_PRODUCT'else q.outputs['Vector']
 def noise(pos,scale,detail=2,rough=.65):
  q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=rough;l.new(pos,q.inputs['Vector']);return q
 def remap(v,a,b,c=0,d=1):
  q=node('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(v,q.inputs[0]);q.inputs[1].default_value=a;q.inputs[2].default_value=b;q.inputs[3].default_value=c;q.inputs[4].default_value=d;return q.outputs[0]
 def mix(f,a,b,label='',op='MIX'):
  q=node('ShaderNodeMixRGB',label);q.blend_type=op
  for i,v in enumerate([f,a,b]):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   elif isinstance(v,(tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 geo=node('ShaderNodeNewGeometry');rel=vec('SUBTRACT',geo.outputs['Position'],origin);u=vec('DOT_PRODUCT',rel,across);v=vec('DOT_PRODUCT',rel,up);xy=node('ShaderNodeCombineXYZ');l.new(u,xy.inputs['X']);l.new(v,xy.inputs['Y']);pos=xy.outputs[0]
 # Two composed elongated susceptibility regions across the panel group.
 # Convex native polygon fields avoid fractal island/satellite organization.
 fine=noise(pos,85,2);edge=noise(pos,24,1.5);U=math('DIVIDE',u,span[0]);V=math('DIVIDE',v,span[1]);medium=noise(pos,2.8,2,.7);directional=noise(pos,5.5,1.3,.6)
 def region(points):
  import math as pymath
  distances=[]
  for (ax,ay),(bx,by) in zip(points,points[1:]+points[:1]):
   ex,ey=bx-ax,by-ay;norm=pymath.hypot(ex,ey)
   d=math('DIVIDE',math('SUBTRACT',math('MULTIPLY',ex,math('SUBTRACT',V,ay)),math('MULTIPLY',ey,math('SUBTRACT',U,ax))),norm);distances.append(d)
  signed=distances[0]
  for d in distances[1:]:signed=math('MINIMUM',signed,d)
  signed=math('ADD',signed,math('ADD',math('MULTIPLY',math('SUBTRACT',edge.outputs['Fac'],.5),.020),math('MULTIPLY',math('SUBTRACT',medium.outputs['Fac'],.5),.09)))
  return remap(signed,-.045,.065)
 r1=region([(-.12,.06),(.12,-.14),(.67,.73),(.51,1.15),(.24,.72)])
 r2=region([(.64,-.09),(1.12,.12),(1.13,.50),(.91,.48),(.71,.22)])
 mask=math('MAXIMUM',r1,math('MULTIPLY',r2,.83));mask.node.label='145 Composed cross-panel susceptibility regions'
 # Same cool substrate everywhere; spatial field changes how strongly warm light is picked up.
 rough=math('ADD',remap(mask,0,1,.83,.42),math('MULTIPLY',math('SUBTRACT',directional.outputs['Fac'],.5),.065));diff=node('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.75,.75,.75,1);drgb=node('ShaderNodeShaderToRGB');l.new(diff.outputs[0],drgb.inputs[0]);dbw=node('ShaderNodeRGBToBW');l.new(drgb.outputs[0],dbw.inputs[0]);illum=remap(dbw.outputs[0],.02,1.2,.42,1.1)
 gloss=node('ShaderNodeBsdfGlossy','145 Actual local specular response');gloss.inputs['Color'].default_value=(.7,.7,.7,1);l.new(rough,gloss.inputs['Roughness']);grgb=node('ShaderNodeShaderToRGB');l.new(gloss.outputs[0],grgb.inputs[0]);gbw=node('ShaderNodeRGBToBW');l.new(grgb.outputs[0],gbw.inputs[0]);spec=remap(gbw.outputs[0],.16,.82)
 # Warmness requires actual red-biased incident light; no warm field in a cool unlit test.
 sep=node('ShaderNodeSeparateColor');l.new(drgb.outputs[0],sep.inputs[0]);warm_light=remap(math('SUBTRACT',sep.outputs['Red'],sep.outputs['Blue']),.01,.30)
 susceptibility=spec;warm=math('MULTIPLY',susceptibility,warm_light)
 body=mix(warm,(.155,.175,.235,1),(.34,.235,.18,1),'145 Sun-dependent cool-to-warm coating response');body=mix(1,body,illum,'145 Actual diffuse value','MULTIPLY');body=mix(.065,body,fine.outputs['Fac'],'145 Fine retained coating grain','MULTIPLY')
 ao=node('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.12;shadow=remap(ao.outputs['AO'],.15,.85,.60,1);body=mix(1,body,shadow,'145 Local physical recess shadow','MULTIPLY')
 em=node('ShaderNodeEmission','145 Surface color before optional weathering');l.new(body,em.inputs[0]);out=node('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs['Surface']);m['145 material']='Spatial roughness/susceptibility with actual diffuse+glossy response; no fixed warm albedo mask';return m
