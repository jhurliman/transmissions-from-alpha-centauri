# 189 native fastener rust

Use `tools/bolt_rust_189.py::append_payload(scene)` on retained 188 geometry after beam material work. It appends one world-space mesh collection and privately resets the obsolete 137 material overlay on both Y splice plates and their eight bolts. Do not separately call reset; append already does this. `apply(scene)` rebuilds deterministically in about 147 seconds. Source meshes, normals, transforms, lights and existing material graphs remain intact. New thin, receiver-conforming native pigment faces use one translucent diffuse material; excluded from Freestyle.

3,253 of 4,066 actual head occurrences receive corrosion (80.005%). Paired shanks/washers are excluded from the denominator. 3,023 have ray-conforming receiver/root film; 230 fully occluded or receiver-rejected heads instead have a spot attached directly to their native head face. No selected head has zero applied geometry. 2,088 selected centers project into the frame; this is not an occlusion visibility claim.

Four of 42 real four-bolt plates are heavy (9.52%, nearest integer to 10%): left Y splice, upper left wall shoe, near right pilaster shoe and deeper right wall shoe. Actual emitted wash cell area is 46.14%, 44.60%, 60.26%, 31.79% respectively. All 16 associated bolts have applied corrosion. The full 42 plates share rectangular face geometry, so emitted uniform-cell ratio is plate-face coverage; bolt/root films are additional to the broad wash.

Fresh visibility audit on 188 finds zero hidden objects, parent chains, hidden instance collections or hidden scene collection paths among eligible occurrences.

Root must inspect actual integrated render before visual acceptance. Particular checks: oxide light response under stylized lighting, no black outlines on pigment faces, no repeated equal drips, meaningful small weathering across both alley walls. Candidate is not user approved.
