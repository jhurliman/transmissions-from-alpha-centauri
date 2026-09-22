# Art development rules

Use this directory as the canonical project root. Keep purchased games and publisher extras in private/; reference collections in references/. Neither belongs in a release or public repository. Build releases from an explicit allowlist, never by zipping the project root.

Before every visual change, select 3–5 reference IDs from references/manifest.json across at least two sources. Write the specific visual property being studied; do not copy a composition, character, vehicle or distinctive setting. Preserve creator credits and source links. Reference images are not licensed game assets.

Record the iteration in config/ with hypothesis, changed variables, fixed camera/layout, and review criteria. Use tools/render_iteration.py or an equivalent versioned Blender scene. Compare the baseline, candidate, reference crops/full frames, grayscale readability and interaction anchors. Inspect actual renders. Record observations and next change in the iteration review.json. An agent's visual inspection is not user approval; only mark approved after the user's decision. Keep prior renders. Drafts may be 1280x720; approved production assets target the explicitly recorded aspect and 4K output.

Space Quest IV experiments must retain logical coordinates, timing, pivots, collision and priority behavior. Do not equate the current original-room web prototype with a working SCI patch. Preserve the original-IP fallback in reusable original scenes, rigs and systems.

## Geometry-only acceptance (user correction)

The 80+ creator–critic threshold applies ONLY to actual editable geometry and materials rendered without any projected full-frame image, camera-dependent paint layer, composited finished artwork or baked character. Painted studies may be displayed as comparison targets but cannot satisfy a scoring axis. Keep them disabled during review. Record honest scores and remaining gaps; do not substitute a change of medium for closing geometry gaps.

## Component-first architecture (user direction)

Develop one architectural family at a time, beginning with pipes. Enlarge and inventory reference features; distinguish visible evidence from inferred construction. Build reusable clean component masters with explicit connection rules, then assemble them into larger structures. Review the isolated family before wholesale scene replacement. Keep authored unique details and optional procedural weathering/damage/decay as separate layers over the clean kit. Preserve accepted scene scale while studying components.

## Service endpoints and dramatic scale (user direction)

Every new pipe route must declare destinations for both ends. Prefer a 90-degree wall entry with a fitted collar, or a connection into a projecting architectural receiver. Use deliberate end caps occasionally. Vents may be functional terminals. Do not leave exposed open spools as accidental endpoints. Fit elbows, collars and mounting brackets to the actual local facade plane, including its inset, slope and ground cladding.

Choose service scale at the game camera, not only in isolated catalogues. Use strongly contrasting primary, companion and fine-service sizes. Large distant trunks and ducts should remain visually substantial and convey the size of the architecture. Preserve the accepted camera and depth; generate dimensioned larger masters instead of stretching finished instances. Stagger route positions so a large primary does not erase its smaller companions in projection.

For published infrastructure-scale comparison, use `references/darius-puia/DP-08-layered-infrastructure.jpg` as the primary BakaArts reference. Keep previous reference provenance intact. Preview geometry with PBR materials and readable lighting; defer flat/toon shading. Rectangular duct collars should share the duct body color or differ only subtly, rather than creating a high-contrast repeated stripe pattern.

## Approved pipes

The user approved pipe geometry at iteration 031 ("pipe geometry is a+ done"). Preserve those service assemblies while refining buildings unless explicitly requested otherwise. This approval does not apply to the whole scene.

## Right-side geometry checkpoint

At iteration 036 the user accepted the right-side geometry as pretty good conditional on removal of the complete rear-right pipe at y=23. That route, roof return, supports and flashing are removed. Preserve the remaining right-side geometry during look development.

## Distinct service weathering

User correction at 043: do not apply the facade blue/brown flaking pattern to pipes or ducts. Keep a separate metal-weathering treatment (joint corrosion, runoff, abrasion) for services. Use large predominantly warm facade regions as counterpoints; avoid splotched-blue coating on every building surface.

## Surface-interior texture reference (user correction, after 055)

Use the linked UP-01/UP-02/UP-03 set in `references/user-pipe-surface-study/` for surface-treatment reviews, especially UP-03. The dominant remaining gap is connected multi-scale tonal texture across flat and rounded surface interiors, not just edge/corner wear or sparse speckles. Include interior-only panel and pipe crops in critic reviews, and evaluate medium-scale coverage and highlight integration separately from geometry/edge detail. See the set README for the proposed native material proof. These illustrative studies are references, not acceptable native output.

