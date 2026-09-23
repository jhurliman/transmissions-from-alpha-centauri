# 129 inward arch thickness

Frozen API: `tools/coliseum_arch_thickness_129.py::apply(C, factor=1.75)` on fresh128 geometry **after** `coliseum_b10_prepared_128.apply(C)`. Root retains all integration authority. Do not apply twice.

The combined two-ring normal profile scales inward around its fixed outermost0.83m authored offset. Its full width0.86→1.505m (1.75×); the ring gap also scales, avoiding overlapping rings. Inner boundary inset is0.645m authored. Both actual tunnel wall and jamb geometry move inward consistently, so this is a smaller genuine opening, not a rim floating over the old opening. Elliptical arches remain elliptical parallel profiles; damagedB10 retains its earlier circular basis and receives the same inset. All54 openings are covered.

All1,622 affected meshes are closed and have zero strict crossings. The5,594 sampled outer-profile vertices have exactly0 raw and evaluated127-group world displacement. Outer identification uses a0.002 authored-unit tolerance to accommodate existing inverse-transform float error; matching outer vertices are copied bit-for-bit. Wall vertices below the opening base are guarded. Floor bands, platforms, column geometry, radial arch depth and current material slots remain unchanged. Original-position attributes are updated on moved surfaces; front-quarter depth values remain attached.

Actual4K B8 crown sample, matching angular positions:10.4147→16.7318px. Its screen ratio differs from1.75 because the two rings occupy different projecting depth planes. The authored combined thickness ratio is exactly1.75.

Inspected actual native before/after painted and untextured workbench crops. Thicker masonry and smaller clear openings are visible; broad outer outline remains stable. `render.use_compositing=False` explicitly disables stylization for clay. The pre-existing apparent radial shading ticks remain visible; no global lighting/ink workaround was introduced.

Files: `geometry.blend`, `baseline.blend`, `audit.json`, `floor-audit.json`, and matched `before/after-main4k.png`, `before/after-painted-close.png`, `before/after-clay.png`. Isolated candidate, not user approval.
