# Historical shader-cache experiment

Study 256 compared a fresh Blender process with repeated close-up renders in one warm process: roughly 180 seconds initially, then 66 seconds. This was a diagnostic without the full Freestyle/compositor workload, not a full-scene speed guarantee. Repeat output differed by up to six channel values.

The useful observation is that keeping the same process alive can reuse shader work. It does not establish a portable, persistent Metal cache. Historical warm-worker scripts and benchmark evidence remain in the local research archive and are not part of the public reproduction interface.

For v1 use the single-render [release launcher](../release/REPRODUCING.md). Do not repeatedly install scene handlers into a warm worker without addressing handler accumulation. See the [Freestyle notes](freestyle-performance-257.md) for the separate CPU bottleneck.
