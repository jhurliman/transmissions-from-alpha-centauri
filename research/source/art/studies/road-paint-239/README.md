# 239 — dark road pigment structure

Source237's main road is one dense packed pigment image, multiplied by18%ambient occlusion. The pale roadside is a separate preserved shader branch. This study copies the active ground material and modifies only image color entering `Mix (Legacy).012` input1, before existing AO and the exact road/bank selector.

Three unequal world-space fields introduce darker compaction, a warmer right-side dust drift and a cooler left mineral shoulder. Their boundaries combine broad authored placement with restrained ragged breakup. Selected compacted areas average nine native texture samples across0.1–0.21m offsets, quieting dense fine mottling without changing the image asset. No geometry, cracks, stones or scene clutter is added or moved.

The material is assigned through the active OBJECT-linked slot; downstream helpers must use `Street foundation.material_slots[0].material`. The original data material table stays intact. Parent adds the independently authored character-shadow response after this pass, since the source road has no direct diffuse-light term.

Audit verifies original mesh/transforms, unrelated material bindings and pale-bank selector links. No full render was launched; actual combined native comparison remains required. References UCL-01, DP-03 and DP-08 guide unequal broad ground fields and quieter spaces around industrial fragments.
