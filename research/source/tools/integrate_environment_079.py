import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/reviews/xenon-079';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-078/scene.blend'));s=bpy.context.scene
from ground_bank_079 import apply
report=apply(s)
for ma in bpy.data.materials:
 if ma.name not in ['075 soil palette','077 earth fracture interior','077 illuminated earth lips']:continue
 for n in ma.node_tree.nodes:
  if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-15)<.001:
   for link in n.outputs['Fac'].links:
    r=link.to_node
    if r.type=='MAP_RANGE' and abs(r.inputs['To Min'].default_value-.5)<.001 and abs(r.inputs['To Max'].default_value-1.5)<.001:
     n.inputs['Scale'].default_value=22;r.inputs['To Min'].default_value=.7;r.inputs['To Max'].default_value=1.3
# A minority of footprint stones carry the reference's cool mineral undertone.
m=bpy.data.materials.get('077 soil stone 6')
if m:
 for q in m.node_tree.nodes:
  if q.type=='RGB':q.outputs[0].default_value=tuple(((v/255+.055)/1.055)**2.4 for v in (109,104,125))+(1,)
(O/'integration.json').write_text(json.dumps(report,indent=2,default=str));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
