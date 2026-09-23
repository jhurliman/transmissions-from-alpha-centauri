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
   for family,spacing in enumerate((.22,.35,.61)):
    phase=self.add(seed,edge*47.91+family*19.73)
    along=self.add(s,self.mul(phase,.139))
    cell=self.op('FLOOR',self.op('DIVIDE',along,spacing))
    h=self.hash(self.add(cell,phase));h2=self.hash(self.add(cell,self.add(phase,37.12)))
    cluster=self.hash(self.add(self.op('FLOOR',self.op('DIVIDE',along,1.17)),phase))
    center=self.mul(spacing,self.add(cell,self.add(.12,self.mul(.76,h))))
    reach=self.mul(self.add(.35,self.mul(.60,cluster)),self.add(.60,self.mul(.40,h2)))
    t=self.op('DIVIDE',d,reach)
    # Each strand starts at the physical edge; width and opacity decrease inward.
    root_width=self.mul(spacing,self.add(.20,self.mul(.22,h2)))
    width=self.mul(root_width,self.add(.035,self.op('POWER',self.clamp(self.sub(1,t)),.85)))
    lean=self.mul(self.sub(h,.5),.28)
    lateral=self.op('ABSOLUTE',self.sub(self.sub(along,center),self.mul(lean,d)))
    body=self.smooth(self.op('DIVIDE',self.sub(width,lateral),self.mul(width,.62)))
    fade=self.smooth(self.op('DIVIDE',self.sub(1,t),.30))
    active=self.smooth(self.op('DIVIDE',self.sub(cluster,.19),.10))
    strength=self.add(.64,self.mul(.30,h))
    mask=self.mul(self.mul(body,fade),self.mul(active,strength))
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
 return {'materials':rows,'shared_group_nodes':len(g.nodes),'new_meshes':0,'shape':'Independent edge-seeded tapered inward bristles; no detached cloud or island mask','references':['RS-01','RS-02','RS-03','UP-03'],'right_50_percent_applied':False,'right_193_hook_preserved':True,'sampling_note':'CPU analytic broad-face coverage estimate, not rendered visibility measurement'}
if __name__=='__main__':
 out=ROOT/'art/studies/beam-feather-194';out.mkdir(parents=True,exist_ok=True)
 audit=apply(bpy.context.scene);audit['module_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (out/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate.blend'))
 print('194_READY',len(audit['materials']),audit['shared_group_nodes'])
