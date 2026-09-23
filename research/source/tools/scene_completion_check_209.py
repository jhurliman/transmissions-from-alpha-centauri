"""Fresh saved-state completion checks; visual criteria are separately reviewed."""
import bpy,sys,json,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-completion-209';sys.path.insert(0,str(R/'tools'));bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
source=(R/'tools/scene_integration_138.py').read_text();exec(source[source.index('def objects('):source.index("if 'render' not in sys.argv:")]);saved=fingerprint(s);expected=json.loads((O/'candidate-fingerprint.json').read_text());mats=material_snapshot();old=json.loads((O/'source-materials.json').read_text())
errors=[]
for k,v in expected.items():
 if saved.get(k)!=v:errors.append({'object':k,'problem':'Saved scene differs from build fingerprint','fields':[f for f in v if saved.get(k,{}).get(f)!=v[f]]})
for k,v in old.items():
 if mats.get(k)!=v:errors.append({'material':k,'problem':'Original graph missing or changed'})
assert s.render.resolution_x==3840 and s.render.resolution_y==2885 and s.render.resolution_percentage==100
assert s.render.use_compositing
ink=s.view_layers.get('192 Architecture ink without pigment films');assert ink and ink.use
excluded={}
def walk(lc):
 if lc.collection.name in ['189 Fastener oxide films','192 Plate rusty water','195 Plate rusty water']:excluded[lc.collection.name]=lc.exclude
 for ch in lc.children:walk(ch)
walk(ink.layer_collection)
assert excluded.get('195 Plate rusty water') is True
clouds=[o for o in bpy.data.collections['082 Derived flat clouds'].all_objects if o.type=='MESH'];assert all(any(sl.material and sl.material.get('199 native cloud refinement')for sl in o.material_slots)for o in clouds)
assert s.objects['Distant dust volume - real lighting'].active_material.name.startswith('202 ')
col=bpy.data.collections['110 Coliseum detailed front ruin'];crumbling=[o.name for o in col.all_objects if o.get('190 local face method')];assert crumbling
beam=bpy.data.objects['Y arm front flange.010'];assert beam.material_slots[0].material.name.startswith('201 ')
right=[]
for ob in s.objects['Architecture | gangway_single_Y_8m.001'].instance_collection.all_objects:
 if not ob.name.startswith(('Y arm','Y stem')):continue
 for sl in ob.material_slots:
  m=sl.material;hits=[n for n in m.node_tree.nodes if n.type=='MATH'and n.operation=='MULTIPLY'and any('193' in x for x in [n.name,n.label])]
  right.append({'object':ob.name,'nodes':[{'name':n.name,'label':n.label,'unlinked_values':[i.default_value for i in n.inputs if not i.is_linked]}for n in hits]})
result={'saved_scene_sha256':hashlib.sha256((O/'scene.blend').read_bytes()).hexdigest(),'errors':errors,'status':'PASS'if not errors else 'FAIL','saved_entries':len(saved),'old_materials_verified':len(old),'render_size':[3840,2885],'native_current_scene_ink':True,'ink_film_exclusions':excluded,'crumbling_meshes':crumbling,'cloud_meshes':len(clouds),'left_beam_connector':beam.material_slots[0].material.name,'right_half_strength_nodes':right,'scope':'Structural saved-state audit only; use root/independent actual-render comparison for all visual completion claims.'}
(O/'fresh-check.json').write_text(json.dumps(result,indent=2));print(result['status'],len(errors));assert not errors,errors
