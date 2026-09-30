# Rev D: full (hierarchical, board-shaped parts, every pin) + simplified (one page, used pins only).
import sys, os, json, math, uuid
import kicore as K
from kicore import Sheet, custom, CUSTOM, G, F, FH, U, NINST

BASE=sys.argv[1]
STROKE='(stroke (width 0.254) (type default))'
def rect(x1,y1,x2,y2,fill="none",w=0.254):
    f={"none":"(fill (type none))","bg":"(fill (type background))","board":"(fill (type color) (color 0 129 132 0.18))",
       "black":"(fill (type outline))","grey":"(fill (type color) (color 150 150 150 0.5))","green":"(fill (type color) (color 120 200 90 0.45))",
       "purple":"(fill (type color) (color 110 60 160 0.18))","blue":"(fill (type color) (color 40 90 200 0.18))","hdr":"(fill (type color) (color 30 30 30 0.85))"}[fill]
    return f'(rectangle (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f}) (stroke (width {w}) (type default)) {f})'
def circ(x,y,r,fill="none"): return f'(circle (center {x:.2f} {y:.2f}) (radius {r}) {STROKE} (fill (type {"outline" if fill=="black" else fill})))'
def poly(pts,w=0.254): return '(polyline (pts %s) (stroke (width %s) (type default)) (fill (type none)))'%(" ".join(f"(xy {x:.2f} {y:.2f})" for x,y in pts),w)
def txt(t,x,y,sz=1.27,rot=0): return f'(text "{t}" (at {x:.2f} {y:.2f} {rot*10}) (effects (font (size {sz} {sz}))))'
NF='(effects (font (size 0.85 0.85)))'
def pin(num,name,x,y,ang,L=2.54): return f'(pin passive line (at {x:.2f} {y:.2f} {ang}) (length {L}) (name "{name}" {F}) (number "{num}" {NF}))'
def phys(name,desc,units,ref="U",hidenum=False,hidename=False):
    subs=[f'(symbol "{name}_{i}_1" {" ".join(g)} {" ".join(p)})' for i,(g,p) in enumerate(units,1)]
    opts=("(pin_numbers (hide yes))" if hidenum else "")+("(pin_names (hide yes))" if hidename else "(pin_names (offset 0.762))")
    return (f'(symbol "carnival:{name}" {opts} (exclude_from_sim no) (in_bom yes) (on_board yes)'
            f'(property "Reference" "{ref}" (at 0 0 0) {F})(property "Value" "{name}" (at 0 -2.54 0) {F})'
            f'(property "Footprint" "" (at 0 0 0) {FH})(property "Datasheet" "" (at 0 0 0) {FH})(property "Description" "{desc}" (at 0 0 0) {FH}) {" ".join(subs)})')

# ======================= GIGA R1 WiFi, board-shaped ==========================================
# Positions read off Arduino's ABX00063 full pinout (page 1, top view, USB at the top), true scale.
k=101.6/608; X=lambda px:-26.67+(px-333)*k; Y=lambda py:50.8-(py-80)*k
LEFT=[(33.02,["OFF","GND","VRTC"]),(22.86,["NC","IOREF","RESET","3V3","5V","GND","GND","VIN"]),
      (0.0,[f"A{i}/D{76+i}" for i in range(8)]),(-22.86,["A8","A9","A10","A11","DAC0/D84","DAC1/D85","CANRX/D93","CANTX/D94"])]
RIGHT=[(33.02,["D101/SCL1","D102/SDA1","AREF","GND","~D13","~D12","~D11","~D10","~D9","~D8"]),
       (5.08,["~D7","~D6","~D5","~D4","~D3","~D2","D1/TX0","D0/RX0"]),
       (-17.78,["D14/TX3","D15/RX3","D16/TX2","D17/RX2","D18/TX1","D19/RX1","D20/SDA","D21/SCL"])]
NUM={}   # display name -> list of pin numbers
def edge(groups,side):
    out=[]; n=0
    for y0,names in groups:
        for i,nm in enumerate(names):
            n+=1; num=f"{side}{n}"; NUM.setdefault(nm,[]).append(num)
            x=-30.48 if side=="L" else 30.48
            out.append(pin(num,nm,x,y0-i*G,0 if side=="L" else 180,3.81))
    return out
bw=26.67
board_g=[f'(polyline (pts (xy {-bw} 50.8) (xy {bw} 50.8) (xy {bw} -50.8) (xy {-bw+3.81} -50.8) (xy {-bw} -46.99) (xy {-bw} 50.8)) (stroke (width 0.3) (type default)) (fill (type color) (color 0 129 132 0.18)))',
  rect(X(370),Y(68),X(408),Y(155),"black"), txt("AUDIO",X(389),Y(160),1.0),
  rect(X(433),Y(68),X(512),Y(150),"grey"), txt("USB-A",X(472),Y(110),1.27),
  rect(X(540),Y(75),X(595),Y(118),"grey"), txt("USB-C",X(567),Y(97),1.0),
  rect(X(335),Y(90),X(353),Y(108)), circ(X(344),Y(99),0.9), txt("BOOT0",X(344),Y(113),0.8),
  rect(X(630),Y(90),X(648),Y(108)), circ(X(639),Y(99),0.9), txt("RESET",X(639),Y(113),0.8),
  circ(X(610),Y(95),1.0), txt("u.FL",X(610),Y(105),0.8), circ(X(520),Y(93),0.8), txt("RGB",X(520),Y(101),0.8),
  rect(X(413),Y(185),X(570),Y(222),"hdr"), txt("J6 CAMERA (2x10)",X(491),Y(234),1.0),
  rect(X(458),Y(290),X(541),Y(370),"black"), txt("STM32H747",X(500),Y(378),1.0),
  rect(X(406),Y(445),X(458),Y(490),"hdr"), txt("JTAG",X(432),Y(498),0.9),
  rect(X(470),Y(448),X(518),Y(488),"hdr"), txt("SPI",X(494),Y(498),0.9),
  rect(X(400),Y(548),X(583),Y(600),"hdr"), txt("J5 DISPLAY (2x12)",X(491),Y(610),1.0),
  rect(X(370),Y(630),X(645),Y(665),"hdr"), txt("D22-D53 (2x18)",X(508),Y(675),1.0),
  txt("ARDUINO GIGA R1 WiFi",1.27,-4.6,1.4), txt("top view, USB up",1.27,-6.9,0.9)]
