"""Integrate only validated repaired walls; remap material roles and remove stale attachments."""
import bpy
from coliseum_crown_repair_123 import apply_prepared,NAMES
from coliseum_weathering_117 import exposed_core

def apply(C):
 removed=[]
 for ob in list(C.objects):
  if ob.get('120 owner') in NAMES:removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 repairs=apply_prepared(C);coremat=exposed_core();rows=[]
 n,l=coremat.node_tree.nodes,coremat.node_tree.links;em=next(q for q in n if q.type=='EMISSION');old=em.inputs[0].links[0].from_socket
 attr=n.new('ShaderNodeAttribute');attr.attribute_name='115 Original world position'
 noise=n.new('ShaderNodeTexNoise');noise.label='123 Fine exposed mineral variation';noise.inputs['Scale'].default_value=8.;noise.inputs['Detail'].default_value=1.5;l.new(attr.outputs['Vector'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.label='Restrained grain on fracture faces only';ramp.color_ramp.elements[0].position=.28;ramp.color_ramp.elements[0].color=(.88,.88,.88,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(1.06,1.06,1.06,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1.;l.new(old,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0])
 for name in NAMES:
  ob=bpy.data.objects[name];me=ob.data;mask=me.attributes.get('117 Exposed core') or me.attributes.new('117 Exposed core','FLOAT','FACE');normal=ob.matrix_world.to_3x3().inverted().transposed();z0=min((ob.matrix_world@v.co).z for v in me.vertices)
  idx=len(me.materials);me.materials.append(coremat);wall=next((i for i,m in enumerate(me.materials)if m and m.get('role')=='wall'),0)
  crown=0
  for f in me.polygons:
   if (normal@f.normal).normalized().z>.12 and (ob.matrix_world@f.center).z>z0+1.25:mask.data[f.index].value=1.;crown+=1
   f.material_index=idx if mask.data[f.index].value>.5 else wall
  rows.append({'object':name,'wall_material':me.materials[wall].name,'core_material':coremat.name,'crown_faces_tagged':crown})
 return {'repairs':repairs,'removed_stale_core_attachments':removed,'material_role_mapping':rows,'scope':'Only two bay8 repaired L/R wall meshes and their old attached facets'}
