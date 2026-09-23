import bpy,math,random,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/reviews/xenon-010';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-009/scene.blend'));s=bpy.context.scene;random.seed(1010)
bpy.data.objects['Broad diffuse facade fill'].data.energy=1700;s.view_settings.exposure=-.3
for n in s.world.node_tree.nodes:
 if n.type=='BACKGROUND' and n.inputs[1].default_value>1:n.inputs[1].default_value=1.3
for o in bpy.data.objects:
 if o.name.startswith('Distant dust volume'):
  o.dimensions.z=18;o.location.z=7.5
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='MATH' and n.operation=='GREATER_THAN':n.inputs[1].default_value=.34
# Mesh-level damage at selected cladding boundaries: these cavities are actual booleans.
plates=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Left broad battered','Right facade plate'))]
random.shuffle(plates)
for ob in plates[:42]:
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];xmin=min(v.x for v in vs);xmax=max(v.x for v in vs);ymin=min(v.y for v in vs);ymax=max(v.y for v in vs);zmin=min(v.z for v in vs);zmax=max(v.z for v in vs)
 x=(xmin+xmax)/2;y=random.choice([ymin,ymax]);z=random.uniform(zmin+.25,zmax-.25)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,z));cut=bpy.context.object;cut.name='Temporary cutting solid';cut.scale=(.65,random.uniform(.10,.28),random.uniform(.16,.44));cut.rotation_euler.x=random.uniform(-.8,.8);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual fractured cladding edge','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Small asymmetry to structural bay outlines; deliberately keep service trunk straight.
for ob in bpy.data.objects:
 if ob.name.startswith('Left corner rib') and random.random()<.4:ob.rotation_euler.x+=random.uniform(-.012,.018)
 if ob.name.startswith('Right narrow upright') and random.random()<.3:ob.rotation_euler.x+=random.uniform(-.01,.025)
# Render and independent scene audit.
image_nodes=[]
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':image_nodes.append(m.name)
assert not image_nodes
assert all(v.material_override is None for v in s.view_layers)
s.use_nodes=False
(O/'audit.json').write_text(json.dumps({'image_texture_nodes':image_nodes,'material_overrides':False,'compositor_enabled':False,'mesh_objects':sum(o.type=='MESH' for o in s.objects),'actual_lights':sum(o.type=='LIGHT' for o in s.objects),'notes':'No painted finish included in this geometry acceptance render.'},indent=2)+'\n')
s['stage']='Geometry-only round010';s.render.filepath=str(O/'render.png');s.cycles.samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