unitA=(board_g, edge(LEFT,"L")+edge(RIGHT,"R"))

def dual(title,rows,prefix,note=""):
    # 2-row header drawn like Arduino's detail view: pin 1 top-left, odd left, even right
    top=(len(rows)-1)*G/2; top=math.ceil(top/G)*G
    g=[rect(-17.78,top+2.54,17.78,top-len(rows)*G,"bg"), rect(-1.27-1.27,top+1.27,1.27+1.27,top-len(rows)*G+1.27,"hdr",0.15),
       txt(title,0,top+4.3,1.27)]+([txt(note,0,top-len(rows)*G-1.6,1.0)] if note else [])
    ps=[]
    for r,(a,b) in enumerate(rows):
        y=top-r*G
        for col,(nm,x,ang) in enumerate(((a,-20.32,0),(b,20.32,180))):
            num=f"{prefix}{2*r+col+1}"; NUM.setdefault(nm,[]).append(num); ps.append(pin(num,nm,x,y,ang))
        g.append(circ(-1.27,y,0.45,"black")); g.append(circ(1.27,y,0.45,"black"))
    g.append(txt("1",-3.6,top+1.6,0.9))
    return (g,ps)
unitB=dual("D22-D53 HEADER",[("5V","5V")]+[(f"D{n}",f"D{n+1}") for n in range(22,53,2)]+[("GND","GND")],"H",
           "inner row = even D, board-edge row = odd D")
unitC=dual("J6 CAMERA",[("3V3","GND"),("D101/SCL1","D102/SDA1")]+[(f"D{n}",f"D{n+1}") for n in range(54,66,2)]+[("D66","D67"),("D66","D67")],"J6-",
           "D66/D67 appear on two rows (Arduino: duplicated)")
unitD=dual("J5 DISPLAY",[("DSI_D1N","DSI_D1P"),("GND","GND"),("DSI_CKN","DSI_CKP"),("GND","GND"),("DSI_D0N","DSI_D0P"),("GND","GND"),
           ("D68","D69"),("D70","D71"),("D72","D73"),("D74","D75"),("5V","GND"),("3V3","VIN")],"J5-","DSI pins: display only, no GPIO")
unitE=dual("JTAG",[("3V3","SWDIO"),("GND","SWCLK"),("GND","NC"),("NC","NC"),("GND","RESET")],"JT")
unitF=dual("SPI",[("D89/CIPO","5V"),("D91/SCK","D90/COPI"),("RESET","GND")],"SP")
CUSTOM["carnival:GIGA_R1_WiFi"]=phys("GIGA_R1_WiFi","Arduino GIGA R1 WiFi (ABX00063). Board-shaped, true scale, every header pin.",
                                   [unitA,unitB,unitC,unitD,unitE,unitF],"A")

# ======================= TMC2209 StepStick (BTT V1.3) ===========================================
tmcL=[("8","EN"),("7","MS1"),("6","MS2"),("5","RX"),("4","TX"),("3","CLK"),("2","STEP"),("1","DIR")]
tmcR=[("9","VM"),("10","GND"),("11","A2"),("12","A1"),("13","B1"),("14","B2"),("15","VIO"),("16","GND")]
tg=[rect(-12.7,12.7,12.7,-12.7,"purple",0.3), rect(-3.81,-0.64,3.81,-6.99,"black"), txt("TMC2209",0,-8.9,1.0),
    circ(0,3.3,1.4), poly([(-1,3.3),(1,3.3)],0.2), txt("Vref pot",0,1.1,0.75), txt("BTT V1.3",0,-11.0,0.9)]
tp=[pin(n,nm,-15.24,7.62-i*G,0) for i,(n,nm) in enumerate(tmcL)]+[pin(n,nm,15.24,7.62-i*G,180) for i,(n,nm) in enumerate(tmcR)]
tp+=[pin(n,nm,x,15.24,270) for n,nm,x in (("17","DIAG",-2.54),("18","INDEX",0),("19","VREF",2.54))]
CUSTOM["carnival:TMC2209_StepStick"]=phys("TMC2209_StepStick","BIGTREETECH TMC2209 V1.3 StepStick, top view",[(tg,tp)])

# ======================= 16x2 LCD module ==========================================================
lg=[rect(-40.64,17.78,40.64,-17.78,"blue",0.3), rect(-30.48,7.62,30.48,-10.16,"green"), txt("16 x 2 LCD (HD44780)",0,-1.27,1.8),
    rect(-35.56,17.0,5.08,14.2,"hdr",0.15)]+[circ(x,y,1.3) for x in (-38.1,38.1) for y in (15.24,-15.24)]
lnames=["VSS","VDD","V0","RS","RW","E","D0","D1","D2","D3","D4","D5","D6","D7","A","K"]
lp=[pin(str(i+1),nm,-33.02+i*G,20.32,270) for i,nm in enumerate(lnames)]
CUSTOM["carnival:LCD1602_Module"]=phys("LCD1602_Module","1602 character LCD module, 16-pin header along the top edge",[(lg,lp)],"DS")

# ======================= MP3-TF-16P ===============================================================
mL=["VCC","RX","TX","DAC_R","DAC_L","SPK_1","GND","SPK_2"]; mR=["BUSY","USB-","USB+","ADKEY_2","ADKEY_1","IO_2","GND","IO_1"]
mg=[rect(-10.16,10.16,10.16,-12.7,"blue",0.3), rect(-5.08,5.08,5.08,-2.54,"black"), rect(-6.35,-5.08,6.35,-11.43,"grey"), txt("microSD",0,-8.3,1.0),
    txt("MP3-TF-16P",0,7.4,1.0)]
