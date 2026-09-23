"""Material-only near scrap palette/spec treatment. apply(scene) is integration entrypoint."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scrap-077'
def apply(scene):
 col=bpy.data.collections.get('075 Scrap integration')
 if col is None:raise RuntimeError('075 Scrap integration missing')
 originals={};meshcopies={};changed=[]
 def graded(mat):
  if mat.name.startswith('077 Near scrap'):return mat
  if mat in originals:return originals[mat]
  new=mat.copy();new.name='077 Near scrap | '+mat.name.split('|')[-1].strip();originals[mat]=new
  if not new.use_nodes:return new
  nt=new.node_tree;n=nt.nodes;l=nt.links
  out=next(x for x in n if x.type=='OUTPUT_MATERIAL' and x.is_active_output)
  if not out.inputs['Surface'].is_linked:return new
  em=out.inputs['Surface'].links[0].from_node
  if em.type!='EMISSION' or not em.inputs['Color'].is_linked:return new
  final=em.inputs['Color'].links[0].from_node
  # Existing native spec is a glossy-light response stylized into a color mix.
  selective=final.type=='MIX_RGB' and final.inputs[0].is_linked and final.inputs[1].is_linked and not final.inputs[2].is_linked
  target=final.inputs[1] if selective else em.inputs['Color'];source=target.links[0].from_socket
  bw=n.new('ShaderNodeRGBToBW');bw.name='077 preserve deep cool shadows';l.new(source,bw.inputs[0])
  strength=n.new('ShaderNodeMapRange');strength.inputs['From Min'].default_value=.012;strength.inputs['From Max'].default_value=.075;strength.inputs['To Min'].default_value=.20;strength.inputs['To Max'].default_value=1;strength.clamp=True;l.new(bw.outputs[0],strength.inputs['Value'])
  warm=n.new('ShaderNodeMixRGB');warm.name='077 measured rust wash';warm.blend_type='MULTIPLY';warm.inputs[0].default_value=1;warm.inputs[2].default_value=(1.70,.94,.43,1);l.new(source,warm.inputs[1])
  mix=n.new('ShaderNodeMixRGB');mix.name='077 rust bodies cool cavities';l.new(strength.outputs[0],mix.inputs[0]);l.new(source,mix.inputs[1]);l.new(warm.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],target)
  if 'rim' not in mat.name.lower():
   cap=n.new('ShaderNodeVectorMath');cap.name='077 reserve bright values for specular strips';cap.operation='MINIMUM';cap.inputs[1].default_value=(.32,.19,.15);l.new(mix.outputs[0],cap.inputs[0]);l.new(cap.outputs[0],target)
  if selective:
   rim='rim' in mat.name.lower()
   final.inputs[2].default_value=(.56,.34,.27,1) if rim else (.48,.245,.19,1)
   factor=final.inputs[0].links[0].from_node
   if factor.type=='MATH' and factor.operation=='MULTIPLY':
    for sock in factor.inputs[:2]:
     if not sock.is_linked and 0<float(sock.default_value)<1:sock.default_value=.82 if rim else .52
  for node in n:
   if node.type=='BSDF_GLOSSY':node.inputs['Roughness'].default_value=.20 if 'rim' in mat.name.lower() else .20;node.inputs['Color'].default_value=(.82,.72,.62,1)
  new['077_palette']='cool dark cavities; rust-brown body; peach/silver physical specular';return new
 for ob in col.all_objects:
  if ob.type!='MESH' or ob.get('zone')!='near':continue
  if ob.data not in meshcopies:
   me=ob.data.copy()
   for i,m in enumerate(me.materials):
    if m:me.materials[i]=graded(m)
   meshcopies[ob.data]=me
  ob.data=meshcopies[ob.data];changed.append(ob.name)
 return {'objects':len(changed),'materials':[m.name for m in originals.values()],'geometry_changed':False,'scope':'near scrap only','reference_body_hex':['#322b35','#423e50','#644439','#8f635c','#a57a6f']}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;report=apply(s)
 (O/'changes.json').write_text(json.dumps(report,indent=2));s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
 s.render.resolution_x=2160;s.render.resolution_y=1620;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=0;s.render.border_max_y=.25;s.render.filepath=str(O/'near.png');bpy.ops.render.render(write_still=True)
