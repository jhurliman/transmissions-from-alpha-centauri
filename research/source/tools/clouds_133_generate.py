"""Derive procedural cloud pigment/edge fields from owned082 native cloud assets only."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,zoom,map_coordinates
R=Path(__file__).resolve().parents[1];O=R/'art/studies/clouds-133/assets';O.mkdir(parents=True,exist_ok=True)
cfg=json.loads((R/'config/clouds-133.json').read_text());U=cfg['upscale'];rows=[]
for k,src in enumerate(sorted((R/'art/studies/cloud-082/assets').glob('*-pigment.png'))):
 a=np.array(Image.open(src).convert('RGBA'));mask=a[:,:,3]>128;d=distance_transform_edt(mask)-distance_transform_edt(~mask);d=zoom(d,U,order=1)*U;h,w=d.shape;rng=np.random.default_rng(cfg['seed']+k*97)
 def noise(sy,sx):
  q=gaussian_filter(rng.standard_normal((h,w)),(sy*U,sx*U));return q/max(q.std(),1e-8)
 # Scales vary in aspect and amplitude; fine roughness rides coherent broad edge gusts.
 broad=noise(2.2,7.0);mid=noise(.85,1.9);fine=noise(.30,.65)
 yy,xx=np.mgrid[:h,:w];edge=np.minimum.reduce([yy,xx,h-1-yy,w-1-xx]);taper=np.clip(edge/(8*U),0,1);contour=d+U*(2.1*broad+1.0*mid+.45*fine)*taper
 alpha=np.clip(contour/(.72*U)+.5,0,1);alpha=alpha*alpha*(3-2*alpha)
 # Extend native tone out to the edge before softening; avoid dark transparent padding.
 idx=distance_transform_edt(~mask,return_distances=False,return_indices=True)
 tone=(a[:,:,0].astype(float)-198)/12;tone[~mask]=tone[tuple(idx[:,~mask])]
 tone=zoom(tone,U,order=1);tone=map_coordinates(tone,[yy+U*.8*noise(2,10),xx+U*1.8*noise(3,12)],order=1,mode="nearest");tone=gaussian_filter(tone,(1.8*U,3.6*U))
 veil=noise(4.5,15);fold=noise(1.6,6)
 tone=np.clip(.48+(tone-.5)*cfg['interior_contrast']+.075*veil+.028*fold,0,1)
 # Same accepted dark/mid/light pigment family, continuously layered, no threshold bands.
 dark=np.array([193,77,56]);middle=np.array([204,81,56]);light=np.array([215,92,61]);f=np.minimum(tone*2,1)[...,None];rgb=dark+(middle-dark)*f;f=np.maximum(tone*2-1,0)[...,None];rgb=rgb+(light-middle)*f
 q=rgb/255;linear=np.where(q<=.04045,q/12.92,((q+.055)/1.055)**2.4);rgba=np.concatenate([linear,alpha[...,None]],axis=2).astype('float32');np.savez_compressed(O/(src.stem+'.npz'),rgba=rgba)
 Image.fromarray(np.uint8(np.dstack([rgb,alpha*255]).clip(0,255))).save(O/(src.stem+'-preview.png'))
 oldarea=mask.sum();newarea=(alpha>.5).sum()/U**2;oldyx=np.argwhere(mask).mean(0);newyx=np.argwhere(alpha>.5).mean(0)/U
 rows.append({'family':src.stem,'source':str(src.relative_to(R)),'source_size':list(a.shape[:2]),'generated_size':[h,w],'area_change_fraction':newarea/oldarea-1,'centroid_delta_source_pixels':(newyx-oldyx).tolist(),'reference_pixels_used':False})
(O.parent/'asset-audit.json').write_text(json.dumps(rows,indent=2))
