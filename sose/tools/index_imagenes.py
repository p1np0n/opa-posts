#!/usr/bin/env python3
"""Reconstruye sose/db/imagenes.csv: catálogo de todas las gráficas SOSE del repo.
Uso (desde la raíz del repo): python3 -I sose/tools/index_imagenes.py
Columnas: fecha, slot, archivo, url_publica, categoria, tema, texto, estado.
estado = fecha_pasada si la hora ya pasó (hora de Chile; no confirma que Make lo publicó), programado si no."""
import csv, glob, json, os, datetime
from zoneinfo import ZoneInfo
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SOSE = os.path.join(ROOT, "sose")
RAW = "https://raw.githubusercontent.com/p1np0n/opa-posts/main/sose/"
now = datetime.datetime.now(ZoneInfo("America/Santiago"))
specs = {}
for f in glob.glob(os.path.join(SOSE, "specs", "*.json")):
    try: specs[os.path.basename(f)[:-5]] = json.load(open(f, encoding="utf-8"))
    except Exception: pass
rows = []
for jpg in sorted(glob.glob(os.path.join(SOSE, "20*_*.jpg"))):
    base = os.path.basename(jpg)[:-4]
    fecha, slot = base.split("_")[:2]
    s = specs.get(base, {})
    when = datetime.datetime.strptime(fecha + slot, "%Y-%m-%d%H%M").replace(tzinfo=ZoneInfo("America/Santiago"))
    rows.append([fecha, slot, base + ".jpg", RAW + base + ".jpg", s.get("categoria", ""), s.get("tema", ""),
                 s.get("texto", s.get("titulo", "")), "fecha_pasada" if when <= now else "programado"])
with open(os.path.join(SOSE, "db", "imagenes.csv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["fecha", "slot", "archivo", "url_publica", "categoria", "tema", "texto", "estado"])
    w.writerows(rows)
print(f"imagenes.csv: {len(rows)} gráficas")
