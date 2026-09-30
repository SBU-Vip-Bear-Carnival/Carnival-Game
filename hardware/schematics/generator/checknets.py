import sys, xml.etree.ElementTree as E
r=E.parse(sys.argv[1]).getroot(); mode=sys.argv[2]
nets=[sorted(f"{x.get('ref')}.{x.get('pin')}" for x in n) for n in r.find('nets') if not n.get('name').startswith('unconnected')]
names={n.get('name'):sorted(f"{x.get('ref')}.{x.get('pin')}" for x in n) for n in r.find('nets')}
nc=sum(1 for n in r.find('nets') if n.get('name').startswith('unconnected'))
# pin ids differ between versions: full uses board pin numbers, simple uses D-numbers
if mode=="full":
    import json; NUM=json.load(open("num.json")); P=lambda n,i=0:"A1."+NUM[n][i]
else:
    P=lambda n,i=0:"A1."+n.replace("~","").split("/")[0].lstrip("D") if n not in("VIN","GND") else "A1."+n
want=[[P("D43"),"SW1.1"],[P("D41"),"SW2.1"],[P("D39"),"SW3.1"],[P("D37"),"SW4.1"],[P("D35"),"SW5.1"],
 [P("D53"),"U1.2"],[P("D51"),"U1.1"],[P("D25"),"SW6."+("2" if mode=="full" else "1")],[P("D23"),"SW7."+("2" if mode=="full" else "1")],
 [P("D49"),"U4.2"],[P("D47"),"U4.1"],[P("D29"),"SW8."+("2" if mode=="full" else "1")],[P("D27"),"SW9."+("2" if mode=="full" else "1")],
 [P("D22"),"DS1.4"],[P("D24"),"DS1.6"],[P("D26"),"DS1.11"],[P("D28"),"DS1.12"],[P("D30"),"DS1.13"],[P("D32"),"DS1.14"],
 [P("D1/TX0"),"R3.1"],["R3.2","U5.2"],[P("D0/RX0"),"U5.3"],["LS1.1","U5.6"],["LS1.2","U5.8"],["DS1.3","RV1.2"],["DS1.15","R2.2"],
 [P("~D13"),"R1.1"],["J1.2","R1.2"]]+[[f"M{t}.{p}",f"{u}.{q}"] for t,u in ((1,"U1"),(2,"U4")) for p,q in ((1,12),(2,11),(3,13),(4,14))]
bad=[w for w in want if sorted(w) not in nets]
print("signal nets missing:",bad or "none")
v12=names.get("+12V",[]); v5=names.get("+5V",[]); v33=names.get("+3V3",[]); g=names.get("GND",[])
print("+12V:",v12); print("+5V:",v5); print("+3V3:",v33); print("GND pins:",len(g),"| no-connect pins:",nc)
print("driver GNDs:",all(f"{u}.{p}" in g for u in("U1","U4") for p in (6,7,8,10,16)), "| VIN on +12V:", P("VIN") in v12)
extra=[k for k,v in names.items() if not k.startswith('unconnected') and k not in("+12V","+5V","+3V3","GND") and v not in [sorted(w) for w in want]]
print("unexpected nets:",extra or "none")
