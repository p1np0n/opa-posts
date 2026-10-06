# opa-posts
Publicaciones diarias de OverPowerArmor (Instagram y Facebook).
Cada publicacion son dos archivos en `posts/` con el mismo nombre: `AAAA-MM-DD_HHMM.jpg` (imagen 1080x1350) y `AAAA-MM-DD_HHMM.txt` (texto con hashtags).
Horarios (hora de Chile): 0900, 1400 y 2130. Un escenario de Make lee estos archivos y publica.

## Herramientas
`tools/render.py <archivo.json>` genera `png/<id>.png` y `jpg/<id>.jpg` (1080x1350, calidad 90) para cada publicacion del JSON (campos: id, kind, pillar, tag, motif, hue, big, title, sub, caption, tags). Requiere Python con Playwright (Chromium) y Pillow. Luego se copia `jpg/<id>.jpg` a `posts/AAAA-MM-DD_HHMM.jpg` y se escribe el `.txt` con el caption, una linea en blanco y los hashtags.
