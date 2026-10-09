# opa-posts
Publicaciones diarias de OverPowerArmor (Instagram y Facebook).
Cada publicacion son dos archivos en `posts/` con el mismo nombre: `AAAA-MM-DD_HHMM.jpg` (imagen 1080x1350) y `AAAA-MM-DD_HHMM.txt` (texto con hashtags).
Horarios (hora de Chile): 0900, 1400 y 2130. Un escenario de Make lee estos archivos y publica.

## Herramientas
`tools/render.py <archivo.json>` genera `png/<id>.png` y `jpg/<id>.jpg` (1080x1350, calidad 90) para cada publicacion del JSON (campos: id, kind, pillar, tag, motif, hue, big, title, sub, caption, tags). Requiere Python con Playwright (Chromium) y Pillow. Luego se copia `jpg/<id>.jpg` a `posts/AAAA-MM-DD_HHMM.jpg` y se escribe el `.txt` con el caption, una linea en blanco y los hashtags.

## Reels
`reels/AAAA-MM-DD_HHMM.mp4` (9:16, 1080x1920, H.264/AAC, 3 a 90 s) y `.txt` con el caption. El escenario de Make los publica como reel en Instagram (tambien en el feed) y Facebook a la hora indicada (hoy solo existe la ventana 1800). Scripts: `tools/reel_video.py` y `tools/reel_music.py` (musica original sintetizada).

### Generar un reel (tools/)
1. Musica: `REEL_BPM=118 REEL_PROG=b REEL_SEED=7 REEL_WAV=music.wav python3 tools/reel_music.py 38` (BPM 110-128; REEL_PROG a/b/c/d; cambiar seed para variar).
2. Video: `python3 tools/reel_make.py spec.json salida.mp4 full music.wav`. El spec es un JSON con `intro` [numero, linea1, linea2, linea3], `outro` [linea1, linea2, llamado, texto final] y `scenes` (5 a 6): game (etiqueta), title, d (numero grande, max 4 caracteres), m (palabra bajo el numero), sub, sub2, hue (0-359), short y right (para la lista final). La duracion es 3 s + 6,2 s por escena + 4 s.
3. Remux sin edit list: `ffmpeg -i salida.mp4 -c copy -use_editlist 0 -movflags +faststart final.mp4`. Requisitos de Instagram: MP4 H.264/AAC, 9:16, 3 a 90 s.
