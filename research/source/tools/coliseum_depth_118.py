"""Recover architectural recess depth in the attached painted material."""
import bpy

def cavity_shade(objects):
    """Shade only modeled recess faces; absent attribute leaves intact masonry untouched."""
    cache = {}
    for ob in objects:
        if ob.type != 'MESH':
            continue
        for slot in ob.material_slots:
            src = slot.material
            if not src or not src.use_nodes:
                continue
            if src in cache:
                slot.material = cache[src]
                continue
            m = src.copy()
            m.name = '118 Recess shade ' + src.name
            cache[src] = m
            slot.material = m
            n, l = m.node_tree.nodes, m.node_tree.links
            em = next((q for q in n if q.type == 'EMISSION'), None)
            if not em or not em.inputs['Color'].is_linked:
                continue
            old = em.inputs['Color'].links[0].from_socket
            attr = n.new('ShaderNodeAttribute')
            attr.attribute_name = '118 Recess interior'
            factor = n.new('ShaderNodeMath')
            factor.operation = 'MULTIPLY'
            factor.inputs[1].default_value = .65
            l.new(attr.outputs['Fac'], factor.inputs[0])
            mix = n.new('ShaderNodeMixRGB')
            mix.label = '118 Modeled recess deposit shade'
            mix.blend_type = 'MULTIPLY'
            mix.inputs[2].default_value = (.42, .38, .48, 1)
            l.new(factor.outputs[0], mix.inputs[0])
            l.new(old, mix.inputs[1])
            l.new(mix.outputs[0], em.inputs['Color'])
    return {'materials': len(cache), 'attribute': '118 Recess interior', 'strength': .65,
            'broad_lighting_unchanged': True}

def refine(objects):
    cache = {}
    records = []
    for ob in objects:
        if ob.type != 'MESH':
            continue
        for slot in ob.material_slots:
            src = slot.material
            if not src or not src.use_nodes:
                continue
            if src in cache:
                slot.material = cache[src]
                continue
            m = src.copy()
            m.name = '118 Architectural shade ' + src.name
            cache[src] = m
            slot.material = m
            nodes = m.node_tree.nodes
            palette = next((n for n in nodes if n.label == 'Warm exposed stone, violet recesses'), None)
            if palette:
                light = palette.inputs[0].links[0].from_node
                for inp in light.inputs:
                    if not inp.is_linked:
                        continue
                    mul = inp.links[0].from_node
                    if mul.type != 'MATH' or mul.operation != 'MULTIPLY':
                        continue
                    for factor in mul.inputs:
                        if factor.is_linked:
                            continue
                        if abs(factor.default_value - .82) < .0001:
                            factor.default_value = .60
                        elif abs(factor.default_value - .18) < .0001:
                            factor.default_value = .40
            for node in nodes:
                if node.type == 'AMBIENT_OCCLUSION':
                    node.inputs['Distance'].default_value = 1.4
            records.append({'material': m.name, 'orientation_weight': .60 if palette else None,
                            'actual_light_weight': .40 if palette else None, 'crevice_distance': 1.4})
    return records
