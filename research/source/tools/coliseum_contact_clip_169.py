"""Clip only native contact spans whose former masonry support was removed by167."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-169/contact';BOX=[(-15,-8),(173,202),(35,45)]
def snapshot(gp):
 out=[]
 for li,l in enumerate(gp.data.layers):
  for fi,f in enumerate(l.frames):
   dr=f.drawing;attrs={}
   for a in dr.attributes:
    prop=next((k for k in ('vector','color','value')if len(a.data)and hasattr(a.data[0],k)),None)
    if prop:
     vals=[]
     for q in a.data:
      v=getattr(q,prop);vals.append(list(v)if hasattr(v,'__len__')else v)
     attrs[a.name]={'domain':a.domain,'type':a.data_type,'prop':prop,'values':vals}
   off=0;strokes=[]
   for i,st in enumerate(dr.strokes):
    n=len(st.points);strokes.append({'point':{k:v['values'][off:off+n]for k,v in attrs.items()if v['domain']=='POINT'},'curve':{k:v['values'][i]for k,v in attrs.items()if v['domain']=='CURVE'}});off+=n
   out.append({'layer':li,'frame':fi,'strokes':strokes,'schema':{k:{j:v[j]for j in ['domain','type','prop']}for k,v in attrs.items()}})
 return out
def digest(snap):return hashlib.sha256(json.dumps(snap,sort_keys=True).encode()).hexdigest()
def tree(C,names=None):
 dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
 for ob in C.all_objects:
  if ob.type!='MESH'or ob.hide_render or names is not None and ob.name not in names:continue
  ev=ob.evaluated_get(dg);bb=[ev.matrix_world@Vector(v)for v in ev.bound_box]
  if any(max(v[k]for v in bb)<lo-.2 or min(v[k]for v in bb)>hi+.2 for k,(lo,hi)in enumerate(BOX)):continue
  me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
def interpolate(st,t):
 n=len(st['point']['position']);i=min(n-2,max(0,int(math.floor(t))));q=t-i;out={}
 for k,vv in st['point'].items():
  a,b=vv[i],vv[i+1]
  if q<1e-9:out[k]=a
  elif q>1-1e-9:out[k]=b
  elif isinstance(a,list):out[k]=[(1-q)*x+q*y for x,y in zip(a,b)]
  elif isinstance(a,(int,bool)):out[k]=a if q<.5 else b
  else:out[k]=(1-q)*a+q*b
 return out
def run(st,a,b):
 ts=[a]+[float(i)for i in range(math.floor(a)+1,math.ceil(b))if a<i<b]+[b];pp=[interpolate(st,t)for t in ts]
 return {'point':{k:[p[k]for p in pp]for k in pp[0]},'curve':dict(st['curve'])}
def apply(C):
 payload=json.load(open(O/'clip-payload.json'));gp=bpy.data.objects['110 Landmark contact ink'];before=snapshot(gp)
 if digest(before)!=payload['source_digest']:raise RuntimeError('169 contact source changed; rerun scoped support audit')
 transform=json.load(open(O/'source-transform.json'))
 if [list(row)for row in gp.matrix_world]!=transform['matrix_world']:raise RuntimeError('169 contact transform changed; world support evidence is invalid')
 if transform['attribute_digest']!=payload['source_digest']:raise RuntimeError('169 source transform/drawing records disagree')
 surf=tree(C);minimum=1e9
 from coliseum_contact_certificate_169 import certify
 continuous=certify(payload,before,gp.matrix_world,surf)
 for row in payload['changes']:
  for p in row['removal_samples_world']:
   d=surf.find_nearest(Vector(p))[3];minimum=min(minimum,d)
   if d<.029:raise RuntimeError('169 refused: proposed removed contact now has real support')
 gp.data=gp.data.copy();count=0;retained=[]
 for record in before:
  li,fi=record['layer'],record['frame'];changes=[r for r in payload['changes']if r['layer']==li and r['frame']==fi]
  if not changes:continue
  dr=gp.data.layers[li].frames[fi].drawing;removed=sorted(r['stroke']for r in changes);expected=[s for i,s in enumerate(record['strokes'])if i not in removed];newruns=[s for r in changes for s in r['runs']]
  dr.remove_strokes(indices=removed);basepoint=sum(len(s.points)for s in dr.strokes);basecurve=len(dr.strokes)
  if newruns:
   dr.add_strokes(sizes=[len(s['point']['position'])for s in newruns]);off=basepoint
   for j,st in enumerate(newruns):
    for k,values in st['point'].items():
     a=dr.attributes[k];prop=record['schema'][k]['prop']
     for i,v in enumerate(values):setattr(a.data[off+i],prop,v)
    for k,v in st['curve'].items():setattr(dr.attributes[k].data[basecurve+j],record['schema'][k]['prop'],v)
    off+=len(st['point']['position'])
  retained.append((li,fi,expected));count+=len(removed)
 after=snapshot(gp)
 for li,fi,expected in retained:
  actual=next(r for r in after if r['layer']==li and r['frame']==fi)['strokes'][:len(expected)]
  if actual!=expected:raise RuntimeError('169 untouched contact attributes changed')
 return {'object':gp.name,'changed_source_strokes':count,'source_strokes':sum(len(r['strokes'])for r in before),'result_strokes':sum(len(r['strokes'])for r in after),'minimum_removed_span_sample_distance_to_surviving_solid_m':minimum,'source_matrix_exact':True,'continuous_support_certificate':{k:v for k,v in continuous.items()if k!='intervals'},'all_unaffected_stroke_attributes_exact':True,'geometry_materials_lights_unchanged':True,'source_digest':payload['source_digest'],'after_digest':digest(after),'scope':'Only167 former-support contact spans; all surrounding native contact strokes preserved'}
