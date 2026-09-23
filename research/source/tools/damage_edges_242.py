"""Fine native chipping along retained near-facade recess contours.
Only the 198 recess family is touched. Original extent, depth, material binding,
placement and all unbroken host vertices are retained.
"""
import bpy, bmesh, hashlib, random
from mathutils import Vector

def apply(scene, explicit_names=None):
    rows=[]
    for obj in bpy.data.objects:
        if obj.type!='MESH': continue
        if explicit_names is not None:
            if obj.name not in explicit_names: continue
        elif obj.get('198 native damage')!='recess' or obj.name.startswith('215 Kit '): continue
        assert not obj.get('242 chipped recess'), 'Apply to fresh 241 only'
        cut={i for i,s in enumerate(obj.material_slots) if s.material and ('exposed aggregate' in s.material.name.lower() or 'dense floor scuffs' in s.material.name.lower() or 'dark exposed substrate' in s.material.name.lower())}
        assert cut, obj.name
        mesh=obj.data.copy(); obj.data=mesh
        bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
        before_v=len(bm.verts);before_f=len(bm.faces)
        original_nonmanifold=sum(not e.is_manifold for e in bm.edges)
        original_volume=abs(bm.calc_volume())
        # Boundary and recessed floor/sidewall joins; no pristine panel perimeter.
        edges=[]
        for e in bm.edges:
            fs=list(e.link_faces)
            if len(fs)!=2 or e.calc_length()<.045:continue
            inside=[f.material_index in cut for f in fs]
            outer=inside[0]!=inside[1]
            inner=all(inside) and max(-f.normal.y for f in fs)>.97 and min(-f.normal.y for f in fs)<.94
            if outer or inner:edges.append((e,outer))
        rng=random.Random(int(hashlib.sha256(obj.name.encode()).hexdigest()[:12],16))
        added=0;maximum=0
        # Split each edge separately so long edges receive independently placed
        # chips rather than a regular sawtooth. Offsets lie within panel XZ plane.
        for edge,outer in edges:
            a,b=(v.co.copy() for v in edge.verts)
            tangent=b-a; perp=Vector((-tangent.z,0,tangent.x))
            if perp.length<1e-8:continue
            perp.normalize()
            cuts=3 if tangent.length>.16 else 2
            endvert=edge.verts[1]
            current=edge
            for k in range(cuts):
                startvert=next(v for v in current.verts if v!=endvert)
                newedge,v=bmesh.utils.edge_split(current,startvert,1/(cuts+1-k))
                current=next(e for e in v.link_edges if endvert in e.verts)
                amp=min(.017 if outer else .009,tangent.length*.11)
                shift=rng.uniform(-amp,amp)
                v.co=a+tangent*((k+1)/(cuts+1)+rng.uniform(-.04,.04))+perp*shift
                maximum=max(maximum,abs(shift));added+=1
        bm.normal_update()
        # The altered sloping reveal produces native uneven fracture facets
        # without filling the recess or adding dark washes.
        # Keep manifold reveal ngons; Blender tessellates these native nonplanar facets.
        bm.normal_update()
        nonmanifold=sum(not e.is_manifold for e in bm.edges)
        zeros=sum(f.calc_area()<1e-12 for f in bm.faces)
        volume=abs(bm.calc_volume())
        assert nonmanifold==original_nonmanifold,(obj.name,nonmanifold,original_nonmanifold)
        assert zeros==0,(obj.name,zeros)
        assert abs(volume-original_volume)<max(.002,original_volume*.01),(obj.name,volume,original_volume)
        bm.to_mesh(mesh);bm.free();mesh.update()
        # Recompute floor edge marks after topology edits, avoiding stale indices.
        adj={}
        for p in mesh.polygons:
            for key in p.edge_keys:adj.setdefault(tuple(sorted(key)),[]).append(p)
        attr=mesh.attributes.get('freestyle_edge') or mesh.attributes.new('freestyle_edge','BOOLEAN','EDGE')
        marks=0
        for e in mesh.edges:
            fs=adj.get(tuple(sorted(e.vertices)),[])
            inner=len(fs)==2 and all(f.material_index in cut for f in fs) and max(-f.normal.y for f in fs)>.97 and min(-f.normal.y for f in fs)<.94
            attr.data[e.index].value=inner
            marks+=inner
        obj['242 chipped recess']=True
        rows.append({'object':obj.name,'vertices_before':before_v,'vertices_after':len(mesh.vertices),'faces_before':before_f,'faces_after':len(mesh.polygons),'new_chip_vertices':added,'max_chip_displacement_m':maximum,'floor_contour_edges':marks,'nonmanifold_before':original_nonmanifold,'nonmanifold_after':nonmanifold,'zero_area_faces':zeros,'volume_before':original_volume,'volume_after':volume})
    styles=[]
    for vl in scene.view_layers:
        for ls in vl.freestyle_settings.linesets:
            if ls.name.startswith('208 Fine recessed floor'):
                ls.linestyle.thickness=.40
                styles.append({'layer':vl.name,'lineset':ls.name,'width':.40})
    assert len(rows)==(len(explicit_names) if explicit_names is not None else 14),len(rows)
    return {'scope':explicit_names or '14 retained 198 near facade recesses only','objects':rows,'styles':styles,'material_changes':0,'geometry_checks_passed':True,'visual_status':'Await parent integrated render; not user-approved'}

def apply_impact(scene):
    """Supplement the exact user-cited upper-left impact, after the recess pass."""
    audit=apply(scene,explicit_names=['Upper recessed mass panel.057'])
    obj=bpy.data.objects['Upper recessed mass panel.057']
    # Keep fine inner fracture joins owned by the existing dedicated edge-only
    # style. Broad panel edges are neither added nor selected by this style.
    coll=bpy.data.collections.get('208 Recess inner edge selection')
    if coll and obj.name not in coll.objects:coll.objects.link(obj)
    audit['exact_user_target']='Upper recessed mass panel.057'
    return audit
