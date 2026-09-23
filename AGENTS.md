# Repository instructions

## Current scope

Transmissions from Alpha Centauri is a completed Blender illustration. The creator approved study 258 as v1.0.0 on 2026-09-21. It is not a playable game, an SCI patch, or a Space Quest integration. There is no active scene-refinement backlog.

Read README.md first, then docs/release/REPRODUCING.md and docs/release/PROVENANCE.md. Preserve the user's README wording and edits; make targeted corrections rather than replacing it wholesale.

## Preserve the approved artwork

- Treat releases/v1.0.0/scene.blend, main-4k.png, runtime, and evidence as frozen. Do not change geometry, lighting, materials, characters, fog, framing, or ink without a new user request.
- The supported entry point is releases/v1.0.0/render.py. Opening the scene alone does not restore every render-time ink callback.
- Use the pinned Blender build and a new output directory. Never overwrite the source scene or authoritative PNG while testing.
- Visual changes belong in a new version. Do not move the v1.0.0 tag or replace published release assets.
- User approval is authoritative. Historical study scores and pending flags are not current instructions.

## Verification and documentation

Run `python3 tools/release/verify.py` after changes. The manifest includes documentation as well as artwork; on the development branch, refresh only the hashes of intentionally changed documentation/tooling. Do not silently bless changed scene, image, runtime, or evidence bytes. Published tags and archives retain their original manifests.

A documentation-only change needs checksum and link checks, not a full render. Rendering changes need an actual full-frame comparison; --check-only cannot validate render-time callbacks or the finished picture. Never promise bit-identical output across future GPUs or Blender versions.

## Public/private boundary

.gitignore is an explicit release allowlist. Keep private/, references/, archives/, and the local research workspace excluded unless the user explicitly approves a reviewed publication set. Never package the project root wholesale or use blanket force-add commands.

Private work includes personal photographs, purchased game data, correspondence, social-video work and commercial music. Historical study folders may contain third-party references: a numbered experiment is not proof of ownership or redistribution rights. Preserve historical work locally; do not delete it as housekeeping.

Project-authored software is GPL-3.0-or-later; artwork, scene data and documentation are CC-BY-SA-4.0. Consult LICENSE for scope and exclusions. Preserve third-party notices. Do not apply project licensing to reference collections or commercial music.

## Future art work, when requested

Preserve editable native environment geometry and materials. Do not replace geometry with a projected reference painting. The approved pixel-art characters and native-derived cloud/soil assets are intentional exceptions to an entirely geometric scene. Keep the exact character art unless asked to change it.

The curated historical code is in research/source; run `python3 research/verify.py` when changing that archive and update its explicit manifest only for intentional changes. Never bulk-execute historical scripts: some overwrite inputs and require missing scenes. Historical iteration tools, review pages and performance experiments are not the supported rendering interface. See docs/release/ARCHIVING.md for the research-archive assessment and preservation plan.
