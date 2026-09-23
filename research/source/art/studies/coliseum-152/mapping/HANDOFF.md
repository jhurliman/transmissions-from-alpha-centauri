# Package B: composed facade-age mapping (read-only)

Source: **150 scene and actual main-4k.png**. Nothing in that scene or its materials was edited/saved. Primary local landmark receivers were ray-tested; transparent haze/sky and unrelated scene objects were excluded from this diagnostic ray pass. No render was needed.

## Two unequal groups

**Primary — Tower7 / U7–U8 frieze / T2 band07–08:** review footprint `[1685,545,1915,765]`,230×220 native pixels, approximately108×103 at1800 display width. This deliberately reaches ABOVE the arcade ledge into the broad flat sill/frieze. Keeping the field only below the cornice would repeat the narrow-shaft failure. Connect one broad U7 field through the existing collar/ledge, then descend asymmetrically on the Tower7 front shoulder and first front spandrel. Retain the adjacent round column and arch stones unchanged.

Main original-coordinate frame:
- origin: `(-13.705214,193.174927,43.090641)`; actual ray at1791,565 on `COL110 U7 sill wall`,face15.
- across: `(0.963517,-0.267648,0)`.
- up: `(0.005480,0.019728,0.999790)`.
- front normal: `(-0.267592,-0.963315,0.020475)`.
- approximate finite composition span in this frame: across−5.8..+9.2m, up−14.4..+0.95m. These are conservative receiver bounds, not a rectangle to fill.
- Additional exact collar/shoulder/spandrel anchors and their individual bases are in the JSON. The collar ray is1719,583, `COL111 Tower7 tier2 stepped belt0`,face15. The front shoulder ray is1725,649, `COL110 Tower7 core`,face21.

**Secondary — Tower10 / U10–U11 frieze / T2 band10–11:** footprint `[2080,575,2260,750]`,180×175 native pixels. Use about half to two-thirds the primary pigment coverage/contrast and a shorter, differently terminated shoulder. The visible side return of Tower10 and protected niche remain quiet; do not darken the entire support.

Secondary original-coordinate frame:
- origin: `(14.259430,193.323029,42.735844)`; ray2160,601, `COL110 U10 sill wall`,face19.
- across: `(0.963133,0.269025,0)`.
- up: `(-0.005174,0.018522,0.999815)`.
- front normal: `(0.268975,-0.962955,0.019231)`.
- approximate span: across−7.8..+10.9m, up−13.8..+1.4m.
- Collar:2112,589, `COL111 Tower10 tier2 stepped belt1 remnant0`,face11. Shoulder:2118,685, `COL110 Tower10 core remnant0`,face12.

## Continuous native masks, not sampled triangles

`package-B-map.json` contains19 primary receiver objects and18 secondary (36 unique). Each has:
- **`exhaustive_front_class_face_ids`**: complete receiving front-face classification. Recommended shader-mask source, with continuous finite original-coordinate pigment field.
- `exhaustive_finite_region_face_ids`: same class conservatively intersected with that receiver's sampled original-space bounds plus0.65m. Optional prefilter; never use its polygon boundary as the pigment shape.
- `sampled_face_ids`: ray evidence only. **Do not use these alone as a material mask.**
- actual ray anchors, normals, materials and original-coordinate bounds.

For example, T2 band07 profile2 expands from11 sampled IDs to502 true front-class faces (305 within the finite regional prefilter). All exhaustive raw/evaluated face indices were verified to have identical vertex sequences. This is safe for face attributes on the current150 receiver meshes; revalidate after any future topology edits.

Classification rules are recorded and reproducible in `expand_faces.py`. The continuous T2 wall permits only existing `116 115 Painted masonry wall` front-facing polygons, excluding `120 Two-depth interior`, pier returns and tunnel faces. Sill fronts reject horizontal backs/undersides. Cornice classes reject existing exposed/core material assignments, retaining prior damage colors. Round columns, archivolts, platforms, drains, native ink and separate niche components are absent from the allowlist.

Tower protection: use each tower's supplied front anchor/normal, `normal dot >0.96`, and per-shading-point signed depth **−0.08..+0.06m**. Measured deep niche backs are about−0.18m on Tower7 and−0.20m on Tower10. Keep the point-depth gate even with the complete face set; it prevents a partly sloping face from carrying pigment into the recess. Do not use a single global plane-depth test across the curved arcade: each bay has a different front plane. The face class plus finite field and object allowlist supplies that protection.

## Coverage / reference reading

Primary has1243 landmark-hit samples and604 eligible front-masonry samples on the6px grid; secondary869 and269. Many remaining hits are intentionally protected tunnel/arch/collar undersides, not more paintable wall. Sky holes receive no field. Aim to affect only25–40% of eligible lit masonry, leaving at least60% quiet, with the original deepest shadows untouched. A continuous organization can span the entire group without coating all of it.

UCL-01 (user-created ChatGPT Images2.5 original) shows age grouped around real collar/ledge transitions with unequal descents, broad quiet facing areas and preserved dark cavities. UCL-02 supplies a closer view of stronger localized losses; its limited resolution does not justify inventing dense tiny texture. DP-03 (Darius Puia/BakaArts) supports the hierarchy of coherent medium-scale surface groups against quiet structural planes, not transplanting its robot/composition. Reference overviews and crops are stored here with source IDs in the mapping JSON.

`primary/secondary-receiver-map-3x.png` visualize evidence points and numbered anchors on current150 beauty. They are technical annotations, not candidate weathering. No visual-quality score or approval is implied by this mapping.
