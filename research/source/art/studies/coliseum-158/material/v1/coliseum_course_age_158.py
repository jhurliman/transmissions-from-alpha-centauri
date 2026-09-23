"""Recompose the existing secondary age field around the157 course failure.

Uses original material coordinates and existing exhaustive receiving-face
masks. It adds no image, shading layer, geometry, lighting or ink.
"""
import json
from pathlib import Path
import bpy
from coliseum_facade_age_152 import shader_group

R = Path(__file__).resolve().parents[1]


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
        "palette_strength_noise_and_receiver_masks_unchanged": True,
        "geometry_normals_lighting_ink_unchanged": True,
        "reference_ids": list(study["references"]),
        "status": "Unreviewed material proof; do not integrate without actual visual review",
    }
