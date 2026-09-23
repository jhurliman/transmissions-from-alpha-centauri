"""145 isolated native-alley placement. Runtime imports latest approved panel builder.
No render; caller controls materials/details and foreground ink refresh.
"""
import bpy,json,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-145/actual'
TARGETS=[('Architecture | layout_broad.007','Folded sheet face.045',2,'impact + crack'),('Architecture | layout_access.008','Folded sheet face.035',0,'top loss'),('Architecture | layout_transition.010','Folded sheet face.044',1,'facing pits')]
def bounds(o):
 vs=[v.co for v in o.data.vertices];return Vector(tuple(min(v[k]for v in vs)for k in range(3))),Vector(tuple(max(v[k]for v in vs)for k in range(3)))
def plan(scene=None):
 s=scene or bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();from bpy_extras.object_utils import world_to_camera_view
 out=[]
 for hn,on,variant,label in TARGETS:
  h=bpy.data.objects[hn];o=bpy.data.objects[on];M=next(i.matrix_world.copy() for i in dg.object_instances if i.object.original==o and i.parent and i.parent.original==h);lo,hi=bounds(o);origin=M@Vector((lo.x,lo.y,lo.z));uv=[M.to_3x3()@Vector(a)for a in [(1,0,0),(0,0,1),(0,-1,0)]];pp=[world_to_camera_view(s,s.camera,M@v.co)for v in o.data.vertices];hits={}
  for a in range(1,6):
   for b in range(1,6):
    p=M@Vector((lo.x+(hi.x-lo.x)*a/6,lo.y,lo.z+(hi.z-lo.z)*b/6));d=p-s.camera.location;q=s.ray_cast(dg,s.camera.location,d.normalized(),distance=d.length+.005);n=q[4].name if q[0]else'none';hits[n]=hits.get(n,0)+1
  # Field backing is already part of the factory module; measure in sheet-local Y.
  backs=[]
  for q in h.instance_collection.all_objects:
   if q.type=='MESH' and 'Panel field backing'in q.name:
    rel=o.matrix_world.inverted()@q.matrix_world;vs=[rel@v.co for v in q.data.vertices];backs.append({'object':q.name,'front_y_from_sheet_front':min(v.y for v in vs)-lo.y,'clear_gap_from_sheet_rear':min(v.y for v in vs)-hi.y})
  out.append({'host':hn,'source':on,'variant_index':variant,'variant':label,'width':hi.x-lo.x,'height':hi.z-lo.z,'thickness':hi.y-lo.y,'local_min':list(lo),'matrix_world':[list(r)for r in M],'origin':list(origin),'u':list(uv[0]),'v':list(uv[1]),'normal':list(uv[2]),'projected_bounds_4k':[min(p.x for p in pp)*3840,(1-max(p.y for p in pp))*2885,max(p.x for p in pp)*3840,(1-min(p.y for p in pp))*2885],'visible_grid_samples':hits.get(on,0),'grid_samples':25,'occluder_samples':hits,'existing_backing':backs})
 return out

