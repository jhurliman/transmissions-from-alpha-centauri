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
"""Seat accepted215 roof bands on the new roof slabs; no source-kit modification."""
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def apply(scene,audit_path=None):
 roots=bpy.data.collections['215 Short alley composition'];masters={o.instance_collection for o in roots.objects if o.instance_collection};roofs={o for c in masters for o in c.objects if o.name.startswith('215 real roof slab')};assert len(roofs)==14,len(roofs)
 rows=[]
 for ob in roofs:
  assert not ob.get('215 roof band seated'),'Already corrected'
  old=ob.data;ob.data=old.copy();xyz=[v.co.copy()for v in ob.data.vertices];xmax=max(v.x for v in xyz);zmax=max(v.z for v in xyz)
  assert abs(xmax+.075)<.002,(ob.name,xmax)
  for v in ob.data.vertices:
   if abs(v.co.x-xmax)<1e-5:v.co.x=.25
   if abs(v.co.z-zmax)<1e-5:v.co.z+=.025
  ob.data.update();ob['215 roof band seated']=True
  rows.append({'object':ob.name,'old_front_x':xmax,'new_front_x':.25,'roof_top_z_delta':.025,'band_back_x':.144,'bearing_overlap_x_m':.106,'vertical_overlap_m':.015,'original_data_retained':old.name,'private_data':ob.data.name})
 bpy.context.view_layer.update()
 # Onlyadded roof volume could hide a previouslyretained contact; no priorcontact canbe revealed.
 # Reuse the proven native run/attribute clipper against these changed slabs alone.
 vs=[];ts=[];owners=[];dg=bpy.context.evaluated_depsgraph_get()
 for ins in dg.object_instances:
  if ins.object.original not in roofs:continue
  me=ins.object.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ins.matrix_world@v.co for v in me.vertices);ts.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);owners.extend([ins.object.original.name]*len(me.loop_triangles));ins.object.to_mesh_clear()
 tree=BVHTree.FromPolygons(vs,ts,all_triangles=True)
 import landmark_contact_visibility_210 as clip
 original=clip.external_tree
 clip.external_tree=lambda scene:(tree,owners,{'scope':'215 changed roof slabs only; monotonic opaquegeometry addition','triangles':len(ts),'vertices':len(vs)})
 try:contacts=clip.apply(scene)
 finally:clip.external_tree=original
 report={'scope':'Only14new215roofslab private meshes; unchanged originalnativebands/sourcecomponents','seating':rows,'incremental_contact_visibility':contacts,'no_blanket_reclip':True}
 if audit_path:
  from pathlib import Path
  Path(audit_path).write_text(json.dumps(report,indent=2))
 return report

def install_line_counter(scene,path):
 from freestyle.types import StrokeShader
 import parameter_editor
 from pathlib import Path
 from collections import Counter
 counts=Counter();a={'style':'215 Distant component architecture','strokes':0,'points':0,'visible_points':0,'shape_counts':{}}
 def flush(*args):a['shape_counts']=dict(counts);Path(path).write_text(json.dumps(a,indent=2))
 class Count(StrokeShader):
  def shade(self,stroke):
   a['strokes']+=1
   for p in stroke:
    a['points']+=1;a['visible_points']+=int(p.attribute.visible)
    fe=p.fedge;shape=fe.viewedge.viewshape if fe and fe.viewedge else None
    if shape:counts[shape.name]+=1
   if a['strokes']%32==0:flush()
 def cb(scene,layer,ls):return[Count()]if ls.name==a['style']else[]
 cb._count215=True;parameter_editor.callbacks_modifiers_post[:]=[f for f in parameter_editor.callbacks_modifiers_post if not getattr(f,'_count215',False)];parameter_editor.callbacks_modifiers_post.append(cb)
 bpy.app.handlers.render_complete.append(flush);flush();return a
