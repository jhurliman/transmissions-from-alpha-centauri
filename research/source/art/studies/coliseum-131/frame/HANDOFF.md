# Tower10 upper frame extension

`tools/coliseum_frame_extension_131.py::apply(C)` adds three native closed meshes to the existing landmark collection. It preserves all existing rods, masonry and materials. New pieces reuse the accepted armature steel materials.

Two unequal upright continuations start at the exact center of existing upright0 and upright2 terminal rings. A kinked top tie joins both continuations and penetrates the actual Tower10 core side by0.22m, with its contact0.36 authored metres below the surviving core top. This gives a higher connected frame without increasing the intact masonry silhouette.

`audit.json` records actual world points, attachment owner, embed depth and closed-manifold/positive-volume checks. Adjacent metal pieces intentionally intersect at joined centers; they are separate editable solids, not a Boolean-unioned mesh. The proof is a locked-camera4K-resolution crop at [2040,355,2180,575]. Existing foreground and landmark ink are not regenerated for this bounded proof; root must rebuild new landmark ink during integration.

Only new objects are changed. Source130 remains untouched; geometry.blend is a separate proof scene. This is a geometry delivery, not final user acceptance or a95 score.
