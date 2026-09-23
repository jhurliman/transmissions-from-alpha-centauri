# Ruined transition refinement — study 200, V2

Native refinement of the existing 133 ruined transition kit. The accepted silhouettes, placement, road corridor and city layout remain fixed. References: UCL-01, UCL-02 and DP-03, inspected at whole-image and transition-detail scales.

V2 replaces isolated face-centre recesses with connected, irregular crown losses and descending fractures. Twenty meshes receive 35 real cuts; all 57 kit pieces receive restrained private facing wear. Floor cuts interrupt exposed slab edges. Cut surfaces use a darker core material and real recessed surfaces rather than flat painted hole decals.

The rejected V1 is archived in `held-v1`. It produced pale oval spots. A camera-ray/material audit identified two causes: the isolated recess design and incorrect Boolean material indexing after Blender expanded the target slots. V2 uses explicit core-material identity and asymmetric stepped fractures attached to existing visible crowns.

`tools/city_transition_refinement_200.py:apply(scene)` replays the checked native payload. Before mutation it verifies the 57 source meshes, transforms and material assignments; afterward it verifies edited mesh hashes. The source is study197, and the 133 kit is unchanged in the integration baseline201. Apply 204 after this replay to incorporate the user's later half-strength blue/rust palette request while retaining core darkness.

Validation: preservation audit passed (only 133 objects differ; no original material graph changes), closed-mesh checks passed, exported-payload replay passed. Native proof uses the original 3840×2885 camera and 149/156/161/192 visibility guards. The combined 200+204 crop is a new native render; the reusable candidate and payload do not contain 204.

This is an initial structural refinement, not a claim of complete reference fidelity or user approval. Geometry remains deliberately sparse and connected; the current proof must show visibly broken wall fabric without polka-dot recesses.

V2 actual proof `transition-204-native.png` was inspected beside the baseline: floating oval spots are gone; crown-connected dark losses and long fractures read on both sides. Retained for the integrated203 review. Palette differences in this proof also include204 and are not credited solely to200.
