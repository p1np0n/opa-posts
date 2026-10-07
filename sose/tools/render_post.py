#!/usr/bin/env python3
"""Genera una publicacion SOSE (jpg 1080x1350 + textos ig/fb) desde un JSON y la registra en sose/db/publicaciones.csv.
Uso: python3 sose/tools/render_post.py sose/specs/AAAA-MM-DD_HHMM.json
Campos del JSON: fecha (AAAA-MM-DD), slot (1200|2100), categoria, tema, kicker, titulo, chart{titulo,subtitulo,items[{label,valor,texto}],maximo,nota},
cards[[grande,chico] x3], explicacion[2 lineas], fuente_corta, fuente, url_fuente, caption_ig, caption_fb, hashtags, alt"""
import sys, json, csv, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SOSE = os.path.join(ROOT, "sose")
MARFIL, TINTA, ARCILLA, SALVIA, NOGAL = "#f2ece0", "#2e2a24", "#b15a34", "#7c8b6f", "#5c4530"
W, H = 1080, 1350
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
LORAI = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTERB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f


def center(d, text, y, f, fill):
    d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def wrap_px(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def render(spec, out_jpg):
    img = Image.new("RGB", (W, H), MARFIL); d = ImageDraw.Draw(img)
    logo = Image.open(os.path.join(SOSE, "assets", "SOSE_lockup_horizontal.png")).convert("RGB")
    diff = ImageChops.difference(logo, Image.new("RGB", logo.size, MARFIL)).point(lambda p: 255 if p > 40 else 0).convert("L")
    b = diff.crop((20, 20, logo.width - 20, logo.height - 20)).getbbox()
    logo = logo.crop((b[0] + 20, b[1] + 20, b[2] + 20, b[3] + 20))
    lw = 330; logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, ((W - lw) // 2, 70))
    # kicker
    kf = font(INTERB, 26); txt = spec["kicker"].upper(); sp = 6
    tw = d.textlength(txt, font=kf) + sp * (len(txt) - 1); x = (W - tw) / 2
    for ch in txt:
        d.text((x, 215), ch, font=kf, fill=ARCILLA); x += d.textlength(ch, font=kf) + sp
    # titular (auto-ajuste)
    size = 60
    while True:
        hf = font(LORA, size, "SemiBold"); lines = wrap_px(d, spec["titulo"], hf, 900)
        if len(lines) <= 3 or size <= 44: break
        size -= 2
    y = 275
    for ln in lines:
        center(d, ln, y, hf, TINTA); y += int(size * 1.27)
    # ---- grafica de barras ----
    ch = spec["chart"]; cx0, cx1 = 90, W - 90
    top = 560
    d.text((cx0, top), ch["titulo"].upper(), font=font(INTERB, 22), fill=NOGAL)
    d.text((cx0, top + 32), ch.get("subtitulo", ""), font=font(LORAI, 27, "Italic"), fill=TINTA)
    items = ch["items"]; mx = float(ch.get("maximo") or max(i["valor"] for i in items))
    by = top + 122; bh = 46; gap = 62 if len(items) <= 2 else 52
    labf, valf = font(INTER, 23), font(INTERB, 25)
    for i, it in enumerate(items):
        yy = by + i * (bh + gap)
        d.text((cx0, yy - 34), it["label"], font=labf, fill=TINTA)
        d.rounded_rectangle((cx0, yy, cx1, yy + bh), radius=bh // 2, fill="#e4dccb")
        wbar = max(bh, (cx1 - cx0) * it["valor"] / mx)
        d.rounded_rectangle((cx0, yy, cx0 + wbar, yy + bh), radius=bh // 2, fill=ARCILLA if i % 2 == 0 else SALVIA)
        t = it["texto"]; tw = d.textlength(t, font=valf)
        if wbar - 30 > tw: d.text((cx0 + wbar - tw - 20, yy + 9), t, font=valf, fill=MARFIL)
        else: d.text((cx0 + wbar + 12, yy + 9), t, font=valf, fill=TINTA)
    if ch.get("nota"):
        d.text((cx0, by + len(items) * (bh + gap) - gap + 18), ch["nota"], font=font(INTER, 20), fill="#7a7266")
    # ---- tarjetas ----
    ty0, th, g = 925, 200, 24; cw = (W - 140 - 2 * g) // 3
    for i, (big, small) in enumerate(spec["cards"]):
        x0 = 70 + i * (cw + g)
        d.rounded_rectangle((x0, ty0, x0 + cw, ty0 + th), radius=22, fill="#e9e1d0")
        bs = 38
        while d.textlength(big, font=font(LORA, bs, "SemiBold")) > cw - 24 and bs > 24: bs -= 2
        bf = font(LORA, bs, "SemiBold"); center_x = x0 + (cw - d.textlength(big, font=bf)) / 2
        d.text((center_x, ty0 + 36), big, font=bf, fill=ARCILLA)
        sf = font(INTER, 21); yy = ty0 + 104
        for s in small.split("\n"):
            d.text((x0 + (cw - d.textlength(s, font=sf)) / 2, yy), s, font=sf, fill=TINTA); yy += 30
    ef = font(LORAI, 28, "Italic")
    for i, ln in enumerate(spec["explicacion"]): center(d, ln, 1150 + i * 40, ef, NOGAL)
    sf = font(INTER, 19); center(d, spec["fuente_corta"], 1250, sf, "#7a7266")
    d.line((W / 2 - 40, 1292, W / 2 + 40, 1292), fill=ARCILLA, width=3)
    center(d, "sose · el arte de estar en paz", 1302, font(LORAI, 24, "Italic"), TINTA)
    img.save(out_jpg, "JPEG", quality=92, optimize=True)


def main(path):
    spec = json.load(open(path, encoding="utf-8"))
    base = f"{spec['fecha']}_{spec['slot']}"
    render(spec, os.path.join(SOSE, base + ".jpg"))
    open(os.path.join(SOSE, base + "_ig.txt"), "w", encoding="utf-8").write(spec["caption_ig"].strip() + "\n\n" + spec["hashtags"])
    open(os.path.join(SOSE, base + "_fb.txt"), "w", encoding="utf-8").write(spec["caption_fb"].strip())
    csvp = os.path.join(SOSE, "db", "publicaciones.csv")
    cols = ["fecha", "slot", "categoria", "tema", "titulo", "dato_clave", "caption_instagram", "caption_facebook", "hashtags", "texto_alternativo", "fuente", "url_fuente", "archivo_grafica", "estado"]
    rows = list(csv.DictReader(open(csvp, encoding="utf-8-sig"))) if os.path.exists(csvp) else []
    rows = [r for r in rows if not (r.get("fecha") == spec["fecha"] and r.get("slot") == spec["slot"])]
    rows.append({"fecha": spec["fecha"], "slot": spec["slot"], "categoria": spec["categoria"], "tema": spec["tema"], "titulo": spec["titulo"],
                 "dato_clave": " · ".join(c[0] for c in spec["cards"]), "caption_instagram": spec["caption_ig"], "caption_facebook": spec["caption_fb"],
                 "hashtags": spec["hashtags"], "texto_alternativo": spec["alt"], "fuente": spec["fuente"], "url_fuente": spec["url_fuente"],
                 "archivo_grafica": base + ".jpg", "estado": "programado"})
    with open(csvp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print("ok", base)

if __name__ == "__main__":
    main(sys.argv[1])
