"""User correction: actual crown V-joints should read as black ink."""
import bpy

def apply(scene):
    C=next(c for c in scene.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and c.library is None)
    m=bpy.data.materials.new('133 Black masonry joint ink');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1);em.inputs['Strength'].default_value=1.;out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
    faces=0
    for ob in C.objects:
        if ob.type!='MESH':continue
        at=ob.data.attributes.get('131 Crown joint interior')
        if not at:continue
        ob.data.materials.append(m);slot=len(ob.data.materials)-1
        for p in ob.data.polygons:
            if at.data[p.index].value>.5:p.material_index=slot;faces+=1
    ob=C.objects.get('131 Recessed crown joint ink')
    if ob:
        ob.data.materials.clear();ob.data.materials.append(m)
    return {'groove_faces_black':faces,'curve_black':bool(ob),'color_linear_rgba':[0,0,0,1],'geometry_unchanged':True,'scope':'Actual V-groove interiors and their existing ink core only'}
