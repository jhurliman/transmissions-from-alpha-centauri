"""Native Blender 5.2 intersection-only Grease Pencil Line Art.

Source collection should contain the participating visible solids and terrain.
Keep GP outside it. Other scene geometry retains normal occlusion behavior.
Radius is world-space, so tune at the delivery camera (probe uses .02 at
orthographic scale 7 / 900 px; approximately 2-3 px visible line).
Uses visible level 0 only; no x-ray/hidden-line drawing or shader contact hack.
Actual crossing required: coplanar or merely tangent faces are not intersections.
"""
import bpy

def add_intersection_ink(collection, name='Intersection ink', radius=.02):
 g=bpy.data.grease_pencils.new(name);g.stroke_depth_order='3D';o=bpy.data.objects.new(name,g);bpy.context.scene.collection.objects.link(o)
 layer=g.layers.new('Intersection strokes',set_active=True);layer.use_lights=False
 mat=bpy.data.materials.new(name);bpy.data.materials.create_gpencil_data(mat);mat.grease_pencil.color=(.018,.012,.022,1);mat.grease_pencil.show_fill=False;g.materials.append(mat)
 m=o.modifiers.new(name,'LINEART');m.source_type='COLLECTION';m.source_collection=collection;m.target_layer='Intersection strokes';m.target_material=mat
 for attr in ['use_contour','use_loose','use_crease','use_material','use_edge_mark','use_light_contour','use_shadow'] :setattr(m,attr,False)
 m.use_intersection=True;m.radius=radius;m.opacity=1;m.level_start=0;m.level_end=0;m.use_multiple_levels=False;m.stroke_depth_offset=.005
 return o

def bake_intersection_ink(obj):
    """Bake current camera-visible line geometry before hiding source proxies.

    A real current-frame drawing is required for modifier_apply in Blender 5.2;
    otherwise it reports FINISHED but silently produces no strokes.
    Baked strokes are camera dependent; regenerate when the camera changes.
    """
    scene = bpy.context.scene
    layer = obj.data.layers[0]
    if not any(frame.frame_number == scene.frame_current for frame in layer.frames):
        layer.frames.new(scene.frame_current)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()
    modifier = next(m for m in obj.modifiers if m.type == 'LINEART')
    result = bpy.ops.object.modifier_apply(modifier=modifier.name)
    strokes = sum(len(frame.drawing.strokes) for frame in layer.frames)
    if result != {'FINISHED'} or not strokes:
        raise RuntimeError(f'Intersection bake yielded {strokes} strokes: {result}')
    return strokes
