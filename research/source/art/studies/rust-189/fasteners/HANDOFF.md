# 189 fastener corrosion, V2

Use `tools/bolt_rust_189.py::append_payload(scene)` on retained 188 geometry after beam material work. It appends one world-space mesh and privately resets obsolete 137 corrosion on both Y splice plates and their eight bolts. It also corrects the shared film shader and preserves existing Freestyle exclusions through an unlinked union filter with a fake user, so the filter survives saving. Original meshes, normals, transforms, lights and original material graphs are retained.

3,253 of 4,066 real bolt/screw head occurrences have applied corrosion (80.005%). Paired shanks and washers are not counted twice. 231 heads use a small native-face spot where receiver projection fails; the others have receiver/root film. Zero selected heads lack applied pigment geometry. Render-enabled eligibility was independently checked; screen projection is not an occlusion visibility claim.

Four of 42 real four-bolt plates are heavily weathered: both foreground Y splice plates, plus two visible left-wall anchors at different depths selected from the root camera-occlusion audit. All 16 bolts receive corrosion. Supported broad-wash footprints are 51.88%, 43.90%, 40.65%, and 65.92%, measured at mean native vertex alpha greater than .05 before fine shader porosity. Alpha-weighted areas are 33.17%, 27.62%, 25.37%, and 42.70%.

The wash is a continuous shared-vertex field with a smooth ragged boundary and coherent hue variation. It does not independently color binary cells. One shared native shader retains oxide hue under bounded actual-light response, plus transparency and fine porosity. 46,613 new pigment faces, 187,506 vertices. Rebuild takes about 164 seconds; cache append avoids recomputation.

Rejected V1 caches and audits are archived in v1-rejected. V1 had dark diffuse films and, critically, accidental Freestyle outlines on the film mesh; those could form a black stencil. V2 requires fresh filter membership validation and an actual integrated render review. No visual acceptance or user approval is claimed by this handoff.
