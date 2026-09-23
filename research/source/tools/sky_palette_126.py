"""User sky-colorstrip: median palette, gradient to roofline then constant, native cloud remap."""
import bpy
from sky_gradient_125 import apply as ensure_camera_gradient,linear
SKY_TOP=(227,86,53)
SKY_BOTTOM=(236,99,63)
CLOUD_PALETTE=[(193,77,56),(204,81,56),(215,92,61)]
def apply():
 s=bpy.context.scene
 if s.world.get('126 sky palette revision')==2:return {'already_applied':True,'revision':2}
 ensure_camera_gradient();s.world=s.world.copy();w=s.world;nt=w.node_tree;n=nt.nodes;l=nt.links;base=next(q for q in n if q.label=='075 Amber horizon to vermilion zenith');bg=next(q for q in n if q.label=='075 Camera sky only');strength=bg.inputs['Strength'].default_value
 old={'sky_ramp':[{'position':e.position,'linear':list(e.color)}for e in base.color_ramp.elements]};factor=base.inputs[0].links[0].from_socket;q=next((x for x in n if x.label=='126 Strip top fifth, solid below roofline'),None)
 if q is None:
  q=n.new('ShaderNodeMath');q.operation='MULTIPLY_ADD';q.label='126 Strip top fifth, solid below roofline';q.inputs[1].default_value=5.;q.inputs[2].default_value=-4.;l.new(factor,q.inputs[0])
 l.new(q.outputs[0],base.inputs[0]);base.color_ramp.elements[0].color=tuple(linear(v)/strength for v in SKY_BOTTOM)+(1,);base.color_ramp.elements[1].color=tuple(linear(v)/strength for v in SKY_TOP)+(1,)
 C=bpy.data.collections.get('082 Derived flat clouds')
 if C is None:raise RuntimeError('Expected approved derived cloud collection')
 cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   oldmat=slot.material
   if oldmat not in cache:
    m=oldmat.copy();m.name='126 Strip palette '+oldmat.name;mn=m.node_tree.nodes;ml=m.node_tree.links;tex=next(x for x in mn if x.type=='TEX_IMAGE');em=next(x for x in mn if x.type=='EMISSION');sep=mn.new('ShaderNodeSeparateColor');sep.mode='RGB';sep.label='126 Native pigment luminance family';ml.new(tex.outputs['Color'],sep.inputs[0]);r=mn.new('ShaderNodeValToRGB');r.label='126 Strip dark interior, middle, light exterior';r.color_ramp.interpolation='LINEAR';r.color_ramp.elements.new(.5)
    for e,source,target in zip(list(r.color_ramp.elements),[198,204,210],CLOUD_PALETTE):e.position=linear(source);e.color=tuple(linear(v)for v in target)+(1,)
    ml.new(sep.outputs[0],r.inputs[0]);ml.new(r.outputs['Color'],em.inputs['Color']);cache[oldmat]=m
   slot.link='OBJECT';slot.material=cache[oldmat];rows.append({'object':ob.name,'old_material':oldmat.name,'new_material':cache[oldmat].name})
 w['126 reference sky palette']=True;w['126 sky palette revision']=2;w['126 gradient ends at top-frame fraction']=.20
 return {'reference':'references/user-coliseum/sky-colorstrip.png','strip_size':[21,208],'measurement':'Sky endpoints are authoritative user Photoshop picks, overriding prior regional medians. Muted cloud palette retains the three representative strip populations.','target_sky_top_srgb':list(SKY_TOP),'target_sky_bottom_srgb':list(SKY_BOTTOM),'target_cloud_dark_middle_light_srgb':[list(c)for c in CLOUD_PALETTE],'source_cloud_srgb':[[198,58,40],[204,62,41],[210,67,43]],'mapping':'Gradient from frame top y0 to y0.20, then bottom sky color held constant; existing street/far-city haze untouched','old':old,'cloud_assignments':rows,'new_cloud_materials':len(cache),'native_shader_only':True,'source_cloud_images_unchanged':True,'preserved':'Sun branch, clouds shapes/alpha/UV/layout, non-camera lighting and all geometry; global color management unchanged','interpretation':'Roofline approximation0.20 agreed with root. Latest user Photoshop sky picks override the regional medians; cloud palette unchanged. Difference comes from using different sampling methods/locations, not a supported ICC explanation.', 'superseded_sky_regional_medians':{'top':[225,86,55],'bottom':[235,97,60]},'authoritative_sky_hex':{'top':'#e35635','bottom':'#ec633f'}}
