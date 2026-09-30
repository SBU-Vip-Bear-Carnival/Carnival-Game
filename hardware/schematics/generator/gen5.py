# Rev E: FULL = one A1 sheet, every part drawn like the real thing, every pin, every connection a real wire.
import sys, os, json, uuid
src=open("gen4.py").read(); src=src[:src.index("def pinnum(")]
ns={"__name__":"g4"}; exec(src.replace("BASE=sys.argv[1]","BASE=''"),ns)
CUSTOM,NUM,phys,pin,rect,circ,poly,txt=(ns[k] for k in ("CUSTOM","NUM","phys","pin","rect","circ","poly","txt"))
import kicore as K
from kicore import Sheet
from wiring import Diagram

# grid-true passives and a grid-true stepper (router works on 2.54 mm)
CUSTOM["carnival:R_H"]=phys("R_H","Resistor",[([rect(-2.54,1.02,2.54,-1.02,"bg")],[pin("1","~",-5.08,0,0),pin("2","~",5.08,0,180)])],"R",hidename=True)
CUSTOM["carnival:R_V"]=phys("R_V","Resistor",[([rect(-1.02,2.54,1.02,-2.54,"bg")],[pin("1","~",0,5.08,270),pin("2","~",0,-5.08,90)])],"R",hidename=True)
CUSTOM["carnival:C_V"]=phys("C_V","Capacitor",[([poly([(-2.03,0.64),(2.03,0.64)],0.4),poly([(-2.03,-0.64),(2.03,-0.64)],0.4)],[pin("1","~",0,5.08,270,4.44),pin("2","~",0,-5.08,90,4.44)])],"C",hidename=True)
CUSTOM["carnival:CP_V"]=phys("CP_V","Polarised capacitor",[([rect(-2.03,1.02,2.03,0.51,"none"),rect(-2.03,-0.51,2.03,-1.02,"black"),txt("+",-2.8,1.9,1.0)],
                         [pin("1","~",0,5.08,270,4.06),pin("2","~",0,-5.08,90,4.06)])],"C",hidename=True)
CUSTOM["carnival:POT_V"]=phys("POT_V","Potentiometer",[([rect(-1.02,2.54,1.02,-2.54,"bg"),poly([(2.54,0),(1.27,0)],0.3),poly([(1.27,0),(1.9,0.5)],0.3),poly([(1.27,0),(1.9,-0.5)],0.3)],
                         [pin("1","~",0,5.08,270),pin("3","~",0,-5.08,90),pin("2","~",5.08,0,180,2.54)])],"RV",hidename=True)
ng=[rect(-10.16,10.16,10.16,-10.16,"grey",0.3), circ(5.08,0,3.6), circ(5.08,0,1.0,"black")]+[circ(x,y,0.9) for x in (-7.62,7.62) for y in (7.62,-7.62)]+[txt("NEMA17",0,-8.6,0.9)]
CUSTOM["carnival:Stepper_NEMA17"]=phys("Stepper_NEMA17","Bipolar stepper: coil A = black + green, coil B = red + blue",
    [(ng,[pin("2","A2/green",-12.7,5.08,0),pin("1","A1/black",-12.7,2.54,0),pin("3","B1/red",-12.7,0,0),pin("4","B2/blue",-12.7,-2.54,0)])],"M")

def finish(OUT,proj):
    open(os.path.join(OUT,"carnival.kicad_sym"),"w").write('(kicad_symbol_lib (version 20251024) (generator "gen5.py") '+" ".join(CUSTOM.values())+')')
    open(os.path.join(OUT,"sym-lib-table"),"w").write('(sym_lib_table\n  (version 7)\n  (lib (name "carnival")(type "KiCad")(uri "${KIPRJMOD}/carnival.kicad_sym")(options "")(descr "Carnival Game parts"))\n)\n')
    open(os.path.join(OUT,f"{proj}.kicad_pro"),"w").write(json.dumps({"meta":{"filename":f"{proj}.kicad_pro","version":1}},indent=2))

