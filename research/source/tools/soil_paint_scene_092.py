import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from foundation_contact_092 import apply
O=R/'art/studies/soil-092';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rocks-091/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
stats=apply(s);(O/'contact-audit.json').write_text(json.dumps(stats,indent=2));g=s.objects['Street foundation'];old=g.data.materials[0]
for label in ['A','B']:
 m=old.copy();m.name='092 painted earth '+label;n=m.node_tree.nodes;l=m.node_tree.links
 geo=n.new('ShaderNodeNewGeometry');add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(8.2,10.5,0);l.new(geo.outputs['Position'],add.inputs[0]);scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(1/16.4,1/45.5,0);l.new(add.outputs[0],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/f'pigment-{label}.png'));tex.image.pack();tex.extension='EXTEND';tex.interpolation='Linear';l.new(scale.outputs[0],tex.inputs['Vector'])
 ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.16;mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.18;l.new(tex.outputs['Color'],mix.inputs[1]);l.new(ao.outputs['AO'],mix.inputs[2])
 # Keep the exact existing footprint mask and pale-bank material branch.
 region=n.get('Mix (Legacy).008');l.new(mix.outputs[0],region.inputs[1]);em=next(q for q in n if q.type=='EMISSION');l.new(region.outputs[0],em.inputs[0]);g.data.materials[0]=m
 s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/f'main-{label}.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/f'scene-{label}.blend'));bpy.ops.render.render(write_still=True)
 s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.16;s.render.border_max_x=.80;s.render.border_min_y=.16;s.render.border_max_y=.45;s.render.filepath=str(O/f'detail-{label}.png');bpy.ops.render.render(write_still=True)
