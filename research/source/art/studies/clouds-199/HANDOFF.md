# Cloud refinement199

`tools/cloud_refinement_199.py::apply(scene)` installs four packed EXRs derived solely from owned082 native cloud alpha/pigment sources, in eight private cloud materials. Source197 camera, cloud plate geometry/transforms, world sky and all noncloud assignments remain untouched. `cloud_refinement_199_generate.py` reproduces owned derivative assets; reference images never enter asset generation.

Inspection of197 showed fine contours already present, but near-uniform small roughness and interior noisy blurred lobes.199 redistributes edge activity into unequal billow shoulders, intermediate lobes and restrained fine upper-edge fray. It replaces the old interior noise emphasis with overlapping blurred native tone layers, quieter continuous pigment, and a small blue/green increase for less saturated clouds against the saturated sky. Per-family silhouette area is normalized to accepted133 masks, maintaining current cloud mass.

References: UC-01 broad color masses, UC-04 fine contour layering, DP-08 quiet versus detailed surface hierarchy. All camera/geometry/world invariants are checked by `cloud_refinement_199_check.py` in fresh source/candidate opens. Sky final requested colors remain untouched through preservation of the world shader.

Actual native full-camera render required before closure. GPU coordinated with root. The render entrypoint installs149/156/161/192 native ink callbacks and retains full resolution. Visual approval remains with user.

## V2 final tested revision

V1 actual proof was too flat and overly smooth. It is archived in held-v1. V2 selectively restores unequal upper peaks/shoulders and soft elongated overlapping veils, retaining calm lower edges and body regions. A second full4K native render was completed and compared with V1 and UC references. Independent critic recommends retaining V2: the requested hierarchy/layering improvement is now visible, without cel bands. This remains stylized and intentionally preserves the accepted large masses. Parent integration selection and user approval are separate.