## Camera-scale texture correction after 057
User retains 057 on round PIP services and small rectangular DUCT services only. Remove its uniform tonal noise from other surfaces. Wall treatment must be larger, sparser, less repetitive, palette-color variation rather than only darkening, and preferentially located near geometry edges/corners with quieter flat interiors. Judge at the alley camera first.

## Alleyway buildings approved at 074
The user approved the alleyway buildings at iteration 074. Preserve their geometry, palettes, service routes and weathering while developing the remaining scene. Reflections stay disabled. The canonical remaining-work backlog is `docs/art-direction/remaining-scene-roadmap.md`; update it as work progresses. The big landmark is deliberately last, with an original coliseum-inspired direction. User authorizes independent subagent studies to accelerate review, with separate outputs and primary-agent integration.

## Cloud flattening and soil relief direction (user correction after 080)
The user targets approximately 95/100 visual fidelity for clouds, beyond the earlier 80-point procedural checkpoints. Judge billowy volume, wispy-to-bulbous silhouette hierarchy, selective broad shadow strokes, and composed cloud groups against UC-01/UC-02. The user endorses 3D metaball/ellipsoid cloud masters followed by flattening into 2D with larger contiguous color strokes. Native-source derived cloud layers are expressly allowed for this pipeline; preserve editable 3D sources and never project reference artwork.

Soil now has a relief-driven alternative: coherent microgrit/clods, subtle finite ridges, and accumulation mounds drive lighting mapped into the measured brown palette. Preserve 081 pigment-only variants for comparison. Ground crack highlight lips must be clipped by every intersecting crack void, with no highlights spanning missing surface. Rocks remain a separate pass.

## Sky locked and ground priority (user after084)
Sky084 is user-approved90/100. Preserve layout, colors and cloud assets while refining ground. User rates ground about60. Broad flat homogeneous brown expanses are the largest gap; crack work is secondary. Preserve acceptable fine soil grain, add reference-grounded intermediate-scale surface character, clustered grit and shallow gathered/compacted forms. Road structural break axes must be straight with irregular chipped edges rather than wandering centerlines. Cracks need interrupted light/shadow fragments and trapped pebbles.

## Ground geometry-first direction after 087
User selects C relative macro relief, but wants its mean elevation lowered to A's. C is subtler because lows are filled; avoid calling A gentler. Hide the separate road rock/grain layer during terrain development. Focus on native untextured heightfield geometry first: packed soil, embedded aggregate, compaction, broad shallow rises and hollows. Do not attempt to hide weak geometry with stylization. Preserve this as a separate editable study until geometry is convincing.

## Soil geometry accepted after 088
User accepts the 088 packed-soil geometry study as ready for integration. Integrate the accepted heightfield character while retaining C relative macro relief and A mean road elevation. Keep the previously hidden separate rock layer off until its own tuning pass. Do not restart morphology development merely because an agent score was below a target; user approval governs.

## Soil locked; rocks next after 089
User accepts soil geometry and requests rocks/debris shaped from close reference inspection. Avoid cube-like scatter. Prioritize unequal broad fracture faces, low partially buried road wedges and elongated inclined foundation slabs, then geometry-aware placement. Defer final ground color/paint treatment until rock geometry is settled.

## Road rocks approved after091
User locks small road rocks: preserve their geometry, positions and materials. Foundation rock shapes are good but must rest with physically plausible broad ground contact, not arbitrary buried tilts. Soil geometry remains approved; develop painted surface treatment without regenerating heightmap.

## Soil brushwork direction after092
User selects B stronger brushwork as the right direction. Preserve this broad pigment treatment while comparing additional high-frequency painted flecks/sponge texture. Do not return to uniform rendered micro-bump shading.

## Soil surface locked after094
User selects094C as final soil treatment. Preserve its full pigment density, broad brushwork, geometry and rocks. Next study is missing linework at intersections: outlines should include visible boundaries where soil meets footings and where separate components penetrate each other, without outlining hidden geometry.

