"""Measured gap infill, native floor courses, and top-down footprint audit."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from far_building_layout_226 import boxpoints
from alley_repeat_212 import verts
SPECS=[(-1,94,'215 left gallery 123',0),(-1,113,'215 left service 103',2.18),(-1,134,'215 left gallery 123',0),(1,100,'215 right service 131',2.18),(1,121,'215 right gallery 111',0),(1,140,'215 right gallery 149',4.36)]
def inventory(scene):
 rows=[]
 for root in bpy.data.collections['215 Short alley composition'].objects:
  if not root.instance_collection:continue
  pts=[p for o in root.instance_collection.objects if not any(t in o.name.lower()for t in ('service','shoe','closed')) for p in verts(o,root.matrix_world)]
  rows.append({'name':root.name,'origin':list(root.location),'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]]})
 return rows

def apply(scene):
 C=bpy.data.collections['215 Short alley composition'];before=inventory(scene);added=[];ink=bpy.data.collections['215 Distant accepted component ink'];mesh=[]
 for side,y,srcname,extra in SPECS:
  src=scene.objects[srcname];root=src.copy();root.name=f'230 {"left"if side<0 else"right"} infill {y}';C.objects.link(root)
  old=src.instance_collection;col=bpy.data.collections.new(root.name+' private native prefab');col.use_fake_user=True;col.instance_offset=old.instance_offset;root.instance_collection=col
  peers=sorted((r for r in before if r['origin'][0]*side>0),key=lambda r:r['origin'][1]);a=max((r for r in peers if r['origin'][1]<y),key=lambda r:r['origin'][1]);b=min((r for r in peers if r['origin'][1]>y),key=lambda r:r['origin'][1]);t=(y-a['origin'][1])/(b['origin'][1]-a['origin'][1]);x=a['origin'][0]*(1-t)+b['origin'][0]*t+side*.6
  root.location.x=x;root.location.y=y
  mapping={}
  for o in old.objects:
   q=o.copy();q.name='230 infill '+o.name;col.objects.link(q);mapping[o]=q
   if q.type=='MESH':mesh.append(q)
  if extra:
   panels=[o for o in old.objects if o.instance_collection and 'layout_broad'in o.name]
   street=[o for o in panels if boxpoints(o)[1][0]-boxpoints(o)[0][0]<.5];template=street[0];ta,tb=boxpoints(template);ty=(ta[1]+tb[1])/2
   roofs=[o for o in old.objects if o.name.startswith('215 real roof slab')];heights=[]
   for roof in roofs:
    a0,b0=boxpoints(roof);h=a0[2]+.02;yc=(a0[1]+b0[1])/2;heights.append((yc,h));mapping[roof].location.z+=extra
    for o in old.objects:
     if o.instance_collection and 'floor_band'in o.name:
      aa,bb=boxpoints(o)
      if abs(aa[2]-(h+.17))<.03 and abs((aa[1]+bb[1])/2-yc)<.02:mapping[o].location.z+=extra
    for k in range(round(extra/2.18)):
     q=template.copy();q.name='230 upper facade layout_broad';q.matrix_world=Matrix.Translation((0,yc-ty,h+.02+k*2.18-ta[2]))@template.matrix_world;col.objects.link(q)
   for o in panels:
    aa,bb=boxpoints(o)
    if bb[0]-aa[0]<2.5 or bb[1]-aa[1]>.5:continue
    peers2=[p for p in panels if abs(sum(boxpoints(p)[i][0]for i in(0,1))/2-(aa[0]+bb[0])/2)<.03 and abs(sum(boxpoints(p)[i][1]for i in(0,1))/2-(aa[1]+bb[1])/2)<.03]
    if aa[2]<max(boxpoints(p)[0][2]for p in peers2)-.01:continue
    h=min(heights,key=lambda a:abs(a[0]-(aa[1]+bb[1])/2))[1]
    for k in range(round(extra/2.18)):
     q=o.copy();q.name='230 upper return layout_broad';q.matrix_world=Matrix.Translation((0,0,h+.02+k*2.18-aa[2]))@o.matrix_world;col.objects.link(q)
   for o in old.objects:
    if not any(t in o.name for t in('quiet inner wall','leading interior return','rear wall return','outer rear wall')):continue
    q=mapping[o];q.data=o.data.copy();aa,bb=boxpoints(o)
    # Existing native shell only: extend its upper vertices; panel module dimensions stay fixed.
    for v in q.data.vertices:
     if abs(v.co.z-bb[2])<.001:v.co.z+=extra
  added.append({'root':root.name,'frontage_x':x,'depth_y':y,'additional_native_courses':round(extra/2.18),'source':srcname})
 for o in mesh:
  if o.name not in ink.objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in mesh:
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 bpy.context.view_layer.update();return {'before':before,'added':added,'after':inventory(scene),'existing_roots_unchanged':True,'no_component_scaling':True}
if __name__=='__main__':
 O=R/'art/studies/midground-230';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entry-surround-229/scene.blend'));a=apply(bpy.context.scene);(O/'layout-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'layout-only.blend'));print('230 LAYOUT READY',flush=True)
