# Selected pixel characters217

The user selected the double-detail spacesuit sprites from214 and requested that Airam and Miranda remain in the scene moving forward.

`tools/pixel_characters_217.py::apply(scene)` appends a native Blender compositor group after the existing scene beauty/ink output. It does not replace the original compositor. Two packed transparent character-only canvases preserve the exact selected98/94-pixel bodies enlarged5×6 with nearest-neighbor sampling. This is the approved1.2-times-tall DOS pixel shape.

Airam body bounds are[1698,1787,1933,2375]; Miranda[2013,1811,2208,2375] at3840×2885. Group controls expose integer X/Y offsets separately for each character. No scaling or rotation nodes are used. Applying the helper requires the recorded4Kresolution at100percent. A changed camera, crop or output format requires a new placement review.

The helper removes only the prior15-object placeholder and its8verified character-local contact strokes through the206scoped helper. Unrelated road/contact ink is retained. The selected214source indexed assets are untouched; source attribution and generation prompts remain in214.

These are persistent editable2Dcharacter overlays, not editable3Dcharacter bodies. Their current clear-road placement avoids foreground debris; composited sprites do not acquire automatic new scene occlusion, lighting or contact shadows. The native compositor preservation and pixel-level output comparison are recorded separately.

The isolated native render was compared to the selected214pixel-double comparison: zero changed pixels across the entire frame, zero RGB error, and exactly24opaque colors per character. Blender output dithering is disabled (default1→0); otherwise it introduces±1channel noise even within constant pixel blocks. Original indexed sprites and placed overlay canvases are both packed into the saved scene.
