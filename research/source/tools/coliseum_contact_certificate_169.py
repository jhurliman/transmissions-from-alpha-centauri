"""Read-only continuous-distance certificate for frozen169 removed intervals."""
import math
from mathutils import Vector,Matrix

def certify(payload,snapshot,matrix,surface,tolerance=.02,numerical_margin=1e-4):
 from coliseum_contact_clip_169 import interpolate
 records=[];minimum=1e9;queries=0
 for row in payload['changes']:
  st=next(r for r in snapshot if r['layer']==row['layer']and r['frame']==row['frame'])['strokes'][row['stroke']]
  def p(t):return matrix@Vector(interpolate(st,t)['position'])
  for lo,hi in row['removed_parameter_intervals']:
   breaks=[lo]+[float(i)for i in range(math.floor(lo)+1,math.ceil(hi))if lo<i<hi]+[hi];leaves=[]
   def verify(a,b,depth=0):
    nonlocal minimum,queries
    mid=(a+b)/2;pa,pb,pm=p(a),p(b),p(mid);distance=surface.find_nearest(pm)[3];queries+=1
    # Distance to any closed triangle surface is1-Lipschitz in world metres.
    half_length=(pb-pa).length/2;lower=distance-half_length-numerical_margin
    if lower>tolerance:
     leaves.append({'parameter_interval':[a,b],'midpoint_distance_m':distance,'half_world_length_m':half_length,'certified_lower_bound_m':lower});minimum=min(minimum,lower);return
    if depth>=30 or (pb-pa).length<1e-8:raise RuntimeError(f'169 continuous support certificate failed stroke{row["stroke"]} interval{a,b}:lower{lower}')
    verify(a,mid,depth+1);verify(mid,b,depth+1)
   for a,b in zip(breaks,breaks[1:]):verify(a,b)
   records.append({'layer':row['layer'],'frame':row['frame'],'stroke':row['stroke'],'removed_parameter_interval':[lo,hi],'straight_source_pieces':len(breaks)-1,'leaves':leaves})
 return {'method':'1-Lipschitz midpoint distance minus half world-space straight-piece length, minus numerical margin; adaptive subdivision at original vertices and midpoints','support_tolerance_m':tolerance,'numerical_margin_m':numerical_margin,'removed_intervals':len(records),'leaf_count':sum(len(r['leaves'])for r in records),'distance_queries':queries,'minimum_certified_distance_m':minimum,'all_intervals_certified':True,'intervals':records}
