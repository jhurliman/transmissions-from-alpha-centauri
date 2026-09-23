"""Replace full-height footing slots with shallow top-edge chips and deliberate ink."""
import bpy, bmesh

def apply(scene):
    ob = bpy.data.objects['242 Single concrete footing for left service cluster']
    materials = [slot.material for slot in ob.material_slots]
    x0, x1, y0, y1 = -9.35, -7.68, 8.49, 9.48
    # Intermediate ring is straight along the road-facing side. Only the top
    # ring contains small losses. Damage therefore terminates above ground.
    ring = [(x0+.10,y0),(x1-.09,y0),(x1,y0+.075),
            (x1,8.71),(x1,8.765),(x1,8.83),
            (x1,9.15),(x1,9.195),(x1,9.245),
            (x1,y1-.10),(x1-.11,y1),(x0+.06,y1),
            (x0,y1-.06),(x0,y0+.095)]
    top = list(ring)
    top[4] = (x1-.055,8.769)
    top[7] = (x1-.038,9.191)
    n = len(ring)
    verts = [(x,y,z) for z in (-.24,.235) for x,y in ring]
    verts += [(x,y,.32) for x,y in top]
    faces = [tuple(reversed(range(n))), tuple(range(2*n,3*n))]
    for level in range(2):
        for i in range(n):
            j=(i+1)%n
            faces.append((level*n+i,level*n+j,(level+1)*n+j,(level+1)*n+i))
    mesh = bpy.data.meshes.new('245 Compact footing shallow surface chips')
    mesh.from_pydata(verts,[],faces); mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges)
    bm.to_mesh(mesh);bm.free()
    for mat in materials: mesh.materials.append(mat)
    ob.data=mesh
    # Bevel had split the intended perimeter into several subpixel contours.
    # At this camera scale the actual native chipped edge is the cleaner shape.
    for mod in list(ob.modifiers):
        if mod.type=='BEVEL': ob.modifiers.remove(mod)
    marked=0
    marks=mesh.attributes.new("freestyle_edge","BOOLEAN","EDGE")
    for e in mesh.edges:
        if all(v>=2*n for v in e.vertices):
            marks.data[e.index].value=True;marked+=1
    for layer in scene.view_layers:
        ls=layer.freestyle_settings.linesets.get('242 Service footing visible contour')
        if ls:
            ls.select_crease=False
            ls.select_edge_mark=True
            ls.select_silhouette=True
            ls.select_border=True
            ls.select_external_contour=True
            ls.edge_type_combination='OR'
    audit={'object':ob.name,'bounds':[x0,x1,y0,y1,-.24,.32],
           'chip_depth_vertical_m':.085,'chip_losses_horizontal_m':[.055,.038],
           'damage_above_z':.235,'full_height_notches':False,
           'top_perimeter_marked_edges':marked,'manifold':True,
           'ink':'visible marked top perimeter plus exterior silhouette; no general crease extraction',
           'preserved':'cool concrete material, compact footprint, contact seals, existing native soil visibility guard'}
    ob['245 shallow chip audit']=str(audit)
    return audit
