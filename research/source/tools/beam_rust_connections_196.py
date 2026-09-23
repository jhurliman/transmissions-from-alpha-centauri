"""Native, edge-rooted inward bristle corrosion; preserves accepted steel and oxide palette."""
import bpy, numpy as np, hashlib, json
from pathlib import Path
HOSTS=('Architecture | gangway_single_Y_8m','Architecture | gangway_single_Y_8m.001')
ROOT=Path(__file__).resolve().parents[1]
class Field:
 def __init__(self,tree=None): self.tree=tree
 def op(self,kind,a,b=None):
  if self.tree is not None:
   q=self.tree.nodes.new('ShaderNodeMath');q.operation=kind;q.label='194 '+kind
   for i,v in enumerate([a] if b is None else [a,b]):
    if hasattr(v,'node'):self.tree.links.new(v,q.inputs[i])
    else:q.inputs[i].default_value=float(v)
   return q.outputs[0]
  return {'ADD':lambda:a+b,'SUBTRACT':lambda:a-b,'MULTIPLY':lambda:a*b,'DIVIDE':lambda:a/b,'ABSOLUTE':lambda:np.abs(a),'FLOOR':lambda:np.floor(a),'FRACT':lambda:a-np.floor(a),'SINE':lambda:np.sin(a),'MAXIMUM':lambda:np.maximum(a,b),'MINIMUM':lambda:np.minimum(a,b),'POWER':lambda:np.maximum(0,a)**b}[kind]()
 def add(self,a,b):return self.op('ADD',a,b)
 def sub(self,a,b):return self.op('SUBTRACT',a,b)
 def mul(self,a,b):return self.op('MULTIPLY',a,b)
 def clamp(self,a):return self.op('MINIMUM',1,self.op('MAXIMUM',0,a))
 def smooth(self,a):
  t=self.clamp(a);return self.mul(self.mul(t,t),self.sub(3,self.mul(2,t)))
 def hash(self,a):return self.op('FRACT',self.mul(self.op('SINE',self.add(self.mul(a,12.9898),78.233)),437.585453))
 def mask(self,s,u,seed):
  result=0
  for edge in (-1,1):
   d=self.sub(1,self.mul(edge,u))
   phase=self.add(seed,edge*47.91)
   along=self.add(s,self.mul(phase,.139))
   along=self.add(along,self.add(self.mul(1.50,self.op('SINE',self.add(self.mul(s,.27),phase))),self.mul(.50,self.op('SINE',self.add(self.mul(s,.63),self.mul(phase,1.7))))))
   # A SINGLE common envelope gates every strand on this edge. This creates
   # separated brush swathes rather than six overlapping all-length combs.
   macrocell=self.op('FLOOR',self.op('DIVIDE',along,6.7))
   mh=self.hash(self.add(macrocell,phase));mh2=self.hash(self.add(macrocell,self.add(phase,83.91)))
   center=self.mul(6.7,self.add(macrocell,self.add(.31,self.mul(.38,mh))))
   halfspan=self.add(.55,self.mul(1.95,mh2))
   distance=self.op('ABSOLUTE',self.sub(along,center))
   envelope=self.smooth(self.op('DIVIDE',self.sub(halfspan,distance),self.mul(halfspan,.48)))
   presence=self.smooth(self.op('DIVIDE',self.sub(self.hash(self.add(macrocell,self.add(phase,146.3))),.18),.10))
   envelope=self.mul(envelope,presence)
   # The connected root is narrow. Fine overlapping strands add unequal reach;
   # they terminate inside the same swath, leaving wide clean edge intervals.
   reach=self.mul(envelope,self.add(.68,self.mul(.60,mh)))
   root=self.mul(reach,.22)
   strand_reach=root
   for family,spacing in enumerate((.065,.113,.197)):
    offset=self.add(phase,family*19.73)
    small=self.add(along,self.mul(offset,.029))
    cell=self.op('FLOOR',self.op('DIVIDE',small,spacing))
    h=self.hash(self.add(cell,offset));h2=self.hash(self.add(cell,self.add(offset,37.12)))
    c=self.mul(spacing,self.add(cell,self.add(.23,self.mul(.54,h))))
    width=self.mul(spacing,self.add(.20,self.mul(.30,h2)))
    lateral=self.op('ABSOLUTE',self.sub(small,c))
    brush=self.smooth(self.op('DIVIDE',self.sub(width,lateral),self.mul(width,.70)))
    length=self.mul(reach,self.add(.29,self.mul(.71,h2)))
    strand_reach=self.op('MAXIMUM',strand_reach,self.mul(length,brush))
   # A finite feather fade around every irregular inward tip, no detached spots.
   mask=self.smooth(self.op('DIVIDE',self.sub(strand_reach,d),.055))
   mask=self.mul(mask,self.mul(envelope,self.add(.74,self.mul(.20,mh2))))
   # Low-frequency smoothly varying wet edge runs, with real clean breaks.
   run_s=self.add(self.op('DIVIDE',s,11.7),self.mul(phase,.21))
   run_cell=self.op('FLOOR',run_s);t=self.smooth(self.op('FRACT',run_s))
   a=self.hash(self.add(run_cell,phase));b=self.hash(self.add(run_cell,self.add(phase,1)))
   wet=self.add(a,self.mul(t,self.sub(b,a)))
   continuity=self.smooth(self.op('DIVIDE',self.sub(wet,.22),.18))
   fine=self.add(.055,self.mul(.025,self.op('SINE',self.add(self.mul(s,1.13),phase))))
   rail=self.mul(.72,self.mul(continuity,self.smooth(self.op('DIVIDE',self.sub(fine,d),.022))))
   result=self.op('MAXIMUM',result,self.op('MAXIMUM',mask,rail))
  return result


def apply(scene):
 g=bpy.data.node_groups.new('196 Irregular swathes and broken edge runoff','ShaderNodeTree')
 for name in ('Along in half widths','Across in half widths','Seed'):g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
 g.interface.new_socket(name='Edge rooted coverage',in_out='OUTPUT',socket_type='NodeSocketFloat')
 i=g.nodes.new('NodeGroupInput');o=g.nodes.new('NodeGroupOutput');f=Field(g);g.links.new(f.mask(i.outputs[0],i.outputs[1],i.outputs[2]),o.inputs[0])
 rows=[]
 for hn in HOSTS:
  host=scene.objects[hn]
  for ob in host.instance_collection.all_objects:
   if not ob.name.startswith(('Y arm','Y stem')):continue
   for slot in ob.material_slots:
    old=slot.material;m=old.copy();m.name='196 Irregular connected edge rust | '+ob.name
    fields=[n for n in m.node_tree.nodes if n.type=='GROUP' and n.node_tree and n.node_tree.name.startswith('194 Analytic inward bristle field')]
    assert len(fields)==1,(ob.name,len(fields))
    fields[0].node_tree=g;fields[0].label='196 Irregular brush spacing with interrupted narrow edge runs'
    slot.link='OBJECT';slot.material=m
    rows.append({'host':hn,'object':ob.name,'old_material':old.name,'new_material':m.name,'existing_rust_strength_chain_preserved':True})
 return {'changed':rows,'shape':'Domain-warped unequal swath spacing, omitted clusters, and long interrupted narrow edge rust runs','geometry_and_palette_unchanged':True,'right_half_strength_preserved':True,'references':['RS-01','RS-02','RS-03','UP-03'],'new_group_nodes':len(g.nodes)}
