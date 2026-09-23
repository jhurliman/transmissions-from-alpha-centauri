# Alley damage prototype 133

This isolated scene replaces one front-left cladding panel with a real recessed service cavity and privately weathers the existing Y support and ledge. It is not a whole-wall damage rollout or an approved replacement.

- `after-close-world-final.png`: final native 4K camera region; compare `before-close.png`. Both omit Freestyle consistently.
- `main.png`: full camera at 1440 pixels with native foreground Freestyle restored.
- `prefab.png` / `prefab-proof.blend`: isolated editable service kit proof under a simple inspection light rig.
- `scene.blend`: complete separate study scene.
- `prefabs.blend`: missing-panel service collection and rusted Y/ledge collection marked as assets.
- `audit.json`, `preservation.json`, `geometry-validation.json`, `review.json`: scope, endpoints, non-target preservation, mesh checks and limitations.

The service kit contains 32 objects: 20 closed meshes plus editable bevel curves. It mounts at local Y=0, faces -Y, is 1.408m wide by 1.198m high, and has 0.60m backing depth. Pipe and cable ports are recorded on the collection and in the audit. Visible protruding endpoints in the isolated proof are intentional concealed continuations when installed in the wall.

`tools/alley_damage_133.py:apply(scene)` is deterministic. It returns a JSON-compatible audit and does not save files or change the compositor. Camera, landmark, road, city and existing service geometry are preserved. Only two existing collection-instance assignments and 107 stale damaged-panel ink point opacities change; new materials are copies.

Integration must replace the frozen 128 foreground-ink source with a newly rendered native baseline reflecting this changed alley geometry. Leaving the archived source active would redraw the missing panel. Study proofs disable that compositor and render the current native scene directly; they do not composite reference artwork.

References and analysis crops are in `references/`; provenance remains in the project manifest. Previous rejected weathering proofs are retained under `v1/`.
