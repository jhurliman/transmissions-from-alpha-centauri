"""Read-only SCI1.1 resource inventory. Requires compiled tools/third_party blast bridge."""
import argparse,ctypes,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('game',type=Path);p.add_argument('--decoder',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
lib=ctypes.CDLL(str(a.decoder.resolve()));dec=lib.blast_memory;dec.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint];dec.restype=ctypes.c_int
m=(a.game/'RESOURCE.MAP').read_bytes();vol=(a.game/'RESOURCE.000').read_bytes();dirs=[]
for i in range(0,len(m),3):
 t,off=struct.unpack_from('<BH',m,i);dirs.append((t&31,off))
 if t==255:break
names={0:'view',1:'pic',2:'script',3:'text',4:'sound',6:'vocab',7:'font',9:'patch',11:'palette',15:'message',16:'map',17:'heap'}
counts={};views=[]
for (t,start),(_,end) in zip(dirs,dirs[1:]):
 assert (end-start)%5==0
 counts[names.get(t,str(t))]=(end-start)//5
 if t!=0:continue
 for i in range(start,end,5):
  num=int.from_bytes(m[i:i+2],'little');off=int.from_bytes(m[i+2:i+5],'little')*2
  rt,rn,packed,size,comp=struct.unpack_from('<BHHHH',vol,off);assert rt&31==t and rn==num and comp==19
  src=vol[off+9:off+9+packed];out=ctypes.create_string_buffer(size);assert dec(src,len(src),out,size)==0
  d=out.raw;header=struct.unpack_from('<H',d)[0]+2;n=d[2];ls,cs=d[12:14];assert header>=16 and ls>=16 and cs>=32
  loops=[];unique={}
  for j in range(n):
   k=j;seen=set()
   while d[header+k*ls]!=255:
    assert k not in seen;seen.add(k);k=d[header+k*ls];assert k<n
   base=header+k*ls;nc=d[base+2];co=struct.unpack_from('<I',d,base+12)[0]
   loops.append(dict(loop=j,source_loop=k,cels=nc,mirrored=k!=j))
   for c in range(nc):
    at=co+c*cs;w,h,x,y=struct.unpack_from('<hhhh',d,at);assert w>=0 and h>=0 and at+cs<=len(d)
    unique[at]=dict(width=w,height=h,x_offset=x,y_offset=y)
  views.append(dict(id=num,loops=loops,stored_cels=list(unique.values()),logical_cels=sum(x['cels'] for x in loops)))
r=dict(source=str(a.game.resolve()),resource_map_sha256=hashlib.sha256(m).hexdigest(),resource_counts=counts,view_totals=dict(resources=len(views),loops=sum(len(v['loops']) for v in views),logical_cels=sum(v['logical_cels'] for v in views),stored_cels=sum(len(v['stored_cels']) for v in views)),views=views)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='views'},indent=2))
