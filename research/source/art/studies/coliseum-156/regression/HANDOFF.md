#156 foreground ink regression control

Full native control restores only the five original152 numerical-cleanup meshes;153material,154crown geometry and155age remain. Existing149runtime visibility guard and all line settings remain. No primary scene changed.

Result: the left ledge extension, right ledge break and missing lower-left curved crack are pixel-identical to156. Outside the landmark, control versus152 has676 pixels over4RGB (max127); control versus156 has only18 pixels over4 (max7). The14face cleanup is not the causal source of these three defects.

Likely remaining cause is154 geometry affecting the shared global Freestyle viewmap/chaining; this is an inference pending a154-only restore control. Plain chaining and Sampling are the only geometry line-style operations; no random style modifier was found. The149 guard only checks its two named fascia suspects and cannot establish correctness of these unrelated chains.

A native structural solution may isolate foreground/landmark Freestyle viewmaps into separate current-scene viewlayers/passes. Selection-by-collection alone does not isolate viewmap processing. Such a change needs an actual current native render and comparison, not a raster patch or assumption that the historical130 implementation will be exact. No further render or canonical change is made by this task.

Files: without-cleanup.blend/png, without-cleanup-audit.json, control-comparison.json, three-panel152/156/control crops. GPU is free.
