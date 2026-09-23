import bpy,json,hashlib,array
from pathlib import Path
R=Path.cwd();O=R/'art/studies/scene-details-138'
def ids():
 rows=[]
 for prop in bpy.data.bl_rna.properties:
  try:values=getattr(bpy.data,prop.identifier)
  except:continue
  if prop.type!='COLLECTION':continue
  for x in values:
   if isinstance(x,bpy.types.ID)and x.library:rows.append({'type':x.bl_rna.identifier,'name':x.name,'library':x.library.filepath})
 return rows

def stamp(C):
 s=bpy.context.scene
 if C not in s.collection.children_recursive:s.collection.children.link(C)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out={}
 for ob in C.all_objects:
  d={'type':ob.type,'matrix':[list(v)for v in ob.matrix_world],'materials':[(m.material.name if m.material else None,m.link)for m in ob.material_slots]}
  if ob.type=='MESH':
   e=ob.evaluated_get(dg);me=e.to_mesh();h=hashlib.sha256()
   for coll,key,size,code in [(me.vertices,'co',3,'f'),(me.loops,'vertex_index',1,'i'),(me.polygons,'material_index',1,'i'),(me.corner_normals,'vector',3,'f')]:
    a=array.array(code,[0])*(len(coll)*size);coll.foreach_get(key,a);h.update(a.tobytes())
   d['geometry_normals_material_indices']=h.hexdigest();e.to_mesh_clear()
  out[ob.name]=d
 return out

def read(rel):
 bpy.ops.wm.open_mainfile(filepath=str(R/rel));linked=ids();images=[]
 for im in bpy.data.images:
  if im.source in ['GENERATED','VIEWER']:continue
  p=Path(bpy.path.abspath(im.filepath));images.append({'name':im.name,'source':im.source,'users':im.users,'packed':bool(im.packed_file or im.packed_files),'filepath':im.filepath,'resolved_exists':p.exists()})
 C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
 return {'file':rel,'fresh_open_actual_linked_ids':linked,'library_metadata_only':[l.filepath for l in bpy.data.libraries],'external_images':images,'C_objects':len(C.all_objects),'scene_names':[s.name for s in bpy.data.scenes],'stamp':stamp(C)}
A=read('art/studies/scene-details-138/scene.blend');B=read('art/studies/scene-details-138/kit.blend');P=read('art/studies/coliseum-135/kit-proof/scene.blend');out={}
for key,d in [('scene138',A),('kit138',B),('proof135',P)]:out[key]={k:v for k,v in d.items()if k!='stamp'}
for key,d in [('kit138_vs_scene138',B),('proof135_vs_scene138',P)]:
 a=A['stamp'];b=d['stamp'];out[key]={'expected_objects':len(a),'actual_objects':len(b),'missing':sorted(set(a)-set(b)),'extra':sorted(set(b)-set(a)),'changed':{k:[f for f in v if v[f]!=b.get(k,{}).get(f)]for k,v in a.items()if v!=b.get(k)}}
(O/'fresh-native-delivery-check.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items()if '_vs_'in k},default=str))
