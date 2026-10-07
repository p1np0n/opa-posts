# SOSE
Publicaciones diarias de SOSE (Facebook + Instagram), a las 12:00 y 21:00 (hora de Chile). Un escenario de Make lee estos archivos y publica.
Cada publicacion son tres archivos con el mismo nombre base `AAAA-MM-DD_1200` o `AAAA-MM-DD_2100`: `.jpg` (1080x1350), `_ig.txt` (texto Instagram + hashtags) y `_fb.txt` (texto Facebook).
- `specs/`: JSON de cada publicacion (fuente de verdad del contenido).
- `tools/render_post.py <spec.json>`: genera jpg + textos y registra la fila en `db/publicaciones.csv`.
- `db/publicaciones.csv`: base de datos de contenido. `db/banco_ideas.csv`: temas por investigar.
- `assets/`: logo de SOSE.
