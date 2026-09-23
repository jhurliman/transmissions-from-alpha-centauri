import bpy,json,sys,math
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-050';O.mkdir(exist_ok=True)
variant=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'hybrid'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-049/scene.blend'));s=bpy.context.scene
# Probe options are converted to EEVEE for true shadow-aware light remapping.
s.render.engine='CYCLES' if variant=='baseline' else 'BLENDER_EEVEE'
settings={
 'cel':('CONSTANT',[(0,(.43,.44,.58,1)),(.30,(.73,.75,.88,1)),(.65,(1.20,1.12,1.02,1))],1.15,.90),
 'painted':('EASE',[(0,(.46,.47,.62,1)),(.25,(.68,.70,.82,1)),(.43,(.92,.93,1,1)),(.70,(1.20,1.12,1.02,1))],.65,.62),
 'hybrid':('EASE',[(0,(.22,.23,.33,1)),(.24,(.29,.31,.43,1)),(.31,(.80,.83,.95,1)),(.61,(.88,.90,1,1)),(.68,(1.22,1.13,1.03,1))],.95,.82)
}
interp,stops,thick,alpha=settings[variant]
modified=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree
 bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs:continue
 # Preserve all base color procedural graphs, including coating, runoff and corrosion.
 base=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
 if base is None:
  c=nt.nodes.new('ShaderNodeRGB');c.outputs[0].default_value=bs.inputs['Base Color'].default_value;base=c.outputs[0]
 diffuse=nt.nodes.new('ShaderNodeBsdfDiffuse');diffuse.inputs['Color'].default_value=(1,1,1,1);diffuse.inputs['Roughness'].default_value=0
 light=nt.nodes.new('ShaderNodeShaderToRGB');nt.links.new(diffuse.outputs[0],light.inputs[0])
 bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(light.outputs[0],bw.inputs[0])
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.label='050 '+variant+' painted light';ramp.color_ramp.interpolation=interp
 # EEVEE irradiance of a white diffuse surface is used only as a shadow selector.
 for i,(pos,col) in enumerate(stops):
  e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=tuple(c*.72 for c in col[:3])+(1,)
 nt.links.new(bw.outputs[0],ramp.inputs[0])
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;nt.links.new(base,mix.inputs[1]);nt.links.new(ramp.outputs[0],mix.inputs[2])
 color=mix.outputs[0]
 if variant=='hybrid':
  ao=nt.nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.65;ao.samples=16
  cavity=nt.nodes.new('ShaderNodeValToRGB');cavity.label='050 Local recess shadow';cavity.color_ramp.interpolation='EASE'
  cavity.color_ramp.elements[0].position=.25;cavity.color_ramp.elements[0].color=(.30,.31,.40,1)
  cavity.color_ramp.elements[1].position=.85;cavity.color_ramp.elements[1].color=(1,1,1,1)
  nt.links.new(ao.outputs['AO'],cavity.inputs[0]);cm=nt.nodes.new('ShaderNodeMixRGB');cm.blend_type='MULTIPLY';cm.inputs[0].default_value=1
  nt.links.new(color,cm.inputs[1]);nt.links.new(cavity.outputs[0],cm.inputs[2]);color=cm.outputs[0]
 em=nt.nodes.new('ShaderNodeEmission');nt.links.new(color,em.inputs['Color'])
 for link in list(bs.outputs[0].links):nt.links.new(em.outputs[0],link.to_socket)
 modified.append(m.name)
for o in s.objects:
 if o.type=='LIGHT' and o.data.type=='SUN':o.data.angle=math.radians(1.2)
s.render.use_freestyle=True
for ls in s.view_layers[0].freestyle_settings.linesets:
 ls.linestyle.thickness=thick;ls.linestyle.alpha=alpha;ls.linestyle.color=(.014,.010,.018)
 # Silhouettes and borders only; bevel creases would overdraw the kit.
 ls.select_crease=False
 fs=s.view_layers[0].freestyle_settings
 fs.crease_angle=math.radians(110)
 detail=fs.linesets.new('050 Fine structural creases')
 detail.select_silhouette=False;detail.select_border=False;detail.select_contour=False;detail.select_external_contour=False;detail.select_crease=True
 detail.linestyle.color=(.022,.017,.028);detail.linestyle.thickness=.55;detail.linestyle.alpha=.72
 break
for lines in s.view_layers[0].freestyle_settings.linesets:
 mod=lines.linestyle.alpha_modifiers.new('050 Distance fade','DISTANCE_FROM_CAMERA');mod.range_min=30;mod.range_max=240
 mod.mapping='LINEAR';mod.invert=True
s.render.filepath=str(O/(variant+'.png'))
(O/(variant+'-audit.json')).write_text(json.dumps({'variant':variant,'materials':modified,'engine':s.render.engine,'camera':list(s.camera.location),'lens':s.camera.data.lens,'light_ramp':stops,'line_width':thick,'geometry_changed':False},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/(variant+'.blend')))
bpy.ops.render.render(write_still=True)
