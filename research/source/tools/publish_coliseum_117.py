"""Publish the inspected native sample; keep116 as the integrated baseline."""
from pathlib import Path

R = Path(__file__).resolve().parents[1]
O = R / 'art/studies/coliseum-117'
style = 'body{background:#19191e;color:#eee7df;font:17px/1.55 system-ui;max-width:1440px;margin:32px auto;padding:0 22px}a{color:#efbc91}img{width:100%;display:block}figure{margin:28px 0}figcaption{color:#c5bbc4;padding:8px 0}section{margin:40px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:800px){.pair{grid-template-columns:1fr}}'
parts = [f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>117 · Masonry detail study</title><style>{style}</style>',
         '<h1>117 · Masonry detail study</h1><p>One upper-wall section: recessed architectural panels, a blind niche, an irregular opening and connected trim damage. The accepted placement and surrounding scene are preserved. This is a local study toward richer architecture, not a finished whole-ring treatment.</p>',
         '<p><a href="#sample">Sample</a> · <a href="#reference">Reference</a> · <a href="/prototype/review-116.html">Integrated baseline 116</a></p>']

def figure(filename, caption):
    if (O / filename).exists():
        return f'<figure><img src="/art/studies/coliseum-117/{filename}"><figcaption>{caption}</figcaption></figure>'
    return ''

parts += ['<section id="sample"><h2>Matched geometry comparison</h2><div class="pair">',
          figure('baseline-clay.png', '116: the original section from the same sample camera.'),
          figure('sample-clay.png', '117: added recesses, niche and connected masonry loss.'), '</div><h2>Painted material</h2><div class="pair">',
          figure('baseline-painted.png', '116 material and geometry.'),
          figure('sample-painted.png', 'The same geometry with the existing masonry treatment.'), '</div>',
          figure('sample-weathered.png', 'Localized crust and runoff from the modeled damage sites. Main palette and fine grain retained.'),
          '<p><a href="/art/studies/coliseum-117/geometry-proof.blend">Editable sample</a> · <a href="/art/studies/coliseum-117/geometry.blend">Scene with sample geometry</a></p></section>',
          figure('main.png', 'Locked main camera geometry preview. Final landmark contact ink is pending; the integrated baseline remains116.'),
          '<section id="reference"><h2>Reference details</h2><div class="pair"><figure><img src="/references/user-coliseum/upper-wall-detail.png"><figcaption>UCL-02: wall divisions, openings and damage.</figcaption></figure><figure><img src="/references/user-coliseum/tower-arches-crop.png"><figcaption>UCL-01: tower relief and connected masonry loss.</figcaption></figure></div><p>User-supplied artwork; original artwork by the project creator using ChatGPT Images 2.5. Original project artwork. Exact construction beyond image resolution is inferred.</p></section>',
          '<p>Study remains in development. Whole-ring damage variation, final weathering and final landmark contact ink follow after the sample is convincing. No final acceptance or99 score is implied.</p></html>']
(R / 'prototype/review-117.html').write_text(''.join(parts))
