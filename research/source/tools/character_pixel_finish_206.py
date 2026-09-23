"""Strict, no-dither sprite exports from AI-authored artwork; requested pixel/palette quantization."""
from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206/pixel'
reports=[]
for name,h in [('airam',49),('miranda',47)]:
 src=Image.open(O/f'{name}-generated.png').convert('RGBA')
 alpha=src.getchannel('A').point(lambda a:255 if a>=128 else 0)
 bounds=alpha.getbbox();src=src.crop(bounds)
 for mult in [1,2]:
  hh=h*mult;ww=round(src.width/src.height*hh*1.2)
  # Pillow RGBA resize premultiplies alpha; no white/black fringe is introduced.
  small=src.resize((ww,hh),Image.Resampling.BOX);a=np.array(small);mask=a[:,:,3]>=128
  hsv=np.array(src.convert('RGB').convert('HSV'));sa=np.array(src.getchannel('A'))
  # Keep the pictured red printed motifs as authored accents at this very small grid.
  rgb=np.array(src)[:,:,:3].astype(float);yy=np.arange(src.height)[:,None]/src.height
  shirt=(yy>0.25)&(yy<(0.62 if name=='airam' else 0.54))
  red=((hsv[:,:,0]<9)|(hsv[:,:,0]>245))&(hsv[:,:,1]>105)&(hsv[:,:,2]>110)&(sa>128)&(rgb[:,:,1]<rgb[:,:,2]*1.15)&shirt
  coverage=np.array(Image.fromarray(red.astype('uint8')*255).resize((ww,hh),Image.Resampling.BOX))/255
  redcell=(coverage>=0.22)&mask
  redsource=np.array(src)[:,:,:3][red]
  accent=np.median(redsource,axis=0).astype('uint8') if len(redsource) else np.array([167,35,48],dtype='uint8')
  visible=a[:,:,:3][mask]
  for count in [16,24]:
   packed=Image.fromarray(visible.reshape(1,-1,3)).quantize(colors=count-1,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
   pal=np.array(packed.getpalette()[:(count-1)*3],dtype=np.uint8).reshape(count-1,3)
   pal=np.vstack([pal,accent])
   # Exact nearest palette assignment, no error diffusion or semi-transparent antialias.
   distance=((visible[:,None,:].astype(float)-pal[None,:-1,:])**2).sum(2)
   idx=np.zeros((hh+2,ww+2),dtype=np.uint8);inner=idx[1:-1,1:-1];inner[mask]=np.argmin(distance,axis=1)+1
   inner[redcell]=count
   out=Image.fromarray(idx,mode='P');out.putpalette([0,0,0]+pal.ravel().tolist()+[0]*(768-3-count*3));out.info['transparency']=0
   tag=f'{name}-{hh}h-{count}c';out.save(O/f'{tag}.png',transparency=0,optimize=False)
   preview=out.convert('RGBA').resize((out.width*10,out.height*12),Image.Resampling.NEAREST);preview.save(O/f'{tag}-preview.png')
   colors=len(np.unique(idx[idx>0]));assert colors<=count
   reports.append({'name':name,'file':f'{tag}.png','logical_canvas':[out.width,out.height],'logical_silhouette_height':hh,'logical_body_width':ww,'opaque_colors':colors,'foot_pivot_canvas':[out.width/2,out.height-1],'transparent_index':0,'alpha_values':[0,255],'display_pixel_aspect':1.2,'dither':False,'source_alpha_bounds':list(bounds),'palette_hex':['#'+''.join(f'{c:02x}' for c in rgb) for rgb in pal]})
(O/'exports.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps([{k:x[k]for k in ['file','logical_canvas','opaque_colors']}for x in reports],indent=2))
