# -*- coding: utf-8 -*-
import colorsys, random, math, os, html
from playwright.sync_api import sync_playwright
import json, datetime, sys
POSTS = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'posts.json', encoding='utf-8'))
WD = ['LUN','MAR','MIÉ','JUE','VIE','SÁB','DOM']
MES = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
def chip(p):
    if not p.get('date'): return 'SIEMPRE ÚTIL'
    d = datetime.date.fromisoformat(p['date'])
    return f"{WD[d.weekday()]} {d.day} {MES[d.month-1]}"

W, H = 1080, 1350

def hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s)
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

def motif_svg(m, hue, seed):
    rnd = random.Random(seed)
    acc = hsl(hue + 30, 0.9, 0.62)
    acc2 = hsl(hue - 30, 0.85, 0.55)
    lt = "rgba(255,255,255,0.14)"
    o = []
    cx, cy = 540, 560
    if m == "shards":
        for i in range(14):
            pts = " ".join(f"{rnd.randint(0,W)},{rnd.randint(0,H)}" for _ in range(3))
            o.append(f'<polygon points="{pts}" fill="{rnd.choice([acc,acc2,lt])}" opacity="{rnd.uniform(.12,.3):.2f}"/>')
    elif m == "burst" or m == "rays" or m == "sunburst":
        n = 28 if m != "sunburst" else 40
        for i in range(n):
            a = 2*math.pi*i/n
            a2 = a + math.pi/n*0.8
            R = 1500
            o.append(f'<polygon points="{cx},{cy} {cx+R*math.cos(a):.0f},{cy+R*math.sin(a):.0f} {cx+R*math.cos(a2):.0f},{cy+R*math.sin(a2):.0f}" fill="{lt if i%2 else "rgba(255,255,255,0.05)"}"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="260" fill="{acc}" opacity="0.18"/>')
    elif m == "spotlight":
        o.append(f'<polygon points="540,0 120,1350 960,1350" fill="rgba(255,255,255,0.10)"/>')
        o.append(f'<polygon points="540,0 300,1350 780,1350" fill="rgba(255,255,255,0.10)"/>')
        o.append(f'<circle cx="540" cy="1150" r="230" fill="{acc}" opacity="0.22"/>')
    elif m == "ruler":
        for i in range(0, 1100, 20):
            L = 90 if i % 100 == 0 else (55 if i % 50 == 0 else 28)
            o.append(f'<line x1="{i}" y1="0" x2="{i}" y2="{L}" stroke="rgba(255,255,255,0.35)" stroke-width="3"/>')
            o.append(f'<line x1="0" y1="{i+60}" x2="{L}" y2="{i+60}" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>')
        o.append(f'<rect x="690" y="330" width="260" height="364" rx="22" fill="none" stroke="{acc}" stroke-width="8" opacity=".5"/>')
        o.append(f'<rect x="735" y="378" width="215" height="300" rx="18" fill="none" stroke="rgba(255,255,255,.4)" stroke-width="6" stroke-dasharray="18 12"/>')
    elif m == "slab":
        o.append(f'<rect x="600" y="260" width="360" height="520" rx="30" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="10"/>')
        o.append(f'<rect x="630" y="330" width="300" height="420" rx="18" fill="rgba(255,255,255,.08)"/>')
        o.append(f'<rect x="630" y="280" width="300" height="40" rx="10" fill="{acc}" opacity=".45"/>')
    elif m == "petals":
        for i in range(34):
            x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(30, 120)
            o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{rnd.choice([acc,acc2,"#fff"])}" opacity="{rnd.uniform(.07,.2):.2f}"/>')
        for i in range(12):
            x, y = rnd.randint(0, W), rnd.randint(0, 500)
            o.append(f'<path d="M{x},{y} l40,0 l-20,50 z" fill="{acc}" opacity=".35"/>')
    elif m == "triangles":
        s = 180
        for r in range(0, 9):
            for c in range(-1, 7):
                if rnd.random() < 0.55:
                    x, y = c*s + (s/2 if r % 2 else 0), r*s*0.87
                    o.append(f'<polygon points="{x},{y+s*.87} {x+s/2},{y} {x+s},{y+s*.87}" fill="{rnd.choice([acc,acc2,"#fff"])}" opacity="{rnd.uniform(.05,.17):.2f}"/>')
    elif m == "stack":
        for i in range(8):
            o.append(f'<rect x="{560+i*14}" y="{240+i*40}" width="360" height="460" rx="24" fill="none" stroke="rgba(255,255,255,{0.12+i*0.04:.2f})" stroke-width="6" transform="rotate({-6+i*2},740,470)"/>')
    elif m == "waves":
        for i in range(10):
            y = 300 + i*70
            o.append(f'<path d="M0,{y} Q135,{y-60} 270,{y} T540,{y} T810,{y} T1080,{y}" fill="none" stroke="{rnd.choice([acc,"#fff",acc2])}" stroke-width="6" opacity="{0.10+i*0.02:.2f}"/>')
    elif m == "chart":
        pts = [(80,640),(260,560),(420,600),(600,430),(760,460),(1000,300)]
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        o.append(f'<path d="{d}" fill="none" stroke="{acc}" stroke-width="12" opacity=".6"/>')
        for x, y in pts:
            o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="#fff" opacity=".7"/>')
        for i in range(8):
            o.append(f'<line x1="0" y1="{240+i*60}" x2="{W}" y2="{300+i*110}" stroke="rgba(255,255,255,.08)" stroke-width="3"/>')
    elif m == "pentagon":
        cols = [hsl(h, .8, .6) for h in (50, 210, 0, 120, 280)]
        for i, c in enumerate(cols):
            a = -math.pi/2 + i*2*math.pi/5
            o.append(f'<circle cx="{730+170*math.cos(a):.0f}" cy="{500+170*math.sin(a):.0f}" r="70" fill="{c}" opacity=".28"/>')
        o.append(f'<circle cx="730" cy="500" r="250" fill="none" stroke="rgba(255,255,255,.25)" stroke-width="5"/>')
    elif m == "grid9":
        for r in range(3):
            for c in range(3):
                o.append(f'<rect x="{560+c*130}" y="{200+r*180}" width="110" height="154" rx="14" fill="rgba(255,255,255,{0.10+0.03*(r+c)})" stroke="rgba(255,255,255,.3)" stroke-width="3"/>')
    elif m == "horizon":
        o.append(f'<circle cx="540" cy="780" r="320" fill="{acc}" opacity=".22"/>')
        for i in range(12):
            o.append(f'<line x1="540" y1="800" x2="{-400+i*160}" y2="1350" stroke="rgba(255,255,255,.12)" stroke-width="3"/>')
        for i in range(7):
            o.append(f'<line x1="0" y1="{800+i*i*14+i*20}" x2="{W}" y2="{800+i*i*14+i*20}" stroke="rgba(255,255,255,.12)" stroke-width="3"/>')
    elif m == "andes":
        o.append(f'<polygon points="0,900 220,420 380,720 560,360 760,700 920,500 1080,860 1080,1350 0,1350" fill="rgba(255,255,255,.12)"/>')
        o.append(f'<polygon points="0,1000 200,640 360,880 560,560 760,880 960,700 1080,950 1080,1350 0,1350" fill="rgba(0,0,0,.18)"/>')
        o.append(f'<polygon points="520,370 560,360 600,440 540,420" fill="#fff" opacity=".6"/>')
        o.append(f'<circle cx="880" cy="260" r="80" fill="{acc}" opacity=".4"/>')
    elif m == "checklist":
        for i in range(5):
            y = 260 + i*130
            o.append(f'<rect x="580" y="{y}" width="64" height="64" rx="14" fill="none" stroke="rgba(255,255,255,.4)" stroke-width="6"/>')
            o.append(f'<path d="M594,{y+34} l16,16 l26,-34" fill="none" stroke="{acc}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
            o.append(f'<rect x="670" y="{y+20}" width="{rnd.randint(150,290)}" height="22" rx="11" fill="rgba(255,255,255,.18)"/>')
    elif m == "calendar":
        o.append(f'<rect x="560" y="230" width="400" height="450" rx="36" fill="rgba(255,255,255,.12)" stroke="rgba(255,255,255,.4)" stroke-width="6"/>')
        o.append(f'<rect x="560" y="230" width="400" height="110" rx="36" fill="{acc}" opacity=".45"/>')
        for rr in range(3):
            for cc in range(4):
                o.append(f'<circle cx="{620+cc*95}" cy="{420+rr*80}" r="14" fill="rgba(255,255,255,.35)"/>')
    elif m == "moonrings":
        for i in range(8):
            o.append(f'<circle cx="760" cy="520" r="{80+i*55}" fill="none" stroke="rgba(255,255,255,{0.30-i*0.03:.2f})" stroke-width="5"/>')
        o.append(f'<circle cx="760" cy="520" r="70" fill="{acc}" opacity=".5"/>')
    elif m == "mat":
        o.append(f'<rect x="130" y="470" width="820" height="400" rx="40" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.35)" stroke-width="6"/>')
        for i in range(5):
            o.append(f'<rect x="{190+i*152}" y="{580}" width="120" height="168" rx="14" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="4" stroke-dasharray="14 10"/>')
    elif m == "layers":
        for i in range(5):
            o.append(f'<rect x="{600-i*18}" y="{260-i*18}" width="{300+i*36}" height="{420+i*36}" rx="{26+i*4}" fill="none" stroke="rgba(255,255,255,{0.45-i*0.07:.2f})" stroke-width="6"/>')
    elif m == "tags":
        for i in range(6):
            x, y = 560 + (i%2)*200, 230 + i*120
            o.append(f'<path d="M{x},{y} h140 l50,38 l-50,38 h-140 z" fill="rgba(255,255,255,.12)" stroke="rgba(255,255,255,.35)" stroke-width="4"/>')
            o.append(f'<circle cx="{x+150}" cy="{y+38}" r="8" fill="{acc}"/>')
    elif m == "pages":
        for i in range(5):
            o.append(f'<rect x="{560+i*60}" y="{230+i*30}" width="300" height="420" rx="18" fill="rgba(255,255,255,{0.07+i*0.03:.2f})" stroke="rgba(255,255,255,.3)" stroke-width="4" transform="rotate({i*5-8},700,440)"/>')
    elif m == "trophy":
        o.append(f'<path d="M650,260 h260 v150 a130,130 0 0 1 -260,0 z" fill="none" stroke="{acc}" stroke-width="12" opacity=".7"/>')
        o.append(f'<rect x="760" y="540" width="40" height="120" fill="{acc}" opacity=".6"/>')
        o.append(f'<rect x="700" y="660" width="160" height="34" rx="12" fill="{acc}" opacity=".6"/>')
        for i in range(14):
            o.append(f'<circle cx="{rnd.randint(0,W)}" cy="{rnd.randint(0,H)}" r="{rnd.randint(4,12)}" fill="#fff" opacity=".35"/>')
    elif m == "split":
        o.append(f'<polygon points="0,0 1080,0 0,1350" fill="rgba(255,255,255,.07)"/>')
        o.append(f'<polygon points="1080,1350 1080,0 0,1350" fill="rgba(0,0,0,.20)"/>')
        o.append(f'<circle cx="300" cy="360" r="130" fill="{acc}" opacity=".55"/>')
        o.append(f'<circle cx="780" cy="900" r="130" fill="#fff" opacity=".18"/><circle cx="830" cy="870" r="115" fill="rgba(0,0,0,.35)"/>')
    elif m == "moon":
        o.append(f'<circle cx="760" cy="420" r="210" fill="{acc}" opacity=".5"/>')
        o.append(f'<circle cx="840" cy="380" r="190" fill="rgba(0,0,0,.45)"/>')
        for i in range(30):
            o.append(f'<circle cx="{rnd.randint(0,W)}" cy="{rnd.randint(0,H)}" r="{rnd.randint(2,6)}" fill="#fff" opacity=".4"/>')
        o.append(f'<polygon points="0,1100 140,980 220,1060 360,900 520,1050 700,940 900,1060 1080,960 1080,1350 0,1350" fill="rgba(0,0,0,.35)"/>')
    elif m == "drops":
        for i in range(16):
            x, y, r = rnd.randint(40, W-40), rnd.randint(200, 800), rnd.randint(18, 60)
            o.append(f'<path d="M{x},{y-r*1.6} C{x+r*1.1},{y-r*0.4} {x+r},{y+r} {x},{y+r} C{x-r},{y+r} {x-r*1.1},{y-r*0.4} {x},{y-r*1.6} Z" fill="{rnd.choice([acc,"#fff",acc2])}" opacity="{rnd.uniform(.10,.30):.2f}"/>')
    elif m == "glare":
        for i in range(9):
            x = 300 + i*110
            o.append(f'<polygon points="{x},0 {x+60},0 {x-380},1350 {x-440},1350" fill="rgba(255,255,255,{0.05+0.02*(i%3):.2f})"/>')
        o.append(f'<rect x="600" y="260" width="330" height="460" rx="26" fill="rgba(255,255,255,.10)" stroke="rgba(255,255,255,.4)" stroke-width="5"/>')
    elif m == "stars":
        for i in range(22):
            x, y, r = rnd.randint(30, W-30), rnd.randint(180, 900), rnd.randint(14, 46)
            pts = " ".join(f"{x+(r if k%2==0 else r*0.42)*math.cos(-math.pi/2+k*math.pi/5):.0f},{y+(r if k%2==0 else r*0.42)*math.sin(-math.pi/2+k*math.pi/5):.0f}" for k in range(10))
            o.append(f'<polygon points="{pts}" fill="{rnd.choice([acc,"#fff",acc2])}" opacity="{rnd.uniform(.15,.5):.2f}"/>')
    return "".join(o)

PILLAR_COL = {"NOTICIA": "#ff4d5e", "¿SABÍAS QUE?": "#ffd23f", "ACCESORIOS 101": "#35e0b0",
              "CALENDARIO": "#6ec1ff", "MERCADO": "#9be564", "HOY": "#ff8a3d",
              "QUÉ VIENE": "#c58bff", "EL FUTURO": "#6ec1ff", "COMUNIDAD": "#ff6b8b", "HALLOWEEN": "#ff9f1c", "TIPS": "#ffb86b"}

def page(p, idx):
    h = p["hue"]
    c1, c2 = hsl(h, 0.65, 0.20), hsl(h + 40, 0.75, 0.38)
    ang = 120 + (idx * 29) % 90
    pill = PILLAR_COL.get(p["pillar"], "#fff")
    big = html.escape(p["big"])
    title = html.escape(p["title"])
    sub = html.escape(p["sub"])
    fs = 92 if len(p["title"]) < 30 else (80 if len(p["title"]) < 42 else 70)
    bigsize = 330 if len(p["big"]) <= 2 else (230 if len(p["big"]) <= 4 else 150)
    mot = motif_svg(p["motif"], h, idx*7+3)
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:'Inter','Inter Display','DejaVu Sans',sans-serif;
background:linear-gradient({ang}deg,{c1},{c2});color:#fff;position:relative}}
svg.bg{{position:absolute;inset:0}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,rgba(0,0,0,0) 35%,rgba(0,0,0,.45) 100%)}}
.top{{position:absolute;left:64px;right:64px;top:64px;display:flex;justify-content:space-between;align-items:center}}
.pill{{background:{pill};color:#12121a;font-weight:900;font-size:34px;letter-spacing:.06em;padding:14px 30px;border-radius:999px}}
.date{{font-weight:800;font-size:34px;opacity:.95;letter-spacing:.04em;background:rgba(0,0,0,.35);padding:14px 26px;border-radius:999px}}
.tagline{{position:absolute;left:64px;top:190px;font-size:30px;font-weight:700;letter-spacing:.22em;opacity:.85}}
.big{{position:absolute;left:54px;top:250px;font-weight:900;font-size:{bigsize}px;line-height:1;letter-spacing:-.04em;
color:transparent;-webkit-text-stroke:5px rgba(255,255,255,.55);text-shadow:0 0 0 transparent;max-width:1000px;white-space:nowrap}}
.txt{{position:absolute;left:64px;right:64px;bottom:210px}}
.title{{font-weight:900;font-size:{fs}px;line-height:1.04;letter-spacing:-.02em;text-shadow:0 6px 30px rgba(0,0,0,.45)}}
.sub{{margin-top:26px;font-size:40px;font-weight:600;line-height:1.25;opacity:.95;max-width:900px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:130px;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:space-between;padding:0 64px}}
.brand{{font-weight:900;font-size:40px;letter-spacing:.05em}}
.brand span{{color:{pill}}}
.cta{{font-weight:700;font-size:28px;opacity:.9}}
</style></head><body>
<svg class="bg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{mot}</svg>
<div class="vig"></div>
<div class="top"><div class="pill">{html.escape(p["pillar"])}</div><div class="date">{chip(p)}</div></div>
<div class="tagline">{html.escape(p["tag"])}</div>
<div class="big">{big}</div>
<div class="txt"><div class="title">{title}</div><div class="sub">{sub}</div></div>
<div class="foot"><div class="brand">OVERPOWER<span>ARMOR</span>.CL</div><div class="cta">Info TCG a diario ▸</div></div>
</body></html>'''

os.makedirs("png", exist_ok=True)
os.makedirs("jpg", exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={'width': W, 'height': H})
    for i, p in enumerate(POSTS):
        pg.set_content(page(p, i))
        pg.wait_for_timeout(80)
        pg.screenshot(path=f"png/{p['id']}.png")
    b.close()
from PIL import Image
for p in POSTS:
    Image.open(f"png/{p['id']}.png").convert("RGB").save(f"jpg/{p['id']}.jpg", "JPEG", quality=90)
print(len(POSTS), "ok")
