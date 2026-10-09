import math, colorsys, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=1080,1920,30
DUR=38.0; BPM=124; spb=60/BPM
FB="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FM="/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
def F(p,s): return ImageFont.truetype(p,s)
INTRO=3.0; SC=6.2; N=5; OUT0=INTRO+SC*N
news=[
 dict(game="RIFTBOUND",title="RADIANCE",d="23",m="OCT",sub="180 cartas nuevas y 9 Legends",sub2="Quinto set del TCG de League of Legends",hue=42),
 dict(game="LORCANA",title="HYPERIA CITY",d="23",m="OCT",sub="Llega con personajes de Coco",sub2="Estrena cartas seriadas numeradas",hue=300),
 dict(game="POKÉMON",title="DELTA REIGN",d="6",m="NOV",sub="Mega Evolution: nuevo set principal",sub2="Prerelease desde el 24 de octubre",hue=195),
 dict(game="MAGIC",title="STAR TREK",d="13",m="NOV",sub="Set Universes Beyond",sub2="Commander Decks y Scene Boxes",hue=345),
 dict(game="ONE PIECE",title="OP-18",d="20",m="NOV",sub="Nuevo booster principal en inglés",sub2="Antes: EB-05 Heroines, el 30 de octubre",hue=215),
]
def hsv(h,s,v): 
    r,g,b=colorsys.hsv_to_rgb((h%360)/360,s,v); return (int(r*255),int(g*255),int(b*255))
def eo(x): x=max(0,min(1,x)); return 1-(1-x)**3
def eb(x):
    x=max(0,min(1,x)); c1=1.70158; c3=c1+1
    return 1+c3*(x-1)**3+c1*(x-1)**2
yy=np.linspace(0,1,480)[:,None]
def bg(hue,t):
    top=np.array(hsv(hue,.78,.42),float); bot=np.array(hsv(hue+35,.85,.10),float)
    g=top[None,None,:]*(1-yy[...,None])+bot[None,None,:]*yy[...,None]
    g=np.repeat(g,270,axis=1)
    return Image.fromarray(g.astype('uint8')).resize((W,H),Image.BICUBIC)
def txt(d,xy,s,font,fill,anchor="mm",shadow=True,alpha=255):
    x,y=xy
    if shadow: d.text((x+4,y+6),s,font=font,fill=(0,0,0,int(110*alpha/255)),anchor=anchor)
    d.text((x,y),s,font=font,fill=fill+(alpha,) if len(fill)==3 else fill,anchor=anchor)
def fit(s,path,maxw,start):
    sz=start
    while sz>40:
        f=F(path,sz)
        if f.getlength(s)<=maxw: return f
        sz-=4
    return F(path,40)
def shapes(ov,t,hue,kind):
    d=ImageDraw.Draw(ov)
    ph=(t%spb)/spb; pulse=math.exp(-ph*4)
    acc=hsv(hue+10,.55,1)
    # concentric rings from center-ish
    for i in range(6):
        r=(t*140+i*170)%1020+40
        a=int(70*(1-r/1060))
        d.ellipse((W/2-r,820-r,W/2+r,820+r),outline=acc+(a,),width=6)
    # beat circle
    R=260+pulse*60
    d.ellipse((W/2-R,820-R,W/2+R,820+R),fill=hsv(hue,.6,1)+(int(38+30*pulse),))
    # floating diamonds
    for i in range(9):
        x=(i*137+ t*(40+i*7))%(W+200)-100
        y=(i*211 + math.sin(t*1.3+i)*60)%H
        s=26+10*math.sin(t*3+i)+pulse*10
        d.polygon([(x,y-s),(x+s,y),(x,y+s),(x-s,y)],fill=acc+(70,))
    return pulse