mp=[pin(str(i+1),nm,-12.7,7.62-i*G,0) for i,nm in enumerate(mL)]+[pin(str(16-i),nm,12.7,7.62-i*G,180) for i,nm in enumerate(mR)]
CUSTOM["carnival:MP3_TF_16P_Module"]=phys("MP3_TF_16P_Module","MP3-TF-16P V3.0 (DFPlayer Mini compatible), top view",[(mg,mp)])

# ======================= buck module, NEMA17, microswitch, strip, PSU ===============================
bg=[rect(-20.32,10.16,20.32,-10.16,"blue",0.3), circ(-5.08,0,4.5), txt("L",-5.08,0,1.5), rect(6.35,6.35,11.43,1.27), circ(8.89,3.81,1.2), txt("adj",8.89,-0.2,0.8),
    txt("BUCK 12V -> 5V",0,-7.6,1.1)]
bp=[pin("1","IN+",-22.86,2.54,0),pin("2","IN-",-22.86,-2.54,0),pin("3","OUT+",22.86,2.54,180),pin("4","OUT-",22.86,-2.54,180)]
CUSTOM["carnival:Buck_Module_Phys"]=phys("Buck_Module_Phys","Buck converter module, 3 A+ (XL4015 class)",[(bg,bp)])
ng=[rect(-10.16,10.16,10.16,-10.16,"grey",0.3), circ(5.08,0,3.6), circ(5.08,0,1.0,"black")]+[circ(x,y,0.9) for x in (-7.62,7.62) for y in (7.62,-7.62)]+[txt("NEMA17",0,-8.6,0.9)]
np_=[pin("1","A1/black",-12.7,3.81,0),pin("2","A2/green",-12.7,1.27,0),pin("3","B1/red",-12.7,-1.27,0),pin("4","B2/blue",-12.7,-3.81,0)]
CUSTOM["carnival:Stepper_NEMA17"]=phys("Stepper_NEMA17","Bipolar stepper: coil A = black + green, coil B = red + blue",[(ng,np_)],"M")
wg=[rect(-8.89,5.08,8.89,-5.08,"bg",0.3), poly([(-7.62,5.08),(6.35,8.89)],0.35), circ(6.35,8.89,1.0)]
wp=[pin("1","C",-5.08,-7.62,90),pin("2","NC",0,-7.62,90),pin("3","NO",5.08,-7.62,90)]
CUSTOM["carnival:Microswitch"]=phys("Microswitch","Lever microswitch, pins in order C (common), NC (middle, unused), NO",[(wg,wp)],"SW")
sg=[rect(-2.54,3.81,45.72,-3.81,"bg",0.3)]+[rect(5.08+i*10.16,1.9,10.16+i*10.16,-1.9,"none") for i in range(4)]+[circ(7.62+i*10.16,0,1.2) for i in range(4)]+[txt("WS2812B x 74  ->",25.4,-5.3,1.0)]
sp=[pin("1","+5V",-5.08,2.54,0),pin("2","DIN",-5.08,0,0),pin("3","GND",-5.08,-2.54,0)]
CUSTOM["carnival:WS2812B_Strip"]=phys("WS2812B_Strip","WS2812B strip, input end: +5V, DIN, GND pads",[(sg,sp)],"J")
pg=[rect(-12.7,7.62,12.7,-7.62,"grey",0.3), txt("12 V PSU",0,2.54,1.4), txt("5 A",0,-1.27,1.1)]
pp=[pin("1","+V",15.24,2.54,180),pin("2","-V",15.24,-2.54,180)]
CUSTOM["carnival:PSU_12V"]=phys("PSU_12V","12 V DC power supply, output terminals",[(pg,pp)],"PS")

def pinnum(sym_name,name,i=0): return NUM[name][i]

