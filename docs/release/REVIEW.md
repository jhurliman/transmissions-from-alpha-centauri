# v1.0.0 code and project review

Review date: 2026-09-21. Scope: approved 258 scene, native rendering dependencies, Git/backup status, documentation, clean-checkout reproduction. Independent code and project reviewers examined the existing pipeline; the code reviewer also checked the new portable launcher. This is not an exhaustive audit of every experimental script in the 104 GB art workspace.

## Findings and resolutions

| Priority | Finding | Resolution / remaining limit |
| --- | --- | --- |
| P1 | Project was not a Git repository. No matching `jhurliman/transmissions-from-alpha-centauri` GitHub repository was found, nor a matching name in the account listing. | Created a local Git repository with an explicit compact release allowlist and Git LFS for the scene. Subsequently published to the public GitHub repository; v1.0.0 assets include the complete project ZIP, exact Blender application and Git-history bundle. Remote asset availability was rechecked on 2026-09-22. |
| P1 | Latest 258 output was only a 280 × 540 close-up; most recent whole frame was 257. | Full 258 render from a relocated clean checkout is the release verification. Its result and checks are recorded in `validation.json`. |
| P1 | Simply opening the blend did not restore the entire native ink pipeline. Some callbacks were installed only by setup scripts. | Release launcher explicitly loads the scene and installs the nine-module runtime with embedded autorun disabled. Independent review found render-affecting equivalence with the established setup. |
| P1 | Iteration jobs assume machine-specific absolute paths and an already-loaded scene; the 258 setup overwrote its source and enabled a crop. | Portable launcher resolves its own directory, writes to a new output folder, leaves its input unchanged and explicitly renders the full frame. |
| P2 | Repeated setup in warm workers can accumulate handlers. | Release process renders exactly once. Historical warm-worker tooling is excluded from the supported release interface. |
| P2 | Blender internal Freestyle APIs and exact object names are dependencies; runtime was not pinned. | Exact build/platform and application checksum recorded; local application archived. Future platforms/builds remain unverified. |
| P2 | README and project status still described rejected early art or pending reviews. | Root README and current state now identify approved v1; public project/verification documents now describe the release; superseded development notes remain in history. |
| P2 | Historical provenance table described the discarded maintenance bay; private/reference folders were not a release recipe. | Current provenance and explicit allowlist added. All 17 file images packed; no linked libraries or fonts. Private/references excluded. |
| P2 | Bit-identical future GPU output cannot be guaranteed; same-scene repeats previously differed by up to six channel values in a diagnostic. | Preserve the authoritative full PNG with SHA-256 and separate exact recovery from visual re-rendering. |
| P2 | A local Git repository and same-disk ZIP are not off-site backup. | Release preservation assets are now on GitHub. Still open: an independently managed off-site copy of the entire research workspace; GitHub release storage is not the complete research archive. |

## Five-year assessment

Before this capture, a clean checkout could not reproduce the image: there was no checkout, the instructions were stale, and the native runtime setup was implicit. With the frozen packed scene, explicit runtime, application archive, hashes, final PNG and clean-checkout proof, recovering the image is straightforward **if the preservation set survives**. Re-rendering a visually equivalent image has a much stronger basis, but there is no defensible numerical probability or promise that future OS/GPU combinations will execute this exact Blender build.

The largest residual risks are incomplete off-site preservation of the research history and future ability to run the archived macOS application. Keep redundant independent copies; retain original hardware/OS or a compatible environment when practical. A macOS app ZIP is not a VM image and does not include Apple drivers.

## Project boundary

This release completes the illustration. The historical web interaction experiment is not a working adventure game, SCI patch or verified Space Quest integration. Production-engine integration, walking/occlusion/inventory/save systems are not covered by v1 art approval. Project software and artwork licensing was subsequently finalized in the root LICENSE.

The compact repository intentionally does not claim to preserve the complete procedural evolution, all discarded alternatives, or every source study. The original 104 GB art archive remains local and unchanged; archive it separately if research history matters. Frozen-state reconstruction is the supported v1 contract.

## Verification

See `validation.json` for actual clean-checkout results, timings, dimensions, selected character checks and comparison with the approved close-up. Verification was run from a different directory with packed-image paths no longer referring to the original workspace. The manifest verifies real file contents and catches missing LFS objects. The release archive is built from tracked files, never by zipping the project root.