## Additional ink approved after095
User approves all additional ink and requests full rollout: visible geometry-intersection ink, small rubble contact ink, and geometric crack-boundary ink. Preserve approved widths and occlusion. Material-only pigment flecks remain as in the approved study.

## Dark road locked after097
User approves refined097 soil ink and locks the dark soil road. Preserve its terrain, palette, pigment and ink, plus approved road stones. Foundation rocks should accumulate against actual buildings with diffuse smaller fragments across light soil, rather than lining the soil transition.

## Foundation placement locked after099
User approves099 foundation rock placement. Preserve rocks and dark road. Distant city must form two coherent sides of a continuing street, tapering through perspective; no towers in the roadway. Landmark redesign follows next.

## Distant city layout selected after101
User selects101A original pixel-art layout. Preserve its massing and base colors. Remove tiny repeated window grids; distant facades should be mostly smooth with a few painted details and selective specular use. Rubble-skyscraper destruction remains a future pass.

## Distant city checkpoint after103
User accepts102 facade direction and calls this section done after removing the entire single-story foreground row and relocating the rear brown left tower to pale ground on the right.103 applies those edits:13 short masses hidden; L06 translated to x9.5 at unchanged depth. Preserve this distant-city placement and quiet painted material treatment. Landmark redesign is next; rubble-skyscraper destruction remains future work.

## Scrap lighting palette direction during104
The near scrap warm-rust versus steel-blue division must follow lighting: illuminated faces warm, less-lit faces darker steel blue. Do not drive the main split with random rust coating patches. Weathering is subordinate fine detail; retain selective physically light-responsive highlights with irregular worn interruptions.

## Scrap hue response approved after104
User calls the104 lighting-driven blue-to-rust response perfect. Preserve the hue/light mapping while tuning brightness and contrast toward the darker reference.

## City placement accepted after106
User accepts106 city placement. Preserve the corrected deep right-side pair and outer-front additions. Keep original1x light facade strokes; compare only dark-stroke density at2x/4x/8x to avoid an illuminated thriving-city appearance. Density choice remains pending107 review.

## Far buildings locked at108
User explicitly selects107C (8x dark strokes with1x light strokes), requests a left-side depth extension, then locks far buildings.108 adds four left rear masses to depth174, slightly beyond right rear brown depth156. Preserve108 city geometry, layout, materials and brush density. Canonical integrated scene: art/studies/city-108/scene.blend. Landmark redesign remains separate future work.

## Coliseum direction after109
User selects A reference framing, removes rear wall/half, and requests reference-fitted looming tilt. Screen evidence suggests converging tower verticals and asymmetric cornice curvature rather than uniform sideways roll. Proceed through detailed kit, materials, weathering and final integration; final centerpiece approval remains with user. Preserve all locked nonlandmark systems.

## Coliseum structure accepted after115
User accepts115E overall structure and positioning, with a requested approximately4degree whole-landmark rotation so center arches are not dead-on. Preserve E curved frontage, bay density, balanced arch depth, open rear and accepted low orange haze gradient. Proceed with finer painted surface/light detail. Final integrated centerpiece acceptance remains separate.

## Original coliseum artwork provenance (user clarification)
UCL-01 was created by the project creator using ChatGPT Images 2.5. Treat it as original project artwork, with master art/original/coliseum/coliseum.png and provenance in art/original/manifest.json. Its reference copy and known detail crops retain the same authorship. Do not relabel it as unknown third-party art or apply blanket external-reference asset restrictions to it. Other sources keep their existing credits. The current coliseum build remains a native geometry/material interpretation.

## Selected characters, landmark scale and alley direction after 214
The user selected the double-detail pixel spacesuit sprites for Airam and Miranda from214 and wants both carried into subsequent scene renders. These expressly requested2D character assets are separate from native environment geometry acceptance. The user selected210's70%sky-fill Colosseum scale. Repeated alley architecture is the accepted replacement direction for the old distant city, superseding108's city lock;212's tall repeated layout is rejected because it obscures too much of the landmark. Develop shorter varied component assemblies and placements preserving21070's visible landmark opening. Compare the original sun against a one-apparent-diameter shift right; that sun selection remains pending.

## Descending ground arcade tunnels — user direction after 218

