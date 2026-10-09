import numpy as np, wave
import sys,os
SR=44100; BPM=int(os.environ.get('REEL_BPM',124)); spb=60/BPM
DUR=float(sys.argv[1]) if len(sys.argv)>1 else 38.0
N=int(SR*DUR); out=np.zeros(N)
def add(buf,start,sig,g=1.0):
    i=int(start*SR); j=min(N,i+len(sig))
    if i<N: buf[i:j]+=g*sig[:j-i]
def env(n,a=0.005,d=0.2):
    t=np.arange(n)/SR
    return np.minimum(t/a,1)*np.exp(-t/d)
def kick():
    t=np.arange(int(.35*SR))/SR
    f=45+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)
def clap():
    n=int(.18*SR); t=np.arange(n)/SR
    return np.random.randn(n)*np.exp(-t*30)*0.6
def hat(o=False):
    n=int((.18 if o else .05)*SR); t=np.arange(n)/SR
    x=np.random.randn(n); x=np.diff(x,prepend=0)
    return x*np.exp(-t*(25 if o else 90))*0.25
def saw(f,n,det=0.004):
    t=np.arange(n)/SR
    s=0
    for d in (-det,0,det):
        s=s+2*((t*f*(1+d))%1)-1
    return s/3
def square(f,n):
    t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))
mid=lambda m:440*2**((m-69)/12)
PROGS={'a':[(57,[57,60,64]),(53,[53,57,60]),(48,[48,52,55]),(55,[55,59,62])],
 'b':[(62,[62,65,69]),(58,[58,62,65]),(53,[53,57,60]),(60,[60,64,67])],
 'c':[(60,[60,64,67]),(55,[55,59,62]),(57,[57,60,64]),(53,[53,57,60])],
 'd':[(64,[64,67,71]),(60,[60,64,67]),(55,[55,59,62]),(62,[62,66,69])]}
prog=PROGS[os.environ.get('REEL_PROG','a')]
bars=int(DUR/(4*spb))+1
rng=np.random.default_rng(3); np.random.seed(int(os.environ.get('REEL_SEED',3)))
for b in range(bars):
    root,ch=prog[b%4]; t0=b*4*spb
    intro = b<1
    for beat in range(4):
        tb=t0+beat*spb
        if b>=1 or beat>=0: add(out,tb,kick(),0.9)
        if beat in (1,3) and b>=1: add(out,tb,clap(),0.7)
        for k in range(2):
            if b>=1: add(out,tb+k*spb/2+spb/4*(0 if k==0 else 0),hat(k==1),0.8 if k==0 else 0.6)
    # bass (offbeat 8ths)
    for k in range(8):
        tb=t0+k*spb/2
        n=int(spb/2*SR*0.9)
        add(out,tb,square(mid(root-12),n)*env(n,0.003,0.12)*0.28,1)
    # arpeggio 16ths
    if b>=1:
        pat=[0,1,2,1,0,1,2,1,0,2,1,2,0,1,2,1]
        for k in range(16):
            tb=t0+k*spb/4; n=int(spb/4*SR*1.6)
            m=ch[pat[k]]+12+(12 if (k%8==7) else 0)
            add(out,tb,saw(mid(m),n)*env(n,0.004,0.11)*0.18)
    # pad
    for m in ch:
        n=int(4*spb*SR); s=saw(mid(m+12),n,0.006)*0.07
        e=np.minimum(np.arange(n)/SR/0.3,1)*np.minimum((n-np.arange(n))/SR/0.3,1)
        add(out,t0,s*e)
# sidechain-ish duck on kicks
duck=np.ones(N)
for b in range(bars):
    for beat in range(4):
        i=int((b*4+beat)*spb*SR); L=int(.25*SR)
        if i<N: duck[i:i+L]=np.minimum(duck[i:i+L],np.linspace(0.35,1,min(L,N-i)))
out*=duck
# fades and limiter
fi=int(.4*SR); out[:fi]*=np.linspace(0,1,fi)
fo=int(2.0*SR); out[-fo:]*=np.linspace(1,0,fo)
out=np.tanh(out*1.6)*0.85
st=np.stack([out,np.roll(out,int(0.012*SR))],1)
pcm=(st*32767).astype('<i2')
w=wave.open(os.environ.get('REEL_WAV','music.wav'),'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('ok',DUR,spb)
