import bpy,sys,json
sys.path.insert(0,'/PATH/TO/transmissions-from-alpha-centauri/tools');import bolt_rust_189 as b
bpy.ops.wm.open_mainfile(filepath=str(b.OUT/'candidate.blend'));films=set(bpy.data.collections['189 Fastener corrosion films'].all_objects);old=set(bpy.data.collections['110 Existing ink exclusions'].all_objects);rows=[]
for vl in bpy.context.scene.view_layers:
 for ls in vl.freestyle_settings.linesets:
  objs=set(ls.collection.all_objects) if ls.collection else set();excluded=not bool(films&objs)if ls.collection_negation=='INCLUSIVE'else films<=objs
  rows.append(dict(line_set=ls.name,mode=ls.collection_negation,select_by_collection=ls.select_by_collection,films_excluded=excluded,filter_name=ls.collection.name,old_exclusions_preserved=old<=objs if ls.collection_negation=='EXCLUSIVE'else None,filter_count=len(objs)))
assert all(r['films_excluded']and r['select_by_collection']for r in rows)
a=dict(fresh_reopened=True,passed=True,filters=rows);(b.OUT/'fresh-ink-filter-check.json').write_text(json.dumps(a,indent=2));print(json.dumps(a,indent=2))
