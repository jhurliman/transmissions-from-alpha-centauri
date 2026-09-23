# Next stage: look development before full decay

Use the current clean geometry checkpoint. Preserve a neutral PBR comparison.

1. Establish palette and value hierarchy at the game camera: cool blue-gray architecture, warm light, controlled sky saturation, distance separation and limited material families.
2. Test line treatment: silhouettes, major creases and selected seams, with width and contrast judged at delivery resolution. Avoid outlining every small component equally.
3. Use one small weathering specimen to calibrate the finish: concrete crack, paint chip and runoff stain. Confirm that it reads without becoming noise.
4. Build material-specific procedural masks: paint failure and rust on metal, cracks/spalling on concrete, joint dirt, runoff below openings and service connections. Use controlled authored seeds and local variation; keep clean masters reusable.
5. Add actual geometry damage selectively where it changes silhouette, exposes construction layers or catches light. Broad destruction and rubble remain a separate scene-scale pass.

Do not treat painted reference overlays as acceptance renders. The output must remain based on native editable geometry and materials.
