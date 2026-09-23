"""Shared weathered concrete foundation under the left service terminals."""
import bpy,bmesh
from entrance_weathering_227 import Paint

def apply(scene):
 x0,x1,y0,y1=-9.35,-7.45,4.95,9.55;z0,z1=-.24,.32
 # Unequal cast/chipped corners, a broad continuous footing rather than two pads.
 ring=[(x0+.09,y0),(x1-.065,y0),(x1,y0+.065),(x1,y1-.105),(x1-.105,y1),(x0+.05,y1),(x0,y1-.05),(x0,y0+.09)]
 verts=[(x,y,z)for z in(z0,z1)for x,y in ring];n=len(ring)
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 me=bpy.data.meshes.new('242 Shared service concrete footing');me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
 m=bpy.data.materials.new('242 Quiet weathered concrete footing');m.use_nodes=True;p=Paint(m);p.n.clear()
 geo=p.node('ShaderNodeNewGeometry','footing world position');pos=geo.outputs['Position']
 noise=p.noise(pos,7,3);fine=p.noise(pos,68,2)
 color=p.mix(p.remap(noise,.25,.75),(.18,.18,.195,1),(.29,.27,.235,1),'mineral mottling')
 color=p.mix(p.remap(fine,.28,.38,.28,0),color,(.07,.065,.065,1),'fine aggregate flecks')
 sep=p.node('ShaderNodeSeparateXYZ','height');p.l.new(pos,sep.inputs[0]);dust=p.op('MULTIPLY',p.remap(sep.outputs['Z'],.05,.31,0,.27),p.remap(noise,.24,.65,.4,1))
 color=p.mix(dust,color,(.32,.25,.16,1),'settled soil dust')
 diffuse=p.node('ShaderNodeBsdfDiffuse','actual scene lighting');diffuse.inputs['Color'].default_value=(.8,.8,.8,1);diffuse.inputs['Roughness'].default_value=1
 rgb=p.node('ShaderNodeShaderToRGB','native light response');p.l.new(diffuse.outputs[0],rgb.inputs[0]);bw=p.node('ShaderNodeRGBToBW','light value');p.l.new(rgb.outputs[0],bw.inputs[0]);shade=p.remap(bw.outputs[0],.12,.8,.48,1)
 em=p.node('ShaderNodeEmission','bounded mineral shading');p.l.new(p.mix(1,color,shade,'concrete light','MULTIPLY'),em.inputs['Color']);out=p.node('ShaderNodeOutputMaterial','surface');p.l.new(em.outputs[0],out.inputs['Surface']);me.materials.append(m)
 ob=bpy.data.objects.new('242 Single concrete footing for left service cluster',me);scene.collection.objects.link(ob);ob['242 service footing']=True
 bevel=ob.modifiers.new('Small worn concrete arris','BEVEL');bevel.width=.022;bevel.segments=1
 return {'object':ob.name,'bounds':[x0,x1,y0,y1,z0,z1],'supports':['rectangular duct terminal at(-8.6,5.4)','round pipe terminal at(-8.1,9.0)'],'shared_continuous_native_mesh':True,'ground_embed_m':.24,'height_m':.32,'material':'weathered gray mineral with sparse aggregate and restrained soil dust','existing_objects_unchanged':True}
