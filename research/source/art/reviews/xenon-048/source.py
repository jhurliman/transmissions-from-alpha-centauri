import bpy,json,random,math
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-048';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-047/scene.blend'));s=bpy.context.scene
G=bpy.data.node_groups.new('048 Chromatic seam-fed runoff','ShaderNodeTree')
for name,typ in [('Base','NodeSocketColor'),('Position','NodeSocketVector'),('Strength','NodeSocketFloat')]:G.interface.new_socket(name=name,in_out='INPUT',socket_type=typ)
G.interface.items_tree['Strength'].default_value=.65
G.interface.new_socket(name='Color',in_out='OUTPUT',socket_type='NodeSocketColor');inp=G.nodes.new('NodeGroupInput');out=G.nodes.new('NodeGroupOutput')
def op(kind,a,b=None):
 n=G.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:G.links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(f,a,b):
 n=G.nodes.new('ShaderNodeMixRGB');G.links.new(f,n.inputs[0])
 for i,v in enumerate([a,b],1):
  if isinstance(v,tuple):n.inputs[i].default_value=v
  else:G.links.new(v,n.inputs[i])
 return n.outputs[0]
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
xyz=G.nodes.new('ShaderNodeSeparateXYZ');G.links.new(inp.outputs['Position'],xyz.inputs[0]);x=op('SUBTRACT',11.6,xyz.outputs['Y']);z=xyz.outputs['Z']
coord=G.nodes.new('ShaderNodeVectorMath');coord.operation='MULTIPLY';coord.inputs[1].default_value=(2,47,9);G.links.new(inp.outputs['Position'],coord.inputs[0]);noise=G.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=3;G.links.new(coord.outputs[0],noise.inputs['Vector'])
rng=random.Random(4801);paths=[]
for ci,(cx,count) in enumerate([(.22,3),(.64,2),(1.20,4),(1.91,2),(2.53,3)]):
 for j in range(count):
  paths.append({'x':cx+([0,-.028,.041,.078][j]),'start':2.639,'length':rng.uniform(.65,2.4) if j else [2.36,1.27,2.21,.92,1.81][ci],'radius':rng.uniform(.004,.012) if j else .015,'phase':rng.uniform(0,6.28),'mode':'dark' if (ci+j)%4==0 else 'chromatic','origin':'upper panel edge / bearing runoff'})
for ci,cx in enumerate([.40,1.63,2.27]):
 for j in range(2):paths.append({'x':cx+j*.033,'start':1.339,'length':rng.uniform(.38,1.12),'radius':rng.uniform(.006,.013),'phase':rng.uniform(0,6.28),'mode':'chromatic' if j==0 else 'dark','origin':'horizontal panel seam'})
chrom=0;dark=0
for p in paths:
 dz=op('SUBTRACT',p['start'],z);t=op('DIVIDE',dz,p['length'])
 # Near-vertical paths with tiny wandering, uneven widths and broken tails.
 wiggle=op('MULTIPLY',op('SINE',op('ADD',op('MULTIPLY',z,17),p['phase'])),.0025)
 dist=op('ABSOLUTE',op('SUBTRACT',op('SUBTRACT',x,p['x']),wiggle))
 width=op('MULTIPLY',p['radius'],op('ADD',.4,op('MULTIPLY',noise.outputs['Fac'],1.15)))
 edge=op('MINIMUM',1,op('MAXIMUM',op('MULTIPLY',op('SUBTRACT',1,op('DIVIDE',dist,width)),3.5),0))
 taper=op('MINIMUM',1,op('MAXIMUM',op('MULTIPLY',op('SUBTRACT',1,t),3),0))
 gate=op('MULTIPLY',op('GREATER_THAN',dz,-.003),taper)
 broken=op('MINIMUM',1,op('MAXIMUM',op('MULTIPLY',op('SUBTRACT',noise.outputs['Fac'],.40),5.2),0))
 mask=op('MULTIPLY',edge,op('MULTIPLY',gate,broken))
 if p['mode']=='dark':dark=op('MAXIMUM',dark,mask)
 else:chrom=op('MAXIMUM',chrom,mask)
# Color response depends on the existing coating, rather than painting one brown over every material.
sep=G.nodes.new('ShaderNodeSeparateColor');sep.mode='RGB';G.links.new(inp.outputs['Base'],sep.inputs[0]);warm=op('MINIMUM',1,op('MAXIMUM',op('ADD',.5,op('MULTIPLY',op('SUBTRACT',sep.outputs['Red'],sep.outputs['Blue']),12)),0))
tint=mix(warm,rgb('#947662'),rgb('#747d95'))
color=mix(op('MULTIPLY',chrom,inp.outputs['Strength']),inp.outputs['Base'],tint)
shade=G.nodes.new('ShaderNodeMixRGB');shade.blend_type='MULTIPLY';shade.inputs[0].default_value=1;shade.inputs[2].default_value=(.66,.69,.73,1);G.links.new(inp.outputs['Base'],shade.inputs[1]);color=mix(op('MULTIPLY',dark,inp.outputs['Strength']),color,shade.outputs[0]);G.links.new(color,out.inputs[0])
changed=[]
for m in list(bpy.data.materials):
 if not m.name.startswith('047 Seam loss'):continue
 nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=bs.inputs['Base Color'].links[0].from_socket
 node=nt.nodes.new('ShaderNodeGroup');node.node_tree=G;node.label='Chromatic runoff — independent layer';node.inputs['Strength'].default_value=.65;geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(base,node.inputs['Base']);nt.links.new(geo.outputs['Position'],node.inputs['Position']);nt.links.new(node.outputs[0],bs.inputs['Base Color']);changed.append(m.name)
G.asset_mark();G['rules']='Seam-fed clusters, unequal finite lengths, coherent world-space paths across panels; tint reacts to warm/cool coating; no black ink.'
(O/'audit.json').write_text(json.dumps({'paths':paths,'materials':changed,'strength':.65,'colors_srgb':{'warm':'#947662','cool':'#747d95','dark':'Local base multiplied by (.66,.69,.73)'},'geometry':'Unchanged from approved 047','scope':'Two-panel bay only; world alignment allows uninterrupted vertical paths at its shared seam'},indent=2))
mainloc=s.camera.location.copy();mainrot=s.camera.rotation_euler.copy();mainlens=s.camera.data.lens
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'runoff-material-group.blend'),{G},fake_user=True)
def proof(name,loc,aim,lens):
 s.camera.location=loc;s.camera.rotation_euler=(Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.resolution_x=1100;s.render.resolution_y=950;s.render.use_freestyle=False;s.cycles.samples=32;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
proof('panel-detail',(6,9.35,1.8),(9.85,10.2,1.35),44)
proof('runoff-detail',(8.1,10.6,1.55),(9.85,10.3,1.15),57)
s.camera.location=mainloc;s.camera.rotation_euler=mainrot;s.camera.data.lens=mainlens;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.use_freestyle=True;s.render.filepath=str(O/'render.png');bpy.ops.render.render(write_still=True)
