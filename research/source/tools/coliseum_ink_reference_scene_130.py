"""Native locked-environment Freestyle source; candidate preservation study."""
import bpy
from pathlib import Path

def apply(scene,C):
 if scene.compositing_node_group:raise RuntimeError('Compositor already exists')
 source=Path(__file__).resolve().parents[1]/'art/studies/coliseum-128/scene.blend'
 with bpy.data.libraries.load(str(source),link=True) as (src,dst):
  dst.scenes=[src.scenes[0]]
 locked=dst.scenes[0]
 # A local scene copy retains its linked native geometry and original object names.
 locked=locked.copy();locked.name='130 Locked environment ink source'
 locked.render.resolution_x=scene.render.resolution_x;locked.render.resolution_y=scene.render.resolution_y;locked.render.resolution_percentage=100;locked.render.line_thickness=scene.render.line_thickness;locked.render.use_border=False;locked.render.use_crop_to_border=False;locked.compositing_node_group=None
 foreground=[]
 for ls in scene.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection_negation=='EXCLUSIVE':foreground.append(ls.name);ls.show_render=False
 fs=locked.view_layers[0].freestyle_settings;fs.as_render_pass=True
 for ls in fs.linesets:ls.show_render=ls.name in foreground
 locked.render.use_freestyle=True;locked.view_layers[0].use_freestyle=True
 scene.render.use_freestyle=True;scene.view_layers[0].freestyle_settings.as_render_pass=False
 nt=bpy.data.node_groups.new('130 Locked native foreground ink composition','CompositorNodeTree');scene.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
 beauty=nt.nodes.new('CompositorNodeRLayers');beauty.scene=scene;beauty.layer=scene.view_layers[0].name;beauty.location=(-400,100)
 ink=nt.nodes.new('CompositorNodeRLayers');ink.scene=locked;ink.layer=locked.view_layers[0].name;ink.location=(-400,-180)
 over=nt.nodes.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1.;over.location=(100,0)
 out=nt.nodes.new('NodeGroupOutput');out.location=(380,0)
 nt.links.new(beauty.outputs['Image'],over.inputs['Background']);nt.links.new(ink.outputs['Freestyle'],over.inputs['Foreground']);nt.links.new(over.outputs['Image'],out.inputs['Image'])
 return {'secondary_scene':locked.name,'source':str(source),'source_geometry_linked':True,'foreground_sets':foreground,'landmark_retained_in_secondary_viewmap':True,'external_raster_assets':False,'status':'unvalidated candidate'}

def sync(scene):
 """Call after changing primary output dimensions, before rendering."""
 nt=scene.compositing_node_group
 if not nt:return []
 updated=[]
 for n in nt.nodes:
  if n.bl_idname!='CompositorNodeRLayers' or not n.scene or n.scene==scene:continue
  target=n.scene
  if not target.name.startswith('130 Locked environment ink source'):continue
  for name in ('resolution_x','resolution_y','resolution_percentage','line_thickness','use_border','use_crop_to_border','border_min_x','border_min_y','border_max_x','border_max_y'):
   setattr(target.render,name,getattr(scene.render,name))
  updated.append(target.name)
 return updated
