import json,collections
from pathlib import Path
O=Path(__file__).resolve().parent;rows=json.load(open(O/'material-receivers.json'));graphs=json.load(open(O/'material-native-graphs.json'));bindings=json.load(open(O/'group-bindings.json'));rows=[r for r in rows if r['object'].startswith('COL')]
materials={};noiselabels=['Connected worn pigment islands','Fine stone pits and dry pigment','Interrupted vertical runoff','Grime branches','127 Broken sponge pigment at 4K scale']
for mat in sorted(set(r['material']for r in rows)):
 if mat not in graphs:continue
 ns=graphs[mat];by={n['name']:n for n in ns}
 def upstream(node):
  seen=set();todo=[node]
  while todo:
   k=todo.pop()
   if k in seen or k not in by:continue
   seen.add(k);todo.extend(z['node']for i in by[k]['inputs']for z in i['links'])
  return [by[k]for k in seen]
 emission=[n for n in ns if n['type']=='EMISSION'];active={n['name']for e in emission for n in upstream(e['name'])};dark=[];ao=[]
 for n in ns:
  if n['name']not in active:continue
  if n['type']=='AMBIENT_OCCLUSION':ao.append(n)
  if n['type']=='MIX_RGB'and n['inputs'][0]['links']:
   u=[q for z in n['inputs'][0]['links']for q in upstream(z['node'])];labels=sorted(set(q['label']for q in u if q['label']in noiselabels))
   if labels and not any(q['type']=='AMBIENT_OCCLUSION'for q in u):dark.append({'node':n['name'],'label':n['label'],'blend_type':n.get('blend_type'),'factor_input':n['inputs'][0],'base_color_input':n['inputs'][1],'second_color_input':n['inputs'][2],'factor_noise_sources':labels,'factor_contains_AO':False})
 rr=[r for r in rows if r['material']==mat];materials[mat]={'first_hit_sample_count':len(rr),'objects':dict(collections.Counter(r['object']for r in rr)),'emission':emission,'palette':[n for n in ns if n['name']in active and n['type']=='VALTORGB'and('Warm exposed'in n['label']or 'fracture stone'in n['label'])],'actual_light':[n for n in ns if n['name']in active and(n['type']in['RGBTOBW','SHADERTORGB','BSDF_DIFFUSE']or n['label'].startswith('165 '))],'ambient_occlusion':ao,'noise_driven_mix_hooks':dark,'age_binding':[b for b in bindings if b['material']==mat],'active_age_and_deposit_nodes':[n for n in ns if n['name']in active and n['type']in ['MIX_RGB','GROUP']and any(t in n['label']for t in ['135 ','148 ','150 ','152 ','153 ','155 ','158 ','162 '])]}
(O/'material-hooks.json').write_text(json.dumps(materials,indent=2))
receivers=[]
for key,rr in __import__('itertools').groupby(sorted(rows,key=lambda r:(r['object'],r['material_slot'],r['material'])),key=lambda r:(r['object'],r['material_slot'],r['material'])):
 rr=list(rr);sample=rr[len(rr)//2];receivers.append({'object':key[0],'slot':key[1],'material':key[2],'sample_count':len(rr),'first_hit_sample_bbox':[min(r['pixel'][0]for r in rr),min(r['pixel'][1]for r in rr),max(r['pixel'][0]for r in rr),max(r['pixel'][1]for r in rr)],'observed_face_indices':sorted(set(r['face']for r in rr)),'representative':sample,'downward_normal_sample_count':sum(r['normal'][2]<-.65 for r in rr),'outward_approximately_vertical_sample_count':sum(abs(r['normal'][2])<.3 for r in rr)})
(O/'receiver-summary.json').write_text(json.dumps(receivers,indent=2));print('landmark rays',len(rows),'receiver slots',len(receivers),'materials',len(materials))