# ==================================================================================================
# FULL VERSION (hierarchical)
# ==================================================================================================
def full(OUT):
    os.makedirs(OUT,exist_ok=True); K.OUT=OUT; K.PROJ="carnival_full"; K.ROOT=str(uuid.uuid4()); ROOT=K.ROOT
    root=Sheet("/"+ROOT); root.uuid=ROOT; root.tail='(sheet_instances (path "/" (page "1")))'
    def block(name,fn,page,x,y,w,h,pins_,reuse=None):
        sid=str(uuid.uuid4()); ps=[]
        for (pn,shape,side,pos) in pins_:
            px,py,ang,just={'L':(x,pos,180,"left"),'R':(x+w,pos,0,"right"),'T':(pos,y,90,"right"),'B':(pos,y+h,270,"left")}[side]
            ps.append(f'(pin "{pn}" {shape} (at {px:.2f} {py:.2f} {ang}) (uuid {U()}) (effects (font (size 1.27 1.27)) (justify {just})))')
        root.items.append(f'(sheet (at {x:.2f} {y:.2f}) (size {w:.2f} {h:.2f}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)'
            f'(stroke (width 0.1524) (type solid)) (fill (color 255 255 225 1.0000)) (uuid "{sid}")'
            f'(property "Sheetname" "{name}" (at {x:.2f} {y-0.72:.2f} 0) (effects (font (size 1.524 1.524) (bold yes)) (justify left bottom)))'
            f'(property "Sheetfile" "{fn}" (at {x:.2f} {y+h+0.6:.2f} 0) (effects (font (size 1.27 1.27)) (justify left top)))'
            f'{" ".join(ps)} (instances (project "{K.PROJ}" (path "/{ROOT}" (page "{page}")))))')
        if reuse: reuse.paths.append(f"/{ROOT}/{sid}"); NINST[id(reuse)]=len(reuse.paths); return reuse
        sh=Sheet(f"/{ROOT}/{sid}"); sh.uuid=str(uuid.uuid4()); sh.tail=""; return sh
    def rp(name,x,y,dx,dy,L=5.08):
        e=(x+dx*L,y+dy*L); root.wire((x,y),e,name); root.power(name,*e,(dx,dy))

    LX,LW=30.48,50.8; MX,MW=121.92,63.5; DX,DW=226.06,40.64; TX,TW=304.8,50.8
    btn={"BTN_FORWARD":48.26,"BTN_STOP":53.34,"BTN_SLOWER":58.42,"BTN_FASTER":63.5,"BTN_REVERSE":68.58}
    lcd={"LCD_RS":93.98,"LCD_E":99.06,"LCD_D4":104.14,"LCD_D5":109.22,"LCD_D6":114.3,"LCD_D7":119.38}
    uart={"UART1_TX":147.32,"UART1_RX":152.4}
    Y0={1:40.64,2:124.46}
    step=lambda t:{"STEP":Y0[t]+10.16,"DIR":Y0[t]+15.24}
    coil=lambda t:{"COIL_A1":Y0[t]+10.16,"COIL_A2":Y0[t]+15.24,"COIL_B1":Y0[t]+20.32,"COIL_B2":Y0[t]+25.4}
    lim=lambda t:{"LIM_HOME":Y0[t]+53.34,"LIM_END":Y0[t]+58.42}
    mp=[(n,"input","L",y) for n,y in btn.items()]+[(n,"output","L",y) for n,y in lcd.items()]+[("UART1_TX","output","L",147.32),("UART1_RX","input","L",152.4)]
    for t in (1,2):
        mp+=[(f"{n}{t}","output","R",y) for n,y in step(t).items()]+[(f"{n}{t}","input","R",y) for n,y in lim(t).items()]
    mp+=[("STRIP_DIN","output","R",213.36),("+12V","passive","B",139.7),("GND","passive","B",165.1)]
    mcu=block("MCU - Arduino GIGA R1 WiFi","mcu.kicad_sch",2,MX,40.64,MW,190.5,mp); mcu.paper="A2"
    pwr=block("Power","power.kicad_sch",3,LX,175.26,LW,35.56,[("+12V","passive","R",182.88),("+5V","passive","R",190.5),("+3V3","passive","R",198.12),("GND","passive","L",190.5)])
    drv=None; trk=None; pg=4
    for t in (1,2):
        dp=[(n,"input","L",y) for n,y in step(t).items()]+[(n,"output","R",y) for n,y in coil(t).items()]+[("+12V","passive","T",236.22),("+3V3","passive","T",256.54),("GND","passive","B",246.38)]
        drv=block(f"Motor driver {t}","driver.kicad_sch",pg,DX,Y0[t],DW,35.56,dp,reuse=drv); pg+=1
        tp=[(n,"input","L",y) for n,y in coil(t).items()]+[(n,"output","L",y) for n,y in lim(t).items()]+[("GND","passive","R",Y0[t]+58.42)]
        trk=block(f"Track {t} - motor + limit switches","track.kicad_sch",pg,TX,Y0[t],TW,66.04,tp,reuse=trk); pg+=1
    ctl=block("Controls - 5 buttons","controls.kicad_sch",8,LX,40.64,LW,33.02,[(n,"output","R",y) for n,y in btn.items()]+[("GND","passive","L",58.42)])
    scr=block("Screen - 16x2 LCD","screen.kicad_sch",9,LX,86.36,LW,40.64,[(n,"input","R",y) for n,y in lcd.items()]+[("+5V","passive","L",99.06),("GND","passive","L",109.22)])
    aud=block("Audio - MP3-TF-16P","audio.kicad_sch",10,LX,139.7,LW,20.32,[("UART1_TX","input","R",147.32),("UART1_RX","output","R",152.4),("+5V","passive","L",144.78),("GND","passive","L",154.94)])
    led=block("LED strip","leds.kicad_sch",11,TX,203.2,TW,22.86,[("STRIP_DIN","input","L",213.36),("+5V","passive","R",208.28),("GND","passive","R",218.44)])

    for n,y in {**btn,**lcd,**uart}.items(): root.wire((LX+LW,y),(MX,y))
    for t in (1,2):
        for n,y in step(t).items(): root.wire((MX+MW,y),(DX,y))
        for n,y in coil(t).items(): root.wire((DX+DW,y),(TX,y),n)
        for n,y in lim(t).items(): root.wire((MX+MW,y),(TX,y))
        rp("+12V",DX+10.16,Y0[t],0,-1); rp("+3V3",DX+30.48,Y0[t],0,-1); rp("GND",DX+20.32,Y0[t]+35.56,0,1); rp("GND",TX+TW,Y0[t]+58.42,1,0)
    root.wire((MX+MW,213.36),(TX,213.36))
    rp("+12V",139.7,231.14,0,1); rp("GND",165.1,231.14,0,1)
    for n,y in (("+12V",182.88),("+5V",190.5),("+3V3",198.12)): rp(n,LX+LW,y,1,0,7.62)
    for n,y in (("GND",190.5),("GND",58.42),("+5V",99.06),("GND",109.22),("+5V",144.78),("GND",154.94)): rp(n,LX,y,-1,0)
    rp("+5V",TX+TW,208.28,1,0); rp("GND",TX+TW,218.44,1,0)
    root.text("CARNIVAL GAME - FULL SCHEMATIC",25.4,12.7,2.54,True)
    root.text("WIRE COLOURS  motor coil A: A1 black, A2 green   coil B: B1 red, B2 blue   |   +12V orange   +5V red   +3V3 purple   GND black   signals green",25.4,30.48)
    root.text("Signal chain, left to right: buttons / screen / audio  ->  GIGA  ->  motor driver  ->  motor.  Limit switches report back to the GIGA.\n"
              "Driver 1 and 2 are one page used twice; so are Track 1 and 2. Power rails are global. Simplified one-page version: ../simplified/",25.4,20.32)
    root.text("PAGES 1 Master  2 MCU  3 Power  4 Driver 1  5 Track 1  6 Driver 2  7 Track 2  8 Controls  9 Screen  10 Audio  11 LED strip\n"
              "REVISIONS  A single page  B hierarchical  C two tracks, LCD, MP3, 12 V to VIN  D board-shaped parts, every pin, driver->motor chain",25.4,246.38)

    # ---- MCU (A2): the board, and a detail drawing of every other header -------------
    used={"D43":"hl:input:BTN_FORWARD","D41":"hl:input:BTN_STOP","D39":"hl:input:BTN_SLOWER","D37":"hl:input:BTN_FASTER","D35":"hl:input:BTN_REVERSE",
          "D53":"hl:output:STEP1","D51":"hl:output:DIR1","D25":"hl:input:LIM_HOME1","D23":"hl:input:LIM_END1",
          "D49":"hl:output:STEP2","D47":"hl:output:DIR2","D29":"hl:input:LIM_HOME2","D27":"hl:input:LIM_END2",
          "D22":"hl:output:LCD_RS","D24":"hl:output:LCD_E","D26":"hl:output:LCD_D4","D28":"hl:output:LCD_D5","D30":"hl:output:LCD_D6","D32":"hl:output:LCD_D7",
          "D1/TX0":"hl:output:UART1_TX","D0/RX0":"hl:input:UART1_RX","~D13":"hl:output:STRIP_DIN"}
    conns={NUM[k][0]:v for k,v in used.items()}
    conns[NUM["VIN"][0]]="pwr:+12V"; conns[NUM["GND"][1]]="pwr:GND"   # power-header VIN and first power-header GND
    GIGA="carnival:GIGA_R1_WiFi"
    for unit,(x,y,lab) in {1:(111.76,187.96,(0,-58.42)),2:(261.62,160.02,(0,-33.02)),3:(261.62,261.62,(0,-22.86)),4:(411.48,160.02,(0,-27.94)),
                           5:(411.48,256.54,(0,-12.7)),6:(411.48,309.88,(0,-10.16))}.items():
        mcu.place(GIGA,"A1","Arduino GIGA R1 WiFi",x,y,conns,unit=unit,stub=7.62,default="NC",lab=lab)
    mcu.rail("+12V",40.64,375.92); mcu.rail("GND",40.64,386.08)
    mcu.text("ARDUINO GIGA R1 WiFi - every header pin, laid out like Arduino's official pinout (ABX00063, top view, USB up).\n"
             "Left: board with its edge headers at true scale. Right: detail drawings of the 2x18 header, J6, J5, JTAG and SPI.\n"
             "X = not used. Pin names are Arduino's labels (~ = PWM). Pin numbers: L/R = board edge top to bottom, H/J5-/J6-/JT/SP = header position.\n"
             "Powered from 12 V on VIN (6-24 V). 5V and 3V3 are OUTPUTS, left open. All GPIO are 3.3 V, NOT 5 V tolerant.\n"
             "PROPOSED, not yet wired: Track 2 (49/47, limits 29/27), LCD (22-32 even), MP3 on Serial1 (D0/D1). GUESSED: Track 1 limits 25/23.",40.64,25.4)

    # ---- power -------------------------------------------------------------------------------
    pwr.place("carnival:PSU_12V","PS1","12 V 5 A",50.8,81.28,{"1":"pwr:+12V+FLAG","2":"pwr:GND+FLAG"},lab=(0,-10.16))
    pwr.place("carnival:Buck_Module_Phys","U2","XL4015 buck, set 5.0 V",134.62,81.28,{"1":"pwr:+12V","2":"pwr:GND","3":"pwr:+5V+FLAG","4":"pwr:GND"},lab=(0,-15.24))
    pwr.place("Regulator_Linear:AMS1117-3.3","U3","AMS1117-3.3",210.82,81.28,{"1":"pwr:GND","2":"pwr:+3V3","3":"pwr:+5V"},lab=(0,-10.16))
    pwr.place("Device:C","C2","10uF",195.58,111.76,{"1":"pwr:+5V","2":"pwr:GND"},stub=2.54,lab=(3.81,-1.27))
    pwr.place("Device:C","C3","22uF",226.06,111.76,{"1":"pwr:+3V3","2":"pwr:GND"},stub=2.54,lab=(3.81,-1.27))
    pwr.place("Connector_Generic:Conn_01x02","J3","5V rail out",134.62,142.24,{"1":"pwr:+5V","2":"pwr:GND"})
    pwr.place("Connector_Generic:Conn_01x02","J4","3.3V rail out",210.82,142.24,{"1":"pwr:+3V3","2":"pwr:GND"})
    for i,n in enumerate(("+12V","+5V","+3V3","GND")): pwr.rail(n,279.4,71.12+i*10.16)
    pwr.text("ONE 12 V PSU FEEDS EVERYTHING\n+12V -> both drivers' VM (pages 4, 6), GIGA VIN (page 2), buck -> +5V.\n"
             "+5V  -> LED strip, LCD, MP3 player, AMS1117 -> +3V3 (both drivers' VIO).\n"
             "BUDGET 5 V: strip ~1.4 A at brightness 80 + MP3 up to ~0.6 A + LCD ~40 mA = ~2 A -> 3 A+ buck. 12 V: size the PSU at 5 A.\n"
             "Set the buck trimpot to 5.0 V with a meter BEFORE connecting anything. Rails use regulators, not voltage dividers.",50.8,172.72)

    # ---- driver (used twice) ---------------------------------------------------------------------
    drv.place("carnival:TMC2209_StepStick",("U1","U4"),"TMC2209 V1.3 (BTT)",127,101.6,
      {"8":"tie:L","7":"tie:L","6":"tie:L","5":"NC","4":"NC","3":"NC","2":"hl:input:STEP","1":"hl:input:DIR","17":"NC","18":"NC","19":"NC",
       "9":"pwr:+12V^","10":"pwr:GND!","11":"hl:output:COIL_A2","12":"hl:output:COIL_A1","13":"hl:output:COIL_B1","14":"hl:output:COIL_B2",
       "15":"pwr:+3V3!","16":"pwr:GNDv"},lab=(0,-24.13),stub=7.62)
    drv.tie("L","GND",(-1,0))
    drv.place("Device:C_Polarized",("C1","C5"),"100uF 25V",160.02,71.12,{"1":"pwr:+12V","2":"pwr:GND"},stub=2.54,lab=(3.81,-1.27))
    for i,n in enumerate(("+12V","+3V3","GND")): drv.rail(n,254,71.12+i*10.16)
    drv.text("THE GIGA TALKS TO THE DRIVER (STEP, DIR); THE DRIVER TALKS TO THE MOTOR (A1 A2 B1 B2).\n"
             "Drawn as the real StepStick, top view: EN MS1 MS2 RX TX CLK STEP DIR down the left, VM GND A2 A1 B1 B2 VIO GND down the right,\n"
             "DIAG INDEX VREF pads on top. Left pin numbers are BTT's header order (DIR = 1 ... EN = 8); right side numbered 9-16 top to bottom.\n"
             "EN, MS1, MS2 -> GND: always on, 1/8 microstep.  CLK open.  RX/TX unused: current from the Vref pot, Vref = I_rms x 1.41.\n"
             "VIO on +3V3 to match the GIGA's 3.3 V logic.  C1 right at VM.  Never plug a motor in with VM powered.",63.5,149.86)

    # ---- track (used twice): motor + both limit switches -------------------------------------
    trk.place("carnival:Stepper_NEMA17",("M1","M2"),"Track stepper",152.4,93.98,
      {"1":"hl:input:COIL_A1","2":"hl:input:COIL_A2","3":"hl:input:COIL_B1","4":"hl:input:COIL_B2"},lab=(0,-13.97),stub=10.16)
    for i,(r,v,n) in enumerate([(("SW6","SW8"),"LIMIT - home end","LIM_HOME"),(("SW7","SW9"),"LIMIT - far end","LIM_END")]):
        trk.place("carnival:Microswitch",r,v,127+i*50.8,149.86,{"1":"pwr:GND","2":f"hl:output:{n}","3":"NC"},lab=(0,-15.24))
    for i,n in enumerate(("GND",)): trk.rail(n,254,71.12)
    trk.text("ONE TRACK: the motor that moves the carriage, and a limit switch at each end of the rail.\n"
             "Motor wires (team table): coil A = BLACK + GREEN -> driver A1/A2, coil B = RED + BLUE -> driver B1/B2. Wires drawn in those colours.\n"
             "If the motor buzzes instead of turning, the two coils are crossed: check black-green and red-blue each read a few ohms.\n"
             "Microswitches: C -> GND, NO -> GIGA pin, NC unused. Pressed = LOW (INPUT_PULLUP).",63.5,190.5)

    # ---- controls, screen, audio, strip --------------------------------------------------------
    for i,(r,v,n) in enumerate([("SW1","FORWARD","BTN_FORWARD"),("SW2","STOP","BTN_STOP"),("SW3","SLOWER","BTN_SLOWER"),("SW4","FASTER","BTN_FASTER"),("SW5","REVERSE","BTN_REVERSE")]):
        ctl.place("Switch:SW_Push",r,v,101.6,63.5+i*20.32,{"1":f"hl:output:{n}","2":"pwr:GND"})
    ctl.rail("GND",180.34,63.5)
    ctl.text("Each button: GIGA pin -> button -> GND. INPUT_PULLUP, pressed = LOW. No resistors.\n"
             "Testing: the buttons drive the track. In the game: they drive the menu on the LCD.\n"
             "The bench button-to-pin layout is known to be wrong (2026-09-30): remap in firmware.",63.5,172.72)
    L={"1":"pwr:GND|","2":"~pwr:+5V|","3":"~~~LCD_V0","4":"~~~hl:input:LCD_RS","5":"pwr:GND|","6":"~~~hl:input:LCD_E","7":"NC","8":"NC","9":"NC","10":"NC",
       "11":"~~~hl:input:LCD_D4","12":"~~~hl:input:LCD_D5","13":"~~~hl:input:LCD_D6","14":"~~~hl:input:LCD_D7","15":"~~~~~~LCD_LED_A","16":"pwr:GND|"}
    scr.place("carnival:LCD1602_Module","DS1","16x2 LCD module",177.8,139.7,L,lab=(43.18,-22.86),stub=2.54)
    scr.place("Device:R_Potentiometer","RV1","10k contrast",101.6,76.2,{"1":"pwr:+5V","2":"LCD_V0","3":"pwr:GND"},stub=2.54,lab=(-10.16,-1.27))
    scr.place("Device:R","R2","330R",101.6,116.84,{"1":"pwr:+5V","2":"LCD_LED_A"},stub=2.54,lab=(3.81,-1.27))
    for i,n in enumerate(("+5V","GND")): scr.rail(n,279.4,71.12+i*10.16)
    scr.text("Drawn as the module: 16 pins along the top edge, pin 1 (VSS) on the left.\n"
             "4-bit mode: RS, E, D4-D7 from the GIGA; D0-D3 unused; RW -> GND.  V0 from a 10k pot (bench: fixed 12k).\n"
             "Backlight A through 330R to 5 V (team table: 320R, not a standard value).  Team table leaves pin 11 (D4) blank: it must be wired.",63.5,172.72)
    aud.place("carnival:MP3_TF_16P_Module","U5","MP3-TF-16P V3.0",177.8,101.6,
      {"1":"pwr:+5V^","2":"MP3_RX_R","3":"hl:output:UART1_RX","6":"SPK_P","7":"pwr:GND!","8":"SPK_N","10":"pwr:GND"},default="NC",lab=(0,-15.24))
    aud.place("Device:R","R3","1k",119.38,88.9,{"1":"hl:input:UART1_TX","2":"MP3_RX_R"},stub=2.54,lab=(3.81,-1.27))
    aud.place("Device:Speaker","LS1","Speaker 8R, 3 W max",119.38,127,{"1":"SPK_P","2":"SPK_N"},lab=(5.08,-7.62))
    for i,n in enumerate(("+5V","GND")): aud.rail(n,279.4,71.12+i*10.16)
    aud.text("GIGA Serial1: D1 (TX) -> R3 1k -> player RX;  player TX -> D0 (RX).  R3 cuts the serial-line hiss.\n"
             "Speaker straight on SPK_1 / SPK_2 (onboard 3 W amp): never tie a speaker wire to GND.\n"
             "Player TX should idle near 3.3 V; if it idles at 5 V, divide it (2k / 1k) before D0.",63.5,160.02)
    led.place("Device:R","R1","330R",101.6,76.2,{"1":"hl:input:STRIP_DIN","2":"STRIP_DIN_R"},stub=2.54,lab=(3.81,-1.27))
    led.place("carnival:WS2812B_Strip","J1","WS2812B strip, 74 LEDs",160.02,101.6,{"1":"pwr:+5V^","2":"STRIP_DIN_R","3":"pwr:GNDv"},lab=(20.32,-7.62))
    led.place("Device:C_Polarized","C4","1000uF 10V",129.54,127,{"1":"pwr:+5V","2":"pwr:GND"},stub=2.54,lab=(3.81,-1.27))
    for i,n in enumerate(("+5V","GND")): led.rail(n,279.4,71.12+i*10.16)
    led.text("R1 damps ringing on the data line; C4 across the strip's 5 V input.  Power from the +5V rail, never the GIGA's 5V pin.\n"
             "74 LEDs: ~4 A full white, ~1.4 A at the sketch's brightness 80.  Data is 3.3 V: if the strip glitches add a 74AHCT125.",63.5,152.4)

    for sh,fn,t in ((mcu,"mcu.kicad_sch","MCU - Arduino GIGA R1 WiFi"),(pwr,"power.kicad_sch","Power"),(drv,"driver.kicad_sch","Motor driver (used twice)"),
                    (trk,"track.kicad_sch","Track - motor + limit switches (used twice)"),(ctl,"controls.kicad_sch","Controls"),
                    (scr,"screen.kicad_sch","Screen"),(aud,"audio.kicad_sch","Audio"),(led,"leds.kicad_sch","LED strip")):
        sh.write(fn,t,0,c1="Carnival Game - FULL schematic (every pin)")
    root.write("carnival_full.kicad_sch","Master - signal chain",1,c1="Carnival Game - FULL schematic (every pin)")
    finish(OUT,"carnival_full")

