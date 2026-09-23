"""Native matching-geometry ink pass: pigment films cannot change line endpoints."""
import bpy
from coliseum_ink_isolation_130 import _copy_props

def apply(scene):
    primary = scene.view_layers[0]
    name = '192 Architecture ink without pigment films'
    if scene.view_layers.get(name):
        raise RuntimeError('192 ink isolation already installed')
    films = {c for c in bpy.data.collections if c.name in {'189 Fastener corrosion films', '192 Plate runoff films'}}
    # Accept the author module's actual collection name through its mesh membership.
    film_objects = {o for o in scene.objects if o.name.startswith(('189 Scene-wide fastener rust films', '192 ')) and o.type == 'MESH'}
    for ob in film_objects:
        films.update(c for c in ob.users_collection if c.name.startswith(('189 Fastener', '192 ')))
    if not film_objects:
        raise RuntimeError('No corrosion films found')
    ink = scene.view_layers.new(name)
    _copy_props(primary, ink, {'freestyle_settings'})
    _copy_props(primary.freestyle_settings, ink.freestyle_settings)
    for ls in list(ink.freestyle_settings.linesets):
        ink.freestyle_settings.linesets.remove(ls)
    for ls in primary.freestyle_settings.linesets:
        dst = ink.freestyle_settings.linesets.new(ls.name)
        _copy_props(ls, dst)
        dst.linestyle = ls.linestyle
    originals = {}
    def record(lc, path=''):
        path += '/' + lc.name
        originals[path] = (lc.exclude, lc.hide_viewport, lc.holdout, lc.indirect_only)
        for child in lc.children: record(child, path)
    record(primary.layer_collection)
    excluded = []
    def configure(lc, path=''):
        path += '/' + lc.name
        if path in originals:
            lc.exclude, lc.hide_viewport, lc.holdout, lc.indirect_only = originals[path]
        if lc.collection in films:
            lc.exclude = True
            excluded.append(lc.name)
            return
        for child in lc.children: configure(child, path)
    configure(ink.layer_collection)
    ink.update()
    assert not (set(ink.objects) & film_objects), 'Pigment alias survives in ink layer'
    primary.use_freestyle = False
    ink.use_freestyle = True
    ink.freestyle_settings.as_render_pass = True
    scene.render.use_freestyle = True
    if scene.compositing_node_group:
        raise RuntimeError('Unexpected existing compositor')
    nt = bpy.data.node_groups.new('192 Native beauty plus unbroken architecture ink', 'CompositorNodeTree')
    scene.compositing_node_group = nt
    nt.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    out = nt.nodes.new('NodeGroupOutput')
    beauty = nt.nodes.new('CompositorNodeRLayers'); beauty.layer = primary.name
    lines = nt.nodes.new('CompositorNodeRLayers'); lines.layer = ink.name
    over = nt.nodes.new('CompositorNodeAlphaOver'); over.inputs['Factor'].default_value = 1
    nt.links.new(beauty.outputs['Image'], over.inputs['Background'])
    nt.links.new(lines.outputs['Freestyle'], over.inputs['Foreground'])
    nt.links.new(over.outputs[0], out.inputs['Image'])
    scene.render.use_compositing = True
    return {'excluded_pigment_collections': excluded, 'ink_layer': name, 'line_sets': [ls.name for ls in ink.freestyle_settings.linesets], 'source_geometry_and_materials_changed': False, 'raster_overlay': False, 'status': 'candidate pending native proof'}
