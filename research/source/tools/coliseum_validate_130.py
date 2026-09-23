"""Verify additive arch ink/tunnels and preserve all existing scene geometry."""
from pathlib import Path
import json

R = Path(__file__).resolve().parents[1]
O = R/'art/studies/coliseum-130'
source = (R/'tools/coliseum_lighting_validate_128.py').read_text().split('\nbefore,bm=snapshot(')[0]
exec(source)
O = R/'art/studies/coliseum-130'

before, bm = snapshot(R/'art/studies/coliseum-129/scene.blend')
bg, bw, bp, bl = cloud_geometry(), protected_world(), selected_pipe_dimensions(), landmark_geometry()
lights = {o.name: digest([o.data.type,o.data.energy,tuple(o.data.color),[tuple(r) for r in o.matrix_world]]) for o in bpy.context.scene.objects if o.type=='LIGHT'}
after, am = snapshot(O/'scene.blend')
ag, aw, ap, al = cloud_geometry(), protected_world(), selected_pipe_dimensions(), landmark_geometry()
lights2 = {o.name: digest([o.data.type,o.data.energy,tuple(o.data.color),[tuple(r) for r in o.matrix_world]]) for o in bpy.context.scene.objects if o.type=='LIGHT'}
added = sorted(set(al)-set(bl))
unexpected_added = [x for x in added if not x.startswith(('130 ', 'COL130 '))]
nt = bpy.context.scene.compositing_node_group
result = {
    'baseline':'129', 'candidate':'130',
    'nonlandmark_objects_compared':len(before),
    'changed_nonlandmark_objects':[k for k,v in before.items() if after.get(k)!=v],
    'added_nonlandmark_objects':sorted(set(after)-set(before)),
    'changed_nonlandmark_materials':[k for k,v in bm.items() if am.get(k)!=v],
    'added_nonlandmark_materials':sorted(set(am)-set(bm)),
    'changed_existing_landmark_geometry':[k for k,v in bl.items() if al.get(k)!=v],
    'added_landmark_objects':added,
    'unexpected_added_landmark_objects':unexpected_added,
    'clouds_unchanged':bg==ag,'world_unchanged':bw==aw,
    'lights_unchanged':lights==lights2,'pipe_unchanged':bp==ap,
    'native_compositor_node_types':sorted(set(n.bl_idname for n in nt.nodes)) if nt else [],
    'compositor_image_assets': [n.name for n in nt.nodes if n.type=='IMAGE'] if nt else [],
    'scope':'Add native arch-rim ink and barrel-vault tunnels; separate native Freestyle view maps. Existing geometry and materials remain fixed.',
}
(O/'preservation.json').write_text(json.dumps(result,indent=2)+'\n')
for key in ['changed_nonlandmark_objects','added_nonlandmark_objects','changed_nonlandmark_materials','added_nonlandmark_materials','changed_existing_landmark_geometry','unexpected_added_landmark_objects','compositor_image_assets']:
    assert not result[key], (key,result[key])
assert all(result[k] for k in ['clouds_unchanged','world_unchanged','lights_unchanged','pipe_unchanged'])
bpy.data.libraries.write(str(O/'kit.blend'),{bpy.data.collections['110 Coliseum detailed front ruin']},fake_user=True)
print('130 preservation passed',len(before),'entries;',len(added),'new landmark objects')
