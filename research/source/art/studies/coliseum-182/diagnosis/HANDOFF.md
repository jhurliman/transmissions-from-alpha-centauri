#182 right-core diagnostic — close without art change

The useful actual-light separation seen on164 crown faces is absent here. After black/white perchannel transport calibration, band10profile1face1701 andprofile3face1632 both measure diffuse≈0.384. The oblique profile1returnface1698 also measures≈0.384, despite≈25degree orientation change. The oldpaletteinput distinguishes face1701≈0.5633 fromface1698≈0.4632. Unchanged165 would reduce that≈0.100 difference to≈0.026 and darken both.

No165routing proof is justified by these data. No parameter tuning, materialassignment, geometry/light/ink edit or savedartscene occurred. GPUisfree.

Evidence: review.json, signal-summary.json, calibrated-pixels.json, first-hit-core.json andsignal-comparison.png.673first-hitpixels pass calibration;199are3x3interior. Narrowreturn1698has5usablepixels, so its exactvalue has filtering uncertainty; the broader nearconstant-light conclusion is supported acrossmultiple receivers. No score or acceptance claim.
