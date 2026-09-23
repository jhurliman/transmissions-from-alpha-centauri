"""Recompose the existing primary pigment on a broad native facade family."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from coliseum_facade_age_152 import shader_group
from coliseum_course_age_158 import concentrate_existing_deposit
R=Path(__file__).resolve().parents[1]
def normal(points):
    n=Vector()
    for a,b in zip(points,points[1:]+points[:1]):n+=a.cross(b)
    return n.normalized()
def apply(C):
    study=json.loads((R/'config/coliseum-broad-age-162.json').read_text())
    age158=json.loads((R/'config/coliseum-course-age-158.json').read_text())
    cfg=json.loads((R/'config/coliseum-facade-age-152.json').read_text())
    cfg['groups']['primary']=study['primary'];cfg['groups']['secondary']=age158['secondary']
    group=shader_group(cfg);group.name='162 Unequal broad facade age'
    concentrate_existing_deposit(group,age158)
    masks=[];new_slots={};attrname=study['primary']['receiver_attribute']
    for ob in C.all_objects:
        if ob.type!='MESH':continue
        previous=ob.data.attributes.get('152 primary facade receiver')
        extra=(ob.name in [f'COL110 U{i} sill wall'for i in range(6,10)] or any(ob.name.startswith(f'COL110 T2 band{i:02d} profile')for i in range(6,10)))
        if not previous and not extra:continue
        ob.data=ob.data.copy();me=ob.data;src=me.attributes.get('115 Original world position')
        a=me.attributes.new(attrname,'FLOAT','FACE');previous=me.attributes.get('152 primary facade receiver')
        indices=set(i for i,d in enumerate(previous.data)if d.value>.5)if previous else set()
        if extra:
            assert src,ob.name
            for p in me.polygons:
                ps=[src.data[i].vector.copy()for i in p.vertices];n=normal(ps)
                material=me.materials[p.material_index];name=material.name.lower()if material else ''
                ok=(n.y<-.85 and abs(n.z)<.25)if 'sill wall'in ob.name else(n.y<-.6 and abs(n.z)<.55 and not any(t in name for t in ['exposed','core']))
                if ok:indices.add(p.index)
        for i in indices:a.data[i].value=1.
        if extra:new_slots[ob.name]={me.polygons[i].material_index for i in indices}
        masks.append({'object':ob.name,'faces':len(indices),'existing_primary_mask_preserved':bool(previous),'new_exhaustive_front_classification':extra,'attribute':attrname})
    copies={};assignments=[]
    for ob in C.all_objects:
        if ob.type!='MESH':continue
        for index,slot in enumerate(ob.material_slots):
            old=slot.material
            if not old or not old.use_nodes:continue
            prior=any(n.type=='GROUP'and n.label=='152 Connected facade age'for n in old.node_tree.nodes)
            if not prior and index not in new_slots.get(ob.name,set()):continue
            if old not in copies:
                m=old.copy();m.name='162 Broad facing '+old.name;n,l=m.node_tree.nodes,m.node_tree.links
                if prior:
                    q=next(n for n in n if n.type=='GROUP'and n.label=='152 Connected facade age');q.node_tree=group
                    # Replace this input only; all secondary/core/source links stay.
                    a=n.new('ShaderNodeAttribute');a.attribute_name=attrname;a.label=attrname;l.new(a.outputs['Fac'],q.inputs['primary mask'])
                else:
                    em=next(q for q in n if q.type=='EMISSION'and q.inputs[0].is_linked);base=em.inputs[0].links[0].from_socket
                    q=n.new('ShaderNodeGroup');q.node_tree=group;q.label='152 Connected facade age';q.inputs['Strength'].default_value=1.;l.new(base,q.inputs['Source color'])
                    for attr,inp,output in [('115 Original world position','Original position','Vector'),(attrname,'primary mask','Fac'),('152 secondary facade receiver','secondary mask','Fac')]:
                        a=n.new('ShaderNodeAttribute');a.attribute_name=attr;a.label=attr;l.new(a.outputs[output],q.inputs[inp])
                    l.new(q.outputs['Color'],em.inputs[0])
                copies[old]=m
            slot.link='OBJECT';slot.material=copies[old]
            assignments.append({'object':ob.name,'slot':index,'source_material':old.name,'material':copies[old].name})
    return {'source':study['source'],'primary':study['primary'],'secondary158V2_preserved':True,'receiving_masks':masks,'assignments':assignments,'private_material_count':len(copies),'new_layer':False,'status':'Unreviewed native material study'}
