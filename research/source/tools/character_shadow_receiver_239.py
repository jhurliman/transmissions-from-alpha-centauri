import bpy
from entrance_weathering_227 import Paint

def apply(scene,rows):
 ob=bpy.data.objects['Street foundation'];old=ob.material_slots[0].material;m=old.copy();m.name='239 Road with native character shadow response';ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=m;p=Paint(m);op=p.op
 em=next(n for n in p.n if n.type=='EMISSION');source=em.inputs['Color'].links[0].from_socket
 geo=p.node('ShaderNodeNewGeometry','239 native shadow receiver');sep=p.node('ShaderNodeSeparateXYZ','239 receiver axes');p.l.new(geo.outputs['Position'],sep.inputs[0]);mask=0
 from mathutils import Vector
 ray=Vector(next(n for n in scene.world.node_tree.nodes if n.label=='075 Sun angular distance').inputs[1].default_value).normalized();offset=ray*(-1.75/ray.z);long=Vector((offset.x,offset.y,0)).normalized();half=offset.length*.5
 for row in rows:
  x,y,z=row['foot'];dx=op('SUBTRACT',sep.outputs['X'],x+offset.x*.5);dy=op('SUBTRACT',sep.outputs['Y'],y+offset.y*.5)
  along=op('DIVIDE',op('ADD',op('MULTIPLY',dx,long.x),op('MULTIPLY',dy,long.y)),half+.7);across=op('DIVIDE',op('SUBTRACT',op('MULTIPLY',dx,long.y),op('MULTIPLY',dy,long.x)),.9)
  radius=op('ADD',op('MULTIPLY',along,along),op('MULTIPLY',across,across));mask=op('MAXIMUM',mask,p.remap(radius,.75,1.35,1,0))
 diff=p.node('ShaderNodeBsdfDiffuse','239 actual cast-shadow lighting');diff.inputs['Color'].default_value=(1,1,1,1);rgb=p.node('ShaderNodeShaderToRGB','239 native direct shadow');p.l.new(diff.outputs[0],rgb.inputs[0]);bw=p.node('ShaderNodeRGBToBW','239 shadow luminance');p.l.new(rgb.outputs['Color'],bw.inputs[0])
 factor=p.remap(bw.outputs[0],.18,.52,.50,1,'239 restrained native shadow contrast');factor=op('ADD',op('SUBTRACT',1,mask),op('MULTIPLY',mask,factor));body=p.mix(1,source,factor,'239 only native shadow darkening','MULTIPLY')
 # Tight stylized ambient contact beneath each boot, supplementing the native
 # very broad16m fill whose diffuse shadow is otherwise barely visible.
 contact=0
 for row in rows:
  x,y,z=row['foot']
  for offsetx in (-.17,.17):
   dx=op('DIVIDE',op('SUBTRACT',sep.outputs['X'],x+offsetx),.145);dy=op('DIVIDE',op('SUBTRACT',sep.outputs['Y'],y+.018),.24);q=op('ADD',op('MULTIPLY',dx,dx),op('MULTIPLY',dy,dy));contact=op('MAXIMUM',contact,p.remap(q,.05,1.3,.53,0))
 body=p.mix(contact,body,p.mix(1,body,(.28,.29,.34,1),'239 cool contact tone','MULTIPLY'),'239 soft boot contact');p.l.new(body,em.inputs['Color']);return {'material':m.name,'scope':'Ground within localized character neighborhoods','shadow_factor_range':[.5,1]}
