import json,math,collections
from pathlib import Path
O=Path(__file__).parent;D=json.load(open(O/'raw-map.json'))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
allhits=D['regions']['primary_review']['samples']+D['regions']['secondary_review']['samples']
regions={'primary':{'box':[1685,545,1915,765],'tower':'Tower7','bays':[7,8],'height_bias':'One broad U7 sill/frieze field, ledge connection, unequal shoulder down Tower7 front and first spandrel; terminate before lower band.'},'secondary':{'box':[2080,575,2260,750],'tower':'Tower10','bays':[10,11],'height_bias':'Smaller interrupted upper collar/frieze field, shorter descent, do not repeat primary long shoulder.'}}
result={'source':D['source'],'coordinate_attribute':'115 Original world position','reference_ids':['UCL-01','UCL-02','DP-03'],'groups':{},'scene_modified':False}
for key,info in regions.items():
 x0,y0,x1,y1=info['box'];samples=[q for q in allhits if x0<=q['pixel'][0]<x1 and y0<=q['pixel'][1]<y1];samples=list({tuple(q['pixel']):q for q in samples}.values())
 tw='COL110 Tower7 core' if key=='primary' else 'COL110 Tower10 core remnant0';af=21 if key=='primary' else 2;base=next(q for q in samples if q['object']==tw and q['face']==af);eligible=[]
 for q in samples:
  name=q['object']or'';n=q.get('normal_original');mat=q.get('material','')
  if not n:continue
  ok=False
  if name==tw:ok=dot(sub(q['original_world'],base['original_world']),base['normal_original'])>-.08 and dot(n,base['normal_original'])>.96
  elif name=='COL127 T2 continuous arcade wall':ok=mat=='116 115 Painted masonry wall' and n[1]<-.85 and abs(n[2])<.25
  elif name in [f'COL110 U{j} sill wall'for j in info['bays']]:ok=n[1]<-.85 and abs(n[2])<.25
  elif any(name.startswith(f'COL110 T2 band{j:02d} profile')for j in info['bays']):ok=n[1]<-.6 and abs(n[2])<.55
  elif name.startswith('COL111 '+info['tower']+' tier2 stepped belt'):ok=n[1]<-.6 and abs(n[2])<.55
  elif name.startswith('COL111 '+info['tower']+' tier2 projecting shaft rib'):ok=n[1]<-.75 and abs(n[2])<.2
  if ok:eligible.append(q)
 g=collections.defaultdict(list)
 for q in eligible:g[q['object']].append(q)
 receivers=[]
 for name,qs in sorted(g.items(),key=lambda t:-len(t[1])):
  pts=[q['original_world']for q in qs];receivers.append({'object':name,'visible_sample_count':len(qs),'estimated_visible_sample_area_px2':36*len(qs),'evaluated_face_allowlist':sorted({q['face']for q in qs}),'original_visible_sample_bounds':[[min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)]],'representative_face_anchor':qs[len(qs)//2]})
 desired={'frieze':(1790,565),'collar':(1720,585),'descending_shoulder':(1725,648),'spandrel':(1768,616)}if key=='primary'else{'frieze':(2160,600),'collar':(2110,594),'descending_shoulder':(2110,685),'spandrel':(2190,653)}
 anchors={}
 for label,xy in desired.items():
  pool=[q for q in eligible if ('sill wall'in q['object'] if label=='frieze'else 'stepped belt'in q['object'] if label=='collar'else q['object']==tw if label=='descending_shoulder'else q['object']=='COL127 T2 continuous arcade wall')]
  anchors[label]=min(pool,key=lambda q:sum((a-b)**2 for a,b in zip(q['pixel'],xy))) if pool else None
 result['groups'][key]={**info,'anchors':anchors,'receiver_allowlist':receivers,'sampling':{'total':len(samples),'landmark_hits':sum(q['object']is not None for q in samples),'eligible_front_masonry_hits':len(eligible),'eligible_fraction_of_landmark':len(eligible)/sum(q['object']is not None for q in samples)},'tower_front_depth_anchor':base,'depth_gate':{'tower_front':{'normal_dot_min':.96,'signed_depth_min':-.08,'signed_depth_max':.06,'note':'Measured niche backs are -.18m(Tower7)/-.20m(Tower10), so reject these explicitly.'},'curved_wall':'Use per-face allowlist AND original front-facing normal/material classification. Do not use one global plane to depth-gate both bays: curvature shifts the front plane. Exclude120 Two-depth interior and pier/tunnel faces even within finite field.','sill_and_collar':'Per-object front face allowlists; normal Y<-.85 for sill, Y<-.6 and |Z|<.55 for collar/front molding. No niche/inset/lintel/backing objects.'},'quiet_area_target':'At least60% of eligible lit receiver sample area unchanged/subthreshold; only main25–40% visible deposit/remnant coverage. Original darkest undersides unchanged.'}
(O/'package-B-map.json').write_text(json.dumps(result,indent=2))
for k,v in result['groups'].items():print(k,v['sampling']);print([(n,a['pixel'],a['object'],a['face'])for n,a in v['anchors'].items()if a])
