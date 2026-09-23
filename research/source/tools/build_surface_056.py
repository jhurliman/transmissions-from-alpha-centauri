import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/surface-056'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R/'art/reviews/xenon-055/scene.blend'),link=False) as (a,b):b.node_groups=[n for n in a.node_groups if n.startswith('051 ') or n=='048 Chromatic seam-fed runoff']
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(t/12.92 if t<=.04045 else ((t+.055)/1.055)**2.4 for t in v)+(1,)
def op(nt,kind,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(nt,a,b,f,kind='MIX'):
 n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type=kind
 for i,v in [(0,f),(1,a),(2,b)]:
  if isinstance(v,tuple):n.inputs[i].default_value=v
  elif isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def vec(nt,kind,a,b):
 n=nt.nodes.new('ShaderNodeVectorMath');n.operation=kind
 for i,v in [(0,a),(1,b)]:
  if isinstance(v,tuple):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def noise(nt,pos,scale,detail=2):
 n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail;n.inputs['Roughness'].default_value=.72;nt.links.new(pos,n.inputs['Vector']);return n
G=bpy.data.node_groups.new('056 Connected tonal islands','ShaderNodeTree')
for name,typ in [('Base','NodeSocketColor'),('Position','NodeSocketVector'),('Strength','NodeSocketFloat')]:G.interface.new_socket(name=name,in_out='INPUT',socket_type=typ)
for name,typ in [('Color','NodeSocketColor'),('Field','NodeSocketFloat')]:G.interface.new_socket(name=name,in_out='OUTPUT',socket_type=typ)
G.interface.items_tree['Strength'].default_value=1
nt=G;i=nt.nodes.new('NodeGroupInput');out=nt.nodes.new('NodeGroupOutput');pos=i.outputs['Position']
warp=noise(nt,pos,11,3);warped=vec(nt,'ADD',pos,vec(nt,'MULTIPLY',vec(nt,'SUBTRACT',warp.outputs['Color'],(.5,.5,.5)),(.16,.16,.16)))
medium=noise(nt,warped,2.6,2);fine=noise(nt,warped,27,1);field=op(nt,'ADD',op(nt,'MULTIPLY',medium.outputs['Fac'],.85),op(nt,'MULTIPLY',fine.outputs['Fac'],.15))
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.label='056 Related tonal islands';ramp.color_ramp.interpolation='CONSTANT'
stops=[(.0,(.54,.58,.67,1)),(.405,(.73,.77,.85,1)),(.47,(.93,.96,1,1)),(.53,(1.15,1.12,1.05,1)),(.595,(1.40,1.31,1.19,1))]
for j,(p,c) in enumerate(stops):
 e=ramp.color_ramp.elements[j] if j<2 else ramp.color_ramp.elements.new(p);e.position=p;e.color=c
nt.links.new(field,ramp.inputs[0]);quiet=noise(nt,pos,.65,1);coverage=op(nt,'ADD',.35,op(nt,'MULTIPLY',quiet.outputs['Fac'],.95));strength=op(nt,'MULTIPLY',coverage,i.outputs['Strength']);color=mix(nt,i.outputs['Base'],ramp.outputs[0],strength,'MULTIPLY');nt.links.new(color,out.inputs['Color']);nt.links.new(field,out.inputs['Field']);G.asset_mark();G.asset_data.description='Connected multiscale tonal islands; use on shaded surface color, including highlight regions. No images or bump.'
controls=[]
def material(name,base,pipe):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();geo=nt.nodes.new('ShaderNodeNewGeometry');dot=nt.nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';nt.links.new(geo.outputs['Normal'],dot.inputs[0]);dot.inputs[1].default_value=(.55,-.78,.30)
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements[0].position=-.1;ramp.color_ramp.elements[0].color=(.42,.44,.52,1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(1.18,1.16,1.10,1);nt.links.new(dot.outputs['Value'],ramp.inputs[0]);body=mix(nt,rgb(base),ramp.outputs[0],1,'MULTIPLY')
 tex=nt.nodes.new('ShaderNodeGroup');tex.node_tree=G;nt.links.new(geo.outputs['Position'],tex.inputs['Position']);nt.links.new(body,tex.inputs['Base']);tex.inputs['Strength'].default_value=0
 # A related field deforms the edges of broad highlight strips.
 full=nt.nodes.new('ShaderNodeValue');full.label='056 Stage';full.outputs[0].default_value=0
 probe=nt.nodes.new('ShaderNodeGroup');probe.node_tree=G;nt.links.new(geo.outputs['Position'],probe.inputs['Position'])
 perturb=op(nt,'MULTIPLY',op(nt,'SUBTRACT',probe.outputs['Field'],.5),op(nt,'MULTIPLY',full.outputs[0],.18))
 value=op(nt,'ADD',dot.outputs['Value'],perturb)
 band=op(nt,'GREATER_THAN',value,.91) if pipe else op(nt,'MULTIPLY',op(nt,'GREATER_THAN',value,.88),op(nt,'LESS_THAN',value,.96))
 highlighted=mix(nt,body,rgb('#b8b5ae'),op(nt,'MULTIPLY',band,.50 if pipe else .16))
 nt.links.new(highlighted,tex.inputs['Base'])
 wear=nt.nodes.new('ShaderNodeGroup');wear.node_tree=bpy.data.node_groups['051 Services | sparse enamel abrasions' if pipe else '051 Facade | clustered chips and short scars'];nt.links.new(tex.outputs['Color'],wear.inputs['Base']);weather=nt.nodes.new('ShaderNodeValue');weather.label='056 Additional wear';weather.outputs[0].default_value=0
 result=mix(nt,tex.outputs['Color'],wear.outputs[0],weather.outputs[0])
 if not pipe:
  sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);co=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(op(nt,'SUBTRACT',11.6,op(nt,'SUBTRACT',sep.outputs['X'],.20)),co.inputs['Y']);nt.links.new(op(nt,'SUBTRACT',sep.outputs['Z'],2.45),co.inputs['Z']);run=nt.nodes.new('ShaderNodeGroup');run.node_tree=bpy.data.node_groups['048 Chromatic seam-fed runoff'];nt.links.new(result,run.inputs['Base']);nt.links.new(co.outputs[0],run.inputs['Position']);nt.links.new(op(nt,'MULTIPLY',weather.outputs[0],.38),run.inputs['Strength']);result=run.outputs[0]
 em=nt.nodes.new('ShaderNodeEmission');nt.links.new(result,em.inputs[0]);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],o.inputs['Surface']);controls.append((tex,full,weather,pipe));return m