def build(OUT,order=None):
    os.makedirs(OUT,exist_ok=True); K.OUT=OUT; K.PROJ="carnival_full"; K.ROOT=str(uuid.uuid4())
    sh=Sheet("/"+K.ROOT); sh.uuid=K.ROOT; sh.tail='(sheet_instances (path "/" (page "1")))'; sh.paper="A1"
    D=Diagram(sh,841,594)
    P=D.part
    # --- the GIGA: board (edge headers) + detail drawings of every other header -----------
    P("carnival:GIGA_R1_WiFi","A1","Arduino GIGA R1 WiFi",254.0,279.4,unit=1,stub=6)
    P("carnival:GIGA_R1_WiFi","A1","D22-D53 header",381.0,279.4,unit=2,stub=10)
    for u,(x,y) in {3:(502.92,462.28),4:(591.82,462.28),5:(680.72,447.04),6:(680.72,482.6)}.items():
        P("carnival:GIGA_R1_WiFi","A1","GIGA header",x,y,unit=u)
    # --- controls, drivers, motors, limit switches ----------------------------------------
    for i,(r,v) in enumerate([("SW1","FORWARD"),("SW2","STOP"),("SW3","SLOWER"),("SW4","FASTER"),("SW5","REVERSE")]):
        P("Switch:SW_Push",r,v,487.68,139.7+i*15.24)
    for t,(y,u,m,c,sa,sb) in {1:(254.0,"U1","M1","C1","SW6","SW7"),2:(365.76,"U4","M2","C5","SW8","SW9")}.items():
        P("carnival:TMC2209_StepStick",u,f"TMC2209 driver {t}",574.04,y,stub=3)
        P("carnival:Stepper_NEMA17",m,f"Track {t} motor",678.18,y+2.54,stub=3)
        P("carnival:CP_V",c,"100uF 25V",538.48,y-33.02)
        P("carnival:Microswitch",sa,f"Track {t} HOME limit",764.54,y-20.32,stub=3)
        P("carnival:Microswitch",sb,f"Track {t} END limit",764.54,y+30.48,stub=3)
    # --- screen, audio, LED strip -------------------------------------------------------------
    P("carnival:LCD1602_Module","DS1","16x2 LCD",149.86,165.1)
    P("carnival:POT_V","RV1","10k contrast",78.74,114.3)
    P("carnival:R_V","R2","330R",99.06,114.3)
    P("carnival:MP3_TF_16P_Module","U5","MP3-TF-16P",139.7,370.84)
    P("carnival:R_H","R3","1k",99.06,342.9)
    P("Device:Speaker","LS1","Speaker 8R 3W",78.74,393.7)
    P("carnival:R_H","R1","330R",561.34,99.06)
    P("carnival:WS2812B_Strip","J1","WS2812B strip x74",604.52,99.06)
    P("carnival:CP_V","C4","1000uF 10V",584.2,68.58)
    # --- power ----------------------------------------------------------------------------------
    P("carnival:PSU_12V","PS1","12 V 5 A",55.88,480.06)
    P("power:PWR_FLAG","#FLG01","PWR_FLAG",96.52,462.28,textpad=False); P("power:PWR_FLAG","#FLG02","PWR_FLAG",96.52,500.38,textpad=False)
    P("carnival:Buck_Module_Phys","U2","XL4015 buck, set 5.0 V",182.88,480.06)
    P("power:PWR_FLAG","#FLG03","PWR_FLAG",226.06,457.2,textpad=False)
    P("Regulator_Linear:AMS1117-3.3","U3","AMS1117-3.3",287.02,480.06)
    P("carnival:C_V","C2","10uF",256.54,505.46); P("carnival:C_V","C3","22uF",317.5,505.46)
    P("Connector_Generic:Conn_01x02","J3","5V rail out",368.3,480.06); P("Connector_Generic:Conn_01x02","J4","3.3V rail out",408.94,480.06)
    for f in ("#FLG01","#FLG02","#FLG03"):     # a flag's wire leaves downward, under the flag
        gx,gy,_,_=D.pinpos[(f,"1")]; D.pinpos[(f,"1")]=(gx,gy,0,1)

    A=lambda name,i=0:("A1",NUM[name][i])
    N=D.net
    for d,sw in (("D43","SW1"),("D41","SW2"),("D39","SW3"),("D37","SW4"),("D35","SW5")): N("BTN_"+{"SW1":"FORWARD","SW2":"STOP","SW3":"SLOWER","SW4":"FASTER","SW5":"REVERSE"}[sw],A(d),(sw,"1"))
    N("STEP1",A("D53"),("U1","2")); N("DIR1",A("D51"),("U1","1")); N("STEP2",A("D49"),("U4","2")); N("DIR2",A("D47"),("U4","1"))
    N("LIM_HOME1",A("D25"),("SW6","3")); N("LIM_END1",A("D23"),("SW7","3")); N("LIM_HOME2",A("D29"),("SW8","3")); N("LIM_END2",A("D27"),("SW9","3"))
    for d,p in (("D22","4"),("D24","6"),("D26","11"),("D28","12"),("D30","13"),("D32","14")): N({"4":"LCD_RS","6":"LCD_E","11":"LCD_D4","12":"LCD_D5","13":"LCD_D6","14":"LCD_D7"}[p],A(d),("DS1",p))
    N("LCD_V0",("RV1","2"),("DS1","3")); N("LCD_LED_A",("R2","2"),("DS1","15"))
    N("UART1_TX",A("D1/TX0"),("R3","1")); N("MP3_RX",("R3","2"),("U5","2")); N("UART1_RX",("U5","3"),A("D0/RX0"))
    N("SPK_P",("U5","6"),("LS1","1")); N("SPK_N",("U5","8"),("LS1","2"))
    N("STRIP_DIN",A("~D13"),("R1","1")); N("STRIP_R",("R1","2"),("J1","2"))
    for t,u,m in ((1,"U1","M1"),(2,"U4","M2")):
        for dp,mp,c in (("12","1","A1"),("11","2","A2"),("13","3","B1"),("14","4","B2")): N(f"M{t}_{c}",(u,dp),(m,mp))
    N("+12V",("PS1","1"),("#FLG01","1"),("U2","1"),("A1","L11"),("C1","1"),("U1","9"),("C5","1"),("U4","9"))
    N("+5V",("U2","3"),("#FLG03","1"),("U3","3"),("C2","1"),("J3","1"),("RV1","1"),("R2","1"),("DS1","2"),("U5","1"),("C4","1"),("J1","1"))
    N("+3V3",("U3","2"),("C3","1"),("J4","1"),("U1","15"),("U4","15"))
    N("GND",("PS1","2"),("#FLG02","1"),("U2","2"),("U2","4"),("U3","1"),("C2","2"),("C3","2"),("J3","2"),("J4","2"),("A1","L9"),
      ("RV1","3"),("DS1","1"),("DS1","5"),("DS1","16"),("U5","7"),("U5","10"),
      *[(sw,"2") for sw in ("SW1","SW2","SW3","SW4","SW5")],
      *[(u,p) for u in ("U1","U4") for p in ("8","7","6","10","16")],("C1","2"),("C5","2"),
      *[(sw,"1") for sw in ("SW6","SW7","SW8","SW9")],("J1","3"),("C4","2"))
    sig=[n for n in D.nets if n not in ("+12V","+5V","+3V3","GND")]
    D.symnets={"GND"}
    fails=D.run(order or sig+["+12V","+3V3","+5V"])
    build.order=order or sig+["+12V","+3V3","+5V"]
    D.emit(); D.labels(sig); D.pinlabels({"A1"},skip=())
    L=ns["LEG"] if "LEG" in ns else ""
    sh.text("CARNIVAL GAME - FULL WIRING DIAGRAM (every part, every pin, every connection)",12.7,12.7,3.0,True)
    sh.text("Every line is a real wire between two pins. A dot is a joint; lines that cross without a dot do not touch.\n"
            "GROUND is drawn as the ground symbol at each pin (no ground wire runs round the sheet): every ground symbol is the same connection.\n"
            "Parts are drawn to look like the real hardware: the GIGA board (top view, USB up) with every header pin, the TMC2209 StepSticks, NEMA17 motors,\n"
            "lever microswitches, the 16x2 LCD module, the MP3-TF-16P module, the WS2812B strip, the buck module and the 12 V PSU. X = pin not used.\n"
            "WIRE COLOURS  motor coil A: A1 black, A2 green / coil B: B1 red, B2 blue  |  +12V orange  +5V red  +3V3 purple  GND black  |  buttons teal  LCD brown  limit switches pink\n"
            "              STEP/DIR gold  MP3 serial navy  LED data cyan  speaker grey.  Every used GIGA pin has its signal name printed on its lead.\n"
            "Not yet confirmed on hardware: Track 1 limits 25/23 (guessed); Track 2, LCD and MP3 pins proposed. Confirmed 2026-09-30: buttons 35-43, Track 1 STEP 53 / DIR 51.",12.7,20.32)
    sh.write("carnival_full.kicad_sch","Full wiring diagram",1,rev="E",c1="Carnival Game - FULL wiring diagram (every pin, every wire)")
    finish(OUT,"carnival_full")
    json.dump({n:sorted(f"{r}.{p}" for r,p in v if not r.startswith("#")) for n,v in D.nets.items()},open(os.path.join(OUT,"..","expected_full.json"),"w"),indent=1)
    return fails

if __name__=="__main__":
    # rip-up and reroute: nets that failed go first on the next pass
    order=None
    for attempt in range(8):
        f=build(sys.argv[1],order)
        if not f: break
        failed=list(dict.fromkeys(n for n,_ in f)); order=failed+[n for n in build.order if n not in failed]
        print(f"pass {attempt+1}: {len(failed)} nets failed, rerouting them first:",failed)
    print("route failures:",f or "none")
