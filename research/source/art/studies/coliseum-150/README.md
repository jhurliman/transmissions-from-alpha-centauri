# Coliseum 150 — uneven support weathering

Two distinct native pigment fields connect the main tower collars to the shafts. The primary field has a broad asymmetric upper shoulder, a protected recessed niche and a quieter fading tail. The secondary field remains smaller and weaker. V1 was held because it merely strengthened an existing vertical stripe; V2 passed the independent local gate. Full-scene assessment remains separate.

Source:149 current geometry and materials, including147's3× bottom splatter and longer fading alley rust. Native preservation checks20490 scene/instance objects: only12 selected landmark objects receive four private materials; all geometry, normals, camera, lights, transforms and prior material graphs remain unchanged.

The full scene also fixes149's confirmed hidden-edge Freestyle leak on the foreground fascia. A native geometric visibility callback considers only the two identified flange/joist shapes and tests their segments against the actual evaluated opaque fascia. It never masks image pixels or excludes entire structural objects. Existing line widths and exposed lines remain unchanged.

For reproducible rendering, use tools/coliseum_integration_150.py with the render argument. The standalone blend contains self-contained text149 Native fascia visibility guard.py: enable trusted script execution for this authored scene, or run that embedded text before rendering. No global Blender security setting is changed by the project. The companion colosseum kit does not need the foreground-only callback.

Local proofs, mapping, preservation checks and full-frame comparison artifacts are kept beside the editable scene and kit. This is a working candidate, not user approval or an all-axes95 claim.

Full4K rendered in116.05seconds and independently retained. Scores remain95/95/91/92/93/94: local support aging is useful but too modest to justify whole-axis gains. The native visibility fix hid12 proven occluded segments in the full frame. All165 outside-landmark changed pixels were grouped and inspected:120 are in the main correction region,7 at the adjacent fascia tip,38 in small existing outlines elsewhere. No new disconnected stroke was found. These are visual observations, not a bit-identical raster preservation claim.
