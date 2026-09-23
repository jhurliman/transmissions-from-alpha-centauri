# Sky study 075

Open index.html for the cloud-density comparison and selected proof. Selected uses variant B with a restrained pale amber sun. All results are native world-node shaders; no images are projected. The saved full scene exists for reproducibility, but integration only requires the world change.

## Integration

```python
import sys
sys.path.insert(0, str(ROOT / "tools"))
from study_sky_075 import apply_sky
apply_sky(bpy.context.scene, "B")
```

Call once after loading the integration baseline. This copies its world, sends the original shader to non-camera rays, and changes only the camera-visible sky. Preserve the existing atmosphere volume and architectural lighting. No collection to append.

A/B/C are density trials; selected.png/selected.blend include the corrected sun direction and smaller disc. Native helper direction.exr was a diagnostic direction measurement, not a texture input. No diagnostic image is used by any material.
