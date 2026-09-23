import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/reviews/xenon-075';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-075/scene.blend'));s=bpy.context.scene
# Keep the approved native shadow response while changing soil colors.
old=bpy.data.materials.get('Weathered street')
if old:
 for ma in bpy.data.materials:
  if not ma.name.startswith(('075 soil palette','075 mineral')):continue
  for n in ma.node_tree.nodes:
   if n.type!='VALTORGB' or not n.inputs[0].is_linked:continue
   source=n.inputs[0].links[0].from_node.type
   label='050 hybrid painted light' if source=='RGBTOBW' else ('050 Local recess shadow' if source=='AMBIENT_OCCLUSION' else '')
   src=next((q for q in old.node_tree.nodes if q.label==label and label),None)
   if src:
    while len(n.color_ramp.elements)>2:n.color_ramp.elements.remove(n.color_ramp.elements[-1])
    n.color_ramp.interpolation=src.color_ramp.interpolation
    for i,e in enumerate(src.color_ramp.elements):
     q=n.color_ramp.elements[i] if i<2 else n.color_ramp.elements.new(e.position);q.position=e.position;q.color=e.color
info=json.loads((R/'art/studies/scrap-075/integration.json').read_text())
for ob in s.objects:
 if any(ob.name.startswith(p) for p in info['hide_old_prefixes']):ob.hide_render=True
with bpy.data.libraries.load(str(R/'art/studies/scrap-075/kit.blend'),link=False) as (a,b):b.collections=[info['collection']]
s.collection.children.link(b.collections[0])
# Distant skyline exports keep all approved alley assemblies separate.
far=json.loads((R/'art/studies/far-075/layout.json').read_text())
for name in far['hide_objects']:
 ob=bpy.data.objects.get(name)
 if ob:ob.hide_render=True
with bpy.data.libraries.load(str(R/'art/studies/far-075/kit.blend'),link=False) as (a,b):b.collections=[far['collection']]
s.collection.children.link(b.collections[0])
from study_sky_075 import apply_sky
apply_sky(s,'B')
from polish_scrap_075 import apply_polish
apply_polish(s)
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
