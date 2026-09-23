"""Localized native dust deposits; existing road texture is sampled unchanged."""
import bpy
from entrance_weathering_227 import Paint

def apply(scene,strength=1.5):
 ob=bpy.data.objects['Street foundation'];old=ob.material_slots[0].material;m=old.copy();m.name='245 Alley-mouth dispersed soil';ob.material_slots[0].material=m
 p=Paint(m);op=p.op;region=m.node_tree.nodes['Mix (Legacy).008'];original=region.inputs[1].links[0].from_socket
 assert m.node_tree.nodes['Mix (Legacy).012'].inputs[1].links[0].from_node.name=='Image Texture'
 geo=p.node('ShaderNodeNewGeometry','245 world soil');sep=p.node('ShaderNodeSeparateXYZ','245 world axes');p.l.new(geo.outputs['Position'],sep.inputs[0]);x,y,z=sep.outputs
 # Unequal, lightly bending exits; footprints/tyres disperse material rather than cut ruts.
 distance=op('SUBTRACT',8.3,x);reach=p.remap(distance,1.0,5.6,1,0)
 envelope=op('MULTIPLY',p.remap(x,3.7,5.3),p.remap(x,8.4,9.3,1,0))
 coarse=p.noise(p.vec(op('MULTIPLY',x,2.5),op('MULTIPLY',y,4.2),0),1,3)
 grit=p.noise(geo.outputs['Position'],45,2)
 wobble=op('MULTIPLY',op('SUBTRACT',coarse,.5),.32)
 trails=0
 for center,slope,width in[(1.10,-.28,.37),(3.0,-.23,.46),(4.5,.20,.63)]:
  mid=op('ADD',center,op('ADD',op('MULTIPLY',distance,slope),op('MULTIPLY',op('MULTIPLY',distance,distance),.024)))
  delta=op('ABSOLUTE',op('ADD',op('SUBTRACT',y,mid),wobble))
  body=p.remap(delta,width*.25,op('ADD',width,op('MULTIPLY',distance,.12)),1,0)
  trails=op('MAXIMUM',trails,body)
 fan=op('MULTIPLY',p.remap(y,-1.4,.9),p.remap(y,4.7,6.5,1,0))
 support=op('MULTIPLY',envelope,op('MULTIPLY',reach,op('MAXIMUM',op('MULTIPLY',trails,.92),op('MULTIPLY',fan,.23))))
 # Multiscale broken pigment with sharp grain islands; no averaging or smooth repaint.
 broken=p.remap(op('ADD',op('MULTIPLY',coarse,.62),op('MULTIPLY',grit,.38)),.40,.54)
 deposit=op('MULTIPLY',strength,op('MULTIPLY',support,broken))
 # Tint the exact original road grain toward bank soil, retaining its modulation.
 tint=p.mix(1,original,(.22,.16,.075,1),'245 deposited mineral pigment over original grain','ADD')
 p.l.new(p.mix(deposit,original,tint,'245 additive dispersed soil'),region.inputs[1])
 m['245 strength']=strength;m['245 preservation']='Unmodified original image sample, AO and downstream contact layers; local color deposition only'
 return {'strength':strength,'extent_x':[3.7,9.3],'fan_extent_y':[-1.4,6.5],'trail_extent_y_approx':[-1.4,7.2],'original_texture_unchanged':True,'approach':'unequal curved broken trails plus loose granular fan','material':m.name}
