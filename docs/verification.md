# Verification

From a checkout with Git LFS assets downloaded:

```sh
python3 tools/release/verify.py
```

This checks the manifest's file sizes and SHA-256 hashes, required scene/runtime files, real scene bytes rather than an LFS pointer, and the authoritative image's 3840 × 2885 dimensions.

The [reproduction guide](release/REPRODUCING.md) explains rendering with the pinned Blender build. [validation.json](release/validation.json) records the completed clean-checkout render; [REVIEW.md](release/REVIEW.md) records findings and limitations. A successful checksum check proves preserved bytes, not compatibility with a new OS/GPU.

Documentation housekeeping does not require re-rendering unchanged artwork. Future visual or runtime changes require full-frame verification and a new version. Historical prototype interaction tests are not tests of this illustration release.
