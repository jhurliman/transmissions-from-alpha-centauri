import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-174/native';records={}
for tag,path in [('source',R/'art/studies/coliseum-168/scene.blend'),('candidate',O/'candidate.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));o=bpy.data.objects['COL110 U4 aperture head'];me=o.data;attrs={}
 for a in me.attributes:
  prop=next((k for k in ['value','vector','color']if len(a.data)and hasattr(a.data[0],k)),None)
  if not prop:continue
  vals=[]
  for x in a.data:
   v=getattr(x,prop);vals.append(list(v)if hasattr(v,'__len__')else v)
  attrs[a.name]={'domain':a.domain,'type':a.data_type,'values':vals}
 records[tag]=attrs;allowedloops=set(li for i in [711,4612]for li in me.polygons[i].loop_indices)
changes={}
for name,a in records['source'].items():
 b=records['candidate'].get(name)
 if a==b:continue
 ids=[i for i,(x,y)in enumerate(zip(a['values'],b['values']))if x!=y];changes[name]={'domain':a['domain'],'indices':ids,'source_values':[a['values'][i]for i in ids],'candidate_values':[b['values'][i]for i in ids]}
expected={'.corner_vert':allowedloops,'.corner_edge':allowedloops,'.edge_verts':{1413}};valid=all(k in expected and set(v['indices'])<=expected[k]for k,v in changes.items())
audit={'all_attribute_names_unchanged':set(records['source'])==set(records['candidate']),'all_non_topology_attributes_exact':valid,'generated_topology_differences':changes,'expected_edge':1413,'expected_corner_loops':sorted(allowedloops),'unexplained_changes':[]if valid else list(changes),'passed':valid and set(records['source'])==set(records['candidate'])};(O/'all-attribute-audit.json').write_text(json.dumps(audit,indent=2));print(audit)
