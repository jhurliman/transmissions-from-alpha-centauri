# SPDX-FileCopyrightText: 2026 John Hurliman and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. This program is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See LICENSES/GPL-3.0-or-later.txt for the full terms.
#
"""Suppress proven hidden edges behind the left building return, preserving exposed ink.
Source ownership/depth is recorded in corner-ink-207/ownership.json and native-strokes.json.
No screen-space trimming, geometry mutation or global line-width change.
"""
import bpy, math
PAIRS={
 '145 Panel 03 impact':('Building side return.002',),
 '145 Panel 03 impact folded top':('Building side return.002',),
 'Folded sheet face.047':('Building side return.002',),
 'Top / bottom return.094':('Building side return.002',),
}

def install(scene,audit_path=None):
 from mathutils.bvhtree import BVHTree
 from freestyle.types import StrokeShader
 import parameter_editor
 dg=bpy.context.evaluated_depsgraph_get();targets={n for ns in PAIRS.values()for n in ns};data={n:([],[])for n in targets}
 for inst in dg.object_instances:
  name=inst.object.name
  if name not in targets:continue
  me=inst.object.to_mesh();me.calc_loop_triangles();vv,tt=data[name];off=len(vv);vv.extend(inst.matrix_world@v.co for v in me.vertices);tt.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);inst.object.to_mesh_clear()
 assert all(vv and tt for vv,tt in data.values()),'207 side-return receiver missing'
 trees={n:BVHTree.FromPolygons(vv,tt,all_triangles=True)for n,(vv,tt)in data.items()};M=scene.camera.matrix_world.copy();origin=M.translation.copy()
 audit={'threshold_m':.02,'pairs':PAIRS,'sampled_segments':0,'hidden_segments':0,'by_shape':{},'examples':[],'resampling':'Only strokes with proven hidden target samples: add native interpolated vertices at <=1px spacing; preserve polyline and attributes.'}
 def shape_name(p):
  fe=p.fedge;shape=fe.viewedge.viewshape if fe and fe.viewedge else None
  return shape.name if shape else None
 def gap(p,target):
  d=p-origin;hit=trees[target].ray_cast(origin,d.normalized(),d.length)
  return d.length-hit[3] if hit[0]is not None else -1
 def flush():
  if audit_path:
   import json
   from pathlib import Path
   Path(audit_path).write_text(json.dumps(audit,indent=2))
 class VisibleNativeOnly(StrokeShader):
  def shade(self,stroke):
   points=list(stroke)
   if not any((n:=shape_name(p))in PAIRS and any(gap(M@p.point_3d,t)>.02 for t in PAIRS[n])for p in points):return
   length=sum((b.point-a.point).length for a,b in zip(points,points[1:]));stroke.resample(max(len(points),int(math.ceil(length))+1));points=list(stroke)
   for a,b in zip(points,points[1:]):
    source=shape_name(a)
    if source not in PAIRS:continue
    wa=M@a.point_3d;wb=M@b.point_3d;samples=(wa,(wa+wb)/2,wb)
    for target in PAIRS[source]:
     gaps=[gap(p,target)for p in samples];audit['sampled_segments']+=1
     if min(gaps)>.02:
      a.attribute.visible=False;audit['hidden_segments']+=1;audit['by_shape'][source]=audit['by_shape'].get(source,0)+1
      if len(audit['examples'])<64:audit['examples'].append(dict(source=source,occluder=target,gaps_m=gaps,pixel=[list(a.point),list(b.point)],world_segment=[list(wa),list(wb)]))
      break
   flush()
 def callback(scene,layer,ls):return[VisibleNativeOnly()]if ls.name in ('Selective geometry contours','050 Fine structural creases')else[]
 callback._guard207=True;callback._guard207_audit=audit
 parameter_editor.callbacks_modifiers_post[:]=[f for f in parameter_editor.callbacks_modifiers_post if not getattr(f,'_guard207',False)];parameter_editor.callbacks_modifiers_post.append(callback);flush();return audit

def apply(scene,embed=True,audit_path=None):
 def render_pre(scene,*args):install(scene,audit_path)
 render_pre._guard207=True;bpy.app.handlers.render_pre[:]=[f for f in bpy.app.handlers.render_pre if not getattr(f,'_guard207',False)];bpy.app.handlers.render_pre.append(render_pre);audit=install(scene,audit_path)
 if embed:
  from pathlib import Path
  name='207 Proven upper-return occlusion guard.py';t=bpy.data.texts.get(name)or bpy.data.texts.new(name);t.clear();t.write(Path(__file__).read_text()+'\napply(bpy.context.scene,embed=False)\n');t.use_module=True
 return audit
