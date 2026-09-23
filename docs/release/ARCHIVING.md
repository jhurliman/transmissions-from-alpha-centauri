# Research archive assessment

Measured 2026-09-22. This is an inventory and preservation proposal, not a claim that the research archive has been uploaded or independently backed up.

## Measured footprint

| Material | Files | Logical size |
| --- | ---: | ---: |
| Historical Blender scenes (`.blend`, excluding released scene) | 766 | 69.76 GiB |
| Blender backups (`.blend1`) | 260 | 26.48 GiB |
| Research PNGs | 3,536 | 4.94 GiB |
| Research EXRs | 36 | 1.13 GiB |
| Complete research set, including code/config/reviews and other files | 9,728 | **103.66 GiB** |
| Same research set, unique SHA-256 contents | 8,847 | **97.11 GiB** |
| Research set without `.blend1` files, unique contents | — | 75.95 GiB |

The research set is `art/`, `tools/`, `config/`, `prototype/`, and `docs/`, measured before this housekeeping pass. It excludes `.git`, `private/`, `references/`, `archives/`, release assets, cache directories and symlink targets. Byte counts are logical file lengths, not APFS physical allocation or compressed archive sizes. Exact duplicate content accounts for 6.55 GiB. No files were deleted; backup versions can contain unique work and must remain in the preservation copy.

Other local material: private work 7.89 GiB, references 0.10 GiB, existing preservation archives 0.81 GiB, and release files 0.25 GiB. The initial counted workspace totals about 112.70 GiB before `.git`, excluded caches and external/symlink dependencies. Those categories can overlap in content; do not add them to a deduplicated total without hashing them too.

The local audit includes per-file SHA-256 checksums for all 9,728 research files. Its detailed manifests remain private because file paths and study contents have not been cleared for publication. Historical documents replaced during housekeeping were separately copied into the private audit folder and also remain in Git history.

## “258 studies” is not 258 portable projects

Study numbers include variants, component experiments, close-up renders, read-only reviews and interrupted runs. The earlier video inventory found images under 245 of the numbers 001–258. That is image coverage, not evidence that the other studies are lost or that every numbered study can be rerendered.

The current release preserves the final scene and native runtime. Historical setups often refer to earlier scenes, machine-specific paths and shared assets. A complete evolution archive needs the scripts, configurations, components, original project-owned assets and dependency relationships as well as pictures and scene files. The third-party `001candidate` reference must not be misrepresented as project-owned artwork.

## Impact of putting everything into Git

Ordinary Git is a poor fit: many scenes exceed GitHub's 100 MB single-object limit. GitHub recommends keeping the compressed repository within 10 GB and storing generated outputs outside Git. See [repository limits](https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits).

Git LFS is technically feasible, but each distinct version consumes its entire file size. The current attributes only put `.blend` in LFS; simply force-adding the workspace would leave other large binaries in ordinary Git and bypass privacy exclusions. An archive repository would need its own reviewed attributes and publication manifest.

A fully hydrated checkout of the entire research tree would materialize about 104 GiB. An LFS checkout also retains its local object cache: budget roughly 200 GiB for cache plus working files before temporary space. Skipping LFS downloads makes a lightweight clone possible, but then the art is not locally available. A full transfer of roughly 100 GiB has an ideal lower bound of about 2.4 hours at 100 Mbps, before overhead.

