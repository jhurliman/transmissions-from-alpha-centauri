# Broken soil ink

An independent native Grease Pencil layer over the accepted096 scene. Source contours are archived in source-contours.json, extracted from the native rejected soil intersections before filtering. No reference pixels or new heightfield are used.

The generator keeps original contour positions/visibility, subdivides in camera space, breaks cumulative sharp turns over a local window, segments long paths, and varies widths and taper. Settings live in tools/soil_ink_097.py. The archived contours make rebuilding independent of Blender backup rotation.

The soil geometry/material, primary road cracks, rocks and all096 scene ink remain unchanged. The drawings are camera-specific, like the approved intersection pass.
