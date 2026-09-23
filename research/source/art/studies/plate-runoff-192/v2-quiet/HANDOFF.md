# 192 plate runoff

Use `tools/plate_runoff_192.py::append_payload(scene)` on accepted 189 geometry, or `apply(scene)` to rebuild in about 3 seconds after the source scene loads. No original objects, materials, films or broad washes are edited. The new mesh reuses the existing bounded-light oxide shader.

135 selected heads across all 42 four-bolt plates receive 190 short water lines: 80 heads receive one, 55 receive two. This includes 127 ordinary 073 mounting-plate heads and all 8 Y splice heads, hence all 16 bolts on the selected heavy plates. Global 189 selection remains 3,253/4,066.

Each line is two overlaid native receiver-fitted ribbons: a warm translucent outer wash with feathered edges, plus a narrower darker oxide stream. Both taper and fade downward. Upper lines target 15% of actual plate height; secondary lines are shorter. Lower lines fit the exact remaining distance and stop 1.2 mm inside the plate bottom. The maximum measured actual geometry clearance is 1.2002 mm. They follow the actual bottom bevel, with zero rejected surface quads and no missing selected heads.

24,320 new quads, 97,280 vertices. Colors and alpha vary continuously across each ribbon. Existing 189 film geometry and material assignments remain intact.

The new mesh is excluded from all active Freestyle line filters through a persistent fake-user union preserving the old exclusions. This alone DOES NOT establish that transparent films preserve existing ink visibility. Root is separately investigating that renderer behavior; native render validation remains required. No GPU render was performed by this module's author.
