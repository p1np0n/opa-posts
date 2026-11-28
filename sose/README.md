# SOSE
Publicaciones diarias de SOSE (Facebook + Instagram), a las 12:00 y 21:00 (hora de Chile). Un escenario de Make lee estos archivos y publica.
Cada publicacion son tres archivos con el mismo nombre base `AAAA-MM-DD_1200` o `AAAA-MM-DD_2100`: `.jpg` (1080x1350), `_ig.txt` (texto Instagram + hashtags) y `_fb.txt` (texto Facebook).
- `specs/`: JSON de cada publicacion (fuente de verdad del contenido).
- `tools/render_post.py <spec.json>`: genera jpg + textos y registra la fila en `db/publicaciones.csv`.
- `db/publicaciones.csv`: base de datos de contenido. `db/banco_ideas.csv`: temas por investigar.
- `assets/`: logo de SOSE.
- `db/imagenes.csv`: catálogo de todas las gráficas (fecha, hora, link público, tema, estado). Se regenera con `python3 -I sose/tools/index_imagenes.py`.
- Colchón: la tarea nocturna mantiene siempre 7 días de posts listos por adelantado y rellena cualquier hueco.
- Fuentes para render_post.py: Lora (google/fonts) en /usr/share/fonts/truetype/google-fonts/ e Inter 4.0 en /usr/share/fonts/opentype/inter/.
