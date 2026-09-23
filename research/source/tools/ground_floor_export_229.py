"""Export the two reusable native ground-floor masters without the full scene."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/components/facades/v229';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/entry-surround-229/scene.blend'))
masters=[bpy.data.collections[n]for n in ['222 Clean master garage','222 Clean master passage']]
clean=[m for m in bpy.data.materials if m.name.startswith('222 Clean ')]
bpy.data.libraries.write(str(O/'ground-floor-kit.blend'),set(masters+clean),fake_user=True,compress=True)
a=json.loads((R/'art/studies/ground-floor-kit-222/audit.json').read_text())
rows=[]
for r in a['placements']:
 r=dict(r);r.pop('root');r.pop('origin');r['local_origin']='Center of exterior opening at threshold height';r['axes']={'inward':'+X','frontage_width':'+Y','up':'+Z'};r['placement_rules']=['Cut host facade to clear opening; do not overlay intact wall','Preserve or supply structural lintel above clear opening','Check services, braces and approach clearance','Register new component edges in existing architecture ink pass','Clip old facade contact ink against removed skin and new receivers']
 if r['kind']=='passage':r['setback_note']='1.8 m along the angled passage, not perpendicular facade depth; native angled geometry is fixed and editable.'
 rows.append(r)
(O/'interfaces.json').write_text(json.dumps({'library':'ground-floor-kit.blend','components':rows,'clean_material_sources':[m.name for m in clean],'weathering':'Default overrides retain227 garage and gate weathering;229 passage plaster uses a continuous warm palette. Original222 clean material sources are included as historical unweathered alternatives.','native_units':'metres','review':'Integrated scene proof in study229; no separate fidelity score or user approval.'},indent=2)+'\n')
print('227 WEATHERED LIBRARY EXPORTED',flush=True)
