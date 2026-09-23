"""Separate native landmark and foreground Freestyle view maps. No raster overlay."""
import bpy

def _copy_props(src,dst,skip=()):
 for p in src.bl_rna.properties:
  if p.identifier in {'rna_type','name',*skip} or p.is_readonly or p.type=='COLLECTION':continue
  try:setattr(dst,p.identifier,getattr(src,p.identifier))
  except (TypeError,AttributeError,ValueError):pass

def apply(scene,C):
 name='130 Foreground ink isolated'
 if scene.view_layers.get(name):raise RuntimeError('Ink isolation already exists')
 primary=scene.view_layers[0];members=set(C.all_objects)
 # New layer has independent collection visibility and line selections, shared native styles.
 ink=scene.view_layers.new(name);_copy_props(primary,ink,{'freestyle_settings'})
 _copy_props(primary.freestyle_settings,ink.freestyle_settings)
 for ls in list(ink.freestyle_settings.linesets):ink.freestyle_settings.linesets.remove(ls)
 selected=[]
 for ls in primary.freestyle_settings.linesets:
  is_foreground=ls.collection_negation=='EXCLUSIVE' and ls.select_by_collection and ls.collection and C in ls.collection.children_recursive
  if not is_foreground:continue
  dst=ink.freestyle_settings.linesets.new(ls.name);_copy_props(ls,dst);dst.linestyle=ls.linestyle
  selected.append(ls.name);ls.show_render=False
 if not selected:raise RuntimeError('No legacy foreground line sets found')
 originals={}
 def remember(lc,path=''):
  path+='/'+lc.name;originals[path]=(lc.exclude,lc.hide_viewport,lc.holdout,lc.indirect_only)
  for child in lc.children:remember(child,path)
 remember(primary.layer_collection)
 excluded=[]
 def configure(lc,path=''):
  path+='/'+lc.name
  if path in originals:
   lc.exclude,lc.hide_viewport,lc.holdout,lc.indirect_only=originals[path]
  objs=set(lc.collection.all_objects)
  if lc.collection==C or (objs and objs.issubset(members)):
   lc.exclude=True;excluded.append(lc.collection.name);return
  for child in lc.children:configure(child,path)
 configure(ink.layer_collection)
 # Assert no C mesh survives through a collection alias.
 ink.update()
 survivors=[o.name for o in ink.objects if o in members and o.type=='MESH']
 if survivors:raise RuntimeError('Landmark aliases survive isolated layer: '+str(survivors[:8]))
 primary.use_freestyle=True;primary.freestyle_settings.as_render_pass=False
 ink.use_freestyle=True;ink.freestyle_settings.as_render_pass=True;scene.render.use_freestyle=True
 nt=scene.compositing_node_group
 if nt is not None:raise RuntimeError('Existing compositor requires explicit integration')
 nt=bpy.data.node_groups.new('130 Native isolated foreground ink','CompositorNodeTree');scene.compositing_node_group=nt
 nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
 out=nt.nodes.new('NodeGroupOutput');out.location=(520,0)
 beauty=nt.nodes.new('CompositorNodeRLayers');beauty.layer=primary.name;beauty.label='Beauty and landmark ink';beauty.location=(-420,100)
 lines=nt.nodes.new('CompositorNodeRLayers');lines.layer=ink.name;lines.label='Native foreground ink; landmark excluded from view map';lines.location=(-420,-220)
 over=nt.nodes.new('CompositorNodeAlphaOver');over.location=(240,0);over.inputs['Factor'].default_value=1.
 nt.links.new(beauty.outputs['Image'],over.inputs['Background']);nt.links.new(lines.outputs['Freestyle'],over.inputs['Foreground']);nt.links.new(over.outputs[0],out.inputs['Image'])
 return {'primary_layer':primary.name,'isolated_layer':ink.name,'foreground_line_sets':selected,'excluded_collections':excluded,'surviving_landmark_meshes':len(survivors),'native_render_pass':'Freestyle','image_overlays_used':False,'geometry_and_materials_changed':False,'validation':'Candidate; compare full-frame outputs before adoption'}
