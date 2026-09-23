# Native scene-lighting feasibility

`airam-anime.png` and `miranda-anime.png` preserve the generated transparent alpha. Their ink and fixed cel shading were generated from the user's spacesuit artwork with209 scene style guidance.

`proof.blend` contains only the separate native light/card scene copied from206, which preserves the209 camera, world and lights. New art and body-fit UV coordinates are substituted; the environment is not rerendered. Materials use65% authored color plus35% native diffuse response. A second actual render reduces light energy to15% for the measured comparison. Both passes are retained.

The cards have one surface normal. They cannot relight individual limbs/hair or cast physically grounded contact shadows in this study. Metallic-looking highlights are illustrated, not simulated moving reflections. The scene composite is an explicitly labelled2D art study, not geometry acceptance.