# ==================================================================================================
# SIMPLIFIED VERSION (one page, only the pins in use)
# ==================================================================================================
def simple(OUT):
    os.makedirs(OUT,exist_ok=True); K.OUT=OUT; K.PROJ="carnival_simple"; K.ROOT=str(uuid.uuid4())
    sh=Sheet("/"+K.ROOT); sh.uuid=K.ROOT; sh.tail='(sheet_instances (path "/" (page "1")))'
    gl=[("43","D43 FORWARD"),("41","D41 STOP"),("39","D39 SLOWER"),("37","D37 FASTER"),("35","D35 REVERSE"),None,
        ("22","D22 LCD_RS"),("24","D24 LCD_E"),("26","D26 LCD_D4"),("28","D28 LCD_D5"),("30","D30 LCD_D6"),("32","D32 LCD_D7"),None,("1","D1 TX"),("0","D0 RX")]
    gr=[("53","D53 STEP1"),("51","D51 DIR1"),("25","D25 HOME1"),("23","D23 END1"),None,("49","D49 STEP2"),("47","D47 DIR2"),("29","D29 HOME2"),("27","D27 END2"),None,
        ("13","D13 STRIP"),None,("VIN","VIN"),("GND","GND")]
    gl=[(a,b.replace(" ","_")) if b else None for x in gl for a,b in [x or (None,None)]]; gl=[x if x and x[0] else None for x in gl]
    gr=[(a,b.replace(" ","_")) if b else None for x in gr for a,b in [x or (None,None)]]; gr=[x if x and x[0] else None for x in gr]
    CUSTOM["carnival:GIGA_simple"]=custom("GIGA_simple","Arduino GIGA R1 WiFi, only the pins in use",[(gl,gr)],17.78,"A")
    CUSTOM["carnival:TMC_simple"]=custom("TMC_simple","TMC2209, pins in use",[([("8","EN"),("7","MS1"),("6","MS2"),None,("2","STEP"),("1","DIR"),None,("15","VIO"),("9","VM"),("16","GND")],[("12","A1"),("11","A2"),("13","B1"),("14","B2")])],7.62)
    CUSTOM["carnival:LCD_simple"]=custom("LCD_simple","16x2 LCD, pins in use",[([("4","RS"),("6","E"),("11","D4"),("12","D5"),("13","D6"),("14","D7")],[("2","VDD"),("1","VSS"),("5","RW"),("3","V0"),("15","A"),("16","K")])],7.62,"DS")
    CUSTOM["carnival:MP3_simple"]=custom("MP3_simple","MP3-TF-16P, pins in use",[([("2","RX"),("3","TX")],[("1","VCC"),("7","GND"),("6","SPK_1"),("8","SPK_2")])],7.62)
    s=sh
    s.place("carnival:GIGA_simple","A1","Arduino GIGA R1 WiFi",190.5,111.76,
      {"43":"BTN_FORWARD","41":"BTN_STOP","39":"BTN_SLOWER","37":"BTN_FASTER","35":"BTN_REVERSE","22":"LCD_RS","24":"LCD_E","26":"LCD_D4","28":"LCD_D5","30":"LCD_D6","32":"LCD_D7",
       "1":"MCU_TX","0":"MCU_RX","53":"STEP1","51":"DIR1","25":"HOME1","23":"END1","49":"STEP2","47":"DIR2","29":"HOME2","27":"END2","13":"STRIP_DIN","VIN":"pwr:+12V","GND":"pwr:GND"},
      stub=7.62,lab=(0,-25.4))
    for i,(r,v,n) in enumerate([("SW1","FORWARD","BTN_FORWARD"),("SW2","STOP","BTN_STOP"),("SW3","SLOWER","BTN_SLOWER"),("SW4","FASTER","BTN_FASTER"),("SW5","REVERSE","BTN_REVERSE")]):
        s.place("Switch:SW_Push",r,v,50.8,45.72+i*12.7,{"1":n,"2":"pwr:GND"},lab=(0,-5.08))
    for t,(y,u,m,sa,sb,cc) in {1:(55.88,"U1","M1","SW6","SW7","C1"),2:(127,"U4","M2","SW8","SW9","C5")}.items():
        s.place("carnival:TMC_simple",u,f"TMC2209 driver {t}",279.4,y,{"8":f"tie:T{t}","7":f"tie:T{t}","6":f"tie:T{t}","2":f"STEP{t}","1":f"DIR{t}","15":"pwr:+3V3","9":"pwr:+12V","16":"pwr:GND",
                "12":f"M{t}_A1","11":f"M{t}_A2","13":f"M{t}_B1","14":f"M{t}_B2"},lab=(0,-20.32))
        s.tie(f"T{t}","GND",(-1,0))
        s.place("Motor:Stepper_Motor_bipolar",m,f"Track {t} motor",345.44,y,{"1":f"M{t}_A1","2":f"M{t}_A2","3":f"M{t}_B1","4":f"M{t}_B2"},lab=(7.62,-2.54))
        s.place("Switch:SW_Push",sa,f"Track {t} HOME limit",370.84,y+20.32,{"1":f"HOME{t}","2":"pwr:GND"},lab=(0,-5.08))
        s.place("Switch:SW_Push",sb,f"Track {t} END limit",370.84,y+33.02,{"1":f"END{t}","2":"pwr:GND"},lab=(0,-5.08))
        s.place("Device:C_Polarized",cc,"100uF",251.46,y+22.86,{"1":"pwr:+12V","2":"pwr:GND"},stub=2.54,lab=(3.81,-1.27))
    s.place("carnival:LCD_simple","DS1","16x2 LCD",60.96,137.16,{"4":"LCD_RS","6":"LCD_E","11":"LCD_D4","12":"LCD_D5","13":"LCD_D6","14":"LCD_D7",
            "2":"pwr:+5V","1":"pwr:GND","5":"pwr:GND","3":"LCD_V0","15":"LCD_LED_A","16":"pwr:GND"},lab=(0,-15.24),stub=7.62)
    s.place("Device:R_Potentiometer","RV1","10k contrast",101.6,160.02,{"1":"pwr:+5V","2":"LCD_V0","3":"pwr:GND"},stub=2.54,lab=(5.08,-5.08))
    s.place("Device:R","R2","330R",116.84,160.02,{"1":"pwr:+5V","2":"LCD_LED_A"},stub=2.54,lab=(3.81,-1.27))
    s.place("carnival:MP3_simple","U5","MP3-TF-16P",60.96,195.58,{"2":"MP3_RX_R","3":"MCU_RX","1":"pwr:+5V","7":"pwr:GND","6":"SPK_P","8":"SPK_N"},lab=(0,-12.7),stub=7.62)
    s.place("Device:R","R3","1k",30.48,180.34,{"1":"MCU_TX","2":"MP3_RX_R"},stub=2.54,lab=(3.81,-1.27))
    s.place("Device:Speaker","LS1","Speaker",101.6,198.12,{"1":"SPK_P","2":"SPK_N"},lab=(5.08,-5.08))
    s.place("Device:R","R1","330R",243.84,190.5,{"1":"STRIP_DIN","2":"STRIP_R"},stub=2.54,lab=(3.81,-1.27))
    s.place("Connector_Generic:Conn_01x03","J1","LED strip (74x WS2812B)",279.4,203.2,{"1":"pwr:+5V^","2":"STRIP_R","3":"pwr:GNDv"},lab=(0,-10.16))
    s.place("Connector_Generic:Conn_01x02","PS1","12 V PSU",172.72,187.96,{"1":"pwr:+12V+FLAG","2":"pwr:GND+FLAG"},lab=(0,-7.62))
    s.place("carnival:Buck_Module","U2","Buck 12V->5V",172.72,215.9,{"1":"pwr:+12V","2":"pwr:GND","3":"pwr:+5V+FLAG","4":"pwr:GND"},lab=(0,-10.16))
    s.place("Regulator_Linear:AMS1117-3.3","U3","AMS1117-3.3",218.44,215.9,{"1":"pwr:GND","2":"pwr:+3V3","3":"pwr:+5V"},lab=(0,-10.16))
    s.text("CARNIVAL GAME - SIMPLIFIED WIRING (one page, only the pins in use)",25.4,17.78,2.54,True)
    s.text("WIRE COLOURS  motor coil A: A1 black, A2 green   coil B: B1 red, B2 blue   |   +12V orange   +5V red   +3V3 purple   GND black   signals green",25.4,35.56)
    s.text("Read left to right: buttons -> GIGA -> TMC2209 driver -> motor. Limit switches report back to the GIGA.\n"
           "Same wires as the full schematic (../full/), which draws every pin on every part.\n"
           "Proposed, not yet wired: Track 2 pins, LCD pins, MP3 on D0/D1. Guessed: Track 1 limits 25/23.",25.4,25.4)
    s.write("carnival_simple.kicad_sch","Simplified wiring",1,c1="Carnival Game - SIMPLIFIED (pins in use only)")
    finish(OUT,"carnival_simple")

def finish(OUT,proj):
    open(os.path.join(OUT,"carnival.kicad_sym"),"w").write('(kicad_symbol_lib (version 20251024) (generator "gen4.py") '+" ".join(CUSTOM.values())+')')
    open(os.path.join(OUT,"sym-lib-table"),"w").write('(sym_lib_table\n  (version 7)\n  (lib (name "carnival")(type "KiCad")(uri "${KIPRJMOD}/carnival.kicad_sym")(options "")(descr "Carnival Game parts"))\n)\n')
    open(os.path.join(OUT,f"{proj}.kicad_pro"),"w").write(json.dumps({"meta":{"filename":f"{proj}.kicad_pro","version":1}},indent=2))

full(os.path.join(BASE,"full")); simple(os.path.join(BASE,"simplified")); print("ok")
