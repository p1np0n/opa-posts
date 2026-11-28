# -*- coding: utf-8 -*-
"""Muestra hasta qué fecha hay contenido cargado y avisa si el margen es bajo.

Uso: python3 tools/opa_status.py [dias_objetivo=14] [dias_alerta=7]
Imprime los huecos de los próximos dias_objetivo días y termina con una línea
"ALERTA" si algún horario de los próximos dias_alerta días está vacío.
"""
import os, sys, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CL = ZoneInfo('America/Santiago')
SLOTS = [('posts', '0900', '.jpg'), ('posts', '1400', '.jpg'), ('reels', '1800', '.mp4'), ('posts', '2130', '.jpg')]


def ok(folder, day, hm, ext):
    base = os.path.join(ROOT, folder, f"{day}_{hm}")
    return os.path.exists(base + ext) and os.path.exists(base + '.txt')


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    alert = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    today = datetime.datetime.now(CL).date()
    gaps, first_gap = [], None
    for i in range(target + 1):
        day = (today + datetime.timedelta(days=i)).isoformat()
        for folder, hm, ext in SLOTS:
            if not ok(folder, day, hm, ext):
                gaps.append(f"{day}_{hm}")
                if first_gap is None:
                    first_gap = i
    last = {}
    for folder, hm, ext in SLOTS:
        days = sorted(f[:10] for f in os.listdir(os.path.join(ROOT, folder)) if f.endswith(f"_{hm}{ext}"))
        last[hm] = days[-1] if days else '-'
    print('Hoy (Chile):', today.isoformat())
    print('Último día cargado por horario:', ', '.join(f"{k}: {v}" for k, v in last.items()))
    print(f'Huecos en los próximos {target} días: {len(gaps)}')
    for g in gaps:
        print('  ' + g)
    if first_gap is not None and first_gap <= alert:
        print(f'ALERTA: hay horarios sin contenido dentro de {first_gap} días')
    else:
        print('OK: margen suficiente')


if __name__ == '__main__':
    main()
