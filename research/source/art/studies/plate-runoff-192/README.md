# 192 — plate runoff and architectural ink repair

Source: retained 189 full scene. This revision preserves beam rust and existing plate washes, adds short layered water trails across the ordinary and heavy anchor-plate family, and keeps transparent pigment surfaces out of the native architecture ink calculation.

The separate ink view layer uses the same current scene geometry and camera. It excludes only the 189/192 pigment-film collections. Its live Freestyle pass is combined with the current material render; no saved reference image or old rendered scene is overlaid.

The matched visible/hidden diagnostic confirms that 189 pigment geometry causes the lower horizontal stroke to overrun the wall corner. Hiding that geometry restores the prior termination. The upper projecting contour also exists in the baseline; the user has now flagged its two overruns separately, and their source is under investigation. See `ink-diagnostic/diagnosis.json`.

Run `tools/plate_runoff_build_192.py -- render` in Blender to render the saved scene with its embedded native visibility guards installed. `tools/publish_plate_runoff_192.py` produces review crops from the full native output.

Visual acceptance remains pending until the full render is inspected. User approval is not implied by author or critic checks.
