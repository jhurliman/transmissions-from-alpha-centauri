# Coliseum 116 delivery

Current visual candidate: **scene.blend**. Rendered 4K output: **main-4k.png**. The camera and surrounding scene match the approved 115E checkpoint. The landmark has the requested +4° turn and revised painted lighting.

- **kit.blend** — isolated three-level bay, projecting tower and damaged crown, with its transformation hierarchy retained. Append the full collection to preserve its assembled shape.
- **kit.png / kit-clay.png** — painted and untextured views from the kit camera.
- **main-clay.png** — current landmark geometry in the full scene.
- **generation-settings.json** — fixed source scenes, source hashes, material parameters, and physical yaw/recentering settings.
- **preservation.json** — comparison of the camera, world, lights, nonlandmark geometry, ink, and material graphs against 115E.
- **critic116.json** — independent visual scores; all six axes are 90 or higher. Scores do not imply user acceptance.
- **completion-audit116.json** — plan requirements, evidence, and remaining delivery work.

The structural and damage stages remain versioned separately in tools/. The linked intact masters precede the perspective warp in coliseum-110/geometry.blend. The validated **linked/scene.blend** companion restores shared source components through native per-instance Geometry Nodes: 2,374 instances across342 shared source groups. Damaged pieces remain unique. Evaluated topology, materials and ink flags match; maximum world vertex difference is0.000574m. Its 4K comparison is visually consistent with the reviewed scene, with tiny numerical raster differences. It renders97.48s versus90.52s for the primary and is slightly larger, so the original remains the main render file. See linked/image-comparison.json and linked/world-verification.json.

Reference artwork is stored separately in references/user-coliseum/, credited as user-supplied with artist unspecified. It is used only for analysis, never projected into the scene.

Final user acceptance is pending. The centerpiece is not marked locked.
