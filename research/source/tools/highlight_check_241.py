"""Read-only diagnostic of241 yellow-green removal and accepted240 blue retention.

Run after the native render; all thresholds are review aids, not approval.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
PATHS={
 '239':R/'art/studies/road-characters-239/main-4k.png',
 '240':R/'art/studies/hybrid-atmosphere-240/main-4k.png',
 '241':R/'art/studies/hybrid-finish-241/main-4k.png',
}
OUT=R/'art/studies/highlight-fix-241/pixel-check.json'

def yellow_green(a):
 r,g,b=np.moveaxis(a,-1,0)
 return (r>120)&(g>125)&(b<g*.72)&(r<g*1.2)

def main():
 missing=[str(p)for p in PATHS.values()if not p.exists()]
 if missing:raise SystemExit('Render not available yet: '+', '.join(missing))
 images={k:np.asarray(Image.open(p).convert('RGB'),dtype=np.float64) for k,p in PATHS.items()}
 assert all(a.shape==(2885,3840,3)for a in images.values()),'Expected unchanged4Kframe'
 crops={k:a[:1450,:1600]for k,a in images.items()}
 masks={k:yellow_green(a)for k,a in crops.items()}
 counts={k:int(m.sum())for k,m in masks.items()}
 old=masks['240'];new=masks['241'];remaining_at_old=int((new&old).sum());new_elsewhere=int((new&~old).sum())
 # Fixed240mask avoids bias from allowing candidate colors to select themselves.
 # Upper-left architecture excludes changed lower ruins and lower-arcade haze.
 ref=images['240'][:1100,:1400];r,g,b=np.moveaxis(ref,-1,0)
 cool=(b>r*1.08)&(b>g*1.03)&(np.max(ref,axis=-1)<145)&(np.min(ref,axis=-1)>25)&~yellow_green(ref)
 a=ref[cool];z=images['241'][:1100,:1400][cool];delta=z-a
 med0=np.median(a,axis=0);med1=np.median(z,axis=0)
 blue0=np.median(a[:,2]-.5*(a[:,0]+a[:,1]));blue1=np.median(z[:,2]-.5*(z[:,0]+z[:,1]))
 reduction=1-counts['241']/max(1,counts['240'])
 result={
  'status':'diagnostic only; visual inspection and user decision remain required',
  'mask':{'space':'8-bit sRGB rendered pixels','crop_xyxy':[0,0,1600,1450],'formula':'R>120 AND G>125 AND B<0.72*G AND R<1.2*G'},
  'yellow_green_counts':counts,'fraction_removed_vs240':float(reduction),'remaining_at_same240pixels':remaining_at_old,'new_matching_pixels_elsewhere':new_elsewhere,
  'blue_retention':{'fixed_mask_source':'240','crop_xyxy':[0,0,1400,1100],'formula':'B>1.08*R AND B>1.03*G AND max(RGB)<145 AND min(RGB)>25 AND not yellow_green','pixels':int(cool.sum()),'median240_rgb':med0.tolist(),'median241_rgb':med1.tolist(),'median_rgb_delta':(med1-med0).tolist(),'mean_absolute_channel_change':float(np.abs(delta).mean()),'p95_absolute_channel_change':float(np.percentile(np.abs(delta),95)),'fraction_pixels_all_channels_within3':float((np.abs(delta).max(axis=1)<=3).mean()),'median_blue_excess240':float(blue0),'median_blue_excess241':float(blue1),'median_blue_excess_delta':float(blue1-blue0)},
  'advisory_criteria':{'highlight_reduction_at_least95percent':bool(reduction>=.95),'blue_median_each_channel_within3':bool(np.max(np.abs(med1-med0))<=3),'blue_excess_within2':bool(abs(blue1-blue0)<=2),'interpretation':'Prefer239-like near-zero yellow-green count; ≥95% removal is a useful first screen. Retained blue medians within3/255 and blue excess within2/255 support palette preservation. These are not proof of artifact removal; inspect vent slats, seams, condenser and frame edges.'}}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
