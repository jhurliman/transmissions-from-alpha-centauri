> Historical development record. Current approved v1 artwork and reproduction instructions are in the root README and `docs/release/`. This record does not describe the current deliverable.

# Project brief

## Agreed direction

- Primary target: Space Quest IV: Roger Wilco and the Time Rippers, DOS CD-ROM edition.
- Proposed release: completely free and noncommercial, with no fundraising, donations, Patreon links, advertising, or paid access.
- Preserve contrasting visual treatments across eras and their associated visual humor.
- Base artwork on editable original Blender scenes.
- Public Space Quest-specific release is conditional on suitable written permission.
- If permission is unavailable, pivot to an original point-and-click IP using the original artwork, visual language, tools, and gameplay systems.
- User is based in Oakland, California, US.

## Initial milestone — completed foundation

An invented orbital maintenance bay, authored in Blender, rendered in two treatments at 4K. A local browser prototype tests four interactive objects and one repair sequence. Geometry, images, dialogue, and puzzle are original to this project.

## Next milestones

1. Review the visual study with the user. Establish desired camera perspective, richness, atmospheric depth, and the strength of contrast between treatments before detailed art production.
2. Produce a polished original room: layered set dressing, wear, distant scenery, meaningful silhouette, and a neutral original player-scale reference. Keep important puzzle shapes legible.
3. Add walking, walkable regions, occlusion, cursor verbs, and a small inventory test. Choose a production engine after testing the requirements rather than treating this browser harness as a final engine decision.
4. Evaluate authorized original-game integration separately: exact purchased edition, license, rendering hooks, coordinate mapping, aspect ratio, original audio behavior, and permitted patch packaging. No such compatibility is currently demonstrated.
5. If permission arrives, adapt the approved pipeline within its terms. If unavailable, develop an original protagonist, premise, locations, dialogue, and puzzle chain; changing names alone is not the fallback plan.

## Architecture boundary

Keep core scene descriptions, interaction logic, camera data, render presets, and original assets independent of Space Quest. Any future game-specific room mappings and integration belong in a separate adapter. The present prototype deliberately has no original-game dependencies.

## Scope limits

This project start does not include a completed remake, approved final art style, licensed BakaArts artwork, or an authorized Space Quest adaptation. The first room is a pipeline and readability study.
