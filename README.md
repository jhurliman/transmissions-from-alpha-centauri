# Transmissions from Alpha Centauri — v1.0.0

The ruined-street illustration is **user-approved and complete**, as of 2026-09-21 (scene iteration 258). The release is an editable Blender scene and its finished 3840 × 2885 image. This milestone is artwork, not a playable game or a working SCI/Space Quest patch.

## Reproduce the image

Use Python 3.9+ for verification. Install Git LFS before cloning, then fetch the large scene file:

```sh
git lfs install
git lfs pull
python3 tools/release/verify.py
blender -b --disable-autoexec --python-exit-code 1 -t 0 \
  --python releases/v1.0.0/render.py -- --output /tmp/tfac-v1-render
```

Use **Blender 5.2.1 LTS, build `9e2066aef7ef`**. On the original Mac, replace `blender` with `/Applications/Blender.app/Contents/MacOS/Blender`. Choose an output directory that does not already exist. Rendering uses Blender's bundled Python; no pip packages, online services, original-game files, or private photos are required. Allow tens of minutes, particularly for Freestyle.

- [Reproduction and recovery guide](docs/release/REPRODUCING.md)
- [Code and project review](docs/release/REVIEW.md)
- [Asset provenance and scope](docs/release/PROVENANCE.md)
- [Version and file checksums](releases/v1.0.0/manifest.json)
- [Approved editable scene](releases/v1.0.0/scene.blend)
- [Final full-resolution image](releases/v1.0.0/main-4k.png)

The release uses packed textures, explicitly restored ink-rendering rules, and a frozen camera, lighting, atmosphere, materials, and selected character art. The launcher renders one image without saving over its input. Opening the `.blend` and pressing Render alone is **not** the supported reproduction path.

The local Git repository intentionally captures the finished release and supporting documentation, not the 104 GB research archive. `private/` and `references/` are excluded. See the review for GitHub publication status and remaining preservation limitations. No distribution license has been chosen.
