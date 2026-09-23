import bpy,sys,json,collections,hashlib
sys.path.insert(0,'/PATH/TO/transmissions-from-alpha-centauri/tools');import bolt_rust_189 as b
bpy.ops.wm.open_mainfile(filepath=str(b.R/'art/studies/coliseum-188/scene.blend'))
s=bpy.context.scene;visible=set()
def walk(c,hidden=False):
 hidden=hidden or c.hide_render
 if not hidden:visible.update(o.name for o in c.objects if not o.hide_render)
 for cc in c.children:walk(cc,hidden)
walk(s.collection)
issues=[];count=0;families=collections.Counter()
for i in bpy.context.evaluated_depsgraph_get().object_instances:
 o=i.object
 if not b.head(o.name):continue
 count+=1;families[o.name.split('.')[0]]+=1
 if o.hide_render:issues.append([o.name,'object hidden'])
 if i.parent:
  par=i.parent
  while par:
   if par.hide_render:issues.append([o.name,'parent hidden',par.name])
   par=par.parent
  if i.parent.name not in visible:issues.append([o.name,'host absent render-visible collection path',i.parent.name])
  if i.parent.instance_collection and i.parent.instance_collection.hide_render:issues.append([o.name,'instance collection hidden',i.parent.instance_collection.name])
 elif o.name not in visible:issues.append([o.name,'standalone absent render-visible path'])
a=json.loads((b.OUT/'audit.json').read_text());res=dict(logical_heads=count,families=dict(families),hidden_issues=issues,passed=not issues,selected_actual=a['applied_bolt_occurrences'],actual_fraction=a['applied_bolt_occurrences']/count,heavy_plate_areas_pass=all(.2<=p['rendered_grid_fraction']<=.8 for p in a['heavy_plates']),all_heavy_bolts_pass=all(p['all_four_bolts_applied']for p in a['heavy_plates']))
(b.OUT/'visibility-check.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
