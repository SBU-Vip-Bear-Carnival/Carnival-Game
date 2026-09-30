# compare a KiCad netlist with the intended connections: every intended net must appear exactly, and nothing else may join
import sys, json, xml.etree.ElementTree as E
r=E.parse(sys.argv[1]).getroot(); want=json.load(open(sys.argv[2]))
got=[sorted(f"{x.get('ref')}.{x.get('pin')}" for x in n if not x.get('ref').startswith('#')) for n in r.find('nets')]
got=[g for g in got if g]
gs={tuple(g) for g in got}
missing=[n for n,v in want.items() if tuple(v) not in gs]
wanted={tuple(v) for v in want.values()}
extra=[g for g in got if tuple(g) not in wanted and len(g)>1]
print(f"intended nets: {len(want)} | found exactly: {len(want)-len(missing)} | missing/wrong: {missing or 'none'}")
print("unexpected multi-pin nets (shorts or strays):", extra or "none")
