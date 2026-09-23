from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, sobel
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-053'
boxes={'facade':(1050,30,1440,550),'pipes':(280,120,560,670)}
def metrics(im):
 im=im.convert('RGB');im=im.resize((round(im.width*600/im.height),600),Image.Resampling.LANCZOS);a=np.array(im)/255
 mx=a.max(2);mn=a.min(2);sat=(mx-mn)/np.maximum(mx,.001);y=a@np.array([.2126,.7152,.0722]);lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);lum=lin@np.array([.2126,.7152,.0722])
 gx=sobel(y,axis=1)/8;gy=sobel(y,axis=0)/8;edge=np.hypot(gx,gy)
 # Local dark lines: pixel darker than neighborhood, distinct from broad shadow areas.
 darkline=(gaussian_filter(y,1.8)-y>.035)&(y<.23)
 # Chromatic vertical-band energy, excluding near-black lines and strong luminance edges.
 chrom=a[:,:,0]-a[:,:,2];band=gaussian_filter(chrom,(3,.6))-gaussian_filter(chrom,(3,3));mask=(y>.20)&(edge<.055)
 vals={'median_saturation':float(np.median(sat)),'p90_saturation':float(np.quantile(sat,.9)),'linear_luminance_std':float(lum.std()),'display_p90_p10':float(np.quantile(y,.9)-np.quantile(y,.1)),'dark_area_pct':float((y<.16).mean()*100),'dark_line_pct':float(darkline.mean()*100),'edge_pct':float((edge>.045).mean()*100),'vertical_chromatic_band_rms':float(np.sqrt(np.mean(band[mask]**2))),'fine_detail_rms':float(np.std(y-gaussian_filter(y,1.2)))}
 return {k:round(v,5) for k,v in vals.items()}
results={}
for region,box in boxes.items():
 results[region]={}
 ref=Image.open(R/'art/reviews/xenon-051'/('reference-'+region+'.png'));results[region]['reference']=metrics(ref)
 for key,path in [('052',R/'art/reviews/xenon-052/render.png')]+[(k,O/(k+'.png')) for k in ['A','B','C']]:
  if path.exists():
   im=Image.open(path).crop(box);im.save(O/(key+'-'+region+'.png'));results[region][key]=metrics(im)
(O/'metrics.json').write_text(json.dumps({'method':'Crops resized to height 600 preserving aspect; sRGB saturation; linear luminance spread; local dark-line mask; chromatic vertical bandpass excluding dark/strong edges.','limits':['Crops show comparable subjects, not registered identical structures.','Dark-line and vertical-band measures are proxies: seams, geometry, chips and shadows can contribute.','Statistics are evidence for direction, not an aesthetic score or target to maximize.'],'regions':results},indent=2));print(json.dumps(results,indent=2))
