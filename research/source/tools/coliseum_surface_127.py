"""Measured-scale painted stone grain using the existing native light response."""
import bpy

def apply(C,strength=.7):
 cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or not any(n.label=='Warm exposed stone, violet recesses' for n in old.node_tree.nodes):continue
   if old not in cache:
    m=old.copy();m.name='127 Mineral pigment '+old.name;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
    # Bring existing subpixel grain up to a legible painted scale. No extra geometry.
    for q in n:
     if q.label=='Fine stone pits and dry pigment':q.inputs['Scale'].default_value=2.3
     if q.label=='Connected worn pigment islands':q.inputs['Scale'].default_value=.6
    em=next(x for x in n if x.type=='EMISSION');base=em.inputs[0].links[0].from_socket
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='115 Original world position';attr.label='127 Stable original pigment position'
    grain=n.new('ShaderNodeTexNoise');grain.label='127 Broken sponge pigment at 4K scale';grain.inputs['Scale'].default_value=1.65;grain.inputs['Detail'].default_value=2.;grain.inputs['Roughness'].default_value=.72;l.new(attr.outputs['Vector'],grain.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.label='127 Muted light and dark mineral flecks';ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements[0].position=.27;ramp.color_ramp.elements[0].color=(1.10,1.08,1.05,1);ramp.color_ramp.elements[1].position=.68;ramp.color_ramp.elements[1].color=(.61,.62,.66,1);mid=ramp.color_ramp.elements.new(.48);mid.color=(1.,1.,1.,1);l.new(grain.outputs['Fac'],ramp.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.label='127 Painted grain preserves physical lighting';depth=n.new('ShaderNodeAttribute');depth.attribute_name='120 Actual arch tunnel depth';depth.label='127 Preserve quiet dark arch returns';gate=n.new('ShaderNodeMapRange');gate.clamp=True;gate.inputs['From Min'].default_value=.10;gate.inputs['From Max'].default_value=.30;gate.inputs['To Min'].default_value=.65*strength;gate.inputs['To Max'].default_value=.65*strength*.35;l.new(depth.outputs['Fac'],gate.inputs['Value']);l.new(gate.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(ramp.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'old':old.name,'new':cache[old].name})
 return {'strength':strength,'materials':len(cache),'assignments':rows,'geometry_unchanged':True,'native_texture_coordinates':'115 Original world position','study_status':'Separate painted grain study, not user approved'}
