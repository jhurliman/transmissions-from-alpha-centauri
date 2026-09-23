"""Private roof backing chip and cool, heavily aged upper fascia only."""
import bpy
from entrance_weathering_227 import Paint

def apply(scene):
 o=bpy.data.objects['Building structural backing.002']
 assert not o.get('244 roof edge'), 'Already applied'
 original=o.data;original.use_fake_user=True
 # A genuine missing wedge traverses the metre-thick backing. Neither a decal
 # nor a dark triangle placed on an otherwise unchanged skyline.
 profile=[(20,0),(32,0),(32,17),(28.6,17),(28.33,16.92),(28.11,16.58),(27.77,16.53),(27.47,16.79),(27.15,16.83),(26.96,17),(20,17)]
 N=len(profile);verts=[(x,y,z)for x in(-10.7,-9.7)for y,z in profile]
 faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
 mesh=bpy.data.meshes.new('244 Chipped roof backing solid');mesh.from_pydata(verts,[],faces);mesh.update()
 for m in original.materials:mesh.materials.append(m)
 o.data=mesh
 # Preserve original shader everywhere except the exposed top metre.
 old=o.material_slots[0].material;m=old.copy();m.name='244 Cool weathered exposed roof backing'
 p=Paint(m);out=next(n for n in p.n if n.type=='OUTPUT_MATERIAL'and n.is_active_output);surface=out.inputs['Surface'].links[0].from_socket
 geo=p.node('ShaderNodeNewGeometry','244 native surface position');xyz=p.node('ShaderNodeSeparateXYZ','244 roof band gate');p.l.new(geo.outputs['Position'],xyz.inputs[0]);x,y,z=xyz.outputs
 broad=p.noise(geo.outputs['Position'],2.15,3);fine=p.noise(geo.outputs['Position'],26,2)
 grain=p.noise(geo.outputs['Position'],75,1)
 rain=p.noise(p.vec(p.op('MULTIPLY',x,7),p.op('MULTIPLY',y,7),p.op('MULTIPLY',z,.42)),2,2)
 patches=p.remap(broad,.39,.62,0,1)
 color=p.mix(patches,(.029,.030,.046,1),(.078,.084,.117,1),'244 charcoal violet mineral exposures')
 color=p.mix(p.op('MULTIPLY',p.remap(rain,.45,.61),.48),color,(.024,.026,.038,1),'244 unequal vertical runoff')
 flecks=p.remap(fine,.58,.69,0,.65);color=p.mix(flecks,color,(.135,.139,.174,1),'244 pale blue mineral grit')
 color=p.mix(p.remap(grain,.63,.72,0,.72),color,(.013,.015,.022,1),'244 dense tiny pits')
 em=p.node('ShaderNodeEmission','244 weathered recess pigment');p.l.new(color,em.inputs['Color']);em.inputs['Strength'].default_value=1
 mix=p.node('ShaderNodeMixShader','244 preserve lower backing');p.l.new(p.remap(z,15.90,16.08),mix.inputs[0]);p.l.new(surface,mix.inputs[1]);p.l.new(em.outputs[0],mix.inputs[2]);p.l.new(mix.outputs[0],out.inputs['Surface'])
 o.material_slots[0].link='OBJECT';o.material_slots[0].material=m;o['244 roof edge']=True
 # Mark only actual crease edges; maintain native mesh occlusion.
 # Native silhouette/crease extraction uses the true notched mesh.
 return {'target':o.name,'original_mesh':original.name,'new_mesh':mesh.name,'private_material':m.name,'notch_y_m':[26.96,28.6],'notch_max_depth_m':.47,'full_thickness_m':1,'weathering_z_gate_m':[15.9,16.08],'native_geometry':True,'unchanged':'Lights, camera, fog, all other objects and lower recess shader','review':'Parent native scene proof pending'}
