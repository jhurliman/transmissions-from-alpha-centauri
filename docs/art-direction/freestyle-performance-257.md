# Historical Freestyle performance investigation

Studies 256–257 showed substantial CPU time in Freestyle view-map construction and geometry cleanup. These stages can occupy approximately one CPU core; adding render threads or waiting for Metal shader compilation does not remove that bottleneck.

A culling experiment did not establish a speed improvement: the full 257 run took about 1,363 seconds versus roughly 1,108 seconds for 256, with other changes preventing a controlled comparison. Do not describe it as an optimization benchmark.

Potential future work includes simplifying geometry presented to the ink pass and caching ink when geometry, camera, visibility and line settings are unchanged. Those are proposals, not implemented public features. Ink reuse is invalid when those inputs change.

The original profiling logs and study tooling belong to the local research archive. They are not clean-checkout dependencies. The approved v1 render settings and runtime are preserved; see [reproduction](../release/REPRODUCING.md) and the actual release [validation](../release/validation.json).
