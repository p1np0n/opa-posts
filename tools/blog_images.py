#!/usr/bin/env python3
"""Genera las 2 imagenes de un articulo del blog de OPA (portada 1200x630 y diagrama 1200x700).

Uso: python3 tools/blog_images.py spec.json salida/
Crea salida/hero.jpg y salida/diagrama.jpg. Requiere Playwright (Chromium) y Pillow.
Solo formas abstractas y texto: no usar logos, personajes ni arte oficial de ningun juego.

spec.json:
{
 "hero": {"style": "fan" | "frame", "tag": "NOTICIA TCG", "big": "30" (opcional),
          "title": "Texto blanco", "accent": "Texto de color", "note": "frase corta bajo el titulo (solo style frame)"},
 "diagram": {"type": "timeline", "title": "...", "title_accent": "...", "subtitle": "...", "footer": "...",
             "events": [{"date": "16 sep", "title": "...", "text": "...", "color": "#00E5FF"}]}   (3 a 5 eventos)
        o   {"type": "bars", "title": "...", "title_accent": "...", "subtitle": "...", "footer": "...",
             "rows": [{"label": "35 pt", "value": 0.89, "text": "0,89 mm", "caption": "..."}]}      (2 a 6 filas)
}
"""
import asyncio, html, json, sys, os
from playwright.async_api import async_playwright
from PIL import Image

E = html.escape
BASE = """<html><head><meta charset='utf-8'><style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Poppins','Inter',sans-serif;color:#fff;background:#0D0D14;overflow:hidden}
.brand{position:absolute;left:56px;bottom:30px;font-size:20px;letter-spacing:3px;color:#9aa0c8;font-weight:600}
.brand b{color:#00E5FF}
</style></head><body>%s</body></html>"""
PALETTE = ['#00E5FF', '#FFD600', '#FF4FD8', '#7CFF9B', '#FF9A3D']


def hero(h):
    style = h.get('style', 'fan')
    tag = E(h.get('tag', 'NOTICIA TCG'))
    title, accent = E(h.get('title', '')), E(h.get('accent', ''))
    if style == 'fan':
        bg = 'radial-gradient(circle at 78% 45%,#2a2f8f 0%,#14163d 45%,#0D0D14 80%)'
        tagc, tagt = '#FFD600', '#0D0D14'
        big = E(h.get('big', ''))
        big_html = (f'<div style="position:absolute;left:50px;top:120px;font-size:230px;font-weight:800;line-height:1;'
                    f'color:#FFD600;text-shadow:0 0 40px rgba(255,214,0,.45)">{big}</div>') if big else ''
        title_top = 370 if big else 190
        title_size = 46 if big else 58
        art = """<svg style="position:absolute;right:20px;top:40px" width="440" height="550" viewBox="0 0 440 550">
  <g transform="translate(190 285)">
   <rect x="-150" y="-190" width="190" height="270" rx="16" fill="#1b1f5e" stroke="#00E5FF" stroke-width="4" transform="rotate(-14 -55 -55)"/>
   <rect x="-60" y="-210" width="190" height="270" rx="16" fill="#241a5a" stroke="#FF4FD8" stroke-width="4" transform="rotate(4)"/>
   <rect x="10" y="-160" width="190" height="270" rx="16" fill="#0f1a4a" stroke="#FFD600" stroke-width="5" transform="rotate(18 105 -25)"/>
   <polygon points="105,-110 122,-62 172,-62 132,-32 147,16 105,-14 63,16 78,-32 38,-62 88,-62" fill="#FFD600" transform="rotate(18 105 -25) translate(0 20)"/>
  </g></svg>"""
        note = ''
        accent_c = '#00E5FF'
    else:
        bg = 'radial-gradient(circle at 75% 50%,#0f4d5c 0%,#10213a 45%,#0D0D14 80%)'
        tagc, tagt = '#00E5FF', '#0D0D14'
        big_html, title_top, title_size, accent_c = '', 150, 60, '#FFD600'
        note = (f'<div style="position:absolute;left:56px;top:430px;width:600px;font-size:26px;color:#c4c9ee;line-height:1.3">'
                f'{E(h.get("note", ""))}</div>') if h.get('note') else ''
        art = """<svg style="position:absolute;right:50px;top:60px" width="440" height="510" viewBox="0 0 440 510">
  <rect x="60" y="20" width="300" height="410" rx="14" fill="#16314a" stroke="#00E5FF" stroke-width="6"/>
  <rect x="95" y="60" width="230" height="330" rx="10" fill="#0D0D14" stroke="#7fe9ff" stroke-width="3"/>
  <rect x="115" y="85" width="190" height="270" rx="8" fill="#241a5a" stroke="#FFD600" stroke-width="4"/>
  <polygon points="210,130 226,178 276,178 236,206 250,254 210,226 170,254 184,206 144,178 194,178" fill="#FFD600"/></svg>"""
    return f"""<div style="width:1200px;height:630px;position:relative;background:{bg}">
 <div style="position:absolute;left:56px;top:56px;background:{tagc};color:{tagt};font-weight:800;font-size:22px;letter-spacing:3px;padding:8px 18px">{tag}</div>
 {big_html}
 <div style="position:absolute;left:56px;top:{title_top}px;width:{640 if style=='fan' else 620}px;font-size:{title_size}px;font-weight:800;line-height:1.12">{title} <span style="color:{accent_c}">{accent}</span></div>
 {note}{art}
 <div class="brand">OVER POWER <b>ARMOR</b> · {'NOTICIAS TCG' if style=='fan' else 'DATOS TCG'}</div></div>"""


