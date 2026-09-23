"""Sample-only deposits tied to explicit fracture sites in original-world coordinates.

No camera coordinates or image textures. Existing116 palette and fine grain remain.
Regions are supplied by geometry integration, not randomly scattered on intact bays.
"""
import bpy


def exposed_core():
    """Narrow warm masonry family: fracture facets should show form, not gold mosaic."""
    from coliseum_materials_115 import rgba
    m = bpy.data.materials.new('117 Exposed masonry core')
    m.use_nodes = True
    m['role'] = 'fracture'
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    g = n.new('ShaderNodeNewGeometry')
    dot = n.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = (.38, -.67, .64)
    l.new(g.outputs['Normal'], dot.inputs[0])
    diffuse = n.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (.65, .65, .65, 1)
    sr = n.new('ShaderNodeShaderToRGB')
    l.new(diffuse.outputs[0], sr.inputs[0])
    bw = n.new('ShaderNodeRGBToBW')
    l.new(sr.outputs[0], bw.inputs[0])
    a, b, total = [n.new('ShaderNodeMath') for _ in range(3)]
    a.operation = b.operation = 'MULTIPLY'
    a.inputs[1].default_value = .70
    b.inputs[1].default_value = .135
    l.new(dot.outputs['Value'], a.inputs[0])
    l.new(bw.outputs[0], b.inputs[0])
    total.operation = 'ADD'
    l.new(a.outputs[0], total.inputs[0])
    l.new(b.outputs[0], total.inputs[1])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.label = 'Continuous muted fracture stone family'
    ramp.color_ramp.interpolation = 'EASE'
    for i, (position, hexcolor) in enumerate([(0, '66545a'), (.32, '786258'), (.68, '96765f'), (1, 'aa8a6f')]):
        e = ramp.color_ramp.elements[i] if i < 2 else ramp.color_ramp.elements.new(position)
        e.position = position
        c = rgba(hexcolor)
        e.color = tuple(v * .54 for v in c[:3]) + (1,)
    l.new(total.outputs[0], ramp.inputs[0])
    ao = n.new('ShaderNodeAmbientOcclusion')
    ao.inputs['Distance'].default_value = .6
    mix = n.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = .20
    l.new(ramp.outputs[0], mix.inputs[1])
    l.new(ao.outputs['AO'], mix.inputs[2])
    em = n.new('ShaderNodeEmission')
    l.new(mix.outputs[0], em.inputs['Color'])
    out = n.new('ShaderNodeOutputMaterial')
    l.new(em.outputs[0], out.inputs['Surface'])
    return m


def apply(objects, regions, strength=1.0):
    """regions: dictionaries with center and radius in original-world meters."""
    cache = {}
    audit = []
    for ob in objects:
        if ob.type != 'MESH':
            continue
        if not ob.data.attributes.get('115 Original world position'):
            raise ValueError('Missing attached paint coordinates: ' + ob.name)
        for slot in ob.material_slots:
            source = slot.material
            if not source or not source.use_nodes:
                continue
            if source in cache:
                slot.material = cache[source]
                continue
            material = source.copy()
            material.name = '117 Local deposits ' + source.name
            cache[source] = material
            slot.material = material
            nodes, links = material.node_tree.nodes, material.node_tree.links
            emission = next((n for n in nodes if n.type == 'EMISSION'), None)
            if not emission or not emission.inputs['Color'].is_linked:
                continue
            original = emission.inputs['Color'].links[0].from_socket
            attribute = nodes.new('ShaderNodeAttribute')
            attribute.attribute_name = '115 Original world position'
            position = attribute.outputs['Vector']

            def math(operation, a, b=None):
                n = nodes.new('ShaderNodeMath')
                n.operation = operation
                for i, value in enumerate((a, b)):
                    if value is None:
                        continue
                    if isinstance(value, (int, float)):
                        n.inputs[i].default_value = value
                    else:
                        links.new(value, n.inputs[i])
                return n.outputs[0]

            def vector(operation, a, b):
                n = nodes.new('ShaderNodeVectorMath')
                n.operation = operation
                for i, value in enumerate((a, b)):
                    if isinstance(value, (tuple, list)):
                        n.inputs[i].default_value = value
                    else:
                        links.new(value, n.inputs[i])
                return n.outputs[0]

            def noise(v, scale):
                n = nodes.new('ShaderNodeTexNoise')
                n.inputs['Scale'].default_value = scale
                n.inputs['Detail'].default_value = 2.0
                links.new(v, n.inputs['Vector'])
                return n.outputs['Fac']

            def smooth(v, low, high):
                n = nodes.new('ShaderNodeMapRange')
                n.interpolation_type = 'SMOOTHERSTEP'
                n.clamp = True
                n.inputs['From Min'].default_value = low
                n.inputs['From Max'].default_value = high
                links.new(v, n.inputs['Value'])
                return n.outputs[0]

            near, trail = 0.0, 0.0
            for region in regions:
                center = tuple(region['center'])
                radius = region.get('radius', (1.5, 1.5, 2.0))
                radius = (radius, radius, radius) if isinstance(radius, (int, float)) else tuple(radius)
                delta = vector('SUBTRACT', position, center)
                scaled = vector('MULTIPLY', delta, tuple(1 / r for r in radius))
                length = nodes.new('ShaderNodeVectorMath')
                length.operation = 'LENGTH'
                links.new(scaled, length.inputs[0])
                edge = math('ADD', length.outputs['Value'], math('MULTIPLY', math('SUBTRACT', noise(position, 2.8), .5), .32))
                near = math('MAXIMUM', near, math('SUBTRACT', 1, smooth(edge, .35, 1.5)))
                # Each deposit starts at its failure; broad at source, fading downward.
                sep = nodes.new('ShaderNodeSeparateXYZ')
                links.new(delta, sep.inputs[0])
                down = math('MULTIPLY', sep.outputs['Z'], -1)
                height = region.get('runoff_length', radius[2] * 3)
                below = math('MULTIPLY', smooth(down, -.2, .3), math('SUBTRACT', 1, smooth(down, height * .15, height)))
                xy = math('SQRT', math('ADD', math('MULTIPLY', sep.outputs['X'], sep.outputs['X']), math('MULTIPLY', sep.outputs['Y'], sep.outputs['Y'])))
                width = max(radius[0], radius[1]) * .8
                spread = math('SUBTRACT', 1, smooth(xy, width * .2, width))
                stretched = vector('MULTIPLY', position, (1, 1, .18))
                broken = smooth(noise(stretched, 2.4), .38, .66)
                trail = math('MAXIMUM', trail, math('MULTIPLY', below, math('MULTIPLY', spread, broken)))
            # Tone-on-tone pigment retains underlying form light instead of painting black decals.
            mask = math('MULTIPLY', math('MAXIMUM', math('MULTIPLY', near, .34), math('MULTIPLY', trail, .42)), strength)
            mix = nodes.new('ShaderNodeMixRGB')
            mix.label = '117 Damage-connected crust and deposits'
            mix.blend_type = 'MULTIPLY'
            mix.inputs[2].default_value = (.48, .43, .56, 1)
            links.new(mask, mix.inputs[0])
            links.new(original, mix.inputs[1])
            links.new(mix.outputs[0], emission.inputs['Color'])
            audit.append({'material': material.name, 'regions': regions, 'strength': strength, 'coordinates': attribute.attribute_name})
    return audit
