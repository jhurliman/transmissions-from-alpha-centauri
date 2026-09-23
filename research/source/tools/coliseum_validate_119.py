"""Reuse full nonlandmark snapshot coverage from116 against the integrated119 scene."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
source=(R/'tools/validate_coliseum_116.py').read_text()
exec(source.split('x,xm=snapshot(')[0])
before,bm=snapshot(R/'art/studies/coliseum-116/scene.blend')
after,am=snapshot(R/'art/studies/coliseum-119/scene.blend')
result={'baseline':'116','candidate':'119','nonlandmark_objects_compared':len(before),
        'object_changes':[k for k,v in before.items() if after.get(k)!=v],
        'unexpected_objects':sorted(set(after)-set(before)),
        'material_graphs_compared':len(bm),
        'material_changes':[k for k,v in bm.items() if am.get(k)!=v]}
(R/'art/studies/coliseum-119/preservation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
