"""Thin, explicit native edge ownership for the four farther ruined buildings.
No pigment, fog, geometry-position or nearest-ruin changes.
"""
import bpy, math
PREFIXES=('133 L1 ','133 L2 ','133 R4 ','133 R5 ')
EDGE_TYPES=('silhouette','border','crease','ridge_valley','suggestive_contour','material_boundary','contour','external_contour','edge_mark')

def apply(scene):
    assert not scene.get('248 farther ruin ink')
    ruins=bpy.data.collections['133 Ruined transition structures']
    targets=[o for o in ruins.objects if o.type=='MESH' and (o.name.startswith(PREFIXES) or str(o.get('235 host','')).startswith(PREFIXES))]
    near={o.name:(o.data,tuple(o.matrix_world),tuple(s.material for s in o.material_slots)) for o in ruins.objects if o.type=='MESH' and (o.name.startswith(('133 L0 ','133 R3 ')) or str(o.get('235 host','')).startswith(('133 L0 ','133 R3 ')))}
    old=[]
    for layer in scene.view_layers:
        for ls in layer.freestyle_settings.linesets:
            if ls.name in ('230 Broken wall readable contours','235 Fine ruin interior structure'):
                old.append({'name':ls.name,'enabled':ls.show_render,'count':len(ls.collection.objects),'width':ls.linestyle.thickness,'alpha':ls.linestyle.alpha})
    # All four complete assemblies receive coherent exterior contours. Existing
    # floor fragments are actual native meshes rather than invented painted lines.
    changes=[]
    for layer in scene.view_layers:
        for ls in layer.freestyle_settings.linesets:
            if not(ls.select_by_collection and ls.collection):continue
            for o in targets:
                if ls.collection_negation=='EXCLUSIVE':
                    if o.name not in ls.collection.objects:ls.collection.objects.link(o)
                elif o.name in ls.collection.objects:
                    ls.collection.objects.unlink(o);changes.append([ls.name,o.name])
    coll=bpy.data.collections.new('248 Far four ruined wall ink targets');coll.use_fake_user=True
    for o in targets:coll.objects.link(o)
    marks=[]
    for o in targets:
        if o.hide_render:continue
        oldmesh=o.data;o.data=oldmesh.copy()
        faceedges={e.key:[]for e in o.data.edges}
        for p in o.data.polygons:
            for key in p.edge_keys:faceedges[key].append(p)
        total=damage=sharp=0
        attr=o.data.attributes.get("freestyle_edge") or o.data.attributes.new("freestyle_edge","BOOLEAN","EDGE")
        for e in o.data.edges:
            attr.data[e.index].value=False
            ps=faceedges[e.key]
            if len(ps)!=2:continue
            length=(o.matrix_world.to_3x3()@(o.data.vertices[e.vertices[1]].co-o.data.vertices[e.vertices[0]].co)).length
            if length<.075:continue
            diff=ps[0].material_index!=ps[1].material_index
            angle=ps[0].normal.angle(ps[1].normal,0)
            # True chipped recess lips, fractures and construction edges. Outer
            # boundaries are subtracted by the line-set predicate below.
            if diff or angle>math.radians(35):
                attr.data[e.index].value=True;total+=1;damage+=int(diff);sharp+=int(not diff)
        marks.append({'object':o.name,'marked_native_edges':total,'material_separation_edges':damage,'sharp_edges':sharp,'mesh_geometry_unchanged':True})
    layer=scene.view_layers['215 Distant ink without atmospheric boundary']
    styles=[]
    for interior in (False,True):
        name='248 Far ruin damage accents' if interior else '248 Far ruin thin contours'
        ls=layer.freestyle_settings.linesets.new(name);ls.select_by_collection=True;ls.collection=coll;ls.collection_negation='INCLUSIVE';ls.show_render=True
        ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_by_edge_types=True;ls.select_by_image_border=True
        ls.edge_type_combination='AND' if interior else 'OR';ls.edge_type_negation='INCLUSIVE'
        for key in EDGE_TYPES:
            setattr(ls,'select_'+key,False);setattr(ls,'exclude_'+key,False)
        for key in ('silhouette','border','external_contour'):
            setattr(ls,'select_'+key,True)
            if interior:setattr(ls,'exclude_'+key,True)
        if interior:ls.select_edge_mark=True
        ls.linestyle.thickness=.52 if interior else .95
        ls.linestyle.color=(.034,.030,.049) if interior else (.012,.013,.023)
        ls.linestyle.alpha=.88 if interior else .98
        styles.append({'name':name,'width':ls.linestyle.thickness,'alpha':ls.linestyle.alpha,'predicate':'marked native edge AND NOT outer boundary' if interior else 'visible native outer boundary'})
    for n,(me,mat,M) in near.items():
        o=bpy.data.objects[n];assert o.data==me and tuple(o.matrix_world)==mat and tuple(s.material for s in o.material_slots)==M,n
    assert all(o.name not in coll.objects for o in ruins.objects if o.name in near)
    scene['248 farther ruin ink']=True
    return {'study':248,'targets':[o.name for o in targets],'visible_count':sum(not o.hide_render for o in targets),'old_styles':old,'styles':styles,'native_edge_marks':marks,'ownership_changes':changes,'nearest_L0_R3_exact':True,'geometry_material_fog_unchanged':True,'diagnosis':'Prior230/235 styles were enabled with .82/.65px widths and intact22object membership; no missing collection bug found. Private complete-assembly ownership strengthens .95px contour; explicit mesh edge marking makes surviving damage edges unambiguous. Actual combined proof required.','references':['UCL-01','UP-03','DP-08']}
