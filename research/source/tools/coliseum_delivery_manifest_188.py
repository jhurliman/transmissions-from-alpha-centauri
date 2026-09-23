"""Hash-pin the incremental188 native recipe and reviewed delivery."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/coliseum-188'
INPUTS = {
    'historical_native_inputs': [
        'art/studies/coliseum-173/scene.blend',
        'art/studies/coliseum-173/main-4k.png',
        'art/studies/coliseum-173/delivery-manifest.json',
        'art/studies/coliseum-187/geometry/candidate.blend',
    ],
    'reviewed_mesh_replay': [
        'tools/coliseum_left_course_187.py',
        'art/studies/coliseum-187/geometry/payload.blend',
        'art/studies/coliseum-187/geometry/payload.json',
        'art/studies/coliseum-187/geometry/certified-audit.json',
        'art/studies/coliseum-187/geometry/replay-audit.json',
    ],
    'build_code': [
        'tools/coliseum_contact_source_187.py',
        'tools/coliseum_contact_correct_187.py',
        'tools/coliseum_contact_clip_169.py',
        'tools/coliseum_contact_certificate_169.py',
        'tools/coliseum_integration_188.py',
        'tools/scene_integration_138.py',
        'tools/coliseum_ink_regression_149.py',
        'tools/coliseum_foreground_visibility_156.py',
        'tools/coliseum_foreground_visibility_161.py',
    ],
    'configuration': [
        'config/coliseum-left-course-187.json',
        'config/coliseum-integration-188.json',
    ],
    'delivery_code': [
        'tools/coliseum_delivery_audit_188.py',
        'tools/coliseum_kit_proof_188.py',
        'tools/coliseum_validate_188.py',
        'tools/publish_coliseum_188.py',
        'tools/coliseum_delivery_manifest_188.py',
    ],
    'published_comparison_assets': [
        'art/studies/alley-weathering-147/actual/before-crop.png',
        'art/studies/alley-weathering-147/actual/after-crop.png',
        'art/studies/alley-weathering-147/coverage-calibration.json',
        'art/studies/coliseum-134/analysis/independent/reference-display.png',
    ],
}
OUTPUTS = [
    'scene.blend', 'kit.blend', 'main-4k.png', 'generation.json',
    'preservation.json', 'performance.json', 'fresh-native-delivery-check.json',
    'native-ink-visibility.json', 'foreground-ink-visibility.json',
    'fascia-ink-visibility161.json', 'pixel-comparison.json',
    'kit-proof/append-audit.json', 'kit-proof/right-break-painted.png',
    'kit-proof/right-break-clay.png', 'critic.json', 'review.json', 'README.md',
    'delivery-check.json',
]
OTHER_OUTPUTS = [
    'prototype/review-188.html',
    'art/studies/coliseum-187/contact-source/audit.json',
    'art/studies/coliseum-187/contact/corrected-study.blend',
    'art/studies/coliseum-187/contact/audit.json',
    'art/studies/coliseum-187/contact/clip-payload.json',
    'art/studies/coliseum-187/contact/continuous-support-certificate.json',
]


def stamp(rel):
    p = R / rel
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return {'path': rel, 'bytes': p.stat().st_size, 'sha256': h.hexdigest()}


result = {
    'scope': 'Incremental188 from retained173 plus the certified187 native candidate. These native inputs are required; no source-from-nothing rebuild claim. Saved188 scene is self-contained.',
    'runtime': {'blender': '5.2.1', 'delivery': 'Python3, Pillow, numpy, scipy'},
    'inputs': {k: [stamp(p) for p in v] for k, v in INPUTS.items()},
    'outputs': [stamp(str((O / p).relative_to(R))) for p in OUTPUTS] + [stamp(p) for p in OTHER_OUTPUTS],
    'commands_from_project_root': [
        'blender -b -t 4 --python tools/coliseum_contact_source_187.py',
        'blender -b -t 4 --python tools/coliseum_contact_correct_187.py',
        'blender -b -t 4 --python tools/coliseum_integration_188.py',
        'blender -b -t 4 --python tools/coliseum_integration_188.py -- render',
        'blender -b -t 2 --python tools/coliseum_delivery_audit_188.py',
        'blender -b -t 4 --python tools/coliseum_kit_proof_188.py -- coliseum-188',
        'python3 tools/publish_coliseum_188.py',
        'python3 tools/coliseum_validate_188.py',
        'python3 tools/coliseum_delivery_manifest_188.py',
    ],
    'optional_mesh_replay': 'tools/coliseum_left_course_187.py::apply(C) can replace the six source173 meshes from the included payload; verified in187 replay-audit. The main recipe starts from the already certified candidate.',
    'standalone_saved_scene': {
        'external_files_required_to_render': False,
        'native_visibility_texts': ['149 Native fascia visibility guard.py', '156 Proven foreground occlusion guard.py', '161 Proven fascia occlusion guard.py'],
        'instruction': 'Run all three embedded texts before rendering, or use the188 render command. No global trust preference change required.',
        'portable_kit_collection': '110 Coliseum detailed front ruin',
        'portable_kit_extra_object': '110 Landmark contact ink',
        'kit_instruction': 'Append both the collection and separate contact object with their transforms.',
    },
    'limits': [
        'Raster may vary with renderer execution/version/hardware; actual188 outside-raster differences were reviewed and disclosed.',
        'Known inherited mesh crossings and finite-sampling limits remain; no globally clean topology claim.',
        'Review reports contain independent human-like visual judgments and are not recreated by the build commands.',
        'Critic threshold is complete; user approval remains false.',
    ],
}
(O / 'delivery-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print('Recorded', sum(map(len, INPUTS.values())), 'inputs and', len(result['outputs']), 'outputs')
