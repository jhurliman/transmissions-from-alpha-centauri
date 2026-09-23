import bpy,math
def apply(s):
 for ma in bpy.data.materials:
  if ma.name not in ['075 soil palette','077 earth fracture interior','077 illuminated earth lips']:continue
  n=ma.node_tree.nodes;l=ma.node_tree.links
  vor=next((q for q in n if q.type=='TEX_VORONOI' and abs(q.inputs['Scale'].default_value-18)<.01),None)
  if not vor:continue
  vor.inputs['Scale'].default_value=24
  for q in n:
   if q.type=='MIX_RGB' and q.blend_type=='MULTIPLY' and abs(q.inputs[0].default_value-.30)<.001 and not q.inputs[0].is_linked:q.inputs[0].default_value=.45
  less=next((q for q in n if q.type=='MATH' and q.operation=='LESS_THAN' and q.inputs[0].is_linked and q.inputs[0].links[0].from_node==vor),None)
  if less:
   noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=2;l.new(vor.inputs[0].links[0].from_socket,noise.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=.25;r.inputs['From Max'].default_value=.75;r.inputs['To Min'].default_value=.09;r.inputs['To Max'].default_value=.29;r.clamp=True;l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],less.inputs[1])
  for q in n:
   if q.type=='MIX_RGB' and tuple(round(v,2) for v in q.inputs[2].default_value[:3])==(.47,.43,.4):q.inputs[2].default_value=(.62,.58,.54,1)
  # Continuous multiscale mineral grain adds both light and dark pigment variation.
  em=next(q for q in n if q.type=='EMISSION');base=em.inputs[0].links[0].from_socket
  co=n.new('ShaderNodeTexCoord');grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=15;grain.inputs['Detail'].default_value=3;grain.inputs['Roughness'].default_value=.7;l.new(co.outputs['Object'],grain.inputs[0]);r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.3;r.inputs['From Max'].default_value=.7;r.inputs['To Min'].default_value=.5;r.inputs['To Max'].default_value=1.5;l.new(grain.outputs['Fac'],r.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(base,mix.inputs[1]);l.new(r.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0])
 # More buried colored chips at bases, quieter patches in the accumulation band.
 hidden=0
 for ob in s.objects:
  if not ob.name.startswith('077 embedded stone'):continue
  cx=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices);cy=sum(v.co.y for v in ob.data.vertices)/len(ob.data.vertices)
  if abs(cx)>7.25:
   ob.location.z-=.009
   if math.sin(cy*.71+cx*.8)>.8:ob.hide_render=True;hidden+=1
 return {'quiet_patch_stones_hidden':hidden,'grit':'variable size lower coverage and contrast'}