pipe=material('056 steel specimen','#434a5e',True);panel=material('056 blue facade specimen','#53556b',False)
def plain(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=rgb(color);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
dark=plain('056 Joint iron','#24232b')
# Continuous round bent pipe; same geometry in every stage.
curve=bpy.data.curves.new('056 Bent service pipe','CURVE');curve.dimensions='3D';curve.resolution_u=24;curve.bevel_depth=.32;curve.bevel_resolution=6;curve.use_fill_caps=True;sp=curve.splines.new('BEZIER');points=[(-.93,0,5.2),(-.93,0,2.45),(-.60,0,1.80),(-.15,0,1.10),(-.15,0,.25)];sp.bezier_points.add(len(points)-1)
for v,co in zip(sp.bezier_points,points):v.co=co;v.handle_left_type='AUTO';v.handle_right_type='AUTO'
o=bpy.data.objects.new('056 Pipe',curve);bpy.context.collection.objects.link(o);o.data.materials.append(pipe)
for z in [4.1,2.55]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.35,depth=.16,location=(-.93,0,z));o=bpy.context.object;o.name='056 Collar';o.data.materials.append(pipe)
 for dz in [-.09,.09]:
  bpy.ops.mesh.primitive_torus_add(major_radius=.333,minor_radius=.025,major_segments=64,minor_segments=8,location=(-.93,0,z+dz));bpy.context.object.data.materials.append(dark)
bpy.ops.mesh.primitive_cube_add(size=1,location=(1.25,.25,2.65));o=bpy.context.object;o.name='056 Flat panel';o.dimensions=(1.85,.14,4.95);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(panel);be=o.modifiers.new('Small folded edge','BEVEL');be.width=.025;be.segments=1
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1152;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('056 Neutral backdrop');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=rgb('#25242b')
bpy.ops.object.camera_add(location=(2.8,-15,6.0));cam=bpy.context.object;cam.rotation_euler=(Vector((.4,0,2.7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.2;s.camera=cam
s.render.use_freestyle=True;fs=s.view_layers[0].freestyle_settings
for ls in fs.linesets:
 if ls.linestyle is None:ls.linestyle=bpy.data.linestyles.new('056 Fine contour')
 ls.select_crease=False;ls.linestyle.color=(.008,.007,.012);ls.linestyle.alpha=.65;ls.linestyle.thickness=.8
for idx,name in enumerate(['clean','mottled','weathered']):
 for tex,stage,wear,ispipe in controls:
  tex.inputs['Strength'].default_value=(1.0 if ispipe else .60) if idx else 0;stage.outputs[0].default_value=1 if idx else 0;wear.outputs[0].default_value=1 if idx==2 else 0
 s.render.filepath=str(O/(name+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')));bpy.ops.render.render(write_still=True)
bpy.data.libraries.write(str(O/'connected-tonal-islands.blend'),{G},fake_user=True)
(O/'settings.json').write_text(json.dumps({'stages':['clean','mottled','weathered'],'medium_scale':2.6,'small_scale':27,'warp_amplitude_m':.16,'palette_multipliers':stops,'pipe_strength':1,'panel_strength':.6,'lighting':'Fixed orientation-based broad tones; existing accepted pigment colors','camera':list(cam.location),'geometry_fixed':True},indent=2))
