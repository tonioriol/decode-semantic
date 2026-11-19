"""Builds index.html: every figure lives in DATA below with its source. Run: python3 build.py"""
import html
from pathlib import Path
H = Path(__file__).resolve().parent

NAME = 'rsemble'  # default text only; the page's one NAME constant (in its <script>) is what to change

# ---- aggregate benchmark data ----
# Chat search, 45 labelled questions, hit@1/3/10, warm median latency, idle footprint
LADDER = [
    # label, sub, h1, h3, h10, latency, memory, kind
    ('Python Semble 0.7.3', 'in-RAM reference', .511, .711, .822, '41 ms', '4.8 GB', 'ref'),
    ('First Rust port', 'on-disk index', .489, .600, .800, '165 ms', '178 MB', 'old'),
    ('Static, tuned', 'BM25 + potion-code-16M', .533, .644, .778, '~44 ms', '~85 MB', 'old'),
    ('+ e5-small rerank', 'top 20, live', .578, .733, .778, '~1.6 s', '742 MB', 'old'),
    ('+ MiniLM rerank', 'top 20, live', .578, .711, .778, '230 ms', '~128 MB', 'old'),
    ('Stored rerank vectors', 'MiniLM rows made at index time', .578, .711, .778, '42–44 ms', '~125 MB', 'old'),
    ('Now', 'stored vectors, two-worker mapped scan', .578, .689, .778, '19 ms', '~129 MB', 'now'),
]
HOLDOUT = [
    ('Static', '60 unseen questions', .517, .767, .883, '', '', 'old'),
    ('Now', '60 unseen questions', .617, .817, .917, '', '', 'now'),
]
MEMORY_ACC = [
    ('Benchmark', '30 questions', .700, .833, .967, '', '', 'old'),
    ('Unseen', '34 new questions', .941, 1.0, 1.0, '', '', 'now'),
]
CODE = [
    ('Python Semble 0.7.3', '', .449, .626, .766, '17.2 s', '13.2 ms', 'ref'),
    (NAME, '', .449, .626, .766, '4.4 s', '9.9 ms', 'now'),
    ('ck 0.8.1', 'hybrid, bge-small', .290, .458, .626, '88 min', '1.6 s', 'old'),
    ('Probe', 'BM25, no index', .215, .336, .467, 'none', '6.6 s', 'old'),
]
# before/after bars: (panel title, unit, [(label, lo, hi, text, kind)])
BARS = [
    ('Chat search · warm median', 'ms', [
        ('Python Semble', 41, 41, '41 ms', 'ref'),
        ('First Rust port', 165, 165, '165 ms', 'old'),
        ('MiniLM, live rerank', 230, 230, '230 ms', 'old'),
        ('Stored vectors', 42, 44, '42–44 ms', 'old'),
        ('Now', 17, 22, '17–22 ms', 'now')]),
    ('Chat search · idle memory', 'MB', [
        ('Python Semble', 4805, 4805, '4,805 MB', 'ref'),
        ('First Rust port', 178, 178, '178 MB', 'old'),
        ('Now', 119, 132, '~129 MB', 'now')]),
    ('Memory search · warm search', 'ms', [
        ('Before', 204, 327, '204–327 ms', 'old'),
        ('Now', 31, 58, '31–58 ms', 'now')]),
    ('Memory search · idle memory', 'MB', [
        ('Before', 405, 457, '405–457 MB', 'old'),
        ('Now', 50, 50, '~50 MB', 'now')]),
]
EXAMPLES = [
    ('fuse BM25 and semantic candidates by reciprocal rank', 'rsemble-core/src/search.rs:146', 'the search entry point: semantic and BM25 candidates, each through rrf()', '12.1 ms'),
    ('read the index file in place without loading it into memory', 'rsemble-core/src/index.rs:1', 'module doc: "The bulk lives in a persisted file read with positioned reads"', '21.8 ms'),
]
DISK = [
    ('Chat index', '1.7 GB', 'of which stored MiniLM vectors: 382 MB'),
    ('Memory index', '254 MB', '+ 62 MB static model (potion-code-16M)'),
    ('MiniLM rerank model, int8', '22 MB', 'chat search only'),
]

