"""Two continuous world-space tyre trails across road and native alley soil."""
import bpy
from entrance_weathering_227 import Paint

def apply(scene,strength=1.5):
 ob=bpy.data.objects['Street foundation'];m=ob.material_slots[0].material.copy();m.name='246 Two continuous alley tyre trails';ob.material_slots[0].material=m
 p=Paint(m);op=p.op;region=m.node_tree.nodes['Mix (Legacy).008']
 road=m.node_tree.nodes['Mix (Legacy).012'].outputs[0];bank=m.node_tree.nodes['Mix (Legacy).006'].outputs[0]
 # Discard245's three-trail material branch; keep the original native grain/AO source.
 assert m.node_tree.nodes['Mix (Legacy).012'].inputs[1].links[0].from_node.name=='Image Texture'
 geo=p.node('ShaderNodeNewGeometry','246 world soil');sep=p.node('ShaderNodeSeparateXYZ','246 world axes');p.l.new(geo.outputs['Position'],sep.inputs[0]);x,y,z=sep.outputs
 distance=op('MAXIMUM',op('SUBTRACT',8.3,x),0)
 reach=p.remap(distance,1.0,5.6,1,0)
 envelope=op('MULTIPLY',p.remap(x,3.7,5.3),p.remap(x,20.7,21.0,1,0))
 coarse=p.noise(p.vec(op('MULTIPLY',x,2.5),op('MULTIPLY',y,4.2),0),1,3);grit=p.noise(geo.outputs['Position'],45,2)
 wobble=op('MULTIPLY',op('SUBTRACT',coarse,.5),.32);trails=0
 for center,slope,width in [(3.0,-.23,.46),(4.5,.20,.63)]:
  mid=op('ADD',center,op('ADD',op('MULTIPLY',distance,slope),op('MULTIPLY',op('MULTIPLY',distance,distance),.024)))
  delta=op('ABSOLUTE',op('ADD',op('SUBTRACT',y,mid),wobble))
  body=p.remap(delta,width*.25,op('ADD',width,op('MULTIPLY',distance,.12)),1,0)
  trails=op('MAXIMUM',trails,body)
 # Keep the accepted loose road dust, but no third/nearest track by the rock pile.
 fan=op('MULTIPLY',p.remap(y,-1.4,.9),p.remap(y,4.7,6.5,1,0))
 fan=op('MULTIPLY',fan,p.remap(x,7.8,8.5,1,0))
 support=op('MULTIPLY',envelope,op('MULTIPLY',reach,op('MAXIMUM',op('MULTIPLY',trails,.92),op('MULTIPLY',fan,.23))))
 broken=p.remap(op('ADD',op('MULTIPLY',coarse,.62),op('MULTIPLY',grit,.38)),.40,.54)
 deposit=op('MULTIPLY',strength,op('MULTIPLY',support,broken))
 for original,add,index in [(road,(.22,.16,.075,1),1),(bank,(.10,.075,.035,1),2)]:
  tint=p.mix(1,original,add,'246 mineral grains over original soil','ADD')
  p.l.new(p.mix(deposit,original,tint,'246 continuous granular tyre trace'),region.inputs[index])
 return {'tracks':2,'removed_track_center_y':1.1,'retained_centers_y':[3.0,4.5],'native_alley_extension_x':[8.3,21.0],'original_texture_unchanged':True,'bank_pigment_addition':[.10,.075,.035],'strength':strength,'footing245_unchanged':True}
