"""225: remove ground-only sill barriers; lower native tunnel floors to foundation.
Upper sills/platforms, crowns, jambs and structural foundation stay exact.
"""
import bpy,json,math,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from coliseum_contact_clip_169 import snapshot,digest,interpolate,run
def solid_tree(obs,box=None):
 dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[]
 for ob in obs:
  if ob.type!='MESH' or ob.hide_render or 'ink' in ob.name.lower():continue
  ev=ob.evaluated_get(dg);bb=[ev.matrix_world@Vector(v)for v in ev.bound_box]
  if box and any(max(v[k]for v in bb)<a-.1 or min(v[k]for v in bb)>b+.1 for k,(a,b)in enumerate(box)):continue
  me=ev.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in f.vertices)for f in me.loop_triangles);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),vs

def clip_lost_contacts(scene,oldtree,oldvs,C):
 gp=scene.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy();box=[(min(v[k]for v in oldvs)-.05,max(v[k]for v in oldvs)+.05)for k in range(3)]
 newtree,_=solid_tree(C.all_objects,box);changes=[]
 for rec in old:
  for si,st in enumerate(rec['strokes']):
   vv=[M@Vector(p)for p in st['point']['position']]
   if len(vv)<2 or any(max(v[k]for v in vv)<a or min(v[k]for v in vv)>b for k,(a,b)in enumerate(box)):continue
   def unsupported(t):
    p=M@Vector(interpolate(st,t)['position'])
    return all(a<=p[k]<=b for k,(a,b)in enumerate(box)) and oldtree.find_nearest(p)[3]<.02 and newtree.find_nearest(p)[3]>.04
   ts=[0.]
   for i,(a,b)in enumerate(zip(vv,vv[1:])):
    if any(max(a[k],b[k])<lo or min(a[k],b[k])>hi for k,(lo,hi)in enumerate(box)):ts.append(float(i+1));continue
    n=max(1,math.ceil((a-b).length/.01));ts.extend(i+j/n for j in range(1,n+1))
   status=[unsupported(t)for t in ts]
   if not any(status):continue
   assert not st['curve'].get('cyclic',False),'225 cyclic lost contact requires explicit run topology'
   removed=[];start=0. if status[0]else None
   for i in range(1,len(ts)):
    if status[i]==status[i-1]:continue
    a,b=ts[i-1],ts[i];sa=status[i-1]
    for _ in range(20):
     mid=(a+b)/2
     if unsupported(mid)==sa:a=mid
     else:b=mid
    edge=(a+b)/2
    if status[i]:start=edge
    else:removed.append([start,edge]);start=None
   if start is not None:removed.append([start,float(len(vv)-1)])
   kept=[];p=0.
   for a,b in removed:
    if a-p>1e-7:kept.append([p,a])
    p=b
   if len(vv)-1-p>1e-7:kept.append([p,float(len(vv)-1)])
   changes.append({'layer':rec['layer'],'frame':rec['frame'],'stroke':si,'removed_parameter_intervals':removed,'retained_parameter_intervals':kept,'runs':[run(st,a,b)for a,b in kept]})
 if not changes:return {'changed_strokes':0,'original_attributes_exact':True}
 from coliseum_contact_certificate_169 import certify
 payload={'changes':changes};cert=certify(payload,old,M,newtree)
 gp.data=gp.data.copy();gp.data.name='225 Ground sill unsupported contacts removed'
 def stored(v):
  if isinstance(v,list):return [stored(x)for x in v]
  return struct.unpack('f',struct.pack('f',v))[0]if isinstance(v,float)else v
 expected=[]
 for rec in old:
  edits=[r for r in changes if r['layer']==rec['layer']and r['frame']==rec['frame']]
  if not edits:expected.append(rec);continue
  dr=gp.data.layers[rec['layer']].frames[rec['frame']].drawing;indices=sorted(r['stroke']for r in edits);kept=[st for i,st in enumerate(rec['strokes'])if i not in indices];runs=[st for r in edits for st in r['runs']]
  dr.remove_strokes(indices=indices);off=sum(len(st.points)for st in dr.strokes);coff=len(dr.strokes)
  if runs:
   dr.add_strokes(sizes=[len(st['point']['position'])for st in runs])
   for j,st in enumerate(runs):
    for k,vals in st['point'].items():
     for i,v in enumerate(vals):setattr(dr.attributes[k].data[off+i],rec['schema'][k]['prop'],v)
    for k,v in st['curve'].items():setattr(dr.attributes[k].data[coff+j],rec['schema'][k]['prop'],v)
    off+=len(st['point']['position'])
  expected.append(dict(rec,strokes=kept+[{'point':{k:stored(v)for k,v in st['point'].items()},'curve':st['curve']}for st in runs]))
 after=snapshot(gp);assert after==expected
 return {'changed_strokes':len(changes),'removed_intervals':cert['removed_intervals'],'continuous_support_certificate':{k:v for k,v in cert.items()if k!='intervals'},'unaffected_attributes_exact':True,'before_digest':digest(old),'after_digest':digest(after),'changes':[{k:v for k,v in r.items()if k!='runs'}for r in changes]}

