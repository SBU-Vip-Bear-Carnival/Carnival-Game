# Hierarchical KiCad 10 schematic of the Giga bench rig.
# Page 1 = master block diagram, one sub-sheet per subsystem.
import uuid, math, os, sys, json
from sexp import *

OUT="."; PROJ="carnival_bench"; ROOT=""
U=lambda: '"%s"'%uuid.uuid4()
F='(effects (font (size 1.27 1.27)))'
FH='(effects (font (size 1.27 1.27)) (hide yes))'
G=2.54

# ---- custom symbols (multi-unit) -------------------------------------------
def custom(name, desc, units, halfw, ref="U", hidenum=False):
    subs=[]; maxtop=0
    for ui,(left,right) in enumerate(units,1):
        rows=max(len(left),len(right)); top=math.ceil((rows+1)*G/2/G)*G; maxtop=max(maxtop,top)
        ps=[]
        for side,lst in (('L',left),('R',right)):
            y=top-G
            for p in lst:
                if p:
                    num,nm=p; x=-(halfw+G) if side=='L' else halfw+G
                    ps.append(f'(pin passive line (at {x:.2f} {y:.2f} {0 if side=="L" else 180}) (length 2.54) (name "{nm}" {F}) (number "{num}" {F}))')
                y-=G
        subs.append(f'(symbol "{name}_{ui}_1" (rectangle (start {-halfw} {top:.2f}) (end {halfw} {-top:.2f}) (stroke (width 0.254) (type default)) (fill (type background))) {" ".join(ps)})')
    return (f'(symbol "carnival:{name}" {"(pin_numbers (hide yes))" if hidenum else ""} (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)'
            f'(property "Reference" "{ref}" (at 0 {maxtop+1.27:.2f} 0) {F})(property "Value" "{name}" (at 0 {-maxtop-1.27:.2f} 0) {F})'
            f'(property "Footprint" "" (at 0 0 0) {FH})(property "Datasheet" "" (at 0 0 0) {FH})(property "Description" "{desc}" (at 0 0 0) {FH})'
            f'{" ".join(subs)})')

D=lambda n,extra="": (f"D{n}", f"D{n}"+("/"+extra if extra else ""))
GIGA_UNITS=[
  # 1 power / system
  ([("VIN","VIN"),("5V","5V"),("3V3","3V3"),("IOREF","IOREF"),("AREF","AREF"),("VRTC","VRTC"),("OFF","OFF"),("RESET","RESET")],
   [("GND","GND"),None,("ICSP_MISO","ICSP_MISO"),("ICSP_MOSI","ICSP_MOSI"),("ICSP_SCK","ICSP_SCK"),None,("SDA1","SDA1"),("SCL1","SCL1")]),
  # 2 D0-D21
  ([D(0,"RX0"),D(1,"TX0"),D(2,"PWM"),D(3,"PWM"),D(4,"PWM"),D(5,"PWM"),D(6,"PWM"),D(7,"PWM"),D(8,"PWM/SCL2"),D(9,"PWM/SDA2"),D(10,"PWM/SS"),D(11,"PWM/MOSI1")],
   [D(12,"PWM/MISO1"),D(13,"PWM/SCK1"),D(14,"TX3"),D(15,"RX3"),D(16,"TX2"),D(17,"RX2"),D(18,"TX1"),D(19,"RX1"),D(20,"SDA"),D(21,"SCL")]),
  # 3 D22-D53
  ([D(n) for n in range(22,38)],[D(n) for n in range(38,54)]),
  # 4 D54-D75
  ([D(n) for n in range(54,65)],[D(n) for n in range(65,76)]),
  # 5 analog
  ([(f"A{n}",f"A{n}") for n in range(8)],
   [(f"A{n}",f"A{n}/ADC-only") for n in range(8,12)]+[None,("DAC0","DAC0/A12"),("DAC1","DAC1/A13"),None,("CANRX","CANRX"),("CANTX","CANTX")]),
]
TMC_L=[("8","EN"),("7","MS1"),("6","MS2"),("5","RX"),("4","TX"),("3","CLK"),("2","STEP"),("1","DIR"),None,("17","DIAG"),("18","INDEX"),("19","VREF")]
TMC_R=[("9","VM"),("10","GND"),("11","A2"),("12","A1"),("13","B1"),("14","B2"),("15","VIO"),("16","GND")]
LCD_L=[("1","VSS"),("2","VDD"),("3","V0"),("4","RS"),("5","RW"),("6","E"),None,("15","A/LED+"),("16","K/LED-")]
LCD_R=[(str(7+i),f"D{i}") for i in range(8)]
MP3_L=[("1","VCC"),("2","RX"),("3","TX"),("4","DAC_R"),("5","DAC_L"),("6","SPK_1"),("7","GND"),("8","SPK_2")]
MP3_R=[("16","BUSY"),("15","USB-"),("14","USB+"),("13","ADKEY_2"),("12","ADKEY_1"),("11","IO_2"),("10","GND"),("9","IO_1")]
CUSTOM={
 "carnival:LCD_1602":custom("LCD_1602","16x2 character LCD, HD44780 parallel interface",[(LCD_L,LCD_R)],10.16,"DS"),
 "carnival:MP3_TF_16P":custom("MP3_TF_16P","MP3-TF-16P V3.0 (DFPlayer Mini compatible)",[(MP3_L,MP3_R)],10.16),
 "carnival:Arduino_Giga_R1":custom("Arduino_Giga_R1","Arduino GIGA R1 WiFi header pins, from the mbed_giga 4.6.0 variant. 3.3 V logic, not 5 V tolerant.",GIGA_UNITS,15.24,"A",True),
 "carnival:TMC2209_Module":custom("TMC2209_Module","BIGTREETECH TMC2209 V1.3 StepStick",[(TMC_L,TMC_R)],10.16),
 "carnival:Buck_Module":custom("Buck_Module","Adjustable buck converter module, e.g. LM2596",[([("1","IN+"),("2","IN-")],[("3","OUT+"),("4","OUT-")])],7.62),
}

