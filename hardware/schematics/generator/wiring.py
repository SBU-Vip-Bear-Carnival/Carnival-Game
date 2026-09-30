# Flat wiring-diagram engine: places parts, then routes every net pin-to-pin on a 2.54 mm grid.
# Wires of different nets never share a grid segment; they may only cross at right angles.
import heapq, math, uuid
import kicore as K
from kicore import Sheet, U
from sexp import find, unq, pins as allpins

G=2.54
def gc(v): return int(round(v/G))

def geom(sym,unit):
    """body bbox (symbol coords) and pins for one unit of a parsed lib symbol"""
    xs=[];ys=[];ps=[]
    for ch in find(sym,'symbol'):
        u=int(unq(ch[1]).rsplit('_',2)[-2])
        if u not in (0,unit): continue
        for it in ch[2:]:
            if not isinstance(it,list): continue
            t=it[0]
            if t=='rectangle':
                for k in ('start','end'):
                    v=find(it,k)[0]; xs.append(float(v[1])); ys.append(float(v[2]))
            elif t=='circle':
                c=find(it,'center')[0]; r=float(find(it,'radius')[0][1]); xs+= [float(c[1])-r,float(c[1])+r]; ys+=[float(c[2])-r,float(c[2])+r]
            elif t=='polyline' or t=='arc':
                for xy in (find(find(it,'pts')[0],'xy') if t=='polyline' else [find(it,k)[0] for k in ('start','mid','end')]):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
        ps+=allpins([ch])
    if not xs: xs=[0];ys=[0]
    return (min(xs),min(ys),max(xs),max(ys)),ps

