# Surgical seam validation

Frozen helper: `tools/coliseum_seam_repair_127.py::apply(C)`.

T0 had2 new intersections caused by a nearly-collinear inserted front seam vertex departing its original edge by47.9 micrometres. T2 had1 matching new seam intersection,32.6 micrometres. Projection onto the straight neighboring edge removes all3, preserves closedness, and updates115 original-position data.

After helper: T0=0, T1=0, T2=57 proper triangle crossings. The remaining T2 folds are inherited from damaged B10: original126 `COL110 T2 B10 loadbearing arch tunnel` has61 proper crossings despite being closed. Joining reduced that count; the helper does not claim to repair the inherited damage.

`snap.blend`, `snap-audit.json`, and original diagnostic `audit.json` retain evidence. No broad remesh or visible shape change. Legacy B10 repair is deferred until after parent127 integration.
