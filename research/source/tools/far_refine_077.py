"""077 distant-city finish adjustment. apply(scene) leaves geometry/camera/sky untouched."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/far-077'
def rgb(h):
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in [int(h[i:i+2],16)/255 for i in (0,2,4)])+(1,)
def apply(scene):
 cache={};count=0;windows=0
 warm=bpy.data.materials.new('FAR077 muted warm inset');warm.use_nodes=True;nt=warm.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=rgb('a57361');nt.links.new(em.outputs[0],out.inputs[0])
 for ob in list(scene.objects):
  if not ob.name.startswith('FAR075 ') or ob.type not in ['MESH','CURVE']:continue
  layer=int(ob.get('far_layer',5))
  for slot in ob.material_slots:
   src=slot.material
   if not src:continue
   key=(src.name,layer)
   if key not in cache:
    m=src.copy();m.name='FAR077 layer'+str(layer)+' '+src.name;nt=m.node_tree
    if nt:
     for em in [n for n in nt.nodes if n.type=='EMISSION' and n.inputs['Color'].is_linked]:
      orig=em.inputs['Color'].links[0].from_socket
      grey=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(orig,grey.inputs[0]);tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;nt.links.new(grey.outputs[0],tint.inputs[1]);tint.inputs[2].default_value=(.32,.34,.86,1)
      mix=nt.nodes.new('ShaderNodeMixRGB');mix.label='077 quieter violet city pigment';mix.inputs[0].default_value=.85 if layer<3 else .55;nt.links.new(orig,mix.inputs[1]);nt.links.new(tint.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],em.inputs['Color'])
    cache[key]=m
   slot.material=cache[key];count+=1
  # Sparse warm inset color is a painted bounce/opening cue, not a reflection system or glow.
  if layer<3 and 'window' in ob.name:
   k=int(hashlib.sha256(ob.name.encode()).hexdigest()[:8],16)
   if k%13==0:
    ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(warm);windows+=1
 return {'materials':len(cache),'slots':count,'warm_insets':windows,'preserved':['geometry','tall skinny proportions','camera','depth','sky','landmark','alley'],'change':'Quieter violet-blue city pigment and sparse warm insets'}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-075/scene.blend'));s=bpy.context.scene;a=apply(s);(O/'changes.json').write_text(json.dumps(a,indent=2));(R/'config/study-far-077.json').write_text(json.dumps({'references':['DP-08','DP-01','HM-01'],'selected_target':'selected-third','hypothesis':'Measured deeper violet values and reduced cyan coating contrast improve far-city painted continuity.','fixed':['074 alley','075 far proportions and depth','sky','camera','landmark'],'changed':['distant material pigments','sparse warm window insets'],'review_criteria':['matched-crop palette statistics','aerial depth','painted detail hierarchy']},indent=2));s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
