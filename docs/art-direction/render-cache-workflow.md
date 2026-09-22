# Warm native render batches

Use `tools/render_warm_batch.py` with Blender `-b -t 0` for successive local checks. The JSON job names a setup script, a list of output paths with optional in-place edit scripts, and a timing output. Setup loads the versioned scene and installs the existing native visibility guards once. Edit scripts retain the scene and material datablocks; do not reopen the blend between passes. The helper refuses to overwrite outputs.

Keep material graphs and render features stable where possible. New shader variants may still compile; changing geometry may invalidate outline data. This is in-process reuse, not a new persistent disk shader cache. Save versioned scenes separately as usual.

Study256 measured the same native close-up twice:180seconds fresh-process and66seconds immediately repeated, about63percent less total time. Both disabled Freestyle/compositing. This does not establish a full-frame speedup. The GPU outputs differ slightly (maximum6code values); no inputs changed. Full-scene Freestyle view-map work was sampled on one core and requires separate optimization.

Benchmark: `art/studies/gallery-sills-256/cache-benchmark/review.json`.