At the current published estimate of $0.07/GiB-month storage and $0.0875/GiB downloaded, a roughly 97–104 GiB LFS archive would cost about **$6.10–$6.60/month for storage** on Free/Pro if the full 10 GiB allowance were available. One full download in a month would add roughly **$7.60–$8.20**; ten would add roughly **$84–$90**. This is a planning estimate, not an account-specific quote: other repos share allowances, actual LFS eligibility/object totals may differ, and plan/budget settings matter. [GitHub calculator](https://github.com/pricing/calculator), [LFS billing and allowances](https://docs.github.com/en/billing/concepts/product-billing/git-lfs), checked 2026-09-22.

## Source-first preservation (preferred)

The creator prioritizes preserving techniques and reproducible recipes over byte-for-byte copies of every generated scene. The preferred public archive is therefore historical generation code, configurations, technique notes, required project-owned input assets and a small set of validated checkpoints—not all 766 research scenes.

The local inventory found 1,322 Python files across tools and art (about 4.7 MiB) and 339 configuration files (about 0.4 MiB). Some scripts are renderers, audits or copied source snapshots rather than unique generators. Large JSON material/fingerprint dumps account for much more space than the code.

Many experiments are incremental mutations: study 258 opens 257, which opens 256; 258 also addresses specific object names and numbered ink strokes. A saved script alone does not prove replayability. Filename-based study associations and literal scene-load paths have been cataloged locally; dynamic dependencies, imported helpers, inherited state and embedded Blender text blocks require further inspection.

A source/text snapshot has been preserved privately and its archive contents checked against per-file SHA-256 hashes. It excludes raster inputs and Blender files, so it is a technique archive, not yet a complete reconstruction kit or a cleared public publication set.

To make the recipes reproducible:

1. Preserve historical code unchanged, including helpers, configs and third-party notices. Add portable wrappers separately rather than rewriting the historical evidence.
2. Map each study to its actual entry point, parent checkpoint, required assets, Blender version, seeds and expected output. Mark review-only and incomplete studies explicitly.
3. Keep only the checkpoints needed to break expensive or unrecoverable chains; determine those through replay tests rather than guessing from filenames. Retain the already-packed final release.
4. Preserve irreducible inputs such as selected character sprites, authored pigment textures and any manually edited geometry. Generated does not necessarily mean reproducible from the surviving script.
5. Test representative recipes in a relocated clean workspace. Classify each as replay-verified, checkpoint-dependent, or historical technique only. Full 001–258 replay has not been demonstrated.

No existing scenes or backups have been deleted. The whole-workspace estimates below remain useful as an optional preservation ceiling, not the recommended Git payload.

## Optional full-workspace preservation layout

1. **Keep the main repository compact.** Retain the supported final release and add a reviewed study catalog, descriptions, small previews and checksums when the history is ready to publish.
2. **Preserve the complete workspace privately first.** Use an encrypted, versioned off-site backup plus an independent local/external copy. Include unique `.blend1` files, private material, references, Git history/LFS objects, dependencies and the exact Blender application. Record exclusions and resolve external asset paths. Existing same-disk archives are not independent backups.
3. **Publish a curated research archive separately.** Include project-owned study sources/renders and their supporting scripts, with an explicit file manifest and licenses. Exclude purchased assets, reference collections, personal photographs, correspondence and commercial music. Preserve excluded material privately rather than deleting it.
4. **Use downloadable study bundles or archive volumes.** A separate archive repository with release downloads can expose history without making every code checkout huge. GitHub release assets must each be under 2 GiB; GitHub documents no total release-size or bandwidth limit. Split into independently extractable study groups where practical and include checksums and a catalog. An independent archival/object-storage copy is still needed. See [release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
5. **Prove recovery before calling it archived.** Restore into a clean directory, verify every checksum, check asset resolution, and rerender representative early/middle/late scenes. Label preserved-but-unverified studies honestly. No compressed-size saving is assumed until an actual archive is built.

## Current preservation status

The public v1.0.0 release assets and GitHub repository are available. The whole historical workspace is still local; this audit has not uploaded it or created an independent backup. SHA-256 manifests detect future loss or changes but cannot recover missing bytes. A curated text-only source collection is now included under [research/](../../research/README.md): 1,832 files totaling 5.43 MiB before Git compression, with a 258-entry study catalog, checksums and a non-executing verifier. It excludes large diagnostic JSON dumps and one purchased-game pixel reconstruction diagnostic; machine-specific paths are replaced with documented placeholders. The private snapshot retains the originals. This collection preserves techniques but has not established historical replay.

The next source-first actions are dependency mapping, selection of indispensable input assets/checkpoints, and clean-workspace replay tests. An off-site copy of the source archive is still needed; a full-workspace backup is optional additional protection.
