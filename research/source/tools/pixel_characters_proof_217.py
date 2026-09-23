import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/pixel-characters-217'
from pixel_characters_217 import overlay
with bpy.data.libraries.load(str(R/'art/studies/characters-206/anime/proof.blend'),link=False) as (src,dst):dst.scenes=['206 Anime native light feasibility']
s=dst.scenes[0];s.name='217 Exact selected pixel compositor proof';bpy.context.window.scene=s
for ob in list(s.objects):
 if ob.type=='MESH':bpy.data.objects.remove(ob,do_unlink=True)
for other in list(bpy.data.scenes):
 if other!=s:bpy.data.scenes.remove(other)
s.render.use_freestyle=False;s.render.use_border=False;s.render.use_compositing=True;s.render.resolution_percentage=100
nt=bpy.data.node_groups.new('217 Proof native209cleanplate input','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');out=nt.nodes.new('NodeGroupOutput');bg=nt.nodes.new('CompositorNodeImage');bg.image=bpy.data.images.load(str(R/'art/studies/characters-206/anime/clean-background-4k.png'));bg.image.pack();nt.links.new(bg.outputs['Image'],out.inputs['Image']);s.compositing_node_group=nt
report=overlay(s);s.render.filepath=str(O/'native-composite.png');s.render.image_settings.color_mode='RGBA';bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'))
bpy.ops.wm.open_mainfile(filepath=str(O/'proof.blend'));s=bpy.context.scene
assert s.get('217 selected pixel characters');g=next(n for n in s.compositing_node_group.nodes if n.type=='GROUP');assert g.node_tree.name.startswith('217 Selected')
assert all(n.image.packed_file for n in g.node_tree.nodes if n.type=='IMAGE')
assert all(g.inputs[x].default_value==0 for x in ['Airam X','Airam Y','Miranda X','Miranda Y'])
report['fresh_reload_nodes_images_offsets_pass']=True;report['background']='Reused verified native209cleanplate; no environment render';(O/'proof-audit.json').write_text(json.dumps(report,indent=2))
bpy.ops.render.render(write_still=True);print('217_PROOF_DONE',flush=True)