Replace the two sideways tunnels with an arch-shaped tunnel at every first-level opening. Each runs 30 m straight inward, then 30 m along a 45-degree downward slope. Preserve the facade openings and use actual world metres at the selected landmark scale. Study 220 implements all 18 openings; keep this direction in subsequent scenes.

## Ground-floor and atmosphere directions after 220

The user requests stronger haze opacity with orange near the ground grading toward pale warm orange above. Keep nearest facades clear. Extend the native facade kit with a closed garage bay on the blue right frontage and a recessed pedestrian passage with an iron gate set back inside. Preserve existing supports and services when fitting the openings.

Dust stones sitting in pale foundation soil with roughly half-strength matching soil color while retaining each stone's palette and variation. Replace the brown right-side alley floor plate with continuous pale soil and a sparse scatter of small stones resembling the mid-left bank; preserve the main dark street.

Remove bottom sill walls/platforms only from the first-level arcade openings, retaining those on levels two and three. Lower the connected tunnel entry floors to the exposed structural foundation so no former platform-height step remains. The continuous building foundation is preserved; this does not request a street-to-foundation ramp.

## Far-building height and narrowing correction — 226

Follow the user markup retained at `art/studies/far-building-layout-226/reference/user-markup.png`: increase the stepped building heights at the magenta marks, move the furthest building footprints inward to the green boundaries, and allow left pipes to project farther into the road. Additional first-level Colosseum occlusion is intentional and supersedes215's strict retention of21070 exposure. Preserve the selected landmark scale and near facade assemblies.

## Entrance finish and Colosseum approach — 227/228

The user accepts the225 ground-floor geometry and requests facade-matched weathered surrounds, pronounced wear on the metal garage door, and rust on the iron gate. Increase existing foundation-stone dust by50% relative to the223 deposit strength while preserving individual stone variation. Add five broad curved steps connecting existing street soil to the Colosseum foundation; keep first-level openings unobstructed. These are requested directions, not approval of a subsequent render.

## Garage acceptance and passage correction — 229

User accepts228 garage. Preserve it. The228 entryway surround blue-upper/red-lower split is rejected; use a continuous warm plaster palette retaining weathering.


## Midground and arcade refinements — 230–232

User requests plausible varied alley building instances, regularly spaced window groups of two or three, two distinct believable broken panes, full-size pipe connections and fewer projecting C routes. Roof condensers should be 75% of original height with varied supported ducts and pipes. Keep broken-wall weathering heavy and the large left ruin outlined. Upper arcade pyramids retain height but use two-thirds base dimensions; suppress ink only on first-level wraparound arch ornaments through fog. Continue crown cracks through covering trim and physically fracture three upper arches with unequal severity. These are requested directions, not approval of232.


## Far tower weathering accepted — 234

User says the two far towers look great and far better than the crumbling walls in front. Preserve234 far-building geometry, windows, stain palettes and damage while improving the133 broken transition walls to comparable fidelity. Scene-scale construction detail and readable damage matter more than tiny surface marks.


## Sun placement final — after237

User explicitly selects the currently placed sun as final. Preserve237sun position, partially behind the right Colosseum pillar. The218one-diameter-right alternative is no longer an open choice.


## Scene-light alignment —239 user direction

User requests aligning actual scene lighting to the final visible sun. This supersedes prior directional-light preservation for239. Preserve visible sun position and exact selected character sprite art; add grounding shadows and improve broad road pigment/texture hierarchy.


## Hybrid lighting and road correction —240

User prefers239Colosseum/newSUNlighting but requests previousSUNlighting on nearjunk and allstones, slightmiddlepilelift, morefogvariance ratherthanuniformdensity/whitewash, and leftbluepalette restored withoutundoingnewSUNdirection. Userrejects239roadsmearing:restoreoriginaltexture. Future roadpasses mustlayertexture overexistingpattern, neveraverage/blur/replace it.


## Complete scene approved — v1.0.0

On 2026-09-21 the user approved the complete iteration258 scene as v1.0. Preserve the frozen release without further visual changes. The supported portable render entry point is releases/v1.0.0/render.py; see docs/release/REPRODUCING.md. This approval completes the illustration, not a playable game or SCI integration. Subsequent changes belong in a new release.
