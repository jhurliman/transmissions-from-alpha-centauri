# Alley weathering 146

Latest user-directed refinement of145: broad cross-panel lightening regions, finer irregular splotches weighted toward each panel base, and50% longer fading rust reach through a separate translucent layer. This remains a component/placement study toward the full95 target, not a completed global weathering rollout or user-approved lock.

## Native implementation

- `tools/alley_panel_material_146.py`: broad spatial susceptibility spans the whole group. Explicit panel origins and heights anchor only the fine lower-region variation. Actual diffuse/specular signals and incident light color control the response; quiet cool fill does not retain a fixed warm patch. A restrained illumination-driven value catch keeps cool-lit detail possible.
- `tools/alley_surface_details_146.py`: existing dark contact oxide/run remains Layer1. A separate Layer2 uses `Wash strength` and `Wash length multiplier` controls, with length1.5 and continuous opacity falloff toward its endpoint. Authored run anchors and head widths are preserved.
- Geometry, camera and lights are unchanged from corrected145V2. The small-ink Freestyle exclusion and visible crack placement carry forward.

## Review outputs

`prototype/review-146.html` compares145 and146 material controls, combined component proofs, rust layers and actual-alley crops. Native4K resolutions are3840×1745 for the component and3840×2885 for the scene. The editable component kit is `combined/panel-kit.blend`; the scene candidate is `actual/scene.blend`.

`actual/146-vs-145-verification.json` checks identical rendered-object inventory, geometry, normals, transforms, camera and lights. Only material assignments differ. Every instantiated wash length multiplier is exactly1.5; visible low-opacity reach depends on illumination and display size.

The reference master remains the creator's original UCL-01 made using ChatGPT Images2.5. Existing145reference analysis/provenance and supplemental registered surface studies carry forward. No reference pixels are projected onto geometry.

## Status

Component light controls and combined native render inspected. Actual4K inspected; fine coating response stays subtle on the shaded left facade, and fading runs remain subordinate to damage. Earlier145scores preceded the corrected ink integration and should not be treated as fresh146scores. The full95-per-axis goal, broad scene rollout and unfinished coliseum139/141/144 work remain open.
