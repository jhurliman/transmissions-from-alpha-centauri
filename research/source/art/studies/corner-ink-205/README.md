# Corner ink regression — 205

The final203 check caught a lower wall course extending across the nearer building return. CPU camera rays prove the native panel edges sit roughly0.5–0.9m behind that opaque return. The pre-correction native stroke capture confirms three contributing source meshes:145 Panel01 top loss, its folded bottom, and198 Architecture | layout_access.008 Folded sheet face.034.

The separate205 guard preserves192 and earlier guards. It tests native stroke endpoints and midpoint against the actual Building side return.002 BVH and suppresses only portions hidden by more than0.02m. It adds interpolation only where a source stroke already has proven hidden samples. No geometry, material, camera, composition, line width or raster image is changed.

The actual guarded native crop restores the clean corner, preserving the visible course and weathering. Capture showed371hidden segments across the three contributor meshes. One initially considered candidate produced zero affected native segments and was removed from the final guard set without changing the proof result.

API: tools/architecture_ink_visibility_205.py apply(scene, embed=True, audit_path=None). Apply after the inherited149/156/161/192guards. Full-scene render and saved-state preservation remain root responsibilities.
