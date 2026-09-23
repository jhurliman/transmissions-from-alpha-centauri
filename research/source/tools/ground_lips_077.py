import bpy
def apply(s):
 source=bpy.data.materials['075 soil palette'];m=source.copy();m.name='077 illuminated earth lips';n=m.node_tree.nodes;l=m.node_tree.links;e=next(q for q in n if q.type=='EMISSION');base=e.inputs[0].links[0].from_socket
 d=n.new('ShaderNodeBsdfDiffuse');d.inputs[0].default_value=(1,1,1,1);sr=n.new('ShaderNodeShaderToRGB');l.new(d.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.3;r.inputs['From Max'].default_value=.85;r.inputs['To Max'].default_value=.20;l.new(bw.outputs[0],r.inputs[0]);mx=n.new('ShaderNodeMixRGB');l.new(r.outputs[0],mx.inputs[0]);l.new(base,mx.inputs[1]);mx.inputs[2].default_value=(.28,.16,.09,1);l.new(mx.outputs[0],e.inputs[0])
 count=0
 for o in s.objects:
  if o.name.startswith('077 broken earth lip'):o.data.materials.clear();o.data.materials.append(m);count+=1
 return count
