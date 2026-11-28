# Agente de contenido permanente OPA

Objetivo: que Instagram @optcgcl y Facebook "OverPower TCG" nunca se queden sin publicaciones.
El escenario de Make 6523203 lee este repo (rama `main`) y publica a diario, hora de Chile:

| Hora | Archivo | Contenido |
|------|---------|-----------|
| 09:00 | `posts/AAAA-MM-DD_0900.jpg` + `.txt` | Tips o Accesorios 101 (atemporal) |
| 14:00 | `posts/AAAA-MM-DD_1400.jpg` + `.txt` | Noticia TCG real y vigente |
| 18:00 | `reels/AAAA-MM-DD_1800.mp4` + `.txt` | Reel: día impar "5 lanzamientos TCG que vienen", día par "5 datos TCG" |
| 21:30 | `posts/AAAA-MM-DD_2130.jpg` + `.txt` | ¿Sabías que…? (atemporal) |

Si falta un archivo, Make no publica y no marca error. Por eso hay que mantener siempre
**14 días de margen** cargados.

## Rutina (cada ejecución)
1. `pip install -q playwright pillow numpy` si faltan (no ejecutar `playwright install`;
   `tools/render.py` usa `/opt/pw-browsers/chromium` si existe).
2. `python3 tools/opa_status.py 14 7` → lista los horarios vacíos de hoy a hoy+14.
3. Si hay huecos, crear `agente/lotes/AAAA-MM-DD.json` (fecha de hoy) con el mismo formato
   que `agente/lotes/2026-11-28.json` y llenar **todos** los huecos:
   - Noticias 14:00: buscar en la web noticias de los últimos días y próximos lanzamientos de
     Pokémon, Magic, One Piece, Lorcana, Riftbound, Yu-Gi-Oh!, Digimon, Dragon Ball,
     Star Wars Unlimited, Union Arena y Mitos y Leyendas. Verificar fechas en 2 fuentes si se
     puede; marcar rumores como rumores; parafrasear, nunca copiar texto. La noticia debe
     seguir vigente el día que se publica.
   - Atemporales 09:00 y 21:30: temas nuevos. Antes de escribir, revisar títulos ya usados con
     `for f in posts/*.txt; do head -1 "$f"; done` y no repetir temas.
   - Reels: impar = lanzamientos (lista actualizada, fechas futuras al día del reel);
     par = 5 datos (pueden repetirse datos, variar combinación). Cambiar `music.seed` y `prog`.
   - Hue distinto (≥12°) entre publicaciones cercanas; `big` de máx. 5 caracteres; motivos de
     `tools/render.py` (shards, burst, rays, sunburst, spotlight, ruler, slab, petals, triangles,
     stack, waves, chart, pentagon, grid9, horizon, andes, checklist, calendar, moonrings, mat,
     layers, tags, pages, trophy, split, moon, drops, glare, stars).
4. `python3 tools/opa_batch.py agente/lotes/AAAA-MM-DD.json` (no sobrescribe archivos existentes
   ni horarios pasados). Revisar una hoja de contacto de los JPG nuevos y un fotograma del reel.
5. `git add posts reels agente && git commit && git push origin main`.
6. `python3 tools/opa_status.py 14 7` de nuevo e informar el resultado.

## Estilo
- Español neutro, tuteo, emojis moderados, cierre con pregunta para comentar.
- Medidas métricas (mm, cm, g, kg); precios en CLP solo si son de OPA.
- Fundas estándar 63 × 88 mm; japonesas pequeñas 59 × 86 mm.
- No copiar logos, personajes ni arte de ningún juego: solo formas abstractas y texto.
- Contenido informativo; menciones a OverPowerArmor.cl solo en tips de accesorios y reels.

## Aviso
Si `opa_status.py` imprime `ALERTA` después de cargar (huecos a 7 días o menos), avisar a Ivan.
