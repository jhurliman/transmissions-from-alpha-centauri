"""Unify passage plaster pigment; preserve geometry and all metal wear."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/entry-surround-229';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-weathering-steps-228/scene.blend'))
cache={};rows=[]
for o in bpy.data.objects:
 if not o.name.startswith('222 passage '):continue
 for slot in o.material_slots:
  old=slot.material
  if not old or old.get('227 role')!='warm receiver':continue
  if old.name not in cache:
   m=old.copy();m.name='229 Continuous warm passage plaster';n=m.node_tree.nodes
   n['Color Ramp.001'].color_ramp.elements[0].color=(.36,.245,.177,1)
   for i in (1,2):n['Mix (Legacy).013'].inputs[i].default_value=n['Mix (Legacy).014'].inputs[i].default_value
   m['229 change']='Warm pigment across former blue/brown mask; all weathering masks and lighting retained.';cache[old.name]=m
  slot.material=cache[old.name];rows.append(o.name)
assert rows
(O/'audit.json').write_text(json.dumps({'objects':rows,'only_change':'Private passage plaster palette; removed blue versus warm split in base and damaged-pigment branches','geometry_unchanged':True,'garage_and_gate_unchanged':True},indent=2))
bpy.context.scene.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
