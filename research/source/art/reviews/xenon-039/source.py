import bpy,json,math
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-039';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-038/scene.blend'));s=bpy.context.scene
kit=bpy.data.collections['FAC | front_left_section']
# Shared local position field: mesh coordinates remain continuous across separate panels and their tangent transforms.
anchor=bpy.data.objects.new('039 Building coating coordinates',None);s.collection.objects.link(anchor);anchor.matrix_world=bpy.data.objects['Front-left section instance'].matrix_world.copy()
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
materials={}
for ob in kit.objects:
 if ob.type!='MESH':continue
 for slot in ob.material_slots:
  orig=slot.material
  if not orig or not orig.name.startswith(('Cladding','Structure | bare mineral')):continue
  if orig.name not in materials:
   m=orig.copy();m.name='039 Layered coating | '+orig.name;nt=m.node_tree;n=nt.nodes;l=nt.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Base Color'].links):l.remove(link)
   tex=n.new('ShaderNodeTexCoord');tex.object=anchor
   mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.70,.8,.40);l.new(tex.outputs['Object'],mapping.inputs[0])
   broad=n.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=.75;broad.inputs['Detail'].default_value=1.5;broad.inputs['Roughness'].default_value=.55;l.new(mapping.outputs['Vector'],broad.inputs['Vector'])
   edge=n.new('ShaderNodeTexNoise');edge.inputs['Scale'].default_value=8;edge.inputs['Detail'].default_value=3;edge.inputs['Roughness'].default_value=.7;l.new(tex.outputs['Object'],edge.inputs['Vector'])
   mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=.10;mul.inputs[2].default_value=-.05;l.new(edge.outputs['Fac'],mul.inputs[0])
   add=n.new('ShaderNodeMath');add.operation='ADD';l.new(broad.outputs['Fac'],add.inputs[0]);l.new(mul.outputs[0],add.inputs[1])
   ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT';e=ramp.color_ramp.elements;e[0].position=.0;e[0].color=rgb('#777da0');e[1].position=.515;e[1].color=rgb('#b29a81');mid=e.new(.495);mid.color=rgb('#8d8190');l.new(add.outputs[0],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
   # Narrow relief at coating boundaries, not noisy whole-surface displacement.
   bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.003;l.new(ramp.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
   bs.inputs['Roughness'].default_value=.88;materials[orig.name]=m
  slot.material=materials[orig.name]
s.render.use_freestyle=False;s.render.filepath=str(O/'color-only.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
(O/'settings.json').write_text(json.dumps({'scope':'Front-left section only','coordinates':'Shared building-local anchor across mesh components','layers':['blue topcoat','muted intermediate layer','warm undercoat'],'geometry':'unchanged','bump_distance_m':.003},indent=2))