def diagram(d):
    head = f"""<div style="position:absolute;left:56px;top:34px;font-size:34px;font-weight:800">{E(d.get('title',''))} <span style="color:#FFD600">{E(d.get('title_accent',''))}</span></div>
 <div style="position:absolute;left:56px;top:84px;font-size:18px;color:#9aa0c8">{E(d.get('subtitle',''))}</div>"""
    foot = f"""<div class="brand" style="bottom:28px">{E(d.get('footer','OVER POWER ARMOR'))}</div>"""
    body = ''
    if d['type'] == 'timeline':
        ev = d['events']; n = len(ev); step = 1100 / n; w = int(step - 20)
        for i, e in enumerate(ev):
            x = 50 + step * i + step / 2
            c = e.get('color', PALETTE[i % 5])
            body += f"""<text x="{x}" y="215" text-anchor="middle" font-size="36" font-weight="800" fill="{c}">{E(e['date'])}</text>
<circle cx="{x}" cy="270" r="15" fill="{c}"/><line x1="{x}" y1="292" x2="{x}" y2="330" stroke="{c}" stroke-width="3"/>
<foreignObject x="{x-w/2}" y="338" width="{w}" height="220"><div xmlns="http://www.w3.org/1999/xhtml" style="text-align:center;font-family:Poppins;color:#fff"><div style="font-size:21px;font-weight:700;line-height:1.2">{E(e['title'])}</div><div style="font-size:16px;color:#b8bde6;margin-top:8px;line-height:1.35">{E(e.get('text',''))}</div></div></foreignObject>"""
        body = '<line x1="50" y1="270" x2="1150" y2="270" stroke="#3a3f7a" stroke-width="6" stroke-linecap="round"/>' + body
    else:
        rows = d['rows']; mx = max(r['value'] for r in rows); step = 80 if len(rows) > 5 else 92
        for i, r in enumerate(rows):
            y = 132 + i * step; w = 640 * r['value'] / mx; col = '#00E5FF' if i == 0 else '#5b63c9'
            body += f"""<text x="56" y="{y+34}" font-size="30" font-weight="800" fill="#fff">{E(r['label'])}</text>
<rect x="190" y="{y}" width="{w}" height="48" rx="8" fill="{col}"/>
<text x="{190+w+16}" y="{y+34}" font-size="28" font-weight="800" fill="{'#00E5FF' if i==0 else '#fff'}">{E(r['text'])}</text>
<text x="190" y="{y+72}" font-size="16" fill="#9aa0c8">{E(r.get('caption',''))}</text>"""
    return f"""<div style="width:1200px;height:700px;position:relative;background:#0D0D14">{head}
 <svg width="1200" height="700" viewBox="0 0 1200 700" style="position:absolute;left:0;top:0">{body}</svg>{foot}</div>"""


async def main(spec_path, out):
    spec = json.load(open(spec_path, encoding='utf-8'))
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for key, fn, h in (('hero', hero, 630), ('diagram', diagram, 700)):
            pg = await b.new_page(viewport={'width': 1200, 'height': h})
            await pg.set_content(BASE % fn(spec[key]))
            await pg.wait_for_timeout(400)
            png = os.path.join(out, ('hero' if key == 'hero' else 'diagrama') + '.png')
            await pg.screenshot(path=png)
            Image.open(png).convert('RGB').save(png.replace('.png', '.jpg'), quality=90)
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1], sys.argv[2]))
