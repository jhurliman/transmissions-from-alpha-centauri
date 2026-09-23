# Native curved arch ink study130

Reusable module: `tools/coliseum_arch_ink_130.py::apply(C, radius=.035)` on the corrected129 source, once. It creates one native curve object and one dark-plum emission material. All source masonry vertices, materials, existing ink and camera stay unchanged.

Curved perimeter edges are extracted from the actual current stone meshes using constant depth/normal-profile offsets and changing arch angle. Radial end edges are excluded. Front and back opening boundaries are extracted from the actual joined tunnel wall. The selected indices are evaluated through the127 layout modifier before creating ink, so the lines match the accepted positions. Regenerate after geometry/layout changes.

There are5,708 edge runs and19,353 edge segments. Intact tiers each have36 opening runs (18front +18back); the damaged upper tier has38 split runs, preserving actual interrupted geometry. Stone gaps are never connected across objects. Hidden curves use normal scene depth occlusion, not an always-on-top overlay. Ink radius is0.035 world units at front rims,82% on buried stone rear edges and140% at recessed opening rims; the color matches existing dark plum contact ink(.018,.012,.022 linear).

`geometry.blend` is isolated. `preview-main4k.png` is an initial native4K crop without Freestyle. The final matched `before/after-main4k.png` retain the source's Freestyle and existing contact ink. No primary edits or user approval.

Niche archivolts are explicitly excluded. Rear opening rims receive0.049 world radius to avoid disappearing into subpixel antialiasing against the dark return material. `after-gray.png` is the native render exported directly to grayscale for readability review.
