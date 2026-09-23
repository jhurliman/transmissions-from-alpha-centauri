"""Record the finite incremental recipe and verify its exact native inputs.

Run after the 156 scene, kit, render and audits exist. This deliberately calls
the 152 blend a historical input; it does not claim a from-nothing rebuild.
"""
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / "art/studies/coliseum-156"

INPUTS = {
    "historical_native_source": ["art/studies/coliseum-152/scene.blend"],
    "build_code": [
        "tools/coliseum_integration_156.py",
        "tools/scene_integration_138.py",
        "tools/coliseum_crown_continuation_154.py",
        "tools/coliseum_crown_repair_123.py",
        "tools/coliseum_degenerate_cleanup_156.py",
        "tools/coliseum_edge_material_153.py",
        "tools/coliseum_age_placement_155.py",
        "tools/coliseum_facade_age_152.py",
        "tools/coliseum_ink_regression_149.py",
        "tools/coliseum_foreground_visibility_156.py",
    ],
    "shader_configuration": ["config/coliseum-facade-age-152.json"],
    "study_configuration": [
        "config/coliseum-156.json",
        "config/coliseum-crown-continuation-154.json",
        "config/coliseum-edge-material-153.json",
        "config/coliseum-age-placement-155.json",
    ],
    "delivery_code": [
        "tools/coliseum_delivery_manifest_156.py",
        "tools/coliseum_delivery_audit_156.py",
        "tools/coliseum_kit_proof_156.py",
        "tools/coliseum_validate_156.py",
        "tools/publish_coliseum_156.py",
    ],
}
OUTPUTS = [
    "scene.blend", "kit.blend", "main-4k.png", "generation.json",
    "preservation.json", "fresh-native-delivery-check.json",
    "native-ink-visibility.json", "foreground-ink-visibility.json", "kit-proof/append-audit.json",
]


def record(rel):
    p = R / rel
    if not p.is_file():
        raise FileNotFoundError(rel)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return {"path": rel, "bytes": p.stat().st_size, "sha256": h.hexdigest()}


def main():
    evidence = json.loads((O / "fresh-native-delivery-check.json").read_text())
    result = {
        "scope": "Incremental native rebuild of 156 from retained 152; not a clean build from no historical inputs.",
        "runtime": {
            "blender": "5.2.1",
            "build_modules": ["Blender bundled numpy, bpy, bmesh, mathutils"],
            "delivery_modules": ["Python 3, Pillow, numpy, scipy"],
        },
        "inputs": {kind: [record(p) for p in paths] for kind, paths in INPUTS.items()},
        "outputs": [record(str((O / p).relative_to(R))) for p in OUTPUTS],
        "commands_from_project_root": [
            "blender -b -t 4 --python tools/coliseum_integration_156.py",
            "blender -b -t 4 --python tools/coliseum_integration_156.py -- render",
            "blender -b -t 4 --python tools/coliseum_delivery_audit_156.py",
            "blender -b -t 4 --python tools/coliseum_kit_proof_156.py -- coliseum-156",
            "python3 tools/publish_coliseum_156.py",
            "python3 tools/coliseum_validate_156.py",
            "python3 tools/coliseum_delivery_manifest_156.py",
        ],
        "standalone_saved_scene": {
            "external_source_files_required_for_render": False,
            "render_pre_guard": "149 Native fascia visibility guard.py and 156 Proven foreground occlusion guard.py are embedded. Run both saved texts before rendering, or use trusted auto-execution for this project file. No global preference change is needed.",
            "portable_kit": "Append collection '110 Coliseum detailed front ruin' from kit.blend. The kit-proof append audit verifies the resulting geometry against the saved scene.",
            "fresh_reopen_evidence": evidence,
        },
        "limits": [
            "Render hardware and Blender version can produce small pixel differences; saved native inputs are hash-pinned.",
            "The original scene includes historical native geometry and packed pigment images. No reference artwork projection is introduced by this recipe.",
            "A successful build or dependency audit is not a whole-mesh cleanliness certificate or artistic approval.",
        ],
    }
    (O / "delivery-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Recorded", sum(map(len, INPUTS.values())), "inputs and", len(OUTPUTS), "outputs.")


if __name__ == "__main__":
    main()
