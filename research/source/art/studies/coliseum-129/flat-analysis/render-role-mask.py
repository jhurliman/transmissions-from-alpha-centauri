import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-129/flat-analysis';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
def mat(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=col;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
black=mat('MASK occluder',(0,0,0,1));gray=mat('MASK landmark',(.21586,)*3+(1,));white=mat('MASK exposed core',(1,1,1,1));rows=[]
for o in s.objects:
 if o.type in ['LIGHT','GREASEPENCIL']:o.hide_render=True
 if o.type!='MESH':continue
 if any(slot.material and slot.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in slot.material.node_tree.nodes)for slot in o.material_slots):o.hide_render=True;continue
 if o.name in C.all_objects:
  oldm=[slot.material for slot in o.material_slots];me=o.data.copy();o.data=me;tag=me.attributes.get('117 Exposed core');cores=[]
  for p in me.polygons:
   m=oldm[p.material_index]if p.material_index<len(oldm)else None;core=bool((tag and tag.domain=='FACE'and tag.data[p.index].value>.5)or(m and(m.get('role')=='fracture'or'Exposed masonry core'in m.name or'Exposed warm masonry core'in m.name)));cores.append(core)
  me.materials.clear();me.materials.append(gray);me.materials.append(white)
  for slot in o.material_slots:slot.link='DATA'
  for p,core in zip(me.polygons,cores):p.material_index=int(core)
  if any(cores):rows.append({'object':o.name,'faces':sum(cores)})
 else:
  for slot in o.material_slots:slot.link='OBJECT';slot.material=black
w=bpy.data.worlds.new('MASK black');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(0,0,0,1);s.world=w;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=False;s.render.film_transparent=False;s.render.filepath=str(O/'surface-role-mask.png');(O/'mask-source.json').write_text(json.dumps({'source':'128/scene.blend','core_faces':rows,'white':'117 Exposed core FACE tag or fracture/exposed-core material family','gray':'Other landmark surfaces','black':'Nonlandmark occluders/background','limitation':'Semantic tags may omit inherited untagged broken crown faces. Not a universal fracture detector.'},indent=2));bpy.ops.render.render(write_still=True)
