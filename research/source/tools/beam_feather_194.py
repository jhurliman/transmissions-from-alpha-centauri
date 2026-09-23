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
   # A SINGLE common envelope gates every strand on this edge. This creates
   # separated brush swathes rather than six overlapping all-length combs.
   macrocell=self.op('FLOOR',self.op('DIVIDE',along,6.7))
   mh=self.hash(self.add(macrocell,phase));mh2=self.hash(self.add(macrocell,self.add(phase,83.91)))
   center=self.mul(6.7,self.add(macrocell,self.add(.31,self.mul(.38,mh))))
   halfspan=self.add(.82,self.mul(1.40,mh2))
   distance=self.op('ABSOLUTE',self.sub(along,center))
   envelope=self.smooth(self.op('DIVIDE',self.sub(halfspan,distance),self.mul(halfspan,.48)))
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
   result=self.op('MAXIMUM',result,mask)
  return result

def group():
 g=bpy.data.node_groups.new('194 Analytic inward bristle field','ShaderNodeTree')
 for name in ('Along in half widths','Across in half widths','Seed'):
  g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
 g.interface.new_socket(name='Edge rooted coverage',in_out='OUTPUT',socket_type='NodeSocketFloat')
 i=g.nodes.new('NodeGroupInput');o=g.nodes.new('NodeGroupOutput');f=Field(g)
 g.links.new(f.mask(i.outputs[0],i.outputs[1],i.outputs[2]),o.inputs[0]);return g

def apply(scene):
 g=group();rows=[]
 for hn in HOSTS:
  host=scene.objects[hn]
  for ob in host.instance_collection.all_objects:
   if not ob.name.startswith(('Y arm','Y stem')):continue
   pts=np.array([list(host.matrix_world@ob.matrix_world@v.co) for v in ob.data.vertices]);center=pts.mean(0)
   vals,axes=np.linalg.eigh(np.cov((pts-center).T));order=np.argsort(vals);long=axes[:,order[-1]];wide=axes[:,order[-2]]
   half=float(np.max(np.abs((pts-center)@wide)));ends=(pts-center)@long
   seed=int(hashlib.sha256((hn+'|'+ob.name).encode()).hexdigest()[:6],16)%1009*.137
   s=np.linspace(float(ends.min()/half),float(ends.max()/half),1600)[:,None];u=np.linspace(-1,1,256)[None,:]
   measured=Field().mask(s,u,seed)
   for slot in ob.material_slots:
    old=slot.material;m=old.copy();m.name='194 Inward feather oxide | '+ob.name;n=m.node_tree.nodes;l=m.node_tree.links
    mix=next(q for q in n if q.label=='189 Edge-fed oxide over accepted steel')
    geo=n.new('ShaderNodeNewGeometry');geo.label='194 Native world position'
    p=n.new('ShaderNodeVectorMath');p.operation='SUBTRACT';p.inputs[1].default_value=tuple(center);l.new(geo.outputs['Position'],p.inputs[0])
    field=n.new('ShaderNodeGroup');field.node_tree=g;field.label='194 Bristles point across width from both edges';field.inputs[2].default_value=seed
    for index,axis in enumerate((long,wide)):
     dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=tuple(axis/half);l.new(p.outputs[0],dot.inputs[0]);l.new(dot.outputs['Value'],field.inputs[index])
    l.new(field.outputs[0],mix.inputs[0]);slot.link='OBJECT';slot.material=m;m['194 feather corrosion']=True
    rows.append({'host':hn,'object':ob.name,'old_material':old.name,'material':m.name,'world_long_axis':long.tolist(),'world_width_axis':wide.tolist(),'half_width_m':half,'seed':seed,'sampled_broad_face_mask_above_20_percent':float((measured>.2).mean()),'sampled_broad_face_mean_mask':float(measured.mean()),'oxide_palette_and_lighting_unchanged':True,'geometry_unchanged':True})
 return {'materials':rows,'shared_group_nodes':len(g.nodes),'new_meshes':0,'shape':'V2 shared irregular brush swathes with quiet edge gaps and fine unequal inward fringe' ,'references':['RS-01','RS-02','RS-03','UP-03'],'right_50_percent_applied':False,'right_193_hook_preserved':True,'sampling_note':'CPU analytic broad-face coverage estimate, not rendered visibility measurement'}
if __name__=='__main__':
 out=ROOT/'art/studies/beam-feather-194';out.mkdir(parents=True,exist_ok=True)
 audit=apply(bpy.context.scene);audit['module_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (out/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate.blend'))
 print('194_READY',len(audit['materials']),audit['shared_group_nodes'])