class Diagram:
    def __init__(s,sheet,W,H):
        s.sh=sheet; s.W=gc(W); s.H=gc(H)
        s.occ={}      # (gx,gy) -> [net or None, kind]   kind: B body, N node, H, V, X crossing
        s.parts=[]    # (ref,unit,x,y,lid)
        s.pinpos={}   # (ref,pinnum) -> (gx,gy,outdx,outdy)
        s.nets={}; s.paths={}; s.color={}; s.stublen={}; s.leads=[]; s.symnets=set()
    def block(s,x0,y0,x1,y1):
        for gx in range(gc(min(x0,x1)),gc(max(x0,x1))+1):
            for gy in range(gc(min(y0,y1)),gc(max(y0,y1))+1): s.occ[(gx,gy)]=[None,'B']
    def part(s,lid,ref,value,x,y,unit=1,textpad=True,stub=2):
        sym=s.sh.libdef(lid); (bx0,by0,bx1,by1),ps=geom(sym,unit)
        toppins=any(a==270 for *_,a in ps)                 # pins leave through the top edge
        if toppins:
            pbot=min([by0]+[py for _,_,_,py,_ in ps]); lab=(0,-pbot+5.08); ty=y-pbot+2.54
        else:
            ptop=max([by1]+[py for _,_,_,py,_ in ps]); lab=(0,-ptop-7.62); ty=y-ptop-10.16
        s.sh.place(lid,ref,value,x,y,{},unit=unit,lab=lab)
        s.block(x+bx0,y-by1,x+bx1,y-by0)
        if textpad: s.block(x-len(value)*0.6,ty,x+len(value)*0.6,ty+5.08)
        for num,*_ in ps: s.stublen[(ref if not isinstance(ref,tuple) else ref[0],num)]=stub
        for num,nm,px,py,a in ps:
            ex,ey=x+px,y-py
            bdx,bdy=round(math.cos(math.radians(a))),-round(math.sin(math.radians(a)))
            L=0
            for pdef in []: pass
            s.pinpos[(ref if not isinstance(ref,tuple) else ref[0],num)]=(gc(ex),gc(ey),-bdx,-bdy)
            # the pin line between its end and the body belongs to the part
            k=1
            while True:
                c=(gc(ex)+bdx*k,gc(ey)+bdy*k)
                if k>8 or (c in s.occ and s.occ[c][1]=='B'): break
                s.occ[c]=[None,'B']; k+=1
        s.parts.append((ref,unit,x,y,lid,ps))
    def net(s,name,*pins_): s.nets[name]=list(pins_)
    def finish_pins(s,stub=2):
        s.pinnet={}
        for n,v in s.nets.items():
            for p in v: s.pinnet[p]=n
        s.stubend={}
        for (ref,num),(gx,gy,dx,dy) in s.pinpos.items():
            n=s.pinnet.get((ref,num))
            if not n:
                s.occ[(gx,gy)]=[None,'B']; s.sh.items.append(f'(no_connect (at {gx*G:.2f} {gy*G:.2f}) (uuid {U()}))'); continue
            s.occ[(gx,gy)]=[n,'N']
        # every connected pin gets its own straight lead first, so no pin can be walled in
        for (ref,num),(gx,gy,dx,dy) in s.pinpos.items():
            n=s.pinnet.get((ref,num))
            if not n: continue
            k=s.stublen.get((ref,num),stub)
            while k>0 and any(s.occ.get((gx+dx*i,gy+dy*i),[0,''])[1]=='B' for i in range(1,k+1)): k-=1
            cells=[(gx+dx*i,gy+dy*i) for i in range(0,k+1)]
            for c in cells[1:]:
                cur=s.occ.get(c)
                if cur and cur[0]!=n: k=0; break
            cells=cells[:k+1]
            for i,c in enumerate(cells):
                s.occ[c]=[n,'N'] if i in (0,len(cells)-1) else [n,'H' if dy==0 else 'V']
            s.stubend[(ref,num)]=(cells[-1],set(cells))
            if k>0:
                lead=[cells[0],cells[-1]]; s.paths.setdefault(n,[]).append(lead); s.leads.append(lead)
    def route(s,net,start,targets):
        (sx,sy,odx,ody)=start
        BEND=6; CROSS=4
        dist={}; prev={}; pq=[]
        st=(sx,sy,odx,ody); heapq.heappush(pq,(0,st)); dist[st]=0; prev[st]=None
        while pq:
            d,(x,y,dx,dy)=heapq.heappop(pq)
            if d>dist.get((x,y,dx,dy),1e9): continue
            if (x,y) in targets and d>0: return s.unwind(prev,(x,y,dx,dy))
            cell=s.occ.get((x,y))
            crossing=cell is not None and cell[0]!=net and cell[1] in('H','V')
            for ndx,ndy in ((1,0),(-1,0),(0,1),(0,-1)):
                if (ndx,ndy)==(-dx,-dy): continue
                turn=(ndx,ndy)!=(dx,dy)
                if turn and crossing: continue
                nx,ny=x+ndx,y+ndy
                if not (0<nx<s.W and 0<ny<s.H): continue
                c2=s.occ.get((nx,ny))
                if (nx,ny) in targets:
                    k2=c2[1] if c2 else ''
                    if (k2=='H' and ndy==0) or (k2=='V' and ndx==0): continue      # would run along the net, not join it
                elif not s.ok(net,nx,ny,ndx,ndy): continue
                nd=d+1+(BEND if turn else 0)+(CROSS if c2 and c2[0]!=net else 0)
                kk=(nx,ny,ndx,ndy)
                if nd<dist.get(kk,1e9): dist[kk]=nd; prev[kk]=(x,y,dx,dy); heapq.heappush(pq,(nd,kk))
        return None
    def ok(s,net,x,y,dx,dy):
        c=s.occ.get((x,y))
        if c is None: return True
        if c[1] in('B','X','N'): return False
        if c[0]==net: return False            # own-net cells that are not yet part of this tree
        return (c[1]=='H' and dx==0) or (c[1]=='V' and dy==0)
    def unwind(s,prev,end):
        pts=[end[:2]]; k=end
        while prev[k] is not None: k=prev[k]; pts.append(k[:2])
        return pts[::-1]
    def commit(s,net,pts):
        corners=[pts[0]]
        for i in range(1,len(pts)-1):
            a,b,c=pts[i-1],pts[i],pts[i+1]
            if (b[0]-a[0],b[1]-a[1])!=(c[0]-b[0],c[1]-b[1]): corners.append(b)
        corners.append(pts[-1])
        cs=set(corners)
        for i,(x,y) in enumerate(pts):
            cur=s.occ.get((x,y))
            if (x,y) in cs:
                if not cur or cur[0]==net: s.occ[(x,y)]=[net,'N']
            else:
                kind='H' if pts[i-1][1]==y else 'V'
                if cur and cur[0]!=net: s.occ[(x,y)]=[cur[0],'X']
                elif cur and cur[0]==net: s.occ[(x,y)]=[net,'N']
                else: s.occ[(x,y)]=[net,kind]
        s.paths.setdefault(net,[]).append(corners)
    def place_symbols(s):
        # nets drawn as a symbol at every pin (ground): no wire runs round the sheet
        for net in s.symnets:
            groups={}
            for p in s.nets[net]:
                if p not in s.stubend: continue
                (ex,ey),_=s.stubend[p]; _,_,dx,dy=s.pinpos[p]
                key=(p[0],dx,dy,ex if dx else ey)
                groups.setdefault(key,[]).append((ey,ex) if dx else (ex,ey))
            for (ref,dx,dy,fixed),mem in groups.items():
                mem.sort(); runs=[[mem[0]]]
                for m in mem[1:]:
                    (runs[-1].append(m) if m[0]==runs[-1][-1][0]+1 else runs.append([m]))
                for run in runs:
                    pts=[(m[1],m[0]) if dx else (m[0],m[1]) for m in run]   # back to (x,y)
                    if len(pts)>1:
                        s.paths.setdefault(net,[]).append([pts[0],pts[-1]])
                        for q in [(x,y) for x in range(min(pts[0][0],pts[-1][0]),max(pts[0][0],pts[-1][0])+1)
                                        for y in range(min(pts[0][1],pts[-1][1]),max(pts[0][1],pts[-1][1])+1)]:
                            s.occ[q]=[net,'N']
                        mid=pts[len(pts)//2]; ext=(mid[0]+dx*2,mid[1]+dy*2)
                        s.paths[net].append([mid,ext]); s.occ[(mid[0]+dx,mid[1]+dy)]=[net,'N']; at=ext
                    else: at=pts[0]
                    s.occ[at]=[net,'N']
                    s.sh.power(net,at[0]*G,at[1]*G,(dx,dy),hidev=True)
                    for k in (1,2):                                           # the symbol's own footprint, its column only
                        c=(at[0]+dx*k,at[1]+dy*k)
                        if c not in s.occ: s.occ[c]=[None,'B']
    def run(s,order=None):
        s.finish_pins(); s.place_symbols(); fails=[]
        for net in (order or [n for n in s.nets if n not in s.symnets]):
            pins_=[p for p in s.nets[net] if p in s.stubend]
            first=pins_[0]; tree={s.stubend[first][0]}
            rest=pins_[1:]
            while rest:
                rest.sort(key=lambda p:min(abs(s.stubend[p][0][0]-t[0])+abs(s.stubend[p][0][1]-t[1]) for t in tree))
                p=rest.pop(0); (ex,ey),cells=s.stubend[p]; _,_,dx,dy=s.pinpos[p]
                path=s.route(net,(ex,ey,dx,dy),tree)
                if path is None: fails.append((net,p)); continue
                s.commit(net,path); tree|=set(path)|{cells and s.stubend[p][0]}
        return fails
    def trim(s):
        # cut each pin lead back to the last point where a wire actually joins it
        for net,plist in s.paths.items():
            ends={}
            for c in plist:
                for p in (c[0],c[-1]): ends[p]=ends.get(p,0)+1
            for c in plist:
                if not any(c is l for l in s.leads) or net in s.symnets: continue
                a,b=c
                if ends.get(b,0)>1: continue
                dx=(b[0]>a[0])-(b[0]<a[0]); dy=(b[1]>a[1])-(b[1]<a[1])
                n=max(abs(b[0]-a[0]),abs(b[1]-a[1])); keep=0
                for i in range(1,n+1):
                    q=(a[0]+dx*i,a[1]+dy*i)
                    if ends.get(q,0)>0 and q!=b: keep=i
                c[1]=(a[0]+dx*keep,a[1]+dy*keep)
            s.paths[net]=[c for c in plist if c[0]!=c[-1]]
    def emit(s):
        s.trim(); deg={}
        for net,plist in s.paths.items():
            for corners in plist:
                for a,b in zip(corners,corners[1:]):
                    s.sh.wire((a[0]*G,a[1]*G),(b[0]*G,b[1]*G),s.color.get(net,net))
                    for p in (a,b): deg[(net,p)]=deg.get((net,p),0)+1
        # a junction wherever a net's wire ends on the middle of its own wire, or 3+ ends meet
        mids={}
        for net,plist in s.paths.items():
            for corners in plist:
                for a,b in zip(corners,corners[1:]):
                    xs=range(min(a[0],b[0]),max(a[0],b[0])+1); ys=range(min(a[1],b[1]),max(a[1],b[1])+1)
                    for x in xs:
                        for y in ys:
                            if (x,y) not in (a,b): mids[(net,(x,y))]=1
        pinends={(s.pinnet.get(k),(v[0],v[1])) for k,v in s.pinpos.items()}
        for (net,p),n in deg.items():
            if (net,p) in mids or n+((net,p) in pinends)>=3:
                s.sh.items.append(f'(junction (at {p[0]*G:.2f} {p[1]*G:.2f}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
    def labels(s,names):
        # name each signal net once, on a cell that is plain wire of that net only (never a crossing or a joint)
        for net in names:
            best=None
            for corners in s.paths.get(net,[]):
                for a,b in zip(corners,corners[1:]):
                    if a[1]!=b[1]: continue
                    lo,hi=min(a[0],b[0]),max(a[0],b[0])
                    run=[x for x in range(lo+1,hi) if s.occ.get((x,a[1]))==[net,'H']]
                    # longest stretch of consecutive clean cells
                    seg=[];cur=[]
                    for x in run:
                        if cur and x!=cur[-1]+1: seg.append(cur); cur=[]
                        cur.append(x)
                    if cur: seg.append(cur)
                    for sgm in seg:
                        if best is None or len(sgm)>len(best[0]): best=(sgm,a[1])
            if best and len(best[0])>=3:
                x=best[0][len(best[0])//2]*G; y=best[1]*G
                s.sh.items.append(f'(label "{net}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {U()}))')

    def pinlabels(s,refs,skip=()):
        # print the signal name on the lead of each used pin of the given parts, right where it leaves the pin
        for (ref,num),(gx,gy,dx,dy) in s.pinpos.items():
            if ref not in refs: continue
            net=s.pinnet.get((ref,num))
            if not net or net in skip: continue
            for i in (1,2,3):
                c=(gx+dx*i,gy+dy*i)
                if s.occ.get(c)==[net,'H' if dy==0 else 'V']:
                    ang,just={(1,0):(0,"left"),(-1,0):(180,"right"),(0,-1):(90,"left"),(0,1):(270,"right")}[(dx,dy)]
                    s.sh.items.append(f'(label "{net}" (at {c[0]*G:.2f} {c[1]*G:.2f} {ang}) (effects (font (size 1.27 1.27) (bold yes)) (justify {just} bottom)) (uuid {U()}))')
                    break
