# Cloud133 native-source prototype

Run `tools/clouds_133_generate.py` with project Python to regenerate deterministic fields from the owned082 native cloud assets, then call `tools/clouds_133.py::apply(scene)` in the original scene. NumPy is used by Blender to load the resulting fields; SciPy is only required by the offline generator.

The module changes cloud material assignments only. World sky/sun, camera, cloud plate transforms and all other materials remain unchanged. The proof scene intentionally hides noncloud geometry; do not substitute sky-study.blend for the primary scene. Integrate the module instead.

The4K before/after crops and1440 context drafts were visually inspected. Context drafts have Freestyle/compositor disabled equally; final integrated ink remains root-owned. Review.json records the prototype improvement and limitations. No user approval is inferred.
