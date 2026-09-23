# Reproducing v1.0.0

## What is preserved

The approved state is scene iteration 258, frozen at `releases/v1.0.0/scene.blend`. Its 17 file-backed image datablocks are packed: native-derived cloud layers, authored soil pigment, selected character sprites, and their placement canvases. There are no linked Blender libraries or external fonts. Packed image paths were changed to relative `//packed/` labels; the packed bytes are the source, so those paths need not exist. Embedded script autorun is disabled in the release.

`render.py` explicitly opens that file, imports the nine preserved runtime modules, reinstalls the native visibility/ink rules, and renders the whole frame. It never regenerates the scene, calls an AI service, reads purchased-game assets, or saves over the release. The original iterative generation scripts are not needed to render this checkpoint. This is frozen-state reproducibility, not a claim that all 258 design iterations can be regenerated from a seed.

## Pinned environment

- Blender **5.2.1 LTS**, build **9e2066aef7ef**, built 2026-08-25 01:35:57.
- Original tested host: macOS 26.5, Apple M2 Max, 12 CPU cores, 38 GPU cores, 32 GB RAM.
- Blender-bundled Python 3.13.13; EEVEE, Metal on the tested host, native Freestyle, compositor enabled.
- 3840 × 2885, 100%, 64 EEVEE samples, 1024 shadow pool, dither 0, all three view layers enabled, full frame (no render border), native ink culling retained.
- Full settings, node graphs, fonts/material data, view transforms, camera and light values live in the `.blend`; do not reset factory render settings after opening it.

The launcher refuses a different Blender build unless `--allow-different-build` is supplied. That option is a migration experiment, not evidence of compatibility. Cross-OS, future Blender and future GPU rendering have not been validated. Freestyle uses Blender's internal `parameter_editor` API and exact scene object names, so automatic version upgrades are unsafe.

## From Git

1. Install Git and Git LFS. Clone the repository and run `git lfs pull`. A normal Git source ZIP or Git bundle may contain only a small LFS pointer instead of the 238 MiB scene; it is not a complete backup.
2. With system Python 3.9+, run `python3 tools/release/verify.py` from the checkout. It checks every file listed in the manifest, including the scene, runtime and authoritative image, and fails on missing or changed bytes.
3. Run the command in the root README with the pinned Blender. The output directory must be new. You may launch from a different working directory if you use the absolute path to `render.py`.
4. The output includes `main-4k.png`, `run.json`, and native ink audit files. The frozen release remains unchanged.

`--check-only` loads the scene, checks image packing, and installs the early runtime rules without rendering. It cannot test render-time callbacks, GPU compilation, Freestyle or final composition. A real full render is the meaningful test.

The complete release ZIP is the alternative to Git LFS. Extract it and run the same verification/render commands. It includes the real scene bytes, not an LFS pointer. Do not unzip over the only copy of an edited project.

## Exact recovery versus re-rendering

For the **exact approved output**, use the archived `main-4k.png` and verify its SHA-256. This is independent of Blender availability. For editable reconstruction, use the packed scene and pinned application. GPU sampling, shader compiler and driver differences can change a few pixel values even between repeat renders; bit-identical future re-rendering is not promised. Preserve the PNG as the visual authority rather than changing the art to chase a hash.

The `evidence/approved-detail.png` is the original user-reviewed 258 close-up. Historical metadata in `evidence/` retains original source paths and approval fields from earlier studies; those are provenance records, not additional render dependencies or current approval status. The release manifest records final user approval.

## Offline recovery and long-term backup

A local `archives/v1.0.0/` preservation set contains an allowlisted project ZIP with real LFS data, a Git-history bundle, and a ZIP of the exact macOS Blender application. Checksums accompany the set. These large local backups are intentionally outside Git. The application includes its bundled Python/scripts/color configuration; it does not preserve macOS or the GPU driver and cannot guarantee that a future Mac will run it.

Keep copies of the preservation set on independent storage and off-site. GitHub is useful replication, but Git LFS objects and release assets must remain available and are separate from Git commit history. The public v1.0.0 GitHub release now hosts the project ZIP, exact Blender application, checksums and Git-history bundle. Prefer the `-licensed.zip` project asset, which also includes the finalized license notices. These assets do not include the complete research workspace; see [ARCHIVING.md](ARCHIVING.md). A local archive on the same disk is not disaster recovery.

For future migration, preserve v1 unchanged; create a new version, use `--allow-different-build`, compare the complete image and detail crops, and record the new application/hardware and observed differences.
