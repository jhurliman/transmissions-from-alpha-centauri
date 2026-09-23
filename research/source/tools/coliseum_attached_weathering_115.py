"""Keep existing native weathering anchored through a whole-landmark affine transform."""
from mathutils import Matrix

def attach_weathering(collection,world_transform):
 inv=Matrix(world_transform).inverted();mats={m for o in collection.objects if o.type=='MESH' for m in o.data.materials if m and m.use_nodes};count=0
 for mat in mats:
  nodes=mat.node_tree.nodes;links=mat.node_tree.links
  unscale=next((n for n in nodes if n.label=='Preserve authored weathering scale'),None)
  if not unscale:continue
  g=next(n for n in nodes if n.type=='NEW_GEOMETRY');combine=nodes.new('ShaderNodeCombineXYZ');combine.label='Original masonry coordinates'
  for i in range(3):
   dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=tuple(inv[i][:3]);links.new(g.outputs['Position'],dot.inputs[0])
   add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=inv[i][3];links.new(dot.outputs['Value'],add.inputs[0]);links.new(add.outputs[0],combine.inputs[i])
  links.new(combine.outputs[0],unscale.inputs[0]);count+=1
 return count
