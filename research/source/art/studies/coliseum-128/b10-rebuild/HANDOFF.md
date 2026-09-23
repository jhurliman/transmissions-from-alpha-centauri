# Isolated B10 foundation repair

The clean111 B10 arch has the original connected spall. The accepted113 shoulder cavity is replayed on that clean source before the115E/116yaw transforms; unrestricted112 displacement is omitted. The existing127 seam builder then reconstructs the joined tier. No voxel remesh is used.

`tools/coliseum_b10_prepared_128.py::apply(C)` loads only the prepared T2 mesh into an authoritative127 scene, preserving its material datablocks and layout modifier. Run B7 damage after this operation. The source rebuild is `tools/coliseum_b10_rebuild_128.py`. Do not use the abandoned `b10-repair/geometry.blend`, which has open interfaces.

Validation: inherited57 strict crossings become0; nonmanifold edges remain0. Outside the B10 angular sector,2136/2150 vertices retain exact coordinates; maximum remaining point-to-surface deviation is0.000077m. Tier volume18419.184→18445.257 (0.142% increase). This is not an exact shape-preserving topology-only change inside B10: it removes the problematic fine displacement while restoring the earlier approved broad cavity. Camera proof decides acceptability.

Known scope: damagedB10 still retains its earlier opening proportions, as in authoritative127. This repair does not silently resize it to the53 other arches. Other architecture and user material/lighting direction are outside scope.

Final prepared module maps source roles through the127 slot layout and retains the live128 (or later) material datablocks in those slots. Tested directly against128/scene.blend: `live_material_slots_preserved: true`. Unknown material layouts fail explicitly rather than reverting to old materials.

At the actual4K camera,64 pixels exceed8RGB change in the204×176 local crop, confined to the damaged shoulder. The painted close crop retains the broad aperture and cornice shape; the removed fine folded wall fragments are a local cleanup. This is a foundation repair, not a new high-frequency destruction treatment.
