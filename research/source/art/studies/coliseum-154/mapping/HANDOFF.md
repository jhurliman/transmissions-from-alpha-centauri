# Central crown continuation: native map

Read from152, using the current4K camera and registered UCL-01/UCL-02/DP-03 properties. `native-map.json` contains4px actual landmark ray samples, original-position interpolation, native world normals, inward solid-depth probes, vertices/face ownership and raw/evaluated topology. The source image crop is `central-crown-4x.png`.

A meaningful group requires all three existing parts: **U9 fractured upper wall L, U9 aperture head, U9 fractured upper wall R**. Each is closed and strict-crossing0 in152. L alone would repeat the small43px149 event. Together a front-strip proposal runs approximatelyx1976–2070, about94native pixels. The U8 wall and Tower10 are excluded.

Existing protective geometry constrains the lower boundary: left field0 upper course is atworldZ48.78–48.90, right field1 course at47.99–48.17. An unequal cut boundary above49.26left/48.37right can stay above these courses. The left upright border sits atworldX≈4.014; begin to its right at4.23. Actual aperture-head lower edge is at45.38; preserve all geometry below48.15. Existing moldings themselves are never cut.

The actionable map provides original-coordinate bases and actual world anchors. World-space cutters are preferable here to blindly reusing151's radial angle/profile:149 already baked L while the repaired head/R retain later transforms. Bake each evaluated target first, then cut in the common native-world frame, preserving/interpolating `115 Original world position` for new vertices.

A proposed rear plane follows the measured front: `Y=195.95+0.465X+0.09(Z−49.5)+offset`, usingoffset1.30 for the broad retained floor and1.66 for one short unequal deeper return. The common cut reaches above the current crest, so it cannot create a closed box. These are candidate bounds, not validated final geometry.

Thickness is NOT uniform: depth probes near the old fracture margins can be under0.3m, while adjoining broad front samples retain2–6m or more. Do not claim every crest sample has a thick slab behind it. Subtraction may remove a thin front-edge remnant while leaving the real rear mass; final source-containment/volume/opening tests and clay views are necessary.

151V3 supplies a useful method—evaluated mesh, closed exact Boolean DIFFERENCE cutters, strict crossings/closedness, source-envelope samples, inherited corner normals and original-coordinate interpolation—but its profile and radial coordinate constants should not be copied.154 uses a distinct central profile. Parent subsequently authorized an isolated prototype; mapping itself made no scene edits.
