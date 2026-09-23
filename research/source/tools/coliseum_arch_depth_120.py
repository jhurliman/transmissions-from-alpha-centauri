"""Two painted depth families on real arch soffits/jambs; no geometry changes."""
import math
from mathutils import Matrix, Vector

DEPTH='120 Actual arch tunnel depth'

def _authored(ob):
    attr=ob.data.attributes.get('115 Original world position')
    if not attr or attr.domain!='POINT':
        return None
    anchor=Vector((0,-14,3.65))
    unlean=Matrix.Rotation(math.radians(-2),4,'X')
    return [unlean@(anchor+(d.vector-anchor)/.715-Vector((0,347,0))) for d in attr.data]

def _material(base,cache):
    if base in cache:return cache[base]
    m=base.copy();m.name='120 Two-depth interior '+base.name
    nodes=m.node_tree.nodes;links=m.node_tree.links
    em=next((n for n in nodes if n.type=='EMISSION'),None)
    if not em or not em.inputs[0].is_linked:raise RuntimeError('Expected native painted emission material')
    original=em.inputs[0].links[0].from_socket
    a=nodes.new('ShaderNodeAttribute');a.attribute_name=DEPTH;a.label='Actual authored radial depth, front0 back1'
    split=nodes.new('ShaderNodeValToRGB');split.label='Front half lighter, rear half darker'
    split.color_ramp.interpolation='LINEAR'
    split.color_ramp.elements[0].position=.485
    split.color_ramp.elements[0].color=(1.08,1.08,1.08,1)
    split.color_ramp.elements[1].position=.515
    split.color_ramp.elements[1].color=(.63,.63,.63,1)
    links.new(a.outputs['Fac'],split.inputs[0])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.label='Retain native lighting and violet hue'
    links.new(original,mix.inputs[1]);links.new(split.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],em.inputs[0])
    m['reference']='UCL-01; user-selected two-depth arch interior detail'
    m['depth_definition']='Authored radius: front0, back1; restricted to real return polygons'
    cache[base]=m;return m

def apply(C):
    cache={};report={'objects':0,'soffit_faces':0,'jamb_faces':0,'skipped':[],'geometry_changed':False,'front_gain':1.08,'back_gain':.63,'transition':[.485,.515]}
    for ob in C.objects:
        if ob.type!='MESH' or ob.get('120 depth applied'):continue
        is_arch='loadbearing arch tunnel' in ob.name
        is_pier='solid pier' in ob.name and ob.get('tier',-1) in [0,1,2]
        if not(is_arch or is_pier):continue
        coords=_authored(ob)
        if coords is None:report['skipped'].append(ob.name);continue
        # Undo inward batter before measuring radial depth.
        radii=[math.hypot(p.x,p.y)/(1-.055*p.z/78) for p in coords]
        lo,hi=min(radii),max(radii);span=hi-lo
        if span<1:report['skipped'].append(ob.name);continue
        zmax=max(p.z for p in coords);chosen=[]
        for poly in ob.data.polygons:
            ids=list(poly.vertices);rr=[radii[i] for i in ids];zz=[coords[i].z for i in ids]
            if max(rr)-min(rr)<span*.65:continue
            if is_arch and max(zz)>=zmax-.02:continue # exclude top floor and end caps
            if is_pier and max(zz)-min(zz)<1:continue # exclude top/bottom planes
            chosen.append(poly.index)
        if not chosen:report['skipped'].append(ob.name);continue
        if ob.data.users>1:ob.data=ob.data.copy()
        me=ob.data;attr=me.attributes.get(DEPTH) or me.attributes.new(DEPTH,'FLOAT','POINT')
        for i,r in enumerate(radii):attr.data[i].value=max(0,min(1,(hi-r)/span))
        slots={}
        for index in chosen:
            poly=me.polygons[index];old=poly.material_index
            if old not in slots:
                mat=_material(me.materials[old],cache);slots[old]=len(me.materials);me.materials.append(mat)
            poly.material_index=slots[old]
        ob['120 depth applied']=True
        report['objects']+=1;report['soffit_faces' if is_arch else 'jamb_faces']+=len(chosen)
    report['material_variants']=len(cache)
    return report
