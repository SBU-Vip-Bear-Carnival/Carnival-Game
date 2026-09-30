import re
LIB="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
TOK=re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)')
def parse(t):
    stack=[[]]
    for m in TOK.finditer(t):
        s=m.group(1)
        if s=='(': stack.append([])
        elif s==')': x=stack.pop(); stack[-1].append(x)
        else: stack[-1].append(s)
    return stack[0][0]
def dump(x):
    if isinstance(x,list): return '('+' '.join(dump(i) for i in x)+')'
    return x
def unq(s): return s[1:-1] if s.startswith('"') else s
def find(x,tag): return [i for i in x if isinstance(i,list) and i and i[0]==tag]
_cache={}
def libsym(lib,name):
    if lib not in _cache: _cache[lib]=parse(open(LIB+lib+".kicad_sym").read())
    for s in find(_cache[lib],'symbol'):
        if unq(s[1])==name: return s
    raise KeyError(name)
def pins(sym):
    out=[]
    def walk(x):
        for i in x:
            if isinstance(i,list):
                if i and i[0]=='pin':
                    at=find(i,'at')[0]; num=unq(find(i,'number')[0][1]); nm=unq(find(i,'name')[0][1])
                    out.append((num,nm,float(at[1]),float(at[2]),float(at[3]) if len(at)>3 else 0.0))
                else: walk(i)
    walk(sym); return out

_libsym_raw=libsym
def libsym(lib,name):
    s=_libsym_raw(lib,name)
    ext=find(s,'extends')
    if not ext: return s
    base=libsym(lib,unq(ext[0][1])); bn=unq(base[1])
    props={unq(p[1]):p for p in find(s,'property')}
    out=[s[0],s[1]]
    for i in base[2:]:
        if isinstance(i,list) and i[0]=='property' and unq(i[1]) in props: out.append(props[unq(i[1])])
        elif isinstance(i,list) and i[0]=='symbol': out.append([i[0],i[1].replace(bn,name,1)]+i[2:])
        else: out.append(i)
    return out