def nm(): return f'<span class="nm">{NAME}</span>'

def esc(s): return html.escape(s)

def dots(rows, lo, hi, ticks, cols=None):
    pct = lambda v: (v - lo) / (hi - lo) * 100
    out = [f'<div class="dp{"" if cols else " nc"}">']
    if cols:
        out.append(f'<div class="dp-row dp-head"><div></div><div class="axis">' +
                   ''.join(f'<span style="left:{pct(t):.2f}%">{t:.1f}</span>' for t in ticks) +
                   '</div>' + ''.join(f'<div class="num h">{c}</div>' for c in cols) + '</div>')
    for (label, sub, a, b, c, x, y, kind) in rows:
        lab = nm() if label == NAME else esc(label)
        tip = f'{label}: hit@1 {a:.3f} · hit@3 {b:.3f} · hit@10 {c:.3f}'
        out.append(f'<div class="dp-row {kind}" title="{esc(tip)}"><div class="lab"><b>{lab}</b>'
                   f'{f"<small>{esc(sub)}</small>" if sub else ""}</div><div class="track">'
                   + ''.join(f'<i class="grid" style="left:{pct(t):.2f}%"></i>' for t in ticks) +
                   f'<i class="span" style="left:{pct(a):.2f}%;width:{pct(c)-pct(a):.2f}%"></i>'
                   f'<i class="d d10" style="left:{pct(c):.2f}%"></i><i class="d d3" style="left:{pct(b):.2f}%"></i>'
                   f'<i class="d d1" style="left:{pct(a):.2f}%"></i>'
                   f'<em class="v1" style="left:{pct(a):.2f}%">{a:.3f}</em>'
                   f'<em class="v10" style="left:{pct(c):.2f}%">{c:.3f}</em></div>'
                   + (f'<div class="num" data-h="{cols[0]} ">{esc(x)}</div><div class="num" data-h="{cols[1]} ">{esc(y)}</div>' if cols else '') + '</div>')
    out.append('</div>')
    return ''.join(out)

def bars():
    out = ['<div class="bars">']
    for title, unit, rows in BARS:
        mx = max(r[2] for r in rows)
        out.append(f'<div class="panel"><h4>{esc(title)}</h4>')
        for label, a, b, text, kind in rows:
            out.append(f'<div class="bar {kind}" title="{esc(label)}: {esc(text)}"><span class="bl">{esc(label)}</span>'
                       f'<span class="bt"><i class="lo" style="width:{a/mx*100:.2f}%"></i>'
                       f'<i class="hi" style="width:{b/mx*100:.2f}%"></i></span><span class="bv">{esc(text)}</span></div>')
        out.append('</div>')
    out.append('</div>')
    return ''.join(out)

LEGEND = ('<div class="legend"><span><i class="d d1"></i>hit@1</span><span><i class="d d3"></i>hit@3</span>'
          '<span><i class="d d10"></i>hit@10</span><span class="muted">share of questions whose answer is in the top 1, 3 or 10</span></div>')

