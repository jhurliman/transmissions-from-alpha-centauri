"""226: annotated taller near-visible far prefabs and inward far street taper.
Private prefab containers, additional native-size panel courses; no component scaling.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from alley_repeat_212 import verts
HEIGHT=4.36
SHIFTS={'215 left service 103':1.6,'215 left gallery 123':3.5,'215 left service 144':6.2,'215 right gallery 111':-1.3,'215 right service 131':-3.7,'215 right gallery 149':-5.5}
TARGETS=['215 left step 83','215 right step 89']
def boxpoints(o):
 ps=list(verts(o));return [min(p[k]for p in ps)for k in range(3)],[max(p[k]for p in ps)for k in range(3)]
def projected(scene,root,structural=False):
 ps=[]
 for o in root.instance_collection.objects:
  if structural and any(t in o.name.lower()for t in['service','shoe','closed']):continue
  ps.extend(verts(o,root.matrix_world))
 qs=[world_to_camera_view(scene,scene.camera,p)for p in ps]
 return [min(q.x for q in qs)*3840,(1-max(q.y for q in qs))*2885,max(q.x for q in qs)*3840,(1-min(q.y for q in qs))*2885]
def apply(scene,reclip=True):
 if scene.get('layout226_applied'):raise RuntimeError('226 already applied')
 roots=list(bpy.data.collections['215 Short alley composition'].objects);before={o.name:{'all':projected(scene,o),'facade':projected(scene,o,True),'matrix':[list(r)for r in o.matrix_world]}for o in roots if o.instance_collection}
 added=[];raised=[];newmesh=[]
 for name in TARGETS:
  root=scene.objects[name];oldcol=root.instance_collection;col=bpy.data.collections.new('226 Taller private '+name);col.use_fake_user=True;col.instance_offset=oldcol.instance_offset;mapping={}
  for ob in oldcol.objects:
   q=ob.copy();q.name='226 '+ob.name;q['226 source component']=ob.name;col.objects.link(q);mapping[ob]=q;added.append(q.name)
   if q.type=='MESH':newmesh.append(q)
  root.instance_collection=col
  nativepanels=[]
  for ob in oldcol.objects:
   if ob.instance_collection and 'layout_broad'in ob.name:
    a,b=boxpoints(ob)
    if b[0]-a[0]<.5 and abs(b[2]-a[2]-2.16)<.01:nativepanels.append(ob)
  template=max(nativepanels,key=lambda o:boxpoints(o)[0][2]);ta,tb=boxpoints(template);ty=(ta[1]+tb[1])/2
  roofs=[o for o in oldcol.objects if o.name.startswith('215 real roof slab')]
  heights=[]
  def duplicate(ob,label,dz=0,dy=0):
   q=ob.copy();q.name='226 '+label;q.matrix_world=Matrix.Translation((0,dy,dz))@ob.matrix_world;q['226 native component source']=ob.name;col.objects.link(q);added.append(q.name)
   if q.type=='MESH':newmesh.append(q)
   return q
  for roof in roofs:
   a,b=boxpoints(roof);h=a[2]+.02;y=(a[1]+b[1])/2;heights.append({'y':y,'before':h,'after':h+HEIGHT})
   mapping[roof].location.z+=HEIGHT
   for ob in oldcol.objects:
    if ob.instance_collection and 'floor_band'in ob.name:
     aa,bb=boxpoints(ob)
     if abs(aa[2]-(h+.17))<.03 and abs((aa[1]+bb[1])/2-y)<.02:mapping[ob].location.z+=HEIGHT
   for k in range(2):duplicate(template,f'Full facade course {name} bay{y:.1f} level{k}',h+.02+2.18*k-ta[2],y-ty)
  # Extend interior support shells with newly dimensioned native solids; old shell meshes stay exact.
  for ob in oldcol.objects:
   if not any(t in ob.name for t in['quiet inner wall','leading interior return','rear wall return','outer rear wall']):continue
   a,b=boxpoints(ob);lo=b[2]-.015;hi=b[2]+HEIGHT;vs=[(x,y,z)for x,y,z in[(a[0],a[1],lo),(a[0],a[1],hi),(a[0],b[1],lo),(a[0],b[1],hi),(b[0],a[1],lo),(b[0],a[1],hi),(b[0],b[1],lo),(b[0],b[1],hi)]]
   me=bpy.data.meshes.new('226 Structural course solid');me.from_pydata(vs,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.update()
   for m in ob.data.materials:me.materials.append(m)
   q=bpy.data.objects.new('226 Upper structural course '+ob.name,me);col.objects.link(q);added.append(q.name);newmesh.append(q)
  # Accepted panel ends on BOTH returns; each end follows its local stepped roof.
  for ob in oldcol.objects:
   if not(ob.instance_collection and 'layout_broad'in ob.name):continue
   a,b=boxpoints(ob)
   if b[0]-a[0]<2.5 or b[1]-a[1]>.5:continue
   # Only duplicate each end's topmost existing course, once for each new course.
   peers=[p for p in oldcol.objects if p.instance_collection and 'layout_broad'in p.name and abs((boxpoints(p)[0][0]+boxpoints(p)[1][0])/2-(a[0]+b[0])/2)<.03 and abs((boxpoints(p)[0][1]+boxpoints(p)[1][1])/2-(a[1]+b[1])/2)<.03]
   if a[2]<max(boxpoints(p)[0][2]for p in peers)-.01:continue
   end_y=(a[1]+b[1])/2;H=min(heights,key=lambda h:abs(h['y']-end_y))['before']
   for k in range(2):duplicate(ob,f'Upper end panel {name} {ob.name} level{k}',H+.02+2.18*k-a[2])
  raised.append({'root':name,'old_prefab':oldcol.name,'new_private_prefab':col.name,'height_addition_m':HEIGHT,'courses_added_per_bay':2,'native_course_pitch_m':2.18,'heights':heights,'roofs_and_bearing_bands_moved_together':True,'services_geometry_and_endpoints_unchanged':True})
 # IDs for existing thin far ink, with matching exclusion from near-line sets.
 ink=bpy.data.collections['215 Distant accepted component ink']
 for o in newmesh:
  if o.name not in ink.objects:ink.objects.link(o)
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    for o in newmesh:
     if o.name not in ls.collection.objects:ls.collection.objects.link(o)
 for name,dx in SHIFTS.items():scene.objects[name].location.x+=dx
 bpy.context.view_layer.update()
 gp={}
 if reclip:
  from landmark_contact_visibility_210 import restore_unclipped,apply as clip
  gp['restore']=restore_unclipped(scene,'84e3787b91152c4f17587b201a6808531ae69a1e5a96d71e8eda62c2e5da8358');gp['new_external_visibility']=clip(scene)
  from arcade_sills_225 import solid_tree,clip_lost_contacts
  C=bpy.data.collections['110 Coliseum detailed front ruin'];targets=[o for o in C.objects if o.get('tier')==0 and(o.get('125 inset platform')or o.name.endswith(' sill'))];assert len(targets)==36
  hidden={o:o.hide_render for o in targets}
  try:
   for o in targets:o.hide_render=False
   oldtree,oldvs=solid_tree(targets)
  finally:
   for o,v in hidden.items():o.hide_render=v
  gp['preserved225_lost_sill_contact_cleanup']=clip_lost_contacts(scene,oldtree,oldvs,C)
 after={o.name:{'all':projected(scene,o),'facade':projected(scene,o,True),'matrix':[list(r)for r in o.matrix_world]}for o in roots if o.instance_collection}
 scene['layout226_applied']=True
 return {'iteration':226,'annotation_registration':{'scale':1.5,'offset_native_pixels':[1155,-4.5],'normalized_correlation':.99072679237},'raised_prefabs':raised,'inward_translation_x_m':SHIFTS,'added_objects':added,'new_mesh_ink_IDs':len(newmesh),'before':before,'after':after,'contact_ink':gp,'fixed':['Foreground architecture','Landmark scale and geometry','Haze221','Gate222','Dust223','Soil224','Open thresholds/floors225','217 pixel characters'],'review':'CPU projected comparison only; actual native render pending'}
if __name__=='__main__':
 O=R/'art/studies/far-building-layout-226';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/alley-ground-update-225/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('226 READY',flush=True)
