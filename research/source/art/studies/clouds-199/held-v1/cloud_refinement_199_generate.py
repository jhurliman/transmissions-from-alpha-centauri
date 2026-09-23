"""Owned native-volume cloud derivatives; references never enter asset computation."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,zoom,map_coordinates
R=Path(__file__).resolve().parents[1];O=R/'art/studies/clouds-199/assets';O.mkdir(parents=True,exist_ok=True);U=4;rows=[]
for k,src in enumerate(sorted((R/'art/studies/cloud-082/assets').glob('*-pigment.png'))):
 a=np.array(Image.open(src).convert('RGBA'));mask=a[:,:,3]>128;d=zoom(distance_transform_edt(mask)-distance_transform_edt(~mask),U,order=1)*U;h,w=d.shape;rng=np.random.default_rng(199031+k*97)
 def noise(sy,sx):
  q=gaussian_filter(rng.standard_normal((h,w)),(sy*U,sx*U));return q/max(q.std(),1e-8)
 yy,xx=np.mgrid[:h,:w];edge=np.minimum.reduce([yy,xx,h-1-yy,w-1-xx]);taper=np.clip(edge/(8*U),0,1)
 # Unequal billow shoulders, finer lobes, restrained finest fray. Avoid equal grain.
 shoulder=noise(2.4,4.9);lobes=noise(.70,1.45);fine=noise(.24,.55)
 activity=np.clip(.60+.22*noise(7,17),.15,1.0)
 gy,gx=np.gradient(d);upper=np.clip(.5+.5*gy,0,1)
 contour=d+U*((1.65*shoulder+1.05*lobes)*activity+.24*fine*(.4+.6*upper))*taper
 accepted=np.load(R/'art/studies/clouds-133/assets'/(src.stem+'.npz'))['rgba'];target_fraction=float((accepted[:,:,3]>.5).mean());area_offset=float(np.quantile(contour,1-target_fraction));contour-=area_offset
 alpha=np.clip(contour/(.72*U)+.5,0,1);alpha=alpha*alpha*(3-2*alpha)
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True)
 tone=(a[:,:,0].astype(float)-198)/12;tone[~mask]=tone[tuple(idx[:,~mask])];tone=zoom(tone,U,order=1)
 warp_y=U*1.05*noise(2.3,9);warp_x=U*2.7*noise(3.7,12)
 tone=map_coordinates(tone,[yy+warp_y,xx+warp_x],order=1,mode='nearest')
 broad=gaussian_filter(tone,(3.2*U,6.5*U));layer=gaussian_filter(tone,(.9*U,1.8*U))
 # Broad calm body + subtler overlapping native-derived veils. Noise only perturbs
 # these layers slightly; it never defines separate cel-shaped interior bands.
 tone=.48+.24*(broad-.5)+.15*(layer-.5)+.022*noise(5,20)+.010*noise(1.4,6)
 tone=np.clip(tone,0,1)
 dark=np.array([190,79,61]);middle=np.array([203,84,62]);light=np.array([214,94,69]);f=np.minimum(tone*2,1)[...,None];rgb=dark+(middle-dark)*f;f=np.maximum(tone*2-1,0)[...,None];rgb=rgb+(light-middle)*f
 q=rgb/255;linear=np.where(q<=.04045,q/12.92,((q+.055)/1.055)**2.4);rgba=np.concatenate([linear,alpha[...,None]],axis=2).astype('float32');np.savez_compressed(O/(src.stem+'.npz'),rgba=rgba)
 Image.fromarray(np.uint8(np.dstack([rgb,alpha*255]).clip(0,255))).save(O/(src.stem+'-preview.png'))
 newmask=alpha>.5;oldarea=mask.sum();newarea=newmask.sum()/U**2;oldyx=np.argwhere(mask).mean(0);newyx=np.argwhere(newmask).mean(0)/U
 rows.append({'family':src.stem,'source':str(src.relative_to(R)),'source_size':list(a.shape[:2]),'generated_size':[h,w],'area_change_fraction':newarea/oldarea-1,'centroid_delta_source_pixels':(newyx-oldyx).tolist(),'reference_pixels_used':False,'interior_rgb_mean':rgb[newmask].mean(0).tolist()})
(O.parent/'asset-audit.json').write_text(json.dumps(rows,indent=2))
