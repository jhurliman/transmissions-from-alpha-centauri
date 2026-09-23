from pathlib import Path
p=Path(__file__).with_name('diagnose.py');exec(compile(p.read_text().split('for i in issues:')[0],str(p),'exec'))
trials=[]
def health(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);d={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'noncontiguous_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True)};bm.free();return d
for name in ['COL110 U15 fractured upper wall R','COL110 U10 fractured upper wall L','COL110 U4 fractured upper wall L']:
 src=bpy.data.objects[name];before=inspect(src,True);hb=health(src)
 for dist in [1e-7,1e-6]:
  ob=src.copy();ob.data=src.data.copy();bpy.context.scene.collection.objects.link(ob);orig={tuple(v.co)for v in ob.data.vertices};bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bm,dist=dist,edges=list(bm.edges));bm.to_mesh(ob.data);bm.free();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();after=inspect(ob,True);ha=health(ob);trials.append({'object':name,'distance_local':dist,'before_health':hb,'after_health':ha,'evaluated_before':before,'evaluated_after':after,'vertices_not_exact_original':sum(tuple(v.co)not in orig for v in ob.data.vertices),'volume_delta':ha['signed_volume']-hb['signed_volume']});bpy.data.objects.remove(ob,do_unlink=True)
for name in ['COL110 U12 fractured upper wall R','COL127 T2 continuous arcade wall']:
 src=bpy.data.objects[name];base=inspect(src,True)
 for mode in ['BEAUTY','EAR_CLIP']:
  ob=src.copy();ob.data=src.data.copy();bpy.context.scene.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method=mode);bm.to_mesh(ob.data);bm.free();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();trials.append({'object':name,'method':'pretri '+mode,'evaluated_before':base,'evaluated_after':inspect(ob,True),'after_health':health(ob)});bpy.data.objects.remove(ob,do_unlink=True)
(O/'degenerate-trials.json').write_text(json.dumps(trials,indent=2));print('DONE',len(trials))
