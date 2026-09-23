"""Attached native fine-detail pass over accepted E materials; retain all geometry/slots."""
import bpy

def refine(collection,strength=1.):
 cache={};audit=[]
 for ob in collection.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   src=slot.material
   if not src:continue
   if src in cache:slot.material=cache[src];continue
   m=src.copy();m.name='116 '+src.name;cache[src]=m;slot.material=m
   n=m.node_tree.nodes;l=m.node_tree.links
   pal=next((q for q in n if q.label=='Warm exposed stone, violet recesses'),None)
   if not pal:continue
   # Stronger actual light/shadow contribution retains orientation-painted base.
   light=pal.inputs[0].links[0].from_node
   for link in light.inputs:
    if link.is_linked:
     q=link.links[0].from_node
     if q.type=='MATH' and q.operation=='MULTIPLY':
      for socket in q.inputs:
       if not socket.is_linked:
        if abs(socket.default_value-.92)<.001:socket.default_value=.92-.10*strength
        elif abs(socket.default_value-.08)<.001:socket.default_value=.08+.10*strength
   # The existing fine fleck breakup already interrupts worn catches. Raise its
   # light-driven strength instead of adding an all-edge outline/highlight.
   spec=next((q for q in n if q.label=='Restrained worn edge catch'),None)
   if spec:
    spec.inputs['Roughness'].default_value=.54-.09*strength
    st=next(q for q in n if q.bl_idname=='ShaderNodeShaderToRGB' and any(x.from_node==spec for x in q.inputs[0].links))
    bw=next(q for q in n if q.bl_idname=='ShaderNodeRGBToBW' and any(x.from_node==st for x in q.inputs[0].links))
    # Trace descendants; replace the original .21 multiplier only.
    frontier=[bw];seen=set()
    for _ in range(12):
     nxt=[]
     for node in frontier:
      if node in seen:continue
      seen.add(node)
      if node.type=='MATH' and node.operation=='MULTIPLY':
       for inp in node.inputs:
        if not inp.is_linked and abs(inp.default_value-.21)<.0001:inp.default_value=.21+.20*strength
      for out in node.outputs:
       nxt.extend(k.to_node for k in out.links)
     frontier=nxt
   # Broad pigment varies by finite attached patches with hard/soft brush edges.
   # Restrict it to lit surface interiors, retaining quiet dark tunnels.
   attr=n.new('ShaderNodeAttribute');attr.attribute_name='115 Original world position'
   noise=n.new('ShaderNodeTexNoise');noise.label='Broad mineral wash islands';noise.inputs['Scale'].default_value=.22;noise.inputs['Detail'].default_value=1.2;noise.inputs['Roughness'].default_value=.65;l.new(attr.outputs['Vector'],noise.inputs['Vector'])
   ramp=n.new('ShaderNodeValToRGB');ramp.label='Sparse mineral wash coverage';ramp.color_ramp.elements[0].position=.48;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.62;ramp.color_ramp.elements[1].color=(.16*strength,)*3+(1,);l.new(noise.outputs['Fac'],ramp.inputs[0])
   gate=n.new('ShaderNodeMapRange');gate.clamp=True;gate.inputs['From Min'].default_value=.35;gate.inputs['From Max'].default_value=.70;l.new(light.outputs[0],gate.inputs['Value'])
   fac=n.new('ShaderNodeMath');fac.operation='MULTIPLY';l.new(ramp.outputs[0],fac.inputs[0]);l.new(gate.outputs[0],fac.inputs[1])
   em=next(q for q in n if q.type=='EMISSION');old=em.inputs[0].links[0].from_socket
   mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.88,.80,.86,1);l.new(old,mix.inputs[1]);l.new(fac.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],em.inputs[0])
   audit.append({'material':m.name,'strength':strength,'slots_preserved':True,'attached_coordinate_attribute':attr.attribute_name})
 return audit
