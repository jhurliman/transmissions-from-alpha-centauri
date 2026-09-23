"""Give only the nearest two ruined buildings the adjacent rubble ink weight.
Native visible geometry strokes on the existing atmosphere-free ink layer.
"""
import bpy

PREFIXES = ('133 L0 ', '133 R3 ')

def apply(scene):
    assert not scene.get('241 near ruin ink'), '241 near ruin ink already applied'
    ruins = bpy.data.collections['133 Ruined transition structures']
    targets = [o for o in ruins.objects if o.type == 'MESH' and
               (o.name.startswith(PREFIXES) or str(o.get('235 host', '')).startswith(PREFIXES))]
    assert len(targets) == 20, (len(targets), [o.name for o in targets])
    targetset = set(targets)
    farther = [o for o in ruins.objects if o.type == 'MESH' and o not in targetset]
    # Existing style sources remain unchanged. Remove overlapping target eligibility
    # before adding a private collection so these strokes cannot be drawn twice.
    ownership_changes = []
    for layer in scene.view_layers:
        for lineset in layer.freestyle_settings.linesets:
            if not (lineset.select_by_collection and lineset.collection):
                continue
            c = lineset.collection
            for ob in targets:
                if lineset.collection_negation == 'EXCLUSIVE':
                    if ob.name not in c.objects:
                        c.objects.link(ob)
                        ownership_changes.append([layer.name, lineset.name, ob.name, 'exclude'])
                elif ob.name in c.objects:
                    c.objects.unlink(ob)
                    ownership_changes.append([layer.name, lineset.name, ob.name, 'remove duplicate'])
    c = bpy.data.collections.new('241 Front two ruin ink targets')
    c.use_fake_user = True
    for ob in targets:
        c.objects.link(ob)
    layer = scene.view_layers['215 Distant ink without atmospheric boundary']
    edge_types = ('silhouette', 'border', 'crease', 'ridge_valley', 'suggestive_contour',
                  'material_boundary', 'contour', 'external_contour', 'edge_mark')
    created = []
    for interior in (False, True):
        name = '241 Near ruin interior creases' if interior else '241 Near ruin heavy contours'
        ls = layer.freestyle_settings.linesets.new(name)
        ls.select_by_collection = True
        ls.collection = c
        ls.collection_negation = 'INCLUSIVE'
        ls.select_by_visibility = True
        ls.visibility = 'VISIBLE'
        ls.select_by_edge_types = True
        ls.edge_type_combination = 'AND' if interior else 'OR'
        ls.edge_type_negation = 'INCLUSIVE'
        for key in edge_types:
            if hasattr(ls, 'select_' + key):
                setattr(ls, 'select_' + key, False)
            if hasattr(ls, 'exclude_' + key):
                setattr(ls, 'exclude_' + key, False)
        for key in ('silhouette', 'border', 'external_contour'):
            setattr(ls, 'select_' + key, True)
            if interior:
                setattr(ls, 'exclude_' + key, True)
        if interior:
            ls.select_crease = True
        # Match actual foreground pile geometry styles rather than multiplying all ink.
        source = scene.view_layers['ViewLayer'].freestyle_settings.linesets[
            '050 Fine structural creases' if interior else 'Selective geometry contours']
        ls.linestyle = source.linestyle.copy()
        ls.linestyle.name = name
        created.append({'name': name, 'width_px': ls.linestyle.thickness,
                        'alpha': ls.linestyle.alpha, 'color': list(ls.linestyle.color),
                        'predicate': 'crease AND NOT outer boundary' if interior else 'visible outer boundary'})
    scene['241 near ruin ink'] = True
    return {'targets': [o.name for o in targets], 'assembly_ids': ['L0', 'R3'],
            'farther_unchanged': [o.name for o in farther], 'styles': created,
            'owner': layer.name, 'ownership_changes': ownership_changes,
            'geometry_materials_and_fog_unchanged': True,
            'method': 'Existing atmosphere-free native visible ink; no screen-space masks, fog moves or geometry duplication.',
            'render_guards': '192/205/207 callbacks only apply to their named architectural styles; ruin geometry has no special hidden-corner guard pairs.',
            'status': 'Native eligibility verified; actual combined scene proof required'}
