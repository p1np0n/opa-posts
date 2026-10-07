#!/usr/bin/env python3
"""Genera todas las publicaciones del almacén desde tools/contenido.py:
almacen/AAAA-MM-DD_HHMM.jpg (1080x1350) + .txt (caption) y la base de datos almacen/db/publicaciones.csv.
Uso: python3 almacen/tools/render_almacen.py"""
import os, sys, csv
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE); from contenido import C
W, H = 1080, 1350
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"; FM = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
PAL = {"sabias": ("#0f766e", "¿SABÍAS QUE…?"), "util": ("#c2410c", "DATO ÚTIL"), "limpieza": ("#1d4ed8", "TIP DE LIMPIEZA"),
       "efemeride": ("#7e22ce", "HOY ES…"), "almacen": ("#b91c1c", "DEL ALMACÉN")}
CAT = {"sabias": "Sabías que", "util": "Dato útil", "limpieza": "Tip de limpieza", "efemeride": "Efeméride", "almacen": "Del almacén"}
def f(p, s): return ImageFont.truetype(p, s)
def wrap(d, t, fo, mw):
    out, cur = [], ""
    for w in t.split():
        x = (cur + " " + w).strip()
        if d.textlength(x, font=fo) <= mw: cur = x
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out
def render(it, out):
    fecha, slot, cat, titulo, pts, cierre, _ = it
    col, kick = PAL[cat]
    img = Image.new("RGB", (W, H), col); d = ImageDraw.Draw(img)
    d.ellipse((-200, -200, 400, 400), fill=Image.new("RGB",(1,1),col).getpixel((0,0)))
    # logo
    logo = Image.open(os.path.join(A, "assets", "logo_detodo.png")).convert("RGB"); logo.thumbnail((120, 120))
    d.rounded_rectangle((60, 60, 60 + 150, 60 + 150), 20, fill="white"); img.paste(logo, (75, 75))
    # kicker
    kf = f(FB, 30); kw = d.textlength(kick, font=kf)
    d.rounded_rectangle((W - 60 - kw - 50, 95, W - 60, 95 + 70), 35, fill="white"); d.text((W - 60 - kw - 25, 112), kick, font=kf, fill=col)
    # titulo
    s = 70
    while True:
        tf = f(FB, s); L = wrap(d, titulo, tf, 940)
        if len(L) <= 4 or s <= 48: break
        s -= 2
    y = 270
    for l in L: d.text((70, y), l, font=tf, fill="white"); y += int(s * 1.25)
    # tarjeta puntos
    top = max(y + 30, 560); bot = 1090
    d.rounded_rectangle((50, top, W - 50, bot), 40, fill="white")
    pf = f(FM, 36); n = len(pts); avail = bot - top - 60; step = avail / n; yy = top + 40
    for i, p in enumerate(pts):
        d.ellipse((90, yy, 150, yy + 60), fill=col); nf = f(FB, 34); d.text((120 - d.textlength(str(i+1), font=nf)/2, yy + 8), str(i+1), font=nf, fill="white")
        lines = wrap(d, p, pf, 780); ty = yy + 30 - len(lines) * 24
        for l in lines: d.text((180, ty), l, font=pf, fill="#222"); ty += 48
        yy += step
    # cierre
    cf = f(FB, 38); CL = wrap(d, cierre, cf, 940); cy = 1120
    for l in CL: d.text((W/2 - d.textlength(l, font=cf)/2, cy), l, font=cf, fill="white"); cy += 50
    # pie
    d.rectangle((0, 1240, W, H), fill="#111")
    ff = f(FM, 30); t1 = "Almacén DeTodo!!  ·  Bagdad 983, Villa El Abrazo, Maipú"; t2 = "WhatsApp: +56 9 2044 4569"
    d.text((W/2 - d.textlength(t1, font=ff)/2, 1262), t1, font=ff, fill="white")
    d.text((W/2 - d.textlength(t2, font=ff)/2, 1305), t2, font=f(FB, 30), fill="#fde68a")
    img.save(out, "JPEG", quality=90, optimize=True)
def caption(it):
    fecha, slot, cat, titulo, pts, cierre, tag = it
    body = "\n".join("• " + p for p in pts)
    tags = f"#almacen #detodo #maipu #villaelabrazo #{tag.lower()}"
    return f"{titulo}\n\n{body}\n\n{cierre}\n\n📍 Bagdad 983, Villa El Abrazo, Maipú\n📲 WhatsApp +56 9 2044 4569\n\n{tags}"
rows = []
for it in C:
    base = f"{it[0]}_{it[1]}"
    render(it, os.path.join(A, base + ".jpg"))
    cap = caption(it)
    open(os.path.join(A, base + ".txt"), "w", encoding="utf-8").write(cap)
    rows.append({"fecha": it[0], "slot": it[1], "categoria": CAT[it[2]], "titulo": it[3], "puntos": " | ".join(it[4]), "cierre": it[5],
                 "caption": cap, "archivo": base + ".jpg", "estado": "programado"})
os.makedirs(os.path.join(A, "db"), exist_ok=True)
with open(os.path.join(A, "db", "publicaciones.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("ok", len(rows))
