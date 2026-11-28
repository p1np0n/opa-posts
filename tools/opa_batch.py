# -*- coding: utf-8 -*-
"""Carga un lote de contenido en posts/ y reels/.

Uso: python3 tools/opa_batch.py agente/lotes/AAAA-MM-DD.json [--force]

El lote es un JSON con:
  "posts": [ {"slot": "2026-12-05_0900", "kind", "pillar", "tag", "motif", "hue",
              "big", "title", "sub", "caption", "tags", "date"(opcional)} ... ]
  "reels": [ {"slot": "2026-12-01_1800", "caption": "...",
              "music": {"bpm": 118, "prog": "b", "seed": 7},
              "spec": {"intro": [...], "outro": [...], "scenes": [...]}} ... ]

Nunca sobrescribe un archivo que ya existe (salvo --force) y nunca toca
horarios que ya pasaron (hora de Chile).
"""
import json, os, sys, subprocess, shutil, tempfile, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
CL = ZoneInfo('America/Santiago')


def slot_dt(slot):
    d, hm = slot.split('_')
    return datetime.datetime.fromisoformat(f"{d}T{hm[:2]}:{hm[2:]}").replace(tzinfo=CL)


def main():
    batch = json.load(open(sys.argv[1], encoding='utf-8'))
    force = '--force' in sys.argv
    now = datetime.datetime.now(CL)
    work = tempfile.mkdtemp(prefix='opa_')
    done, skipped = [], []

    # ---- posts ----
    todo = []
    for p in batch.get('posts', []):
        slot = p['slot']
        jpg = os.path.join(ROOT, 'posts', slot + '.jpg')
        if slot_dt(slot) <= now:
            skipped.append(slot + ' (ya pasó)'); continue
        if os.path.exists(jpg) and not force:
            skipped.append(slot + ' (ya existe)'); continue
        q = dict(p)
        q['id'] = 'p_' + slot
        q.setdefault('date', slot[:10] if p.get('kind') == 'noticia' else None)
        todo.append(q)
    if todo:
        jf = os.path.join(work, 'posts.json')
        json.dump(todo, open(jf, 'w', encoding='utf-8'), ensure_ascii=False)
        subprocess.run([sys.executable, os.path.join(TOOLS, 'render.py'), jf], cwd=work, check=True)
        for q in todo:
            slot = q['slot']
            shutil.copy(os.path.join(work, 'jpg', q['id'] + '.jpg'), os.path.join(ROOT, 'posts', slot + '.jpg'))
            with open(os.path.join(ROOT, 'posts', slot + '.txt'), 'w', encoding='utf-8') as f:
                f.write(q['caption'].rstrip() + '\n\n' + q['tags'].strip() + '\n')
            done.append('post ' + slot)

    # ---- reels ----
    for r in batch.get('reels', []):
        slot = r['slot']
        mp4 = os.path.join(ROOT, 'reels', slot + '.mp4')
        if slot_dt(slot) <= now:
            skipped.append(slot + ' (ya pasó)'); continue
        if os.path.exists(mp4) and not force:
            skipped.append(slot + ' (ya existe)'); continue
        spec = r['spec']
        dur = 3.0 + 6.2 * len(spec['scenes']) + 4.0
        m = r.get('music', {})
        env = dict(os.environ, REEL_BPM=str(m.get('bpm', 120)), REEL_PROG=m.get('prog', 'a'),
                   REEL_SEED=str(m.get('seed', 1)), REEL_WAV=os.path.join(work, 'music.wav'))
        subprocess.run([sys.executable, os.path.join(TOOLS, 'reel_music.py'), str(dur + 1)], cwd=work, env=env, check=True)
        sf = os.path.join(work, 'spec.json')
        json.dump(spec, open(sf, 'w', encoding='utf-8'), ensure_ascii=False)
        raw = os.path.join(work, 'raw.mp4')
        subprocess.run([sys.executable, os.path.join(TOOLS, 'reel_make.py'), sf, raw, 'full', os.path.join(work, 'music.wav')],
                       cwd=work, env=env, check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-c', 'copy', '-use_editlist', '0',
                        '-movflags', '+faststart', mp4], check=True)
        with open(os.path.join(ROOT, 'reels', slot + '.txt'), 'w', encoding='utf-8') as f:
            f.write(r['caption'].rstrip() + '\n')
        done.append('reel ' + slot)

    shutil.rmtree(work, ignore_errors=True)
    print('Cargados:', len(done)); [print('  ' + x) for x in done]
    if skipped:
        print('Omitidos:', len(skipped)); [print('  ' + x) for x in skipped]


if __name__ == '__main__':
    main()