def unit_pins(sym,unit):
    out=[]
    for ch in find(sym,'symbol'):
        u=int(unq(ch[1]).rsplit('_',2)[-2])
        if u in (0,unit): out+=pins([ch])
    return out

pwrn=[0]; NINST={}
# wire colour code: motor coils in their real wire colours (team table: coil A black + green, coil B red + blue), rails by voltage
COLORS={"A1":(0,0,0),"A2":(0,150,0),"B1":(210,0,0),"B2":(0,70,220),"+12V":(235,120,0),"+5V":(210,0,0),"+3V3":(140,0,200),"GND":(0,0,0)}
def wcolor(net):
    if not net: return None
    n=net.split(":")[-1].rstrip("^v!|+FLAG") if net.startswith(("pwr:","hl:")) else net
    if n.startswith("pwr:"): n=n[4:]
    for k in ("A1","A2","B1","B2"):
        if n.endswith("_"+k) or n==k: return COLORS[k]
    for pre,c in (("BTN_",(0,140,140)),("LCD_",(150,90,0)),("LIM_",(220,0,150)),("STEP",(190,150,0)),("DIR",(190,150,0)),
                  ("UART",(0,0,130)),("MP3_",(0,0,130)),("STRIP",(0,170,220)),("SPK_",(110,110,110))):
        if n.startswith(pre): return c
    return COLORS.get(n)