def apply(scene=None,damage=True):
 s=scene or bpy.context.scene;sys.path.insert(0,str(R/'tools'));import alley_damage_145 as builder
 rows=plan(s);created=[];descriptors=[];audit=[]
 for row in rows:
  h=bpy.data.objects[row['host']];old=h.instance_collection;src=bpy.data.objects[row['source']];private=bpy.data.collections.new('145 Pilot private '+h.name)
  for child in old.children:private.children.link(child)
  for o in old.objects:private.objects.link(o)
  # Native panel parts are grouped by shared assembly location in this factory kit.
  removed=[]
  for q in list(private.objects):
   if (q.location-src.location).length<1e-6 and (q==src or any(t in q.name for t in ['Side folded return','Top / bottom return','Captive panel screw','Screw slot'])):
    private.objects.unlink(q);removed.append(q.name)
  h.instance_collection=private
  saved=builder.W,builder.H,builder.T; original_cutter=builder.cutter
  def adapted_cutter(name,rings,col):
   if 'crack' in name.lower():rings=[[(x+.95,y,z+row['height']-1.42) for x,y,z in ring]for ring in rings]
   elif 'impact entry' in name.lower():rings=[[(x+.70,y,z)for x,y,z in ring]for ring in rings]
   elif name=='Unequal shallow facing spall':
    large=sum(p[2]for p in rings[0])/len(rings[0])>.7;dx,dz=(.50,.30)if large else(.60,.65);rings=[[(x+dx,y,z+dz)for x,y,z in ring]for ring in rings]
   elif name=='Top missing facing volume':rings=[[(x,y,z+(row['height']-1.42 if z<row['height'] else 0))for x,y,z in ring]for ring in rings]
   return original_cutter(name,rings,col)
  try:
   builder.W,builder.H,builder.T=row['width'],row['height'],row['thickness'];builder.cutter=adapted_cutter;C,specs,asset=builder.apply(s)
  finally:builder.W,builder.H,builder.T=saved;builder.cutter=original_cutter
  spec=specs[row['variant_index']]
  shifted=[]
  for fi,poly in enumerate(spec.get('damage_footprints_uv',[])):
   dx,dz=(.70,0) if row['variant_index']==2 else ((.50,.30)if fi==0 else(.60,.65))if row['variant_index']==1 else(0,row['height']-1.42)
   shifted.append([(u+dx/row['width'],v+dz/row['height'])for u,v in poly])
  spec['damage_footprints_uv']=shifted
  panel=spec['object'];family=[q for q in C.objects if q.name.startswith(panel.name) and 'recessed backing'not in q.name]
  if damage and row['variant']=='impact + crack':
   crack=specs[3]['object'];shift=Vector(spec['origin'])-Vector(specs[3]['origin'])
   for v in crack.data.vertices:v.co+=shift
   bpy.context.view_layer.objects.active=panel;mod=panel.modifiers.new('Combine real impact and crack losses','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=crack;bpy.ops.object.modifier_apply(modifier=mod.name)
  if not damage:
   for q in family:bpy.data.objects.remove(q,do_unlink=True)
   family=[]
   for q in asset.objects:
    n=q.copy();n.data=q.data.copy();C.objects.link(n);family.append(n)
   panel=next(q for q in family if 'sheet'in q.name);spec['origin']=(0,0,0)
  # Build at native dimensions, then rigidly place in original collection frame.
  L=Matrix(row['matrix_world'])@Matrix.Translation(Vector(row['local_min']))@Matrix.Translation(-Vector(spec['origin']))
  for q in family:
   q.matrix_world=L@q.matrix_world;q['145 placement host']=h.name;created.append(q)
  for q in list(C.objects):
   if q not in family:bpy.data.objects.remove(q,do_unlink=True)
  C.name='145 Placed panel '+h.name
  d={**spec,'object':panel,'origin':tuple(row['origin']),'u':tuple(row['u']),'v':tuple(row['v']),'across':tuple(row['u']),'up':tuple(row['v']),'normal':tuple(row['normal']),'width':row['width'],'height':row['height'],'instance_host':h,'collection':C}
  descriptors.append(d);audit.append({**row,'removed_only_from_private_instance':removed,'new_objects':[q.name for q in family],'original_collection_unchanged':old.name,'new_collection':private.name,'added_backing':False})
 ink_audit=[]
 for name in ['096 contacts ink','096 damage ink']:
  ink=s.objects.get(name)
  if not ink:continue
  ink.data=ink.data.copy();count=0
  frames=[(Matrix(r['matrix_world']).inverted(),Vector(r['local_min']),r)for r in rows]
  for layer in ink.data.layers:
   for frame in layer.frames:
    for stroke in frame.drawing.strokes:
     for pt in stroke.points:
      world=ink.matrix_world@pt.position
      for iv,lo,r in frames:
       q=iv@world
       if lo.x-.015<q.x<lo.x+r['width']+.015 and lo.z-.015<q.z<lo.z+r['height']+.015 and lo.y-.025<q.y<lo.y+.085:
        if pt.opacity>0:pt.opacity=0;count+=1
        break
  ink_audit.append({'object':name,'local_points_hidden':count,'data_privately_copied':True})
 return {'panels':descriptors,'objects':created,'audit':audit,'ink_cleanup':ink_audit,'requires_foreground_ink_refresh':True}

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-rust-143/scene.blend'));O.mkdir(parents=True,exist_ok=True);rows=plan();(O/'placement-plan.json').write_text(json.dumps({'targets':rows,'mode':'read-only planning; no scene saved','camera_unchanged':True,'backing_policy':'Keep original field backing; do not add160mm kit backing','runtime_api':'apply(scene,damage=True) returns panels/objects/audit; caller supplies latest materials/details and rebuilds affected foreground ink'},indent=2));print(json.dumps(rows))