def frame(t):
    if t<INTRO: sc=-1; lt=t; hue=(t*60)%360*0+230
    elif t<OUT0: sc=int((t-INTRO)//SC); lt=(t-INTRO)-sc*SC; hue=news[sc]['hue']
    else: sc=99; lt=t-OUT0; hue=140
    im=bg(hue,t).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0))
    pulse=shapes(ov,t,hue,0)
    d=ImageDraw.Draw(ov)
    acc=hsv(hue+10,.5,1)
    if sc==-1:
        k=eb(lt/0.6)
        txt(d,(W/2,640),"5",F(FB,int(520*k)+1),(255,255,255))
        k2=eo((lt-0.3)/0.5)
        txt(d,(W/2,1000+(1-k2)*80),"LANZAMIENTOS",fit("LANZAMIENTOS",FB,940,130),(255,255,255),alpha=int(255*k2))
        k3=eo((lt-0.6)/0.5)
        txt(d,(W/2,1130+(1-k3)*80),"QUE VIENEN",fit("QUE VIENEN",FB,940,130),acc,alpha=int(255*k3))
        k4=eo((lt-1.1)/0.5)
        txt(d,(W/2,1290),"TCG  |  OCTUBRE - NOVIEMBRE 2026",F(FM,40),(255,255,255),alpha=int(230*k4))
        txt(d,(W/2,1420),"OVERPOWERARMOR.CL",F(FB,44),acc,alpha=int(255*k4))
    elif sc==99:
        k=eb(lt/0.5)
        txt(d,(W/2,520),"¿CUÁL",F(FB,int(190*k)+1),(255,255,255))
        txt(d,(W/2,700),"ESPERAS MÁS?",fit("ESPERAS MÁS?",FB,940,170),acc)
        k2=eo((lt-0.5)/0.5)
        for i,n in enumerate(news):
            y=900+i*105
            kk=eo((lt-0.5-i*0.12)/0.35)
            x=W/2+(1-kk)*500
            d.rounded_rectangle((120+(1-kk)*500,y-42,960+(1-kk)*500,y+42),radius=42,fill=hsv(n['hue'],.7,.7,)+(int(200*kk),))
            txt(d,(190+(1-kk)*500,y),str(i+1),F(FB,50),(255,255,255),shadow=False,alpha=int(255*kk))
            txt(d,(260+(1-kk)*500,y),f"{n['game']}  {n['title']}",fit(f"{n['game']}  {n['title']}",FM,520,38),(255,255,255),anchor="lm",shadow=False,alpha=int(255*kk))
            txt(d,(930+(1-kk)*500,y),f"{n['d']} {n['m']}",F(FB,36),(255,255,255),anchor="rm",shadow=False,alpha=int(255*kk))
        txt(d,(W/2,1475),"Comenta el número",F(FB,52),(255,255,255),alpha=int(255*eo((lt-1.4)/0.4)))
        txt(d,(W/2,1550),"y síguenos en OverPowerArmor",F(FM,38),acc,alpha=int(255*eo((lt-1.6)/0.4)))
    else:
        n=news[sc]
        # progress segments
        for i in range(N):
            x0=90+i*(900/N); x1=x0+900/N-14
            d.rounded_rectangle((x0,240,x1,252),radius=6,fill=(255,255,255,70))
            if i<sc: f=1
            elif i==sc: f=lt/SC
            else: f=0
            if f>0: d.rounded_rectangle((x0,240,x0+(x1-x0)*f,252),radius=6,fill=(255,255,255,235))
        # number badge
        kb=eb(lt/0.5)
        txt(d,(150,345),f"{sc+1}/5",F(FB,int(52*kb)+1),(255,255,255),anchor="lm")
        # game pill
        kp=eo((lt-0.1)/0.4)
        gf=F(FB,46); gw=gf.getlength(n['game'])+80
        px=W/2-gw/2-(1-kp)*700
        d.rounded_rectangle((px,430,px+gw,520),radius=45,fill=acc+(int(255*kp),))
        txt(d,(px+gw/2,475),n['game'],gf,hsv(hue,.8,.25),shadow=False,alpha=int(255*kp))
        # date
        kd=eb((lt-0.25)/0.55)
        sz=int(520*kd)+1
        txt(d,(W/2,800),n['d'],F(FB,sz),(255,255,255))
        km=eo((lt-0.5)/0.4)
        txt(d,(W/2,1085+(1-km)*60),n['m'],F(FB,150),acc,alpha=int(255*km))
        # title
        kt=eo((lt-0.8)/0.45)
        txt(d,(W/2,1260+(1-kt)*90),n['title'],fit(n['title'],FB,940,120),(255,255,255),alpha=int(255*kt))
        ks=eo((lt-1.2)/0.45)
        txt(d,(W/2,1365+(1-ks)*60),n['sub'],fit(n['sub'],FB,940,52),acc,alpha=int(255*ks))
        k2=eo((lt-1.6)/0.45)
        txt(d,(W/2,1440+(1-k2)*60),n['sub2'],fit(n['sub2'],FM,940,40),(255,255,255),alpha=int(230*k2))
        # flash on transition
        if lt<0.18:
            fl=Image.new("RGBA",(W,H),(255,255,255,int(210*(1-lt/0.18))))
            ov=Image.alpha_composite(ov,fl)
    # brand footer
    if sc not in (-1,99):
        txt(d,(W/2,1565),"OVERPOWERARMOR.CL",F(FB,34),(255,255,255),alpha=210,shadow=False)
    im=Image.alpha_composite(im,ov)
    return im.convert("RGB")
if __name__=="__main__":
    out=sys.argv[1]
    if len(sys.argv)>2 and sys.argv[2]=="stills":
        for name,t in [("s_intro",1.6),("s_sc1",INTRO+2.8),("s_sc3",INTRO+SC*2+3.5),("s_out",OUT0+2.4)]:
            frame(t).save(f"{name}.png")
        sys.exit()
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","music.wav",
        "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),"-c:a","aac","-b:a","160k","-t",str(DUR),"-movflags","+faststart",out],stdin=subprocess.PIPE)
    for i in range(int(DUR*FPS)):
        p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print("done")
