from pathlib import Path
import numpy as np,json,collections,math
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parents[3];box=[2105,570,2235,685];rows=json.load(open(O/'first-hit-core.json'));zero=np.load(O/'black0.npy')[:,:,:3];one=np.load(O/'white1.npy')[:,:,:3];T=one-zero;actual=np.load(O/'actual_diffuse.npy')[:,:,:3];old=np.load(O/'old_palette_input.npy')[:,:,:3];validT=np.min(T,axis=2)>.05;d=(actual-zero)/np.maximum(T,1e-8);p=(old-zero)/np.maximum(T,1e-8);lookup={tuple(r['pixel']):r for r in rows};out=[]
for r in rows:
 x,y=r['pixel'];i=y-box[1];j=x-box[0];v=dict(r);v['calibrated_diffuse_rgb']=d[i,j].tolist();v['calibrated_input_rgb']=p[i,j].tolist();v['transport_rgb']=T[i,j].tolist();v['diffuse']=float(np.median(d[i,j]));v['palette_input']=float(np.median(p[i,j]));v['channel_disagreement']=float(max(np.ptp(d[i,j]),np.ptp(p[i,j])));neighbors=[lookup.get((x+dx,y+dy))for dy in [-1,0,1]for dx in [-1,0,1]];n=np.array(r['normal']);v['interior_coplanar_3x3']=all(q and q['object']==r['object']and q['slot']==r['slot']and float(np.dot(n,q['normal']))>math.cos(math.radians(12))for q in neighbors);v['usable']=bool(validT[i,j]and v['channel_disagreement']<.015 and -.01<=v['diffuse']<=2 and -.01<=v['palette_input']<=2);v['165_predicted_input']=.25*v['palette_input']+.75*(.30+.48*float(np.clip((v['diffuse']-.38)/.22,0,1)));out.append(v)
(O/'calibrated-pixels.json').write_text(json.dumps(out,indent=2));usable=[r for r in out if r['usable']];strict=[r for r in usable if r['interior_coplanar_3x3']]
def stats(rr):
 if not rr:return{'count':0}
 return{'count':len(rr),'diffuse_median':float(np.median([r['diffuse']for r in rr])),'diffuse_p10_p90':np.quantile([r['diffuse']for r in rr],[.1,.9]).tolist(),'old_input_median':float(np.median([r['palette_input']for r in rr])),'old_input_p10_p90':np.quantile([r['palette_input']for r in rr],[.1,.9]).tolist(),'165_predicted_input_median':float(np.median([r['165_predicted_input']for r in rr])),'165_low_clamp_fraction':sum(r['diffuse']<.38 for r in rr)/len(rr),'165_high_clamp_fraction':sum(r['diffuse']>.60 for r in rr)/len(rr),'channel_disagreement_median':float(np.median([r['channel_disagreement']for r in rr]))}
obj={}
for n in sorted(set(r['object']for r in out)):
 rr=[r for r in usable if r['object']==n];ss=[r for r in strict if r['object']==n];obj[n]={'all_usable':stats(rr),'strict_interior':stats(ss)}
groups=collections.defaultdict(list)
for r in usable:groups[(r['object'],r['face'],r['slot'])].append(r)
faces=[]
for (n,f,sl),rr in groups.items():
 if len(rr)<2:continue
 faces.append({'object':n,'face':f,'slot':sl,'normal':np.mean([r['normal']for r in rr],axis=0).tolist(),'representative_pixel':rr[len(rr)//2]['pixel'],'pixels':[r['pixel']for r in rr],**stats(rr)})
faces.sort(key=lambda r:-r['count']);summary={'first_hit_pixels':len(out),'usable_pixels':len(usable),'strict_interior_pixels':len(strict),'objects':obj,'faces':faces,'method':'Perchannel calibrated(signal-black)/(white-black); median of three independently corrected channels. Retained haze/ink transport cancels only under affine common coverage; excludeT<=.05 and corrected channel disagreement>.015. Strict interior requires3x3sameobject/slot within12degree normal.','limits':'Pixel filtering blends subpixelfaces; strict interior subset is preferred. These are diagnostic signals, not an art response or proof of visual gain.165 input computed analytically from frozen165 config, no materialassignment.'};(O/'signal-summary.json').write_text(json.dumps(summary,indent=2))
# Neutral scalar panels and sourcecrop are labelled diagnostic visualizations.
base=Image.open(R/'art/studies/coliseum-173/main-4k.png').crop(tuple(box)).convert('RGB');mask=np.zeros(validT.shape,bool)
for r in usable:mask[r['pixel'][1]-box[1],r['pixel'][0]-box[0]]=True
panels=[('173 retained',base)]
for label,arr in [('calibrated diffuse',np.median(d,axis=2)),('old ramp input',np.median(p,axis=2))]:
 gray=np.uint8(np.clip(arr,0,1)*255);rgb=np.repeat(gray[:,:,None],3,axis=2);rgb[~mask]=[32,32,32];panels.append((label,Image.fromarray(rgb)))
im=Image.new('RGB',(len(panels)*390,375),(24,24,24));dr=ImageDraw.Draw(im)
for k,(label,panel)in enumerate(panels):im.paste(panel.resize((390,345)),(k*390,30));dr.text((k*390+5,8),label,fill='white')
im.save(O/'signal-comparison.png');print(json.dumps({'counts':[len(out),len(usable),len(strict)],'objects':obj},indent=2))
