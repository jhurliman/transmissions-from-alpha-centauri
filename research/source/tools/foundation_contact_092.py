"""Seat foundation fragments on broad base faces; preserve every road stone.
Import apply(scene). Terrain is sampled from actual evaluated Street foundation.
No scene load/save/render happens on import.
"""
import math
from mathutils import Vector, Matrix
import bpy


def apply(scene=None):
    scene = scene or bpy.context.scene
    bpy.context.view_layer.update()
    terrain = scene.objects['Street foundation'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    inverse = terrain.matrix_world.inverted()
    def height(x, y):
        start = inverse @ Vector((x, y, 4))
        direction = (inverse.to_3x3() @ Vector((0, 0, -1))).normalized()
        ok, p, _, _ = terrain.ray_cast(start, direction)
        return (terrain.matrix_world @ p).z if ok else None

    stones = [o for o in scene.objects if o.get('scatter_zone') in ('road', 'bank')]
    banks = [o for o in stones if o.get('scatter_zone') == 'bank']
    # Existing untagged accents must be associated before changing transforms.
    accents = []
    for accent in scene.objects:
        if not accent.name.startswith('091 contact accent') or accent.type != 'MESH':
            continue
        center = sum((accent.matrix_world @ v.co for v in accent.data.vertices), Vector()) / len(accent.data.vertices)
        nearest = min(stones, key=lambda ob: (ob.location.x-center.x)**2 + (ob.location.y-center.y)**2)
        if nearest.get('scatter_zone') == 'bank':
            accents.append((accent, nearest))
    report = {'bank_count': len(banks), 'road_count_unchanged': len(stones)-len(banks), 'rocks': []}
    for ob in banks:
        verts = [v.co.copy() for v in ob.data.vertices]
        min_z = min(v.z for v in verts)
        base = [v for v in verts if v.z < min_z + 1e-5]
        center = sum(base, Vector()) / len(base)
        # Sample footprint edges and interior as well as corners. This averages
        # microgrit while retaining the broad local soil slope under each rock.
        base.sort(key=lambda v: math.atan2(v.y-center.y, v.x-center.x))
        samples = list(base) + [center]
        for a, b in zip(base, base[1:]+base[:1]):
            samples.extend([a.lerp(b, .5), center.lerp(a, .5)])
        yaw = ob.rotation_euler.z
        rotate = Matrix.Rotation(yaw, 3, 'Z')
        xyz = []
        for v in samples:
            p = rotate @ v
            z = height(ob.location.x+p.x, ob.location.y+p.y)
            if z is not None: xyz.append((p.x, p.y, z))
        # Fit z=a*x+b*y+c to actual ground across the broad support face.
        design = Matrix(((sum(x*x for x,y,z in xyz), sum(x*y for x,y,z in xyz), sum(x for x,y,z in xyz)),
                         (sum(x*y for x,y,z in xyz), sum(y*y for x,y,z in xyz), sum(y for x,y,z in xyz)),
                         (sum(x for x,y,z in xyz), sum(y for x,y,z in xyz), len(xyz))))
        rhs = Vector((sum(x*z for x,y,z in xyz),sum(y*z for x,y,z in xyz),sum(z for x,y,z in xyz)))
        a,b,_ = design.inverted_safe() @ rhs
        slope = math.hypot(a,b)
        if slope > .19: a *= .19/slope; b *= .19/slope
        normal = Vector((-a,-b,1)).normalized()
        orientation = Vector((0,0,1)).rotation_difference(normal).to_matrix() @ rotate
        ob.rotation_euler = orientation.to_euler()
        rock_height = max(v.z for v in verts)-min_z
        targets = []
        for v in samples:
            p = orientation @ v
            z = height(ob.location.x+p.x,ob.location.y+p.y)
            if z is not None: targets.append(z-p.z)
        targets.sort()
        # Broad contact, not a single-tip height solve: 75% of the sampled base
        # lies in/under soil. Cap burial so a rock doesn't disappear on rough ground.
        embed = min(.020, rock_height*.08)
        seat = targets[int(.25*(len(targets)-1))] - embed
        seat = max(seat, targets[-1] - rock_height*.34)
        ob.location.z = seat
        gaps = [seat-t for t in targets]
        ob['contact_method_092'] = 'Broad base, fitted terrain slope, multi-point shallow embed'
        ob['contact_fraction_092'] = sum(g <= .001 for g in gaps)/len(gaps)
        ob['contact_max_gap_092'] = max(gaps)
        report['rocks'].append({'name':ob.name,'contact_fraction':ob['contact_fraction_092'],
            'max_base_gap_m':max(gaps),'max_embed_m':-min(gaps),'height_m':rock_height,
            'tilt_degrees':math.degrees(math.atan(min(slope,.19)))})
    for accent, rock in accents:
        # Tight under-rock contact shade. The old oversized disk could itself
        # suggest that a tilted stone was hovering above a displaced shadow.
        for vertex in accent.data.vertices:
            world = accent.matrix_world @ vertex.co
            x = rock.location.x + (world.x-rock.location.x)*.60
            y = rock.location.y + (world.y-rock.location.y)*.60
            z = height(x,y)
            if z is not None: vertex.co = accent.matrix_world.inverted() @ Vector((x,y,z+.001))
        accent['scatter_zone'] = 'bank'
        accent['contact_owner'] = rock.name
        accent.data.update()
    report['bank_accents_tightened'] = len(accents)
    report['max_gap_m'] = max(r['max_base_gap_m'] for r in report['rocks'])
    report['min_contact_fraction'] = min(r['contact_fraction'] for r in report['rocks'])
    bpy.context.view_layer.update()
    return report
