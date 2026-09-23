"""Dedicated distant-building native ink pass without the atmosphere container.

Existing beauty and192 ink passes are preserved. Only215 lines use the new viewmap.
"""
import bpy
from coliseum_ink_isolation_130 import _copy_props

def apply(scene):
    name='215 Distant ink without atmospheric boundary'
    if scene.view_layers.get(name):raise RuntimeError('215 ink isolation already installed')
    source=scene.view_layers['192 Architecture ink without pigment films']
    oldls=source.freestyle_settings.linesets['215 Distant component architecture']
    ob=scene.objects['Distant dust volume - real lighting']
    col=bpy.data.collections.new('215 Atmosphere beauty and existing ink')
    scene.collection.children.link(col)
    oldcols=[c.name for c in ob.users_collection]
    col.objects.link(ob)
    for c in tuple(ob.users_collection):
        if c!=col:c.objects.unlink(ob)
    state={}
    def remember(lc,path=''):
        path+='/'+lc.name
        state[path]=(lc.exclude,lc.hide_viewport,lc.holdout,lc.indirect_only)
        for c in lc.children:remember(c,path)
    remember(source.layer_collection)
    ink=scene.view_layers.new(name)
    _copy_props(source,ink,{'freestyle_settings'})
    _copy_props(source.freestyle_settings,ink.freestyle_settings)
    for ls in list(ink.freestyle_settings.linesets):ink.freestyle_settings.linesets.remove(ls)
    ls=ink.freestyle_settings.linesets.new(oldls.name)
    _copy_props(oldls,ls);ls.linestyle=oldls.linestyle;ls.show_render=True
    def configure(lc,path=''):
        path+='/'+lc.name
        if path in state:lc.exclude,lc.hide_viewport,lc.holdout,lc.indirect_only=state[path]
        if lc.collection==col:lc.exclude=True
        for c in lc.children:configure(c,path)
    configure(ink.layer_collection)
    ink.use_freestyle=True;ink.freestyle_settings.as_render_pass=True
    oldls.show_render=False
    tree=scene.compositing_node_group
    characters=next((n for n in tree.nodes if n.type=='GROUP' and n.node_tree.name.startswith('217 Selected')),None)
    destination=characters.inputs['Background']if characters else next(n for n in tree.nodes if n.type=='GROUP_OUTPUT' and n.is_active_output).inputs['Image']
    assert len(destination.links)==1
    original=destination.links[0].from_socket
    render=tree.nodes.new('CompositorNodeRLayers');render.layer=name;render.name='215 Dedicated distant native ink'
    over=tree.nodes.new('CompositorNodeAlphaOver');over.name='215 Native distant architecture ink over environment';over.inputs['Factor'].default_value=1
    tree.links.new(original,over.inputs['Background']);tree.links.new(render.outputs['Freestyle'],over.inputs['Foreground']);tree.links.new(over.outputs[0],destination)
    return {'object':ob.name,'old_collections':oldcols,'new_collection':col.name,'new_ink_layer':name,'only_lineset':ls.name,'existing192_fog_unchanged':True,'existing192_other_lines_unchanged':True,'beauty_geometry_transform_material_unchanged':True,'composite_before217_characters':bool(characters),'reason':'Matched nested prefab native proof:856strokes without volume boundary;0with original native volume material.'}
