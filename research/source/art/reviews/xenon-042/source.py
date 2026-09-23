import bpy,json
from pathlib import Path
from mathutils import Matrix
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-042';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-041/scene.blend'));s=bpy.context.scene
source=next(m for m in bpy.data.materials if m.name.startswith('039 Layered coating | Cladding | slate'))
anchor=bpy.data.objects.new('042 Street coating coordinates',None);s.collection.objects.link(anchor)
# Common world coordinate source prevents resets between facade modules. Each facade gets its own offset/coverage.
families={
 'left_middle':{'offset':(11,7,0),'scale':(.4,.55,.32),'threshold':.53},
 'left_rear':{'offset':(-8,25,4),'scale':(.5,.65,.42),'threshold':.48},
 'right_front':{'offset':(17,-4,2),'scale':(.45,.5,.35),'threshold':.50},
 'right_middle':{'offset':(-15,13,3),'scale':(.5,.7,.35),'threshold':.565},
 'right_rear':{'offset':(9,35,-2),'scale':(.4,.48,.35),'threshold':.49},
 'services':{'offset':(21,9,4),'scale':(.7,.7,.65),'threshold':.625}}
mats={}
def material(family):
 if family in mats:return mats[family]
 cfg=families[family];m=source.copy();m.name='042 Street coating | '+family;nt=m.node_tree
 tex=next(n for n in nt.nodes if n.type=='TEX_COORD' and n.object);tex.object=anchor
 # Add a family translation upstream of every coordinate consumer, preserving cross-component continuity.
 links=list(tex.outputs['Object'].links);shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=cfg['offset'];nt.links.new(tex.outputs['Object'],shift.inputs[0])
 for link in links:nt.links.new(shift.outputs[0],link.to_socket)
 mapping=next(n for n in nt.nodes if n.type=='VECT_MATH' and n.operation=='MULTIPLY');mapping.inputs[1].default_value=cfg['scale']
 # Shift the full field rather than just thresholds: flakes, substrate and lip masks stay aligned.
 ramp=next(n for n in nt.nodes if n.type=='VALTORGB' and len(n.color_ramp.elements)==3 and any(abs(e.position-.493)<.001 for e in n.color_ramp.elements))
 field=ramp.inputs[0].links[0].from_node;out=field.outputs[0];consumers=list(out.links)
 adjust=nt.nodes.new('ShaderNodeMath');adjust.operation='ADD';adjust.inputs[1].default_value=.515-cfg['threshold'];nt.links.new(out,adjust.inputs[0])
 for link in consumers:nt.links.new(adjust.outputs[0],link.to_socket)
 if family=='services':
  for n in nt.nodes:
   if n.type=='BUMP':n.inputs['Strength'].default_value=.1
 mats[family]=m;return m
cache={};replacements=[]
def coated_collection(col,family):
 key=(col.name,family)
 if key in cache:return cache[key]
 new=bpy.data.collections.new('042 '+family+' | '+col.name);cache[key]=new
 for k in col.keys():new[k]=col[k]
 new['coating_family']=family
 for original in col.objects:
  ob=original.copy();new.objects.link(ob)
  if original.type=='MESH':
   ob.data=original.data.copy()
   for slot in ob.material_slots:
    m=slot.material
    if m and (m.name.startswith('Cladding') or m.name.startswith('DUCT') or 'blue-gray enamel' in m.name):slot.material=material(family)
  if original.instance_collection:ob.instance_collection=coated_collection(original.instance_collection,family)
 for child in col.children:new.children.link(coated_collection(child,family))
 return new
# Existing masters remain clean; each building gets copied instances with its own finish family.
for ob in list(s.objects):
 if ob.hide_render or not ob.instance_collection or ob.name=='Front-left section instance':continue
 x,y,z=ob.matrix_world.translation
 family=None
 if ob.name=='right_vertical_galleries':family='right_middle'
 elif ob.name=='right_horizontal_utility':family='right_rear'
 elif abs(x)>6 and -9<y<33:
  part=ob.instance_collection.get('part_id','')
  if part.startswith(('window','layout','column','slot','floor','gangway')):
   family=('left_middle' if y<20 else 'left_rear') if x<0 else ('right_front' if y<1 else 'right_middle' if y<17.2 else 'right_rear')
  elif ob.instance_collection.name.startswith(('PIP','SERVICE')):family='services'
 if family:ob.instance_collection=coated_collection(ob.instance_collection,family);replacements.append((ob.name,family))
# Coat direct cladding meshes on exposed side-road elevations as part of the front-right family.
for ob in s.objects:
 if ob.hide_render or ob.type!='MESH':continue
 if ob.name.startswith(('Side road','Road-facing','Road window','End wall','Loading portal','Road portal')):
  ob.data=ob.data.copy()
  for slot in ob.material_slots:
   if slot.material and slot.material.name.startswith('Cladding'):slot.material=material('right_front')
(O/'distribution.json').write_text(json.dumps({'families':families,'replaced_instances':replacements,'geometry':'Mesh coordinates, transforms and camera unchanged; copies preserve clean masters','front_left':'041 preserved'},indent=2))
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
