"""Localized true masonry breakage across crown and arcade components. UCL-01.
The cutters remove shallow faces at connected architectural junctions; most bays stay intact.
"""
import bpy,math,bmesh
from mathutils import Matrix,Vector

def add_breakage(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;start=-math.pi;lean=Matrix.Rotation(math.radians(2),4,'X')
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 a=start+4.5*step;auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(a,4,'Z');delta=anchor.matrix_world@auth.inverted()
 def p(rr,aa,z):
  b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(aa),rr*b*math.sin(aa),z));return delta@Vector((v.x,cy+v.y,v.z))
 def cutter(name,angle,outline,back,front):
  # Outline is authored tangentialdistance,height; unequal radialdepth gives fractured returnfaces.
  N=len(outline);vs=[p(rr,angle+u/rad,z) for rr in [back,front] for u,z in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);collection.objects.link(ob);return ob
 audit=[]
 def apply_zone(label,cut,targets):
  changed=[]
  for ob in targets:
   if ob.type!='MESH':continue
   ca=[cut.matrix_world@Vector(v) for v in cut.bound_box];oa=[ob.matrix_world@Vector(v) for v in ob.bound_box]
   if any(max(v[k] for v in ca)<min(v[k] for v in oa) or max(v[k] for v in oa)<min(v[k] for v in ca) for k in range(3)):continue
   old=ob.data;ob.data=old.copy();before=len(ob.data.vertices)
   mod=ob.modifiers.new('Localized masonry fracture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
   bpy.context.view_layer.objects.active=ob
   try:bpy.ops.object.modifier_apply(modifier=mod.name)
   except Exception:
    ob.modifiers.remove(mod);ob.data=old;continue
   bm=bmesh.new();bm.from_mesh(ob.data);nonman=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();after=len(bm.verts);bm.free()
   if nonman or (after and volume<=0):
    ob.data=old;continue
   if after==before:
    ob.data=old;continue
   if not after:
    changed.append({'object':ob.name,'fully_removed_stone':True});bpy.data.objects.remove(ob,do_unlink=True);continue
   if after!=before:
    ob['localized_breakage']=label;changed.append({'object':ob.name,'vertices_before':before,'vertices_after':after,'nonmanifold_edges':nonman,'positive_volume':volume>0})
  bpy.data.objects.remove(cut,do_unlink=True);audit.append({'zone':label,'changed':changed})
 # Irregular bite into exposed high wall adjacent to a large crown loss.
 j=5;aa=start+(j+.87)*step
 cut=cutter('COL110 crown cutter A',aa,[(-1.45,78.5),(1.6,78.5),(1.5,74.2),(.85,73.7),(.5,74.0),(-.15,73.2),(-.65,74.0),(-1.45,74.4)],rad-9,rad+2)
 apply_zone('left crown missing masonry',cut,[o for o in list(collection.objects) if o.get('bay')==j and o.get('tier')==3])
 # Tower's upper outside corner broken away: preserves solid inner/left bearing mass.
 j=10;aa=start+j*step
 cut=cutter('COL110 tower crown cutter',aa,[(.35,81),(3.4,81),(3.3,74.9),(2.4,75.35),(1.8,75.0),(1.55,75.8),(.7,76.2),(.35,77.0)],rad+.7,rad+5)
 apply_zone('central tower crown corner loss',cut,[o for o in list(collection.objects) if o.get('bay')==j and o.name.startswith('COL110 Tower')])
 # A smaller outer upper-wall breach, with exposed full wall thickness.
 j=11;aa=start+(j+.68)*step
 cut=cutter('COL110 crown cutter B',aa,[(-.85,77),(1.05,77),(1.15,72.6),(.65,72.9),(.20,72.25),(-.35,72.7),(-.75,72.45),(-.85,73.5)],rad-9,rad+2)
 apply_zone('right crown edge loss',cut,[o for o in list(collection.objects) if o.get('bay')==j and o.get('tier')==3])
 # Coherent shallow weather failures cross the cornice, spandrel and outer arch voussoirs.
 for j,offset in [(7,-1.0),(10,1.35)]:
  aa=start+(j+.5)*step+offset/rad
  outline=[(-.75,60.0),(.72,60.0),(.92,58.6),(.47,58.2),(.74,57.6),(.44,56.8),(.62,56.1),(.25,55.2),(-.25,54.8),(-.62,55.2),(-.37,56.0),(-.72,56.65),(-.48,57.4),(-.83,58.1),(-.61,58.8)]
  cut=cutter(f'COL110 arcade connected cutter{j}',aa,outline,rad-.55,rad+1.8)
  targets=[o for o in list(collection.objects) if o.get('bay')==j and o.get('tier')==2 and o.get('coliseum_role') in ['wall','arch_molding','band']]
  apply_zone(f'arcade{j} cornice to arch face spall',cut,targets)
 return {'reference':'UCL-01','zones':audit,'method':'native applied manifold booleans, unique copies of impacted linked meshes','camera_dependent':False}
