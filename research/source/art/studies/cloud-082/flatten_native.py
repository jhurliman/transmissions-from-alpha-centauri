"""Derive flat cloud colors from native Blender alpha and illumination only."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,label,binary_fill_holes
P=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
im=np.asarray(Image.open(P/'native-lightfield.png').convert('RGBA'),dtype=float)/255
alpha=im[:,:,3];inside=alpha>.5
v=im[:,:,0];v=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
bg=Image.open(P/'background.png').convert('RGBA')
results={}
for name,sigma,coverage in [('a',8,.23),('b',12,.32),('c',16,.40)]:
 f=gaussian_filter(v*alpha,sigma)/np.maximum(gaussian_filter(alpha,sigma),1e-8)
 threshold=float(np.quantile(f[inside],coverage));shadow=(f<threshold)&inside
 lab,n=label(shadow);sizes=np.bincount(lab.ravel());shadow&=sizes[lab]>max(200,inside.sum()*.002)
 # Absorb tiny light pinholes into surrounding shadow, while preserving the original silhouette.
 holes=binary_fill_holes(shadow)&~shadow;hl,n=label(holes);hs=np.bincount(hl.ravel());shadow|=holes&(hs[hl]<350);shadow&=inside
 shadow=gaussian_filter(shadow.astype(float),2.5)>.5;shadow&=inside
 lit=(f>np.quantile(f[inside],.87))&inside
 # Three contiguous palettes: broad warm face, restrained upper light, selective lower fold.
 out=np.zeros_like(im,dtype=np.uint8);out[:,:,:3]=[204,83,62];out[shadow,:3]=[198,79,61];out[lit,:3]=[210,88,64];out[:,:,3]=np.rint(alpha*255).astype(np.uint8)
 sprite=Image.fromarray(out,'RGBA');sprite.save(P/f'flat-{name}.png');Image.alpha_composite(bg,sprite).convert('RGB').save(P/f'flat-{name}-proof.png')
 results[name]={'smoothing_pixels':sigma,'shadow_target':coverage,'shadow_actual':float(shadow.sum()/inside.sum()),'highlight_actual':float(lit.sum()/inside.sum()),'source':'native-lightfield.png; original alpha unchanged'}
Image.fromarray(np.uint8(inside)*255).save(P/'native-alpha.png')
(P/'flatten-analysis.json').write_text(json.dumps(results,indent=2)+'\n')
