# 160 isolated U10L return repair

Candidate passes structural gates and matched painted/clay inspection. This is a native topology repair with no discernible camera-scale visual gain. It is not integrated or user-approved.

Use `tools/coliseum_return_apply_160.py::apply(C)` to load the validated local-coordinate payload onto the original object. Never adopt the temporary library object's matrix: the accepted transform contains shear. Only the original target modifiers are removed because their evaluated effect is already present in the payload. Preserve private object material assignment. Source is corrected156.

See strip-candidate-audit.json, preservation-audit.json and review.json. Scope: cap and upper right angular-end return. Protected front/back/bottom/left end and low right end keep all 1296 original nonzero triangles; one custom normal has 2.5464e-6 serialization delta. 292 robust crossing pairs become zero, closed topology remains, no zero-area candidate faces.

Native before/after painted and clay crops are present with comparison sheets. Full ink integration still needs verification. U15R remains untouched; do not claim globally clean geometry. V1 was rejected for invalid boundary correspondence and is archived.
