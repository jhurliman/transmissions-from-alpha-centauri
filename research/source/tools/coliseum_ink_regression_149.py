"""Native diagnosis and geometry-based correction of149's hidden-edge leak.

Diagnostic helpers are read-only or modify temporary ink selection. The apply()
entry point registers a narrowly scoped stroke-depth guard, optionally embedded
in the saved scene. It preserves geometry, materials and line widths while
hiding only sampled flange/joist segments occluded by the actual fascia.
"""
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import bpy

SUSPECTS = ('Y arm back flange.010', 'Deck cross joist web.038')
FRAME = (3840, 2885)
REGION = (230, 830, 290, 880)


def diagnose(scene):
    dg = bpy.context.evaluated_depsgraph_get()
    camera = scene.camera
    origin = camera.matrix_world.translation
    frame = camera.data.view_frame(scene=scene)
    rays = []
    for y in (849, 851, 854, 857, 860):
        for x in (248, 251, 255, 260, 266, 271):
            top = frame[3].lerp(frame[0], x / FRAME[0])
            bottom = frame[2].lerp(frame[1], x / FRAME[0])
            direction = (camera.matrix_world @ top.lerp(bottom, y / FRAME[1]) - origin).normalized()
            hit = scene.ray_cast(dg, origin, direction)
            rays.append({'pixel': [x, y], 'object': hit[4].name if hit[0] else None,
                         'face': hit[3] if hit[0] else None,
                         'world_point': list(hit[1]) if hit[0] else None})
    edges = []
    for instance in dg.object_instances:
        ob = instance.object
        if ob.type != 'MESH' or ob.name not in SUSPECTS:
            continue
        mesh = ob.to_mesh()
        points = [instance.matrix_world @ vertex.co for vertex in mesh.vertices]
        projected = [world_to_camera_view(scene, camera, point) for point in points]
        for edge in mesh.edges:
            a, b = [projected[i] for i in edge.vertices]
            p, q = (a.x * FRAME[0], (1-a.y)*FRAME[1]), (b.x*FRAME[0], (1-b.y)*FRAME[1])
            if min(p[0], q[0]) > 270 or max(p[0], q[0]) < 245 or min(p[1], q[1]) > 861 or max(p[1], q[1]) < 845:
                continue
            if max(abs(p[0]-q[0]), abs(p[1]-q[1])) > 100:
                continue
            mid = (points[edge.vertices[0]] + points[edge.vertices[1]]) / 2
            direction = mid - origin
            hit = scene.ray_cast(dg, origin, direction.normalized())
            edges.append({'object': ob.name, 'edge': edge.index, 'screen': [p, q],
                          'first_hit': hit[4].name if hit[0] else None,
                          'occlusion_gap_m': direction.length-(hit[1]-origin).length if hit[0] else None})
        ob.to_mesh_clear()
    return {'rays': rays, 'candidate_edges': edges,
            'geometry_mutated': False, 'materials_mutated': False,
            'fix_applied': False}


def select_suspect_ink_for_temporary_proof(scene):
    # Unlinked collection avoids adding another instance of the source geometry.
    collection = bpy.data.collections.new('149 Diagnostic suspect structural edges')
    for name in SUSPECTS:
        collection.objects.link(bpy.data.objects[name])
    for lineset in scene.view_layers[0].freestyle_settings.linesets:
        lineset.show_render = lineset.name in ('Selective geometry contours', '050 Fine structural creases')
        if lineset.show_render:
            lineset.collection = collection
            lineset.select_by_collection = True
            lineset.collection_negation = 'INCLUSIVE'
    return collection


