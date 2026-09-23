# Spacesuit character study214

Traveler-A and Traveler-B in three separate illustrated treatments: reference-scale pixels, double-detail pixels, and scene-lit anime. Review `prototype/review-214.html`.

The user created the supplied spacesuit images by modifying their photographs with ChatGPT Images2.5. Intact originals are retained privately in `private/character-sources/`; they are excluded from the asset download. Four new treatments were authored with the built-in image generator, one pixel master and one anime illustration per person. All actual prompts and generated masters are retained.

Pixel exports use49/47-pixel body heights and98/94-pixel body heights,16/24-color budgets, a transparent index, binary alpha, and no dithering. Use1.2-times-tall display pixels for DOS proportions. Exports include the exact used color counts and RGB palettes. Traveler-A's yellow sleeve badge and Traveler-B's sampled sage hair colors have reserved palette entries; no accents from the earlier casual-clothes study are introduced. Shapes simplify naturally at the smaller resolution; the yellow badge is a color accent rather than legible insignia at49pixels.

The two pixel comparisons use integer nearest-neighbor scaling and identical foot anchors on the verified clean209 background from206. Anime uses the same height assumptions,1.72m and1.65m. It is rendered on native flat cards with the actual saved scene camera and lights, then alpha-composited over that same background. The source206 and integrated environment files are unchanged.

This is a static rear-view art study. It does not implement animation, a rig, collision, per-limb normals, character contact shadows or editable3D character geometry. Actual native light response is measured in `anime/lighting-response-audit.json`; fixed illustrated shading remains part of the artwork. Artist/user approval remains pending.

The ZIP contains only an explicit asset/documentation allowlist: indexed sprites and previews, authored generated masters and prompts, selected anime assets, scene comparisons, native card-only proof, and audits. No private photos, downloaded reference artwork, or entire project archive is included.
