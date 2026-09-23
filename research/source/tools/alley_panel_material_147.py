"""Native panel pigment/roughness variation with real diffuse+specular light response."""
import bpy

def make_panel_material(name='147 Sun-responsive slate panel',origin=(0,0,0),across=(1,0,0),up=(0,0,1),span=(4.546,1.42),panel_regions=None):
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
 broad=math('MAXIMUM',r1,math('MULTIPLY',r2,.83))
 # Actual panel-local bases weight fine splotches; macro age field continues across panels.
 bottom=0
 if panel_regions:
  for p in panel_regions:
   delta=tuple(p['origin'][k]-origin[k] for k in range(3));pu=sum(delta[k]*across[k]for k in range(3));pv=sum(delta[k]*up[k]for k in range(3));h=p['height'];w=p['width'];lu=math('SUBTRACT',u,pu);lv=math('SUBTRACT',v,pv)
   gate=math('MULTIPLY',math('MULTIPLY',math('GREATER_THAN',lu,0),math('LESS_THAN',lu,w)),math('MULTIPLY',math('GREATER_THAN',lv,-.006),math('LESS_THAN',lv,h)))
   bottom=math('MAXIMUM',bottom,math('MULTIPLY',gate,remap(lv,h*.06,h*.62,1,0)))
 else:
  phase=math('FLOORED_MODULO',v,1.42);bottom=remap(phase,.06,1.0,1,0)
 fleck_pos=vec('MULTIPLY',pos,(1.20,.78,1));fleck=noise(fleck_pos,17,3,.72);fray=noise(pos,55,2,.66)
 pattern=math('ADD',math('MULTIPLY',fleck.outputs['Fac'],.77),math('MULTIPLY',fray.outputs['Fac'],.23));pattern.node.label='147 Fine splatter noise field';bottom.node.label='147 Panel base weight';islands=remap(pattern,0.515872577333,0.566872577333);holes=remap(pattern,0.398800273355,0.488800273355,1,0) # Calibrated density thresholds
 retained=math('MULTIPLY',broad,math('SUBTRACT',1,math('MULTIPLY',math('MULTIPLY',holes,bottom),.42)))
 mask=math('MAXIMUM',retained,math('MULTIPLY',math('MULTIPLY',islands,bottom),.94));mask.node.label='147 Broad fields plus bottom-weighted fine splotches'
 # Same cool substrate everywhere; spatial field changes how strongly warm light is picked up.
 rough=math('ADD',remap(mask,0,1,.83,.42),math('MULTIPLY',math('SUBTRACT',directional.outputs['Fac'],.5),.065));diff=node('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.75,.75,.75,1);drgb=node('ShaderNodeShaderToRGB');l.new(diff.outputs[0],drgb.inputs[0]);dbw=node('ShaderNodeRGBToBW');l.new(drgb.outputs[0],dbw.inputs[0]);illum=remap(dbw.outputs[0],.02,1.2,.42,1.1)
 gloss=node('ShaderNodeBsdfGlossy','147 Actual local specular response');gloss.inputs['Color'].default_value=(.7,.7,.7,1);l.new(rough,gloss.inputs['Roughness']);grgb=node('ShaderNodeShaderToRGB');l.new(gloss.outputs[0],grgb.inputs[0]);gbw=node('ShaderNodeRGBToBW');l.new(grgb.outputs[0],gbw.inputs[0]);spec=remap(gbw.outputs[0],.16,.82)
 # Warmness requires actual red-biased incident light; no warm field in a cool unlit test.
 sep=node('ShaderNodeSeparateColor');l.new(drgb.outputs[0],sep.inputs[0]);warm_light=remap(math('SUBTRACT',sep.outputs['Red'],sep.outputs['Blue']),.01,.30)
 susceptibility=math('MAXIMUM',spec,math('MULTIPLY',mask,.76));warm=math('MULTIPLY',susceptibility,warm_light)
 body=mix(warm,(.155,.175,.235,1),(.34,.235,.18,1),'147 Sun-dependent cool-to-warm coating response');body=mix(1,body,illum,'147 Actual diffuse value','MULTIPLY');body=mix(.065,body,fine.outputs['Fac'],'147 Fine retained coating grain','MULTIPLY');sheen=math('MULTIPLY',mask,remap(dbw.outputs[0],.10,.70,0,.42));lift=mix(1,body,(1.38,1.38,1.38,1),'147 Broad-light sheen value','MULTIPLY');body=mix(sheen,body,lift,'147 Lightening response retains fine pattern in cool fill')
 ao=node('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.12;shadow=remap(ao.outputs['AO'],.15,.85,.60,1);body=mix(1,body,shadow,'147 Local physical recess shadow','MULTIPLY')
 em=node('ShaderNodeEmission','147 Surface color before optional weathering');l.new(body,em.inputs[0]);out=node('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs['Surface']);m['147 material']='Broad and fine bottom-weighted susceptibility with actual warm-incident-light and specular response; no unlit warm field';return m
