import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-171/material-map';rows=json.load(open(O/'material-receivers.json'));names=set(r['material']for r in rows if r['object'].startswith('COL'));bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));groups={};bindings=[]
def dump(tree):
 if tree.name in groups:return
 incoming={}
 for l in tree.links:incoming.setdefault((l.to_node.name,l.to_socket.identifier),[]).append({'node':l.from_node.name,'socket':l.from_socket.name,'identifier':l.from_socket.identifier})
 ns=[]
 for n in tree.nodes:
  rr={'name':n.name,'label':n.label,'type':n.type,'inputs':[]}
  for i,q in enumerate(n.inputs):
   v=getattr(q,'default_value',None)
   if hasattr(v,'__len__')and not isinstance(v,str):v=list(v)
   if not isinstance(v,(str,float,int,list,type(None))):v=str(v)
   rr['inputs'].append({'index':i,'name':q.name,'identifier':q.identifier,'value':v,'links':incoming.get((n.name,q.identifier),[])})
  for k in ['operation','blend_type','attribute_name']:
   if hasattr(n,k):rr[k]=getattr(n,k)
  if hasattr(n,'color_ramp'):rr['ramp']=[{'position':e.position,'color':list(e.color)}for e in n.color_ramp.elements]
  if n.type=='GROUP':rr['node_tree']=n.node_tree.name
  ns.append(rr)
 groups[tree.name]=ns
 for n in tree.nodes:
  if n.type=='GROUP':dump(n.node_tree)
for name in names:
 m=bpy.data.materials.get(name)
 if not m or not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='GROUP':bindings.append({'material':name,'node':n.name,'label':n.label,'group':n.node_tree.name});dump(n.node_tree)
(O/'group-bindings.json').write_text(json.dumps(bindings,indent=2));(O/'group-graphs.json').write_text(json.dumps(groups,indent=2));print('groups',len(groups),'bindings',len(bindings))
