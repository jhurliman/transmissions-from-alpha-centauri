# Historical techniques and generation code

This archive preserves the techniques behind studies 001–258 of Transmissions from Alpha Centauri. It contains generation and modification scripts, helper tools, configurations and technique notes, including rejected alternatives. It is not a supported one-command recreation of the entire design history.

For the finished illustration, use the [main README](../README.md) and [verified release launcher](../docs/release/REPRODUCING.md).

## Find a technique

[source/tools/](source/tools/) contains generators, incremental geometry/material edits, rendering and review tools. [source/config/](source/config/) contains study parameters. [source/art/](source/art/) preserves per-study source snapshots and notes. The [study catalog](studies.json) groups filenames by their study numbers; that association does not establish execution order. The [manifest](manifest.json) records checksums, imports, literal scene references and the publication exclusions.

All files are text. Generated scenes, renders, large diagnostic dumps, purchased assets, private photos and commercial music are not included. Source originals remain in the creator's private snapshot. Machine-specific project and clipboard paths in these published copies have been replaced with `/PATH/TO/...` placeholders; changed files are identified in the manifest. This is a publication cleanup, not a completed portability conversion. Third-party source notices are retained unchanged.

## Reproducibility limits

Many studies open a prior `.blend` and mutate named objects or numbered ink strokes. Others expect Blender to have a scene already loaded. Those inputs are not recreated merely by copying the Python. Dynamic imports and computed asset paths are not fully described by a static catalog. Historical notes, approval flags and instructions describe their original experiments, not current project policy.

Before running a study, read its entry point and imported helpers, supply its parent scene and required assets, replace path placeholders, and work on disposable copies in a separate scratch workspace. Some scripts overwrite their inputs or emit files to fixed locations. Do not run all archived scripts in bulk or against the frozen release. Keep the mirrored tools/config/art paths together; most relative root calculations expect that layout.

Blender 5.2.1 LTS is pinned for the final release; individual historical experiments were not all validated against that build. Auxiliary tools import libraries such as Pillow, NumPy and SciPy. No universal historical dependency lock or complete replay test exists yet. The next step is to map actual entry points and dependencies, retain essential inputs and a few checkpoints, and validate representative recipes. See the [preservation plan](../docs/release/ARCHIVING.md).

## Verification and licenses

From the repository root:

```sh
python3 research/verify.py
python3 tools/release/verify.py
```

The research check verifies its explicit text-file inventory and hashes, parses Python without executing it, and validates JSON. These checks establish archive integrity and syntax, not successful rendering.

Project-authored code is GPL-3.0-or-later. Project-owned notes/configuration metadata follow the scope in [LICENSE](../LICENSE). `source/tools/third_party/blast.c` and `blast.h` retain Mark Adler's permissive notices; their implementation is not relicensed by this archive. References to outside artwork are provenance, not a redistribution license for that artwork.