def apply(scene):
 if scene.get('sills225_applied'):raise RuntimeError('225 already applied')
 C=bpy.data.collections['110 Coliseum detailed front ruin'];sills=[scene.objects[f'COL110 T0 B{i:02d} sill']for i in range(18)];platforms=[o for o in C.objects if o.get('125 inset platform')and o.get('tier')==0];assert len(platforms)==18
 oldtree,vs=solid_tree(sills+platforms);foundation=scene.objects['COL110 half-ring structural foundation'];ftree,fvs=solid_tree([foundation]);zmax=max(v.z for v in fvs);rows=[]
 for bay in range(18):
  ob=scene.objects[f'COL220 T0 B{bay:02d} 30m then45deg down30m'];old=ob.data;me=old.copy();me.name=old.name+' | 225 lowered floor';n=27;assert len(me.vertices)==7*n*2
  before=[ob.matrix_world@v.co for v in me.vertices];deltas=[];support=[]
  for endpoint in(0,n-1):
   p=before[2*n+endpoint];hit=ftree.ray_cast(Vector((p.x,p.y,zmax+2)),Vector((0,0,-1)))
   assert hit[0] is not None,(bay,endpoint,'missing native foundation support')
   deltas.append(hit[0].z-p.z);support.append(list(hit[0]))
  assert all(-3<d<-.2 for d in deltas),(bay,deltas)
  inv=ob.matrix_world.inverted();changed=[];factor=.715*scene.objects['COL127 T0 continuous arcade wall'].matrix_world.to_scale().x
  for station in range(7):
   for end,delta in zip((0,n-1),deltas):
    for layer in(0,1):
     i=station*2*n+layer*n+end;p=before[i]+Vector((0,0,delta));me.vertices[i].co=inv@p
     if '115 Original world position'in me.attributes:me.attributes['115 Original world position'].data[i].vector.z+=delta/factor
     changed.append(i)
  me.update();ob.data=me;ob['225 lowered floor']=True
  import bmesh
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free();assert bad==0 and vol>0
  after=[ob.matrix_world@v.co for v in me.vertices];assert all(a==b for i,(a,b)in enumerate(zip(before,after))if i not in changed)
  center=lambda st: (after[st*2*n]+after[st*2*n+n-1])/2
  mouth=center(1);bend=center(4);outlet=center(6);straight=(bend-mouth).length;down=(outlet-bend).length;drop=bend.z-outlet.z
  assert abs(straight-30)<.001 and abs(down-30)<.001 and abs(drop-30/math.sqrt(2))<.001
  rows.append({'bay':bay,'tunnel':ob.name,'lowering_m':deltas,'foundation_entry_points':support,'mouth_floor_center':list(mouth),'bend_floor_center':list(bend),'outlet_floor_center':list(outlet),'entry_step_error_m':max(abs(after[2*n+e].z-q[2])for e,q in zip((0,n-1),support)),'roof_and_all_other_vertices_exact':True,'modified_vertices':changed,'straight_m':straight,'descending_m':down,'vertical_drop_m':drop,'nonmanifold_edges':bad})
 for o in sills+platforms:o.hide_render=True;o.hide_set(True);o['hidden225']='Ground arcade walk-through threshold removal'
 bpy.context.view_layer.update();ink=clip_lost_contacts(scene,oldtree,vs,C);scene['sills225_applied']=True
 return {'iteration':225,'ground_platforms_hidden':[o.name for o in platforms],'ground_sills_hidden':[o.name for o in sills],'upper_platforms_and_sills_preserved':True,'structural_foundation_columns_jambs_unchanged':True,'tunnel_refits':rows,'contact_ink':ink,'review':'CPU native geometry only; combined main-camera proof pending'}
if __name__=='__main__':
 O=R/'art/studies/arcade-sills-225';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/haze-texture-221/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
