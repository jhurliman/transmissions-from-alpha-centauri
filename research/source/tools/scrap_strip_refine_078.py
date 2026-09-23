"""Select native connected rim reflections instead of mottled broad-face highlights."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scrap-strip-078'
def apply(scene):
 collection=bpy.data.collections['075 Scrap integration'];copies={};meshes={};records=[]
 def grade(src):
  if src.name.startswith('078 Connected scrap'):return src
  if src in copies:return copies[src]
  m=src.copy();m.name='078 Connected scrap | '+src.name;copies[src]=m
  if not m.use_nodes:return m
  nt=m.node_tree;n=nt.nodes;l=nt.links;out=next((q for q in n if q.type=='OUTPUT_MATERIAL' and q.is_active_output),None)
  if not out or not out.inputs[0].is_linked:return m
  em=out.inputs[0].links[0].from_node
  if em.type!='EMISSION' or not em.inputs[0].is_linked:return m
  final=em.inputs[0].links[0].from_node
  if final.type!='MIX_RGB' or not final.inputs[0].is_linked:return m
  factor=final.inputs[0].links[0].from_node
  if factor.type!='MATH':return m
  rim='rim' in src.name.lower()
  for sock in factor.inputs:
   if not sock.is_linked and 0<float(sock.default_value)<1:sock.default_value=.72 if rim else .12
  if rim:
   response=next((q for q in n if q.label=='075 restrained metal glints'),None)
   gate=factor.inputs[0].links[0].from_node if factor.inputs[0].is_linked else None
   if response and gate and gate.type=='MATH' and gate.operation=='MULTIPLY':
    # Keep physical light response and normal-facing test. Remove only discontinuous noise islands.
    co=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.label='078 long worn interruptions';noise.inputs['Scale'].default_value=.70;noise.inputs['Detail'].default_value=1.0;l.new(co.outputs['Position'],noise.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.40;ramp.color_ramp.elements[0].color=(.25,.25,.25,1);ramp.color_ramp.elements[1].position=.58;ramp.color_ramp.elements[1].color=(1,1,1,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(response.outputs[0],mul.inputs[0]);l.new(ramp.outputs[0],mul.inputs[1]);l.new(mul.outputs[0],gate.inputs[1])
   final.inputs[2].default_value=(.46,.25,.195,1)
  records.append({'source':src.name,'rim':rim,'spec_strength':.72 if rim else .12,'body_color_changed':False})
  return m
 for ob in collection.all_objects:
  if ob.type!='MESH' or ob.get('zone')!='near':continue
  if ob.data not in meshes:
   me=ob.data.copy()
   for i,m in enumerate(me.materials):
    if m:me.materials[i]=grade(m)
   meshes[ob.data]=me
  ob.data=meshes[ob.data]
 return {'materials':records,'geometry_changed':False,'body_palette_changed':False,'scope':'near scrap only'}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-077/scene.blend'));s=bpy.context.scene;a=apply(s);(O/'changes.json').write_text(json.dumps(a,indent=2));(R/'config/study-scrap-strip-078.json').write_text(json.dumps({'references':['DP-08','UP-01','UP-03'],'property':'Long contiguous native reflected highlight strips on corners, quieter broad metal faces','baseline':'077','fixed':['geometry','body palette','camera','all other systems'],'changed':['near-body spec strength','rim spec noise continuity'],'review_criteria':['connected edge highlights','less broad-face mottling','preserved warm body palette']},indent=2));s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
 s.render.resolution_x=2160;s.render.resolution_y=1620;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=0;s.render.border_max_y=.25;s.render.filepath=str(O/'near.png');bpy.ops.render.render(write_still=True)
