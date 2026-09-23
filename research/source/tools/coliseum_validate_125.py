"""Reuse full nonlandmark snapshot coverage from116 against the integrated119 scene."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
source=(R/'tools/validate_coliseum_116.py').read_text()
exec(source.split('x,xm=snapshot(')[0])
before,bm=snapshot(R/'art/studies/coliseum-123/scene.blend')
after,am=snapshot(R/'art/studies/coliseum-125/scene.blend')
result={'baseline':'123','candidate':'125','nonlandmark_objects_compared':len(before),
        'object_changes':[k for k,v in before.items() if after.get(k)!=v],
        'unexpected_objects':sorted(set(after)-set(before)),
        'material_graphs_compared':len(bm),
        'material_changes':[k for k,v in bm.items() if am.get(k)!=v]}
(R/'art/studies/coliseum-125/preservation.json').write_text(json.dumps(result,indent=2))
result['authorized_object_changes']=[x for x in result['object_changes'] if x=='__world_graph__']
result['unexpected_object_changes']=[x for x in result['object_changes'] if x!='__world_graph__']
(R/'art/studies/coliseum-125/preservation.json').write_text(json.dumps(result,indent=2))
assert not result['unexpected_object_changes'] and not result['unexpected_objects'] and not result['material_changes']
print(json.dumps(result))
# Current appendable native kit, including shared cornice masters and material nodes.
C=bpy.data.collections['110 Coliseum detailed front ruin']
bpy.data.libraries.write(str(R/'art/studies/coliseum-125/kit.blend'),{C},fake_user=True,compress=True)
