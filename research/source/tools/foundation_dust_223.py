"""Native pale-soil deposition over bank rock colors; geometry and road rocks unchanged."""
import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/foundation-dust-223'
from coliseum_ink_isolation_130 import _copy_props

def bank_color_group(material,leaf):
 tree=material.node_tree;needed=set()
 def visit(n):
  if n in needed:return
  needed.add(n)
  for sock in n.inputs:
   for link in sock.links:visit(link.from_node)
 visit(leaf);g=bpy.data.node_groups.new('223 Exact native pale-soil color','ShaderNodeTree');g.interface.new_socket(name='Color',in_out='OUTPUT',socket_type='NodeSocketColor');mapped={}
 for n in needed:
  q=g.nodes.new(n.bl_idname);_copy_props(n,q,{'parent','location','inputs','outputs','internal_links','color_ramp'});q.name=n.name;q.label=n.label;mapped[n]=q
  for i,sock in enumerate(n.inputs):
   if hasattr(sock,'default_value'):
    try:q.inputs[i].default_value=sock.default_value
    except(TypeError,ValueError,IndexError):pass
  if n.type=='VALTORGB':
   ramp=q.color_ramp;src=n.color_ramp;ramp.interpolation=src.interpolation;ramp.color_mode=src.color_mode;ramp.hue_interpolation=src.hue_interpolation
   while len(ramp.elements)>2:ramp.elements.remove(ramp.elements[-1])
   for i,e in enumerate(src.elements):
    v=ramp.elements[i]if i<2 else ramp.elements.new(e.position);v.position=e.position;v.color=e.color
 for link in tree.links:
  if link.from_node in needed and link.to_node in needed:g.links.new(mapped[link.from_node].outputs[list(link.from_node.outputs).index(link.from_socket)],mapped[link.to_node].inputs[list(link.to_node.inputs).index(link.to_socket)])
 out=g.nodes.new('NodeGroupOutput');g.links.new(mapped[leaf].outputs[0],out.inputs['Color']);return g,len(needed)

def apply(scene):
 rocks=[o for o in scene.objects if o.get('rock_family')and o.get('scatter_zone')=='bank'];assert rocks
 assert not any(sl.material and sl.material.name.startswith('223 ')for o in rocks for sl in o.material_slots),'223 already applied'
 before={o.name:(o.data.as_pointer()if o.data else None,tuple(x for row in o.matrix_world for x in row),tuple(sl.material.as_pointer()if sl.material else None for sl in o.material_slots))for o in scene.objects}
 soil=scene.objects['Street foundation'].data.materials[0];region=soil.node_tree.nodes['Mix (Legacy).008'];leaf=region.inputs[2].links[0].from_node;assert leaf.name=='Mix (Legacy).006',leaf.name;group,nodes=bank_color_group(soil,leaf);cache={};rows=[]
 def copy_material(old):
  m=old.copy();m.name='223 Pale soil dust | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links;em=next(q for q in n if q.type=='EMISSION');oldcolor=em.inputs['Color'].links[0].from_socket
  def mathn(op,a,b,name):
   q=n.new('ShaderNodeMath');q.operation=op;q.name='223 '+name
   for i,x in enumerate((a,b)):
    if isinstance(x,(int,float)):q.inputs[i].default_value=x
    else:l.new(x,q.inputs[i])
   return q.outputs[0]
  geo=n.new('ShaderNodeNewGeometry');geo.name='223 Deposit orientation';sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0]);up=mathn('MAXIMUM',sep.outputs['Z'],0,'Upward-facing retention')
  ao=n.new('ShaderNodeAmbientOcclusion');ao.name='223 Small crevice deposition';ao.inputs['Distance'].default_value=.18;ao.samples=8;crevice=mathn('SUBTRACT',1,ao.outputs['AO'],'Crevice fraction')
  tex=n.new('ShaderNodeTexNoise');tex.name='223 Fine broken dust deposit';tex.inputs['Scale'].default_value=7;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.65;l.new(geo.outputs['Position'],tex.inputs['Vector']);patch=mathn('ADD',.8,mathn('MULTIPLY',tex.outputs['Fac'],.4,'Fine patch range'),'Patch coverage')
  base=mathn('ADD',.16,mathn('MULTIPLY',up,.36,'Upper deposit'),'Sides and upper deposit');coverage=mathn('MINIMUM',.65,mathn('MULTIPLY',patch,mathn('ADD',base,mathn('MULTIPLY',crevice,.18,'Crevice deposit'),'Accumulation'),'Broken accumulation'),'Preserve stone identity')
  dust=n.new('ShaderNodeGroup');dust.node_tree=group;dust.name='223 Actual pale-bank pigment';mix=n.new('ShaderNodeMixRGB');mix.name='223 Dust over original stone';mix.blend_type='MIX';l.new(coverage,mix.inputs[0]);l.new(oldcolor,mix.inputs[1]);l.new(dust.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color']);return m
 for o in rocks:
  for i,sl in enumerate(o.material_slots):
   old=sl.material
   if old is None:continue
   if old not in cache:cache[old]=copy_material(old)
   sl.link='OBJECT';sl.material=cache[old]
  rows.append({'name':o.name,'side':'left'if o.location.x<0 else'right','materials':[sl.material.name if sl.material else None for sl in o.material_slots]})
 for name,(data,matrix,mats)in before.items():
  ob=scene.objects[name];assert (ob.data.as_pointer()if ob.data else None)==data,name;assert tuple(x for row in ob.matrix_world for x in row)==matrix,name
  if ob not in rocks:assert tuple(sl.material.as_pointer()if sl.material else None for sl in ob.material_slots)==mats,name
 return {'rock_count':len(rocks),'left':sum(o.location.x<0 for o in rocks),'right':sum(o.location.x>=0 for o in rocks),'road_rocks_unchanged':sum(o.get('rock_family')is not None and o.get('scatter_zone')=='road'for o in scene.objects),'private_materials':{old.name:m.name for old,m in cache.items()},'native_soil_source':{'material':soil.name,'node':leaf.name,'cloned_upstream_nodes':nodes},'nominal_upper_deposit_fraction':.52,'max_deposit_fraction':.65,'original_stone_graphs_preserved':True,'binding':'Object-level overrides on bank stones only; mesh material tables untouched','all_geometry_transforms_unchanged':True,'all_other_material_bindings_unchanged':True,'rocks':rows,'actual_render_inspected':False,'approved':False}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/haze-texture-221/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('223 CPU READY',a['rock_count'],flush=True)
