#156 native foreground visibility correction — frozen

Use `tools/coliseum_foreground_visibility_156.py::apply(scene, embed=True)` alongside149 guard. Exact implementation is embedded into the saved scene, with no runtime repository imports. Corrected local source: guarded.blend; actual full native proof: guarded.png. No canonical scene changed.

Five named source/receiver pairs are checked in world space. Three samples (start/mid/end) must all be more than0.02m behind the actual receiver before a segment is hidden. There is no screen mask, cached artwork, line-width adjustment or substitute projected stroke.

145 of351 sampled segments are hidden. Left joist leakage, right girder/joist leakage and slab silhouette leaking through the lower-left plinth are removed. Actual visible fascia boundaries remain. The apparent crack is not an authored crack: exact captured source is091 bank slab.036,0.03–0.44m behindGround plinth.002. Do not restore it.

Guarded versus156 changes2771 outside-landmark pixels over4RGB because geometrically hidden chains extend beyond the original three tiny diagnostic crops. This is an intentional native visibility correction, not a claim of exact152raster preservation. Three-panel comparison crops and wider before/after views are included. The source geometry, material graphs, camera/lighting and all line styles remain untouched.

Final root integration should call both guards after scene load and retain both embedded scripts. Refresh source/native delivery manifest as needed; kit geometry is unchanged. Final integrated fullrender/fresh-reopen check is still required. Existing global Freestyle numerical warnings and inherited mesh defects are not silently declared resolved.

## Final component and preservation review

All13 meaningful outside-difference components are saved individually and in guarded-contactsheet-1/2.png, and inspected. No clear valid boundary removal was found. Captured hidden chains account for the intended line corrections. Source fingerprints match all20,490objects and all materialgraphs exactly.

Pixel equality is not claimed:161 landmark pixels exceed4RGB (max21). A separate metallic door-frame speckle region has617 pixels over4 (max31), without visible contour removal. Smaller residual edge/shading variations are also recorded. The exact renderer cause remains unproven; read-only diagnostic had matched original156 there. Promote the native visibility correction only with this raster caveat clearly retained and root inspection of the supplied components.
