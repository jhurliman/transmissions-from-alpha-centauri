"""105 material-local luminance curve; preserve104 lighting hues and physical glints."""
import bpy,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scrap-105';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scrap-104/scene.blend'));s=bpy.context.scene;cache={}
for ob in bpy.data.collections['075 Scrap integration'].all_objects:
 if ob.type!='MESH' or ob.get('zone')!='near':continue
 ob.data=ob.data.copy()
 for i,src in enumerate(ob.data.materials):
  if not src:continue
  if src not in cache:
   m=src.copy();m.name='105 deeper scrap values | '+src.name;cache[src]=m;n=m.node_tree.nodes;l=m.node_tree.links
   spec=next((q for q in n if q.label=='075 bounded warm-gray reflection'),None)
   out=next(q for q in n if q.type=='OUTPUT_MATERIAL' and q.is_active_output);em=out.inputs[0].links[0].from_node
   target=spec.inputs[1] if spec else em.inputs[0];original=target.links[0].from_socket
   bw=n.new('ShaderNodeRGBToBW');l.new(original,bw.inputs[0]);div=n.new('ShaderNodeMath');div.operation='DIVIDE';div.inputs[1].default_value=.18;l.new(bw.outputs[0],div.inputs[0]);power=n.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=.45;l.new(div.outputs[0],power.inputs[0]);gain=n.new('ShaderNodeMath');gain.operation='MULTIPLY';gain.inputs[1].default_value=.55;l.new(power.outputs[0],gain.inputs[0]);scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.label='105 darker midtones, deeper shade, preserved hue';l.new(original,scale.inputs[0]);l.new(gain.outputs[0],scale.inputs['Scale']);l.new(scale.outputs[0],target)
  ob.data.materials[i]=cache[src]
(O/'changes.json').write_text(json.dumps({'scope':'near scrap values only','curve':'body luminance Y becomes .18 * .55 * (Y/.18)^1.45, uniform RGB gain preserves hue','specular':'existing physical highlight mix retained after body curve','materials':len(cache),'fixed':['blue/rust lighting response','fine weathering','geometry','rest of scene']},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if os.environ.get('SCRAP_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=0;s.render.border_max_y=.23;s.render.filepath=str(O/'preview.png')
bpy.ops.render.render(write_still=True)
