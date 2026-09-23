import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-045');bpy.ops.wm.open_mainfile(filepath=str(R/'scene.blend'));s=bpy.context.scene
# World-space process masks originate at actual component joints.
def op(nt,kind,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def setup(m):
 nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');g=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],xyz.inputs[0]);return nt,bs,g,xyz
beam=next(o for o in bpy.data.collections['DAMAGE | concrete_support_01'].objects if o.name.startswith('Solid concrete'))
m=beam.data.materials[0].copy();m.name='045 Bearing-joint concrete runoff';beam.data.materials[0]=m;nt,bs,g,xyz=setup(m)
width=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Y'],7.15)),8)),0)
z=op(nt,'MULTIPLY',op(nt,'LESS_THAN',xyz.outputs['Z'],2.46),op(nt,'MAXIMUM',op(nt,'MULTIPLY',op(nt,'SUBTRACT',xyz.outputs['Z'],.5),.50),0))
scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.5,30,.55);nt.links.new(g.outputs['Position'],scale.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;nt.links.new(scale.outputs[0],noise.inputs['Vector'])
mask=op(nt,'MULTIPLY',op(nt,'MULTIPLY',width,z),op(nt,'MULTIPLY',noise.outputs['Fac'],.48))
mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(mask,mix.inputs[0]);mix.inputs[1].default_value=bs.inputs['Base Color'].default_value;mix.inputs[2].default_value=(.07,.05,.032,1);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
# Independent metal corrosion + localized bright abrasion at housing joints.
changed=[]
for ob in list(s.objects):
 if not ob.instance_collection or abs(ob.location.x-9)>.02 or abs(ob.location.y-8)>.02 or ob.location.z>2.7:continue
 col=bpy.data.collections.new('045 Metal test | '+ob.instance_collection.name)
 for original in ob.instance_collection.objects:
  q=original.copy();col.objects.link(q)
  if q.type!='MESH':continue
  q.data=original.data.copy()
  for slot in q.material_slots:
   if not slot.material or not ('enamel' in slot.material.name or 'steel' in slot.material.name):continue
   m=slot.material.copy();m.name='045 Joint metal wear | '+m.name;slot.material=m;nt,bs,g,xyz=setup(m);base=bs.inputs['Base Color'].default_value[:]
   noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=2;nt.links.new(g.outputs['Position'],noise.inputs['Vector'])
   d=op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Z'],1.1));rust=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',d,3)),0)
   rust=op(nt,'MULTIPLY',rust,op(nt,'GREATER_THAN',noise.outputs['Fac'],.44));rust=op(nt,'MULTIPLY',rust,.65)
   blend=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(rust,blend.inputs[0]);blend.inputs[1].default_value=base;blend.inputs[2].default_value=(.22,.075,.025,1)
   d2=op(nt,'MINIMUM',d,op(nt,'ABSOLUTE',op(nt,'SUBTRACT',xyz.outputs['Z'],2.6)));edge=op(nt,'MULTIPLY',op(nt,'LESS_THAN',d2,.025),op(nt,'GREATER_THAN',noise.outputs['Fac'],.52))
   polish=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(edge,polish.inputs[0]);nt.links.new(blend.outputs[0],polish.inputs[1]);polish.inputs[2].default_value=(.34,.32,.29,1);nt.links.new(polish.outputs[0],bs.inputs['Base Color'])
   bs.inputs['Roughness'].default_value=.65
 ob.instance_collection=col;changed.append(ob.name)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'weather-scene.blend'))
(R/'weather-tests.json').write_text(json.dumps({'runoff_origin':'Concrete bearing at world z=2.45, y=7.15; downward fade and narrow lateral streaks','metal':'Corrosion centered on actual z=1.1 housing joint; sparse abrasion at z=1.1 and 2.6 rims','metal_instances':changed,'scope':'Separate weather specimen; main geometry scene stays independent'},indent=2))
from mathutils import Vector
s.camera.location=(4,3.2,3);s.camera.rotation_euler=(Vector((8.3,7.15,1.25))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=62;s.render.resolution_x=1000;s.render.resolution_y=900;s.cycles.samples=32;s.render.use_freestyle=False;s.render.filepath=str(R/'weather-detail.png');bpy.ops.render.render(write_still=True)
