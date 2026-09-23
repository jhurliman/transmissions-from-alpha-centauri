"""Recompose the existing secondary age field around the157 course failure.

Uses original material coordinates and existing exhaustive receiving-face
masks. It adds no image, shading layer, geometry, lighting or ink.
"""
import json
import math
from pathlib import Path
import bpy
from coliseum_facade_age_152 import shader_group

R = Path(__file__).resolve().parents[1]


def concentrate_existing_deposit(group, study):
    """Redistribute one existing pigment layer on native original coordinates.

    The incoming factor already contains exhaustive front-face, source-value,
    original deposit-shape and strength gates; none are bypassed here.
    """
    spec=study.get('midtone_body')
    if not spec:return None
    n,l=group.nodes,group.links
    def node(kind,label):
        q=n.new(kind);q.label=label;return q
    def mathn(op,*args):
        q=node('ShaderNodeMath','158 body '+op);q.operation=op
        for i,a in enumerate(args):
            if isinstance(a,(float,int)):q.inputs[i].default_value=a
            else:l.new(a,q.inputs[i])
        return q.outputs[0]
    def vec(op,a,b):
        q=node('ShaderNodeVectorMath','158 original frame '+op);q.operation=op
        l.new(a,q.inputs[0]);q.inputs[1].default_value=b
        return q.outputs['Value' if op=='DOT_PRODUCT' else 'Vector']
    inp=next(q for q in n if q.type=='GROUP_INPUT')
    frame=study['secondary']['frame']
    rel=vec('SUBTRACT',inp.outputs['Original position'],frame['origin_original'])
    u=vec('DOT_PRODUCT',rel,frame['across_original']);v=vec('DOT_PRODUCT',rel,frame['up_original'])
    points=spec['polygon'];area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
    if area<0:points=list(reversed(points))
    distances=[]
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        ax=mathn('SUBTRACT',u,a[0]);ay=mathn('SUBTRACT',v,a[1])
        distances.append(mathn('DIVIDE',mathn('SUBTRACT',mathn('MULTIPLY',ax,dy),mathn('MULTIPLY',ay,dx)),math.hypot(dx,dy)))
    distance=distances[0]
    for d in distances[1:]:distance=mathn('MAXIMUM',distance,d)
    # Reuse the established grain frequencies, avoiding an extra noise family.
    coarse=next(q for q in n if q.type=='TEX_NOISE' and abs(q.inputs['Scale'].default_value-1.4)<.001)
    fine=next(q for q in n if q.type=='TEX_NOISE' and abs(q.inputs['Scale'].default_value-7.5)<.001)
    warp=mathn('ADD',mathn('MULTIPLY',mathn('SUBTRACT',coarse.outputs['Fac'],.5),.32),mathn('MULTIPLY',mathn('SUBTRACT',fine.outputs['Fac'],.5),.11))
    edge=node('ShaderNodeMapRange','158 feathered body boundary');edge.clamp=True;edge.interpolation_type='SMOOTHSTEP'
    l.new(mathn('ADD',distance,warp),edge.inputs['Value'])
    edge.inputs['From Min'].default_value=spec['edge_feather'][0];edge.inputs['From Max'].default_value=spec['edge_feather'][1]
    body=mathn('SUBTRACT',1.,edge.outputs[0])
    deposit=next(q for q in n if q.label=='152 secondary connected sheltered deposit')
    old=deposit.inputs[0].links[0].from_socket
    factor=mathn('ADD',spec['periphery_factor'],mathn('MULTIPLY',body,spec['body_factor']-spec['periphery_factor']))
    l.new(mathn('MINIMUM',mathn('MULTIPLY',old,factor),.92),deposit.inputs[0])
    tint=node('ShaderNodeMixRGB','158 existing deposit pigment redistribution');tint.blend_type='MIX'
    l.new(body,tint.inputs[0]);tint.inputs[1].default_value=study['secondary']['deposit_tint'];tint.inputs[2].default_value=spec['body_tint']
    l.new(tint.outputs[0],deposit.inputs[2])
    return spec


def apply(C):
    study = json.loads((R / "config/coliseum-course-age-158.json").read_text())
    cfg = json.loads((R / "config/coliseum-facade-age-152.json").read_text())
    # Keep the retained155 primary placement exactly.
    cfg["groups"]["primary"]["deposit_polygons"][4] = [
        [u + study["primary_155_shift_u"], v]
        for u, v in cfg["groups"]["primary"]["deposit_polygons"][4]
    ]
    before = cfg["groups"]["secondary"]
    cfg["groups"]["secondary"] = study["secondary"]
    group = shader_group(cfg)
    group.name = "158 Attached course-loss age"
    body=concentrate_existing_deposit(group,study)
    copies, assignments = {}, []
    for ob in C.all_objects:
        if ob.type != "MESH":
            continue
        for index, slot in enumerate(ob.material_slots):
            old = slot.material
            if not old or not old.use_nodes:
                continue
            if not any(n.type == "GROUP" and n.label == "152 Connected facade age"
                       for n in old.node_tree.nodes):
                continue
            if old not in copies:
                mat = old.copy()
                mat.name = "158 Attached age " + old.name
                for node in mat.node_tree.nodes:
                    if node.type == "GROUP" and node.label == "152 Connected facade age":
                        node.node_tree = group
                copies[old] = mat
            slot.link = "OBJECT"
            slot.material = copies[old]
            assignments.append({"object": ob.name, "slot": index,
                                "source_material": old.name,
                                "material": copies[old].name})
    return {
        "source": study["source"], "assignments": assignments,
        "private_material_count": len(copies),
        "secondary_before": before, "secondary_after": study["secondary"],
        "primary_155_preserved": True,
        "noise_and_receiver_masks_unchanged": True,
        "finite_deposit_redistribution": body,
        "geometry_normals_lighting_ink_unchanged": True,
        "reference_ids": list(study["references"]),
        "status": "Unreviewed material proof; do not integrate without actual visual review",
    }
