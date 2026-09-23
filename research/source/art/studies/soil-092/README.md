# 092 — painted soil and physically seated foundation stones

User locks 120 small road rocks. Terrain geometry remains approved. This study changes only soil material and bank-rock contact.

## Surface approach
The user-supplied animation still was inspected directly in the browser (Pinterest image opened; web text fetch403). Its useful property is a hierarchy of broad color washes, connected light/shadow, directional dragged pigment and selected fine flecks. Retain our warm road palette rather than importing the green/yellow scene colors.

`soil_paint_fields_092.py` derives coarse slope lighting from the accepted089 relief and macro height. It suppresses full-frequency normal shading, then adds explicit irregular brush-stamp clusters and low-amplitude grain. These are procedural world-space pigment assets, not reference-image projections. A uses subdued strokes; B increases stroke strength and palette grouping. Image fields are packed in the native scene.

`soil_paint_scene_092.py` copies the ground material and replaces its road branch, retaining the existing bank footprint mask/pale soil branch. The soil mesh is never modified. `foundation_contact_092.apply` fits238 bank rocks on broad bases. Road rocks and road contact accents are preserved. Final review pending user.
