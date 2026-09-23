"""Strict, no-dither sprite exports from AI-authored artwork; requested pixel/palette quantization."""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-spacesuit-214/pixel'
reports=[]
for name,h in [('traveler-a',49),('traveler-b',47)]:
 src=Image.open(O/f'{name}-generated.png').convert('RGBA')
 alpha=src.getchannel('A').point(lambda a:255 if a>=128 else 0)
 bounds=alpha.getbbox();src=src.crop(bounds)
 for mult in [1,2]:
  hh=h*mult;ww=round(src.width/src.height*hh*1.2)
  # Pillow RGBA resize premultiplies alpha; no white/black fringe is introduced.
  small=src.resize((ww,hh),Image.Resampling.BOX);a=np.array(small);mask=a[:,:,3]>=128
  # Preserve the pictured yellow shoulder insignia / sage hair accent; no red-heart fallback from206.
  rgb=np.array(src)[:,:,:3].astype(float);sa=np.array(src.getchannel('A'))
  yellow=(rgb[:,:,0]>140)&(rgb[:,:,1]>105)&(rgb[:,:,2]<rgb[:,:,1]*.65)&(sa>128) if name=='traveler-a' else np.zeros(sa.shape,dtype=bool)
  if name=='traveler-b':
   hsv=np.array(src.convert('RGB').convert('HSV'));yy=np.arange(src.height)[:,None]/src.height
   yellow=(hsv[:,:,0]>38)&(hsv[:,:,0]<115)&(hsv[:,:,1]>25)&(sa>128)&(yy<.38)
  coverage=np.array(Image.fromarray(yellow.astype('uint8')*255).resize((ww,hh),Image.Resampling.BOX))/255
  accentcell=(coverage>=.18)&mask
  accent=np.median(rgb[yellow],axis=0).astype('uint8') if yellow.any() else None
  accents=accent[None,:]
  if name=='traveler-b':
   samples=rgb[yellow];lum=samples.mean(1);split=np.median(lum)
   accents=np.array([np.median(samples[lum<=split],axis=0),np.median(samples[lum>split],axis=0)],dtype='uint8')
  visible=a[:,:,:3][mask]
  for count in [16,24]:
   packed=Image.fromarray(visible[~accentcell[mask]].reshape(1,-1,3)).quantize(colors=count-len(accents),method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
   n=count-len(accents)
   pal=np.array(packed.getpalette()[:n*3],dtype=np.uint8).reshape(n,3)
   pal=np.vstack([pal,accents])
   # Exact nearest palette assignment, no error diffusion or semi-transparent antialias.
   distance=((visible[:,None,:].astype(float)-pal[None,:,:])**2).sum(2)
   idx=np.zeros((hh+2,ww+2),dtype=np.uint8);inner=idx[1:-1,1:-1];inner[mask]=np.argmin(distance,axis=1)+1
   if accentcell.any():
    ad=((a[:,:,:3][accentcell,None,:].astype(float)-accents[None,:,:])**2).sum(2)
    inner[accentcell]=n+np.argmin(ad,axis=1)+1
   out=Image.fromarray(idx,mode='P');out.putpalette([0,0,0]+pal.ravel().tolist()+[0]*(768-3-count*3));out.info['transparency']=0
   tag=f'{name}-{hh}h-{count}c';out.save(O/f'{tag}.png',transparency=0,optimize=False)
   preview=out.convert('RGBA').resize((out.width*10,out.height*12),Image.Resampling.NEAREST);preview.save(O/f'{tag}-preview.png')
   colors=len(np.unique(idx[idx>0]));assert colors<=count
   reports.append({'name':name,'file':f'{tag}.png','logical_canvas':[out.width,out.height],'logical_silhouette_height':hh,'logical_body_width':ww,'opaque_colors':colors,'foot_pivot_canvas':[out.width/2,out.height-1],'transparent_index':0,'alpha_values':[0,255],'display_pixel_aspect':1.2,'dither':False,'source_alpha_bounds':list(bounds),'palette_hex':['#'+''.join(f'{c:02x}' for c in rgb) for rgb in pal]})
(O/'exports.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps([{k:x[k]for k in ['file','logical_canvas','opaque_colors']}for x in reports],indent=2))