def install_native_visibility_guard(scene, audit_path=None):
    """Install runtime-only geometric guard; call after loading before rendering.

    It touches only sampled segments from the two named structural members
    which are actually occluded by the evaluated Folded fascia.005 instance.
    No geometry, materials, line thickness or visible-edge selection changes.
    """
    import json
    from mathutils.bvhtree import BVHTree
    from freestyle.types import StrokeShader
    import parameter_editor
    dg = bpy.context.evaluated_depsgraph_get()
    verts, triangles = [], []
    for instance in dg.object_instances:
        if instance.object.name != 'Folded fascia.005':
            continue
        mesh = instance.object.to_mesh()
        mesh.calc_loop_triangles()
        start = len(verts)
        verts.extend(instance.matrix_world @ v.co for v in mesh.vertices)
        triangles.extend(tuple(start+i for i in tri.vertices) for tri in mesh.loop_triangles)
        instance.object.to_mesh_clear()
    bvh = BVHTree.FromPolygons(verts, triangles, all_triangles=True)
    cam_matrix = scene.camera.matrix_world.copy()
    origin = cam_matrix.translation.copy()
    audit = {'sampled_segments': 0, 'hidden_segments': 0, 'names': {}, 'examples': [], 'triangles': len(triangles)}

    def flush():
        if audit_path:
            from pathlib import Path
            Path(audit_path).write_text(json.dumps(audit, indent=2))

    class FasciaVisibilityShader(StrokeShader):
        def shade(self, stroke):
            points = list(stroke)
            for index, vertex in enumerate(points[:-1]):
                fe = vertex.fedge
                if fe is None or fe.viewedge is None or fe.viewedge.viewshape is None:
                    continue
                name = fe.viewedge.viewshape.name
                if name not in SUSPECTS:
                    continue
                audit['names'][name] = audit['names'].get(name, 0) + 1
                next_vertex = points[index+1]
                # Freestyle point_3d is camera-space, as its shading functions
                # use -point_3d as the vector toward the camera.
                world_a = cam_matrix @ vertex.point_3d
                world_b = cam_matrix @ next_vertex.point_3d
                samples = (world_a, (world_a+world_b)/2, world_b)
                gaps = []
                for point in samples:
                    delta = point-origin
                    hit = bvh.ray_cast(origin, delta.normalized(), delta.length)
                    gaps.append(delta.length-hit[3] if hit[0] is not None else -1.0)
                audit['sampled_segments'] += 1
                hidden = min(gaps) > .02
                if hidden:
                    vertex.attribute.visible = False
                    audit['hidden_segments'] += 1
                if len(audit['examples']) < 30:
                    audit['examples'].append({'shape':name,'camera_point':list(vertex.point_3d),'screen':list(vertex.point),'gaps_m':gaps,'hidden':hidden})
            flush()

    def callback(current_scene, layer, lineset):
        if lineset.name in ('Selective geometry contours', '050 Fine structural creases'):
            return [FasciaVisibilityShader()]
        return []
    callback._guard_149 = True
    callback._guard_149_audit = audit
    parameter_editor.callbacks_modifiers_post[:] = [f for f in parameter_editor.callbacks_modifiers_post if not getattr(f, '_guard_149', False)]
    parameter_editor.callbacks_modifiers_post.append(callback)
    flush()
    return audit


def register_native_guard_handler():
    """Register rebuild-before-render so camera/instances remain current."""
    from bpy.app.handlers import persistent
    @persistent
    def render_pre(scene, *args):
        install_native_visibility_guard(scene)
    render_pre._guard_149 = True
    bpy.app.handlers.render_pre[:] = [fn for fn in bpy.app.handlers.render_pre if not getattr(fn, '_guard_149', False)]
    bpy.app.handlers.render_pre.append(render_pre)


def apply(scene, embed=True):
    """Register guard and optionally embed self-contained reload bootstrap.

    Reopened scenes require Blender trusted Python auto-execution, or explicit
    execution of text '149 Native fascia visibility guard.py' before rendering.
    CLI equivalent: --enable-autoexec. No source files are needed after save.
    """
    register_native_guard_handler()
    if embed:
        from pathlib import Path
        name = '149 Native fascia visibility guard.py'
        text = bpy.data.texts.get(name) or bpy.data.texts.new(name)
        text.clear()
        text.write(Path(__file__).read_text() + '\n\nregister_native_guard_handler()\n')
        text.use_module = True
    return {'geometry_changed':False, 'materials_changed':False,
            'widths_changed':False, 'occluder':'Folded fascia.005',
            'target_shapes':list(SUSPECTS), 'embedded':embed,
            'standalone_reload_requires_trusted_python_autoexec':True}
