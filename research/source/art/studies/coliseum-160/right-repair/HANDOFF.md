# 160 U15R return reconstruction — held

The bounded return-only repair cannot satisfy exact front/back preservation and zero crossings simultaneously. No source geometry was edited and no candidate mesh was saved or rendered. U10L remains frozen.

After removing the cap and upper angular-end returns, the protected surfaces retain **14 strict float64 crossings** and two degree-four boundary vertices. The fronts themselves fold: face793 crosses5403/5402/5401/1914; related face pairs are recorded in strip-candidate-audit.json. Front branch vertex366 is at authored(r74.99905,a−0.3577419,z69.76650); rear branch341 is at(r66.99955,a−0.3559883,z69.74308). These are not removable interior-return faces.

The clean111 source has46 vertices/27 faces with an uneven stepped crown and nearly coincident pairs14/43 and15/42 at its high right corner. Later subdivision has produced overlapping skin fans around that corner. A new cap cannot cure intersections entirely within retained skin.

A usable next repair scope is a narrowly bounded reconstruction of the two documented corner fans, preserving their lower seam and outer source silhouette, followed by the ruled return. It must explicitly permit changing those protected skin triangles and be checked for camera silhouette, original material coordinates and custom normals. No arbitrary tolerance increase or global remesh is warranted.

This report stops at that concrete constraint. The full target currently has1397 robust crossing pairs; it is not clean.
