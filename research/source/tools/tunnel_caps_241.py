"""241: close the descending arcade outlets with solid native masonry plugs."""
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def apply(scene):
    assert not scene.get('241 tunnel caps applied'), 'Caps already applied'
    C=bpy.data.collections['110 Coliseum detailed front ruin']
    tunnels=sorted((o for o in C.all_objects if o.get('220 descending arcade tunnel')),key=lambda o:o['bay'])
    assert len(tunnels)==18
    rows=[]; materials={}
    for source in tunnels:
        n=27; me=source.data
        assert len(me.vertices)==7*2*n
        points=[source.matrix_world@v.co for v in me.vertices]
        center=lambda st:(points[st*2*n]+points[st*2*n+n-1])/2
        direction=(center(6)-center(5)).normalized()
        ring=points[6*2*n+n:7*2*n]
        thickness=.65
        verts=ring+[v+direction*thickness for v in ring]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
        mesh=bpy.data.meshes.new(f'241 Ground B{source["bay"]:02d} solid terminal plug')
        mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(me.materials[0])
        original=me.attributes.get('115 Original world position')
        if original:
            attr=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
            for i,d in enumerate(attr.data):d.vector=original.data[6*2*n+n+i%n].vector
        attr=mesh.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
        for d in attr.data:d.value=1
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(mesh);bm.free()
        assert bad==0 and volume>0,(source.name,bad,volume)
        ob=bpy.data.objects.new(f'COL241 T0 B{source["bay"]:02d} closed tunnel outlet',mesh);C.objects.link(ob)
        ob['241 tunnel end cap']=True;ob['tier']=0;ob['bay']=source['bay'];ob['coliseum_role']='tunnel';ob['241 source tunnel']=source.name
        tree=BVHTree.FromPolygons(verts, [tuple(p.vertices)for p in mesh.polygons])
        probe=sum(points[6*2*n:6*2*n+n],Vector())/n
        incoming=tree.ray_cast(probe-direction*2,direction,4)
        outgoing=tree.ray_cast(probe+direction*2,-direction,4)
        assert incoming[0] is not None and outgoing[0] is not None,source.name
        rows.append({'bay':source['bay'],'source':source.name,'cap':ob.name,'thickness_m':thickness,'solid_volume_m3':volume,'nonmanifold_edges':bad,'terminal_shell_fit_m':0,'blocks_both_directions':True,'material':mesh.materials[0].name})
        for material in me.materials:
            if not material or material.name in materials:continue
            materials[material.name]={'nodes':[{'name':node.name,'type':node.type,'label':node.label}for node in material.node_tree.nodes], 'depth_attribute_values':sorted(set(round(d.value,4)for d in me.attributes['120 Actual arch tunnel depth'].data))}
    scene['241 tunnel caps applied']=True
    return {'caps':rows,'material_audit':materials,'existing_tunnel_geometry_unchanged':True,'entrances_and_30m_plus_30m_routes_unchanged':True,'cap_position':'Full outer terminal profile; thickness extends beyond outlet, never shortens route','reference_ids':['UCL-01','UCL-02','DP-01']}