class Sheet:
    def __init__(s,path): s.items=[]; s.libs={}; s.paths=[path]; s.ties={}
    def tie(s,key,name,out):
        # join a column of stub ends with one wire, then one power symbol
        pts=sorted(s.ties[key],key=lambda p:p[1]); s.wire(pts[0],pts[-1],name)
        for p in pts[1:-1]: s.items.append(f'(junction (at {p[0]:.2f} {p[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
        a=pts[-1]; e=(a[0]+out[0]*5.08,a[1]+out[1]*5.08)
        s.items.append(f'(junction (at {a[0]:.2f} {a[1]:.2f}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')
        s.wire(a,e,name); s.power(name,*e,out)
    def libdef(s,lid):
        if lid not in s.libs:
            if lid in CUSTOM: s.libs[lid]=parse(CUSTOM[lid])
            else:
                lib,n=lid.split(':'); x=libsym(lib,n); s.libs[lid]=[x[0],'"%s"'%lid]+x[2:]
        return s.libs[lid]
    def inst(s,ref,unit):
        refs=ref if isinstance(ref,tuple) else (ref,)*len(s.paths)
        return '(instances (project "%s" %s))'%(PROJ," ".join(f'(path "{p}" (reference "{r}") (unit {unit}))' for p,r in zip(s.paths,refs)))
    def power(s,name,x,y,out=None,hidev=False,vt=False):
        # out = direction the wire leaves the pin; the symbol body continues that way
        rs=[]
        for _ in range(NINST.get(id(s),1)): pwrn[0]+=1; rs.append(f"#PWR{pwrn[0]:03d}")
        s.libdef("power:"+name); r=rs[0]
        down=name=="GND"
        if out is None: out=(0,1) if down else (0,-1)
        rot=({(0,1):0,(1,0):90,(0,-1):180,(-1,0):270} if down else {(0,-1):0,(-1,0):90,(0,1):180,(1,0):270})[out]
        if name=="PWR_FLAG": rot=0
        side=out[0]!=0
        vx,vy=x+out[0]*(8.0 if side else 0),y+out[1]*(6.5 if vt else 4.5)
        fa=90 if vt else (rot if side else 0)
        s.items.append(f'(symbol (lib_id "power:{name}") (at {x:.2f} {y:.2f} {rot}) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {U()})'
          f'(property "Reference" "{r}" (at {x:.2f} {y:.2f} 0) {FH})(property "Value" "{name}" (at {vx:.2f} {vy:.2f} {fa}) {FH if name=="PWR_FLAG" or hidev else F})'
          f'(property "Footprint" "" (at 0 0 0) {FH})(property "Datasheet" "" (at 0 0 0) {FH})(pin "1" (uuid {U()})) {s.inst(tuple(rs),1)})')
    def label(s,kind,name,x,y,dx,dy,shape=None):
        ang,just={(-1,0):(180,"right"),(1,0):(0,"left"),(0,-1):(90,"left"),(0,1):(270,"right")}[(dx,dy)]
        if kind=="hl":
            s.items.append(f'(hierarchical_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {U()}))')
        else:
            s.items.append(f'(label "{name}" (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {U()}))')
    def wire(s,a,b,net=None):
        c=wcolor(net); st=f'(stroke (width {0.3 if c else 0}) (type default){" (color %d %d %d 1)"%c if c else ""})'
        s.items.append(f'(wire (pts (xy {a[0]:.2f} {a[1]:.2f}) (xy {b[0]:.2f} {b[1]:.2f})) {st} (uuid {U()}))')
    def text(s,t,x,y,size=1.27,bold=False):
        t=t.replace('"','\\"').replace('\n','\\n')
        s.items.append(f'(text "{t}" (exclude_from_sim no) (at {x:.2f} {y:.2f} 0) (effects (font (size {size} {size}){" (bold yes)" if bold else ""}) (justify left top)) (uuid {U()}))')
    def place(s,lid,ref,value,x,y,conns,unit=1,stub=5.08,lab=(0,-8),default=None):
        sym=s.libdef(lid); pl={p[0]:p for p in unit_pins(sym,unit)}
        allref=ref; ref=ref[0] if isinstance(ref,tuple) else ref
        LF='(effects (font (size 1.27 1.27)) (justify left))' if lab[0] else F
        ps=" ".join(f'(pin "{n}" (uuid {U()}))' for n in pl)
        s.items.append(f'(symbol (lib_id "{lid}") (at {x:.2f} {y:.2f} 0) (unit {unit}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {U()})'
          f'(property "Reference" "{ref}" (at {x+lab[0]:.2f} {y+lab[1]:.2f} 0) {LF})(property "Value" "{value}" (at {x+lab[0]:.2f} {y+lab[1]+G:.2f} 0) {LF})'
          f'(property "Footprint" "" (at 0 0 0) {FH})(property "Datasheet" "" (at 0 0 0) {FH}) {ps} {s.inst(allref,unit)})')
        for num,(_,_,px,py,a) in pl.items():
            c=conns.get(num,default)
            if c is None: continue
            st=stub
            while c.startswith("~"): c=c[1:]; st+=5.08   # each ~ lengthens this pin's stub
            ex,ey=x+px,y-py
            dx,dy=-round(math.cos(math.radians(a))),round(math.sin(math.radians(a)))
            if c=="NC": s.items.append(f'(no_connect (at {ex:.2f} {ey:.2f}) (uuid {U()}))'); continue
            sx,sy=ex+dx*st,ey+dy*st; s.wire((ex,ey),(sx,sy),c.replace("+FLAG",""))
            flag=c.endswith("+FLAG"); c=c.replace("+FLAG","")
            if c.startswith("pwr:"):
                n=c[4:]; vt=n.endswith("|"); n=n.rstrip("|"); hv=n.endswith("!"); n=n.rstrip("!")
                bend=n[-1] if n[-1] in "^v" else None; n=n.rstrip("^v")
                if bend:   # stub, then turn up or down so the symbol clears the neighbouring pins
                    o=(0,-1) if bend=="^" else (0,1); e=(sx,sy+o[1]*5.08); s.wire((sx,sy),e,n); s.power(n,*e,o,vt=vt)
                else: s.power(n,sx,sy,(dx,dy),hv,vt)
            elif c.startswith("tie:"): s.ties.setdefault(c[4:],[]).append((sx,sy))
            elif c.startswith("hl:"):
                _,shape,name=c.split(":",2); s.label("hl",name,sx,sy,dx,dy,shape)
            else: s.label("l",c,sx,sy,dx,dy)
            if flag: s.power("PWR_FLAG",sx,sy)
    def rail(s,name,x,y,shape="passive"):
        # hierarchical port for a power rail: hier label -> wire -> power symbol
        s.power(name,x+5.08,y); s.wire((x,y),(x+5.08,y),name); s.label("hl",name,x,y,-1,0,shape)
    def write(s,fn,title,page,extra="",rev="D",c1="Carnival Game - GIGA controller, two tracks"):
        tb=(f'(title_block (title "{title}") (date "2026-09-30") (rev "{rev}") (company "SBU VIP Bear Carnival")'
            f'(comment 1 "{c1}") (comment 2 "Matches tests/test_track_homing/track_homing.ino"){extra})')
        body=(f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid "{s.uuid}") (paper "{getattr(s,'paper','A3')}") {tb}'
              f'(lib_symbols {" ".join(dump(v) for v in s.libs.values())}) {" ".join(s.items)} {s.tail})')
        open(os.path.join(OUT,fn),"w").write(body)