DIAGRAM = '''<svg viewBox="0 0 760 300" role="img" aria-label="A query runs BM25 and a static embedding over the on-disk index in parallel, fuses them by reciprocal rank, and for chats re-scores the top 20 with stored MiniLM vectors. File events keep the index current without a walk.">
<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" class="fill-ink"/></marker></defs>
<g class="box"><rect x="10" y="118" width="110" height="52" rx="8"/><text x="65" y="141" class="t">query</text><text x="65" y="158" class="s">embedded once</text></g>
<g class="box"><rect x="170" y="58" width="170" height="52" rx="8"/><text x="255" y="81" class="t">BM25</text><text x="255" y="98" class="s">postings via pread</text></g>
<g class="box"><rect x="170" y="178" width="170" height="52" rx="8"/><text x="255" y="201" class="t">static embedding</text><text x="255" y="218" class="s">potion-code-16M · int8 table</text></g>
<g class="box"><rect x="390" y="118" width="130" height="52" rx="8"/><text x="455" y="141" class="t">RRF fusion</text><text x="455" y="158" class="s">+ Semble boosts</text></g>
<g class="box acc"><rect x="570" y="118" width="180" height="52" rx="8"/><text x="660" y="141" class="t">MiniLM rerank</text><text x="660" y="158" class="s">top 20 · 0.3 static / 0.7 MiniLM</text></g>
<text x="660" y="190" class="s">chat search only</text>
<path d="M120 136 C145 136 145 84 168 84" class="ln" marker-end="url(#ah)"/>
<path d="M120 152 C145 152 145 204 168 204" class="ln" marker-end="url(#ah)"/>
<path d="M340 84 C365 84 365 136 388 136" class="ln" marker-end="url(#ah)"/>
<path d="M340 204 C365 204 365 152 388 152" class="ln" marker-end="url(#ah)"/>
<path d="M520 144 L568 144" class="ln" marker-end="url(#ah)"/>
<g class="disk"><rect x="170" y="252" width="380" height="38" rx="8"/><text x="360" y="275" class="s">on-disk index, read in place: postings · int8 vectors · MiniLM rows</text></g>
<path d="M255 230 L255 250" class="ln dash"/>
<path d="M660 170 L660 178" class="ln dash"/><path d="M660 196 L660 271 L552 271" class="ln dash"/>
<g class="disk"><rect x="170" y="8" width="380" height="34" rx="8"/><text x="360" y="29" class="s">File change notifications → re-index changed files only</text></g>
<path d="M255 42 L255 56" class="ln dash"/>
</svg>'''

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NAME}</title>
<style>
/* Layout: one 760px reading column; figures sit in it as quiet bordered plates, summary tiles first. */
:root{{
  color-scheme: light;
  --bg:#f4f6f6; --plate:#ffffff; --ink:#132020; --muted:#5a6968; --rule:#d9e1e0;
  --acc:#0f766e; --acc-soft:#e3f1ef; --old:#a3aeac; --ref:#6f7f7d;
  --k1:#0b5f58; --k3:#2a9d8f; --k10:#8fd3c7;
  --sans: ui-sans-serif, -apple-system, "Segoe UI", system-ui, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --r: 10px;
}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{color-scheme:dark;
  --bg:#0d1414; --plate:#141d1d; --ink:#e4eceb; --muted:#93a3a1; --rule:#263332;
  --acc:#3cc7b4; --acc-soft:#16302d; --old:#55635f; --ref:#7d8d8b;
  --k1:#7ee6d6; --k3:#36a596; --k10:#1d6a61;}}}}
:root[data-theme="dark"]{{color-scheme:dark;
  --bg:#0d1414; --plate:#141d1d; --ink:#e4eceb; --muted:#93a3a1; --rule:#263332;
  --acc:#3cc7b4; --acc-soft:#16302d; --old:#55635f; --ref:#7d8d8b;
  --k1:#7ee6d6; --k3:#36a596; --k10:#1d6a61;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans);font-variant-numeric:tabular-nums;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:760px;margin:0 auto;padding-block:48px 64px;display:grid;gap:56px;grid-template-columns:minmax(0,1fr)}}
h1,h2,h3,h4{{text-wrap:balance;margin:0}}
h1{{font-size:clamp(34px,7vw,52px);line-height:1.05;letter-spacing:-.02em;font-weight:800}}
h1 .nm{{color:var(--acc)}}
h2{{font-size:22px;letter-spacing:-.01em}}
h4{{font-size:13px;font-weight:600;color:var(--muted)}}
p{{margin:0;max-width:65ch}}
.eyebrow{{font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
.lede{{font-size:18px;color:var(--ink)}}
.muted{{color:var(--muted)}}
code,.mono{{font-family:var(--mono);font-size:.9em}}
section{{display:grid;gap:16px;grid-template-columns:minmax(0,1fr)}}
main>*,section>*,.panel>*,.hero>*{{min-width:0}}
.hero{{display:grid;gap:18px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
.tile{{background:var(--plate);border:1px solid var(--rule);border-radius:var(--r);padding:14px 14px 12px;display:grid;gap:2px}}
.tile b{{font-size:28px;line-height:1.1;letter-spacing:-.02em;color:var(--acc)}}
.tile span{{font-size:13px;color:var(--muted)}}
.plate{{background:var(--plate);border:1px solid var(--rule);border-radius:var(--r);padding:18px 18px 14px}}
.note{{font-size:13px;color:var(--muted)}}
/* dot plot */
.dp{{display:grid;gap:4px}}
.dp-row{{display:grid;grid-template-columns:180px 1fr 72px 72px;gap:12px;align-items:center;padding:6px 8px;border-radius:8px}}
.dp-row.now{{background:var(--acc-soft)}}
.nc .dp-row{{grid-template-columns:110px 1fr;padding-inline:6px 14px}}
.dp-head{{padding-block:0}}
.lab b{{display:block;font-weight:600;font-size:14px;line-height:1.2}}
.lab small{{display:block;color:var(--muted);font-size:12px}}
.num{{text-align:right;font-size:14px}} .num.h{{font-size:12px;color:var(--muted)}}
.now .num{{font-weight:700}}
.track{{position:relative;height:34px}}
.axis{{position:relative;height:16px;font-size:11px;color:var(--muted)}}
.axis span{{position:absolute;transform:translateX(-50%)}}
.track .grid{{position:absolute;top:0;bottom:0;width:1px;background:var(--rule)}}
.track .span{{position:absolute;top:16px;height:2px;background:var(--muted);opacity:.45}}
.d{{position:absolute;top:17px;width:12px;height:12px;border-radius:50%;transform:translate(-50%,-50%);display:block}}
.d1{{background:var(--k1);box-shadow:0 0 0 2px var(--plate);z-index:3;width:13px;height:13px}}
.d3{{background:var(--k3);box-shadow:0 0 0 2px var(--plate);z-index:2;width:10px;height:10px}}
.d10{{background:var(--plate);border:2.5px solid var(--k10);z-index:1}}
.now .d1,.now .d3{{box-shadow:0 0 0 2px var(--acc-soft)}}
.now .d10{{background:var(--acc-soft)}}
.track em{{position:absolute;top:24px;font:600 11px/1 var(--sans);font-style:normal;color:var(--muted);transform:translateX(-50%)}}
.track em.v10{{top:0;}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;align-items:center}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.legend .d{{position:static;transform:none}}
/* bars */
.bars{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px 28px}}
.panel{{display:grid;gap:8px;align-content:start}}
.bar{{display:grid;grid-template-columns:118px 1fr 82px;gap:10px;align-items:center;font-size:13px}}
.bl{{color:var(--muted)}} .bv{{text-align:right}}
.bt{{position:relative;height:14px}}
.bt i{{position:absolute;left:0;top:0;bottom:0;border-radius:0 4px 4px 0;min-width:3px}}
.bt .hi{{opacity:.45}}
.bar.old i{{background:var(--old)}} .bar.ref i{{background:var(--ref)}} .bar.now i{{background:var(--acc)}}
.bar.now .bl,.bar.now .bv{{color:var(--ink);font-weight:700}}
/* diagram */
figure{{margin:0;display:grid;gap:10px}}
figcaption{{font-size:13px;color:var(--muted)}}
.dg{{overflow-x:auto}} .dg svg{{min-width:600px;width:100%;height:auto;display:block}}
.box rect{{fill:var(--plate);stroke:var(--rule);stroke-width:1.5}}
.box.acc rect{{fill:var(--acc-soft);stroke:var(--acc)}}
.disk rect{{fill:none;stroke:var(--rule);stroke-dasharray:4 4}}
svg .t{{font:600 14px var(--sans);fill:var(--ink);text-anchor:middle}}
svg .s{{font:12px var(--sans);fill:var(--muted);text-anchor:middle}}
.ln{{fill:none;stroke:var(--ink);stroke-width:1.5;opacity:.7}} .dash{{stroke-dasharray:3 4;marker-end:none}}
.fill-ink{{fill:var(--ink)}}
/* examples */
.ex{{display:grid;gap:10px}}
.q{{display:grid;grid-template-columns:1fr auto;gap:2px 12px;padding:12px 14px;background:var(--plate);border:1px solid var(--rule);border-radius:var(--r)}}
.q .qq{{font-weight:600}} .q .qq::before{{content:"› ";color:var(--acc)}}
.q .ms{{font-size:13px;color:var(--muted);text-align:right}}
.q .hit{{grid-column:1/-1;font:13px/1.45 var(--mono);color:var(--acc)}}
.q .why{{grid-column:1/-1;font-size:13px;color:var(--muted)}}
table{{border-collapse:collapse;width:100%;font-size:14px}}
td{{padding:9px 0;border-top:1px solid var(--rule);vertical-align:top}}
td.v{{text-align:right;font-weight:700;padding-inline:16px;white-space:nowrap}}
td.n{{color:var(--muted);font-size:13px}}
.parts{{display:flex;flex-wrap:wrap;gap:8px}}
.parts span{{font-size:13px;padding:4px 10px;border:1px solid var(--rule);border-radius:999px;background:var(--plate)}}
footer{{font-size:12px;color:var(--muted);display:grid;gap:6px;border-top:1px solid var(--rule);padding-top:16px}}
a{{color:var(--acc)}}
@media (max-width:640px){{
  main{{padding-block:28px 48px;gap:44px}}
  .tiles{{grid-template-columns:1fr 1fr}}
  .bars,.shots{{grid-template-columns:1fr}}
  .dp-row{{grid-template-columns:minmax(0,1fr) auto auto;gap:4px 12px}}
  .dp-row .num{{white-space:nowrap;align-self:start}}
  .nc .dp-row{{grid-template-columns:120px 1fr;padding-inline:6px 14px}}
  .nc .dp-row .track{{grid-column:auto;grid-row:auto}}
  .dp-row .track,.dp-row .axis{{grid-column:1/-1;grid-row:2}}
  .dp-head{{display:none}}
  .dp-row .num::before{{content:attr(data-h);color:var(--muted);font-weight:400;font-size:11px}}
  .td-n{{display:none}}
}}
</style></head>
<body><main>

<header class="hero">
  <div class="eyebrow">Rust · MIT · Semble's ranking, rebuilt for disk</div>
  <h1>{nm()}: semantic search in ~19&nbsp;ms and ~129&nbsp;MB</h1>
  <p class="lede">{nm()} searches a large chat corpus, a shelf of project notes, and source code from one Rust process. It keeps the quality of <a href="https://github.com/MinishLab/semble">Semble</a>'s recipe, BM25 fused with static embeddings, and adds a small neural rerank for chats. It answers faster than Python Semble in 1/37 of its memory.</p>
  <div class="tiles">
    <div class="tile"><b>19 ms</b><span>chat search with rerank, warm median</span></div>
    <div class="tile"><b>4.8 GB → 129 MB</b><span>chat search idle memory vs Python Semble</span></div>
    <div class="tile"><b>.617</b><span>hit@1 on 60 unseen chat questions (static: .517)</span></div>
    <div class="tile"><b>31–58 ms</b><span>notes search, warm (was 204–327 ms)</span></div>
  </div>
</header>

<section>
  <div class="eyebrow">Chat search · 45 labelled questions</div>
  <h2>Every step up the ladder, measured</h2>
  <p class="muted">Each row is a version we shipped or tried. The rerank lifted hit@1 from .533 to .578. Storing its passage vectors at index time cut a search from 230 ms to 42–44 ms, and scanning the vectors on two workers over memory-mapped files to 19 ms. Measured side by side, query by query, the rerank itself adds 2 ms: 19.1 ms with it, 16.5 ms without. Rows are measured on the index of their day; hit@3 moved from .711 to .689 when the fixture was refreshed with newer chats, and the speed changes left every ranking identical.</p>
  <div class="plate">{dots(LADDER, .4, .9, [.4,.5,.6,.7,.8,.9], ['latency','idle'])}</div>
  {LEGEND}
  <div class="bars">
    <div class="panel"><h4>Chat search · 60 unseen questions (holdout)</h4><div class="plate">{dots(HOLDOUT, .4, 1.0, [.4,.6,.8,1.0])}</div></div>
    <div class="panel"><h4>Notes search · hit@1/3/10</h4><div class="plate">{dots(MEMORY_ACC, .4, 1.0, [.4,.6,.8,1.0])}</div></div>
  </div>
</section>

<section>
  <div class="eyebrow">Before → after</div>
  <h2>Faster than the port it started as, lighter than the original</h2>
  <div class="plate">{bars()}</div>
  <p class="note">Physical footprint, decimal MB, on a shared, loaded laptop. Ranges are repeated runs. Python Semble keeps its whole index in RAM; {nm()} reads it from disk in place. Python Semble's 41 ms was measured on an earlier day, not in the same window. Chat latency is the median of 810 warm searches over six rounds with rerank on and off interleaved query by query (round medians 17–22 ms, p90 28 ms). Chat figures come from a benchmark index; a long-running chat process has been seen at 208–273 MB, most of it freed memory macOS had not yet reclaimed. The notes figure is the long-running process; a fresh one reads 90–164 MB for the same reason.</p>
</section>

<section>
  <div class="eyebrow">Code search · 107 questions</div>
  <h2>Same answers as Python Semble, ahead of ck and Probe</h2>
  <div class="plate">{dots(CODE, .1, .9, [.1,.3,.5,.7,.9], ['index','query'])}</div>
  {LEGEND}
  <p class="note">{nm()} scores exactly what Python Semble 0.7.3 scores (hit@1/3/10 and MRR identical) and indexes 3.9× faster. ck 0.8.1 (hybrid, bge-small) took 5,312 s to index; Probe has no index and starts a process per query. Index time is a cold build; query time is the warm median.</p>
</section>

<section>
  <div class="eyebrow">How it works</div>
  <h2>Two stages, one file on disk</h2>
  <figure>
    <div class="plate dg">{DIAGRAM}</div>
    <figcaption>BM25 and a static embedding each pick candidates; reciprocal rank fusion merges them. Chat search then re-scores its top 20 with MiniLM, reading passage vectors stored at index time, so a search embeds only the query.</figcaption>
  </figure>
  <div class="parts">
    <span>index read in place (pread, mmap)</span><span>int8 embedding table</span><span>streamed model load</span>
    <span>index refresh on file change</span><span>chat segments</span><span>stored rerank vectors</span>
  </div>
</section>

<section>
  <div class="eyebrow">Real searches over its own source</div>
  <h2>Ask in words, land on the line</h2>
  <div class="ex">
    {''.join(f'<div class="q"><span class="qq">{esc(q)}</span><span class="ms">{ms}</span><span class="hit">#1 {esc(hit)}</span><span class="why">{esc(why)}</span></div>' for q, hit, why, ms in EXAMPLES)}
  </div>
</section>

<section>
  <div class="eyebrow">On disk</div>
  <h2>What it stores</h2>
  <table>{''.join(f'<tr><td>{esc(a)}</td><td class="v">{esc(b)}</td><td class="n">{esc(c)}</td></tr>' for a, b, c in DISK)}</table>
</section>

<footer>
  <p>{nm()} is MIT-licensed: crates <code><span class="nm">{NAME}</span>-core</code> and <code><span class="nm">{NAME}</span></code>. Ranking is a function-by-function port of <a href="https://github.com/MinishLab/semble">Semble</a> by MinishLab (MIT), with <a href="https://huggingface.co/minishlab/potion-code-16M">potion-code-16M</a> static embeddings and <a href="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2">all-MiniLM-L6-v2</a> (int8) for the chat rerank.</p>
  <p>Hit@k: share of questions whose labelled answer is in the top k results. Chat sets: 45 labelled questions, plus 60 holdout questions never used for tuning. All timings on an Apple-silicon laptop under concurrent load.</p>
</footer>
</main>
<script>
// The engine's public name, in one place.
const NAME = "rsemble";
document.title = NAME;
document.querySelectorAll(".nm").forEach((el) => {{ el.textContent = NAME; }});
</script>
</body></html>'''
(H / 'index.html').write_text(page)
print('wrote', len(page), 'bytes')
