"""Dense version of the retained051 scuff/scratch pass on208 recess floors only."""
import bpy


def dense_group():
    source = next(g for g in bpy.data.node_groups if g.name.startswith('051 Facade | clustered chips and short scars'))
    group = source.copy()
    group.name = '213 Recess floor | dense retained scuffs and scratches'
    changes = []
    for node in group.nodes:
        if node.type != 'MATH' or node.operation != 'GREATER_THAN' or not node.inputs[0].is_linked:
            continue
        noise = node.inputs[0].links[0].from_node
        if noise.type != 'TEX_NOISE':
            continue
        scale = round(noise.inputs['Scale'].default_value, 3)
        prior = node.inputs[1].default_value
        if abs(scale - 1.1) < .01:
            node.inputs[1].default_value = .28
            role = 'Broad active coverage across exposed floor'
        elif abs(scale - 3.5) < .01:
            noise.inputs['Scale'].default_value = 13
            node.inputs[1].default_value = .64
            role = 'Broken small scuffs instead of broad dark scars'
        elif abs(scale - 23) < .01:
            noise.inputs['Scale'].default_value = 40
            node.inputs[1].default_value = .62
            if noise.inputs['Vector'].is_linked:
                stretch = noise.inputs['Vector'].links[0].from_node
                if stretch.type == 'VECT_MATH' and stretch.operation == 'MULTIPLY':
                    stretch.inputs[1].default_value = (1, 1, .28)
            role = 'Dense short thin scratches'
        elif abs(scale - 24) < .01:
            mapped = noise.inputs['Vector'].is_linked and noise.inputs['Vector'].links[0].from_node.type == 'VECT_MATH'
            noise.inputs['Scale'].default_value = 42 if mapped else 47
            node.inputs[1].default_value = .61 if mapped else .575
            role = 'Offset pale chips' if mapped else 'Dense dark pinholes and nicks'
        else:
            continue
        node.label = '213 ' + role
        changes.append({'role': role, 'old_threshold': prior, 'new_threshold': node.inputs[1].default_value, 'scale': noise.inputs['Scale'].default_value})
    required = {'Broad active coverage across exposed floor', 'Dense dark pinholes and nicks', 'Dense short thin scratches', 'Offset pale chips'}
    # The retained source has already revised the old broad-scar branch.
    # Keep that accepted branch intact; require all four surviving detail controls.
    assert required.issubset({c['role'] for c in changes}), changes
    group['213 source pass'] = source.name
    return group, changes


def apply(scene):
    assert not any(m.get('213 floor scuffs') for m in bpy.data.materials), 'Apply213 once to fresh209'
    group, changes = dense_group()
    targets = [o for o in bpy.data.objects if o.get('198 native damage') == 'recess']
    assert len(targets) == 14, len(targets)
    materials, rows = {}, []
    for obj in targets:
        slots = []
        for index, slot in enumerate(obj.material_slots):
            base = slot.material
            if not base or not base.name.startswith('208 Light exposed aggregate'):
                continue
            if base.name not in materials:
                mat = base.copy()
                mat.name = '213 Dense floor scuffs | ' + base.name
                mat['213 floor scuffs'] = True
                nodes, links = mat.node_tree.nodes, mat.node_tree.links
                output = next(n for n in nodes if n.type == 'EMISSION')
                original = output.inputs['Color'].links[0].from_socket
                detail = nodes.new('ShaderNodeGroup')
                detail.node_tree = group
                detail.label = '213 Dense existing alley scuff and scratch pass'
                links.new(original, detail.inputs['Base'])
                geometry = nodes.new('ShaderNodeNewGeometry')
                normal = nodes.new('ShaderNodeVectorTransform')
                normal.vector_type = 'NORMAL'
                normal.convert_from, normal.convert_to = 'WORLD', 'OBJECT'
                links.new(geometry.outputs['Normal'], normal.inputs[0])
                dot = nodes.new('ShaderNodeVectorMath')
                dot.operation = 'DOT_PRODUCT'
                dot.inputs[1].default_value = (0, -1, 0)
                links.new(normal.outputs[0], dot.inputs[0])
                floor = nodes.new('ShaderNodeMath')
                floor.operation = 'GREATER_THAN'
                floor.inputs[1].default_value = .97
                floor.label = '213 Only exposed recess floor; retain sidewall lips'
                links.new(dot.outputs['Value'], floor.inputs[0])
                mix = nodes.new('ShaderNodeMixRGB')
                mix.blend_type = 'MIX'
                links.new(floor.outputs[0], mix.inputs[0])
                links.new(original, mix.inputs[1])
                links.new(detail.outputs['Color'], mix.inputs[2])
                links.new(mix.outputs[0], output.inputs['Color'])
                materials[base.name] = mat
            slot.link = 'OBJECT'
            slot.material = materials[base.name]
            slots.append(index)
        assert slots, obj.name
        floors = [p for p in obj.data.polygons if p.material_index in slots and p.normal.y < -.97]
        rows.append({'object': obj.name, 'slots': slots, 'floor_polygons': len(floors), 'local_floor_area_m2': sum(p.area for p in floors)})
    return {'study': 213, 'source': '209', 'targets': rows, 'materials': {k:v.name for k,v in materials.items()}, 'pass': group.name, 'parameter_changes': changes, 'geometry_camera_lights_unchanged': True, 'original_materials_and_051_group_unchanged': True, 'scope': 'Dense retained scuffs, nicks, short scratches and pale chips on fourteen exposed recess floors.208lighter base and sidewalls retained.', 'status': 'Native visual proof pending in212'}
