#!/usr/bin/env python3
"""Genera el blog de significados de tarot para amulet.cards desde el corpus de la app.

Fuente: ../amulet/Resources/ArcanaCorpus/  (un fichero por carta e idioma)
        NN-slug.(es|en).md            → 22 arcanos mayores
        <suit>-NN.(es|en).md          → 56 arcanos menores (copas/oros/espadas/bastos)
Salida: tarot/<slug-es>/index.html  (ES)  y  en/tarot/<slug-en>/index.html  (EN)
        + tarot/index.html y en/tarot/index.html (índice, mayores + menores por palo).

i18n: cada página lleva lang correcto, <link hreflang> a su par, toggle ES/EN y un
script que, la PRIMERA visita, redirige a tu idioma de navegador (no vuelve a molestar).

Uso:  python3 generate_blog.py            # 78 cartas ES+EN + índices
      APP_STORE_URL=https://apps.apple.com/es/app/idXX:  CTA con link real (si no, "próximamente")
"""
import os
import re
from datetime import date
from pathlib import Path

SITE = "https://amulet.cards"
ROOT = Path(__file__).resolve().parent
CORPUS = Path(os.environ.get("CORPUS", ROOT.parent / "amulet" / "Resources" / "ArcanaCorpus"))
APP_STORE_URL = os.environ.get("APP_STORE_URL", "")  # vacío = estado "próximamente"

# ── Arcanos mayores: número → (slug_es, slug_en). Nombres se leen del corpus. ──
MAJORS = {
    0: ("el-loco", "the-fool"), 1: ("el-mago", "the-magician"),
    2: ("la-sacerdotisa", "the-high-priestess"), 3: ("la-emperatriz", "the-empress"),
    4: ("el-emperador", "the-emperor"), 5: ("el-sumo-sacerdote", "the-hierophant"),
    6: ("los-enamorados", "the-lovers"), 7: ("el-carro", "the-chariot"),
    8: ("la-fuerza", "strength"), 9: ("el-ermitano", "the-hermit"),
    10: ("la-rueda-de-la-fortuna", "wheel-of-fortune"), 11: ("la-justicia", "justice"),
    12: ("el-colgado", "the-hanged-man"), 13: ("la-muerte", "death"),
    14: ("la-templanza", "temperance"), 15: ("el-diablo", "the-devil"),
    16: ("la-torre", "the-tower"), 17: ("la-estrella", "the-star"),
    18: ("la-luna", "the-moon"), 19: ("el-sol", "the-sun"),
    20: ("el-juicio", "judgement"), 21: ("el-mundo", "the-world"),
}

# ── Arcanos menores ──
# palo: (prefijo_fichero, slug_es, slug_en, nombre_es, nombre_en, --accent)
SUITS = [
    ("cups",      "copas",   "cups",       "Copas",   "Cups",       "--rose"),
    ("pentacles", "oros",    "pentacles",  "Oros",    "Pentacles",  "--leaf"),
    ("swords",    "espadas", "swords",     "Espadas", "Swords",     "--vermilion"),
    ("wands",     "bastos",  "wands",      "Bastos",  "Wands",      "--lemon"),
]
# rango 1..14 → (slug_es, slug_en)
RANKS = {
    1: ("as", "ace"), 2: ("dos", "two"), 3: ("tres", "three"), 4: ("cuatro", "four"),
    5: ("cinco", "five"), 6: ("seis", "six"), 7: ("siete", "seven"), 8: ("ocho", "eight"),
    9: ("nueve", "nine"), 10: ("diez", "ten"), 11: ("sota", "page"),
    12: ("caballero", "knight"), 13: ("reina", "queen"), 14: ("rey", "king"),
}
MAJOR_ACCENT = "--cobalt"

STR = {
    "es": dict(back="Significados del tarot", up="Del derecho", rev="Invertida",
               work="En el trabajo", love="En el amor", self="En ti", note="Ojo:",
               cta_h="Lleva un diario de tus tiradas",
               cta_p="Saca tu carta del día en la app o registra tu propia tirada. AMULET guarda cada lectura y te enseña qué vuelve con el tiempo. Sin cuenta, sin suscripción.",
               soon="Próximamente en el App Store", get="Descargar en el App Store",
               other="English", k_major="Arcano mayor", k_minor="Arcano menor",
               majors="Arcanos mayores", minors="Arcanos menores"),
    "en": dict(back="Tarot meanings", up="Upright", rev="Reversed",
               work="At work", love="In love", self="In you", note="Note:",
               cta_h="Keep a journal of your readings",
               cta_p="Draw your daily card in the app or log your own reading. AMULET keeps every reading and shows you what returns over time. No account, no subscription.",
               soon="Coming soon to the App Store", get="Download on the App Store",
               other="Español", k_major="Major Arcana", k_minor="Minor Arcana",
               majors="Major Arcana", minors="Minor Arcana"),
}


def parse(md: str):
    """→ {title, upright:{key:[paras]}, reversed:{key:[paras]}}"""
    lines = md.splitlines()
    title = ""
    data = {"upright": {}, "reversed": {}}
    orient, key = None, None
    KEYS = {"keywords", "image", "reads as", "essay", "work", "love", "self", "not"}
    buf = []

    def flush():
        if orient and key and buf:
            text = "\n".join(buf).strip()
            paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
            data[orient][key] = paras
    for ln in lines:
        if ln.startswith("# ") and not title:
            title = ln[2:].split("·")[0].strip()
        elif ln.strip() == "## upright":
            flush(); orient, key, buf = "upright", None, []
        elif ln.strip() == "## reversed":
            flush(); orient, key, buf = "reversed", None, []
        elif ln.startswith("### ") and ln[4:].strip() in KEYS:
            flush(); key = ln[4:].strip(); buf = []
        else:
            buf.append(ln)
    flush()
    return title, data


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paras(ps):
    return "\n".join(f"<p>{esc(p)}</p>" for p in ps)


CSS = """
:root{--noir:#0b0908;--surface:#12100f;--surface-raised:#171412;--hairline:#2a2521;
--bone:#f4eee2;--dim:#9a9185;--faint:#827a71;--vermilion:#ff4b2e;--lemon:#ffd43a;
--cobalt:#3563ff;--rose:#ff7ac0;--leaf:#29a35c;--max:760px}
*{box-sizing:border-box}html{background:var(--noir);scroll-behavior:smooth}
body{margin:0;background:var(--noir);color:var(--bone);font-family:"Hanken Grotesk",sans-serif;font-weight:300;line-height:1.6}
a{color:inherit}
.wrap{width:min(calc(100% - 48px),var(--max));margin:0 auto}
.site-header{display:flex;align-items:center;justify-content:space-between;height:74px;border-bottom:1px solid var(--hairline)}
.brand{font-family:"Cormorant",serif;font-size:24px;text-decoration:none}
.lang{font-size:13px;color:var(--dim);text-decoration:none;border-bottom:1px solid var(--hairline);padding-bottom:2px}
.lang:hover{color:var(--bone)}
.store-badge{display:inline-block;margin-top:6px}.store-badge img{height:46px;width:auto;display:block}
.store-badge.muted{opacity:.45;pointer-events:none}.cta .soon{margin-top:14px;color:var(--faint);font-size:13px}
.crumbs{margin:34px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--faint)}
.crumbs a{text-decoration:none}.crumbs a:hover{color:var(--bone)}
h1.card{margin:.15em 0 0;font-family:"Cormorant",serif;font-weight:300;font-size:clamp(56px,13vw,108px);line-height:.9}
.num{font-family:"Cormorant",serif;color:var(--accent);font-size:15px;text-transform:uppercase;letter-spacing:.16em}
.lede{margin:26px 0 0;font-size:20px;line-height:1.5;color:var(--bone)}
.image-note{margin:26px 0 0;padding-left:20px;border-left:1px solid var(--accent);font-family:"Cormorant",serif;font-style:italic;font-size:22px;line-height:1.4;color:var(--dim)}
.kw{margin:20px 0 0;color:var(--faint);font-size:14px}
section.block{padding:52px 0;border-top:1px solid var(--hairline)}
.orient{display:block;margin-bottom:22px;font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--accent)}
.essay p{margin:0 0 20px;font-size:17px;line-height:1.75;color:var(--bone)}
.facets{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--hairline);border:1px solid var(--hairline);margin:30px 0 0}
.facet{background:var(--noir);padding:22px 20px}
.facet h3{margin:0 0 10px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--faint);font-weight:400}
.facet p{margin:0;font-size:15px;line-height:1.6;color:var(--dim)}
.notpar{margin:24px 0 0;font-size:15px;color:var(--dim)}.notpar b{color:var(--bone);font-weight:400}
.cta{margin:64px 0;padding:44px;border:1px solid var(--hairline);background:var(--surface-raised);border-radius:8px;text-align:center}
.cta h2{margin:0;font-family:"Cormorant",serif;font-weight:300;font-size:40px;line-height:1.05}
.cta p{margin:16px auto 0;max-width:48ch;color:var(--dim);font-size:16px}
.cta a{display:inline-block;margin-top:26px;padding:13px 22px;border:1px solid var(--bone);border-radius:6px;text-decoration:none;font-size:14px}
.cta a:hover{background:var(--bone);color:var(--noir)}
.cta .soon{margin-top:26px;color:var(--faint);font-size:13px}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin:0 0 8px;font-size:13px;color:var(--faint)}
.prevnext a{text-decoration:none;color:var(--dim)}.prevnext a:hover{color:var(--bone)}
.site-footer{border-top:1px solid var(--hairline);padding:28px 0 60px;color:var(--faint);font-size:12px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.site-footer a{text-decoration:none}
.grp{margin:52px 0 0;display:flex;align-items:baseline;gap:14px}
.grp h2{margin:0;font-family:"Cormorant",serif;font-weight:300;font-size:34px}
.grp .grp-note{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--faint)}
.index-grid{margin:22px 0 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1px;background:var(--hairline);border:1px solid var(--hairline)}
.index-grid a{background:var(--noir);padding:20px;text-decoration:none;display:flex;flex-direction:column;gap:6px}
.index-grid a:hover{background:var(--surface)}
.index-grid .n{color:var(--faint);font-size:12px;text-transform:uppercase;letter-spacing:.1em}
.index-grid .nm{font-family:"Cormorant",serif;font-size:24px;line-height:1.05}
@media(max-width:600px){.facets{grid-template-columns:1fr}.cta{padding:30px 22px}}
"""


def page(lang, name, slug, other_url, data, *, accent, kicker, num_label,
         es_slug, en_slug, prev=None, nxt=None):
    t = STR[lang]
    up, rev = data["upright"], data["reversed"]
    back_url = "/tarot/" if lang == "es" else "/en/tarot/"

    def facets(d):
        return (f'<div class="facets"><div class="facet"><h3>{t["work"]}</h3>{paras(d.get("work",[]))}</div>'
                f'<div class="facet"><h3>{t["love"]}</h3>{paras(d.get("love",[]))}</div>'
                f'<div class="facet"><h3>{t["self"]}</h3>{paras(d.get("self",[]))}</div></div>')

    def notepar(d):
        return f'<p class="notpar"><b>{t["note"]}</b> {esc(" ".join(d.get("not",[])))}</p>' if d.get("not") else ""

    lede = up.get("reads as", [""])[0]
    image = up.get("image", [""])[0]
    kw = up.get("keywords", [""])[0]
    desc = esc(lede)[:155]

    badge = f'<img src="/assets/app-store-badge.svg" alt="{t["get"]}" width="120" height="40">'
    href = APP_STORE_URL if APP_STORE_URL else "/proximamente/"
    cta_link = f'<a class="store-badge" href="{href}">{badge}</a>'

    num_html = f'<span class="num">{esc(num_label)}</span>' if num_label else ""
    prevnext = ""
    if prev or nxt:
        pfx = "/tarot/" if lang == "es" else "/en/tarot/"
        l = f'<a href="{pfx}{prev[0]}/">← {esc(prev[1])}</a>' if prev else "<span></span>"
        r = f'<a href="{pfx}{nxt[0]}/">{esc(nxt[1])} →</a>' if nxt else "<span></span>"
        prevnext = f'<nav class="prevnext">{l}{r}</nav>'

    canon = f"https://amulet.cards/tarot/{slug}/" if lang == "es" else f"https://amulet.cards/en/tarot/{slug}/"
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0908">
<title>{esc(name)} — significado en el tarot | AMULET</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="es" href="https://amulet.cards/tarot/{es_slug}/">
<link rel="alternate" hreflang="en" href="https://amulet.cards/en/tarot/{en_slug}/">
<link rel="alternate" hreflang="x-default" href="https://amulet.cards/tarot/{es_slug}/">
<link rel="icon" href="/assets/app-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;1,400&amp;family=Hanken+Grotesk:wght@300;400;500&amp;display=swap" rel="stylesheet">
<style>{CSS}:root{{--accent:var({accent})}}</style>
</head>
<body>
<div class="wrap">
  <header class="site-header">
    <a class="brand" href="/">AMULET</a>
    <a class="lang" href="{other_url}" hreflang="{'en' if lang=='es' else 'es'}">{t['other']}</a>
  </header>

  <p class="crumbs"><a href="{back_url}">{t['back']}</a> · {kicker}</p>
  {num_html}
  <h1 class="card">{esc(name)}</h1>
  <p class="lede">{esc(lede)}</p>
  <p class="image-note">{esc(image)}</p>
  <p class="kw">{esc(kw)}</p>

  <section class="block">
    <span class="orient">{t['up']}</span>
    <div class="essay">{paras(up.get('essay',[]))}</div>
    {facets(up)}
    {notepar(up)}
  </section>

  <section class="block">
    <span class="orient">{t['rev']}</span>
    <p class="lede" style="font-size:18px">{esc(rev.get('reads as',[''])[0])}</p>
    <div class="essay" style="margin-top:24px">{paras(rev.get('essay',[]))}</div>
    {facets(rev)}
    {notepar(rev)}
  </section>

  <div class="cta">
    <h2>{t['cta_h']}</h2>
    <p>{t['cta_p']}</p>
    {cta_link}
  </div>

  {prevnext}
  <footer class="site-footer">
    <span>AMULET / TAROT JOURNAL</span>
    <span><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="mailto:esthersarasua.dev@gmail.com">Contact</a></span>
  </footer>
</div>
<script>
// auto-idioma: solo la primera visita, no molesta después
(function(){{
  try{{
    if(localStorage.getItem('lang-choice'))return;
    var isES=(navigator.language||'').toLowerCase().indexOf('es')===0;
    var here='{lang}';
    if(isES&&here==='en'){{location.replace('https://amulet.cards/tarot/{es_slug}/');}}
    else if(!isES&&here==='es'){{location.replace('https://amulet.cards/en/tarot/{en_slug}/');}}
  }}catch(e){{}}
}})();
document.querySelector('.lang')&&document.querySelector('.lang').addEventListener('click',function(){{
  try{{localStorage.setItem('lang-choice','1');}}catch(e){{}}
}});
</script>
</body>
</html>"""


def index(lang, groups):
    """groups: [(heading, note, [(label, name, slug), ...]), ...]"""
    t = STR[lang]
    pfx = "/tarot/" if lang == "es" else "/en/tarot/"
    blocks = []
    for heading, note, cards in groups:
        items = "".join(
            f'<a href="{pfx+slug+"/"}"><span class="n">{esc(label)}</span>'
            f'<span class="nm">{esc(name)}</span></a>'
            for label, name, slug in cards)
        note_html = f'<span class="grp-note">{esc(note)}</span>' if note else ""
        blocks.append(f'<div class="grp"><h2>{esc(heading)}</h2>{note_html}</div>'
                      f'<div class="index-grid">{items}</div>')
    other = "/en/tarot/" if lang == "es" else "/tarot/"
    h = "Significados del tarot" if lang == "es" else "Tarot meanings"
    sub = ("Los 78 arcanos, del derecho y del revés — la carta, lo que pide, y qué anotar cuando aparece."
           if lang == "es" else
           "All 78 arcana, upright and reversed — the card, what it asks, and what to note when it shows up.")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0908">
<title>{h} — los 78 arcanos del tarot | AMULET</title>
<meta name="description" content="{sub}">
<link rel="canonical" href="https://amulet.cards{'/tarot/' if lang=='es' else '/en/tarot/'}">
<link rel="alternate" hreflang="es" href="https://amulet.cards/tarot/">
<link rel="alternate" hreflang="en" href="https://amulet.cards/en/tarot/">
<link rel="alternate" hreflang="x-default" href="https://amulet.cards/tarot/">
<link rel="icon" href="/assets/app-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;1,400&amp;family=Hanken+Grotesk:wght@300;400;500&amp;display=swap" rel="stylesheet">
<style>{CSS}:root{{--accent:var(--cobalt)}}</style>
</head>
<body><div class="wrap">
<header class="site-header"><a class="brand" href="/">AMULET</a><a class="lang" href="{other}">{t['other']}</a></header>
<p class="crumbs">{t['k_major']} · {t['k_minor']}</p>
<h1 class="card" style="font-size:clamp(48px,10vw,80px)">{h}</h1>
<p class="lede">{sub}</p>
{"".join(blocks)}
<footer class="site-footer" style="margin-top:60px"><span>AMULET / TAROT JOURNAL</span>
<span><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="mailto:esthersarasua.dev@gmail.com">Contact</a></span></footer>
</div></body></html>"""


def sitemap(pairs, singles):
    """pairs: [(es_path, en_path, xdefault_path)] con alternates hreflang.
    singles: [path] sin traducción. Devuelve XML."""
    lastmod = date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">']

    def alts(es, en, xd):
        return (f'<xhtml:link rel="alternate" hreflang="es" href="{SITE}{es}"/>'
                f'<xhtml:link rel="alternate" hreflang="en" href="{SITE}{en}"/>'
                f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{xd}"/>')
    for es, en, xd in pairs:
        block = alts(es, en, xd)
        for loc in (es, en):
            out.append(f'<url><loc>{SITE}{loc}</loc><lastmod>{lastmod}</lastmod>{block}</url>')
    for s in singles:
        out.append(f'<url><loc>{SITE}{s}</loc><lastmod>{lastmod}</lastmod></url>')
    out.append('</urlset>')
    return "".join(out)


def load(f_es):
    """Devuelve (name_es, data_es, name_en, data_en) o None si falta el par EN."""
    f_en = f_es.with_name(f_es.name.replace(".es.md", ".en.md"))
    if not f_en.exists():
        return None
    name_es, data_es = parse(f_es.read_text())
    name_en, data_en = parse(f_en.read_text())
    return name_es, data_es, name_en, data_en


def write(num_or_none, name_es, slug_es, data_es, name_en, slug_en, data_en,
          accent, kicker_es, kicker_en, num_label, seq_es, seq_en, i):
    """Escribe el par ES/EN. seq_* = lista ordenada [(slug,name)] para prev/next."""
    prev_es = seq_es[i - 1] if i > 0 else None
    nxt_es = seq_es[i + 1] if i + 1 < len(seq_es) else None
    prev_en = seq_en[i - 1] if i > 0 else None
    nxt_en = seq_en[i + 1] if i + 1 < len(seq_en) else None
    (ROOT / f"tarot/{slug_es}").mkdir(parents=True, exist_ok=True)
    (ROOT / f"en/tarot/{slug_en}").mkdir(parents=True, exist_ok=True)
    (ROOT / f"tarot/{slug_es}/index.html").write_text(
        page("es", name_es, slug_es, f"/en/tarot/{slug_en}/", data_es,
             accent=accent, kicker=kicker_es, num_label=num_label,
             es_slug=slug_es, en_slug=slug_en, prev=prev_es, nxt=nxt_es))
    (ROOT / f"en/tarot/{slug_en}/index.html").write_text(
        page("en", name_en, slug_en, f"/tarot/{slug_es}/", data_en,
             accent=accent, kicker=kicker_en, num_label=num_label,
             es_slug=slug_es, en_slug=slug_en, prev=prev_en, nxt=nxt_en))


def main():
    made = 0
    grp_es, grp_en = [], []
    pairs = []  # (es_path, en_path, xdefault_path) para el sitemap

    # ── Arcanos mayores ──
    files = {int(f.name[:2]): f for f in CORPUS.glob("[0-9][0-9]-*.es.md")}
    majors = []  # (num, name_es, slug_es, data_es, name_en, slug_en, data_en)
    for num, (slug_es, slug_en) in sorted(MAJORS.items()):
        f_es = files.get(num)
        r = load(f_es) if f_es else None
        if not r:
            print(f"  ⚠️ falta corpus para mayor {num}"); continue
        majors.append((num, r[0], slug_es, r[1], r[2], slug_en, r[3]))
    seq_es = [(m[2], m[1]) for m in majors]
    seq_en = [(m[5], m[4]) for m in majors]
    for i, (num, ne, se, de, nn, sn, dn) in enumerate(majors):
        write(num, ne, se, de, nn, sn, dn, MAJOR_ACCENT,
              STR["es"]["k_major"], STR["en"]["k_major"], str(num), seq_es, seq_en, i)
        made += 1
    grp_es.append((STR["es"]["majors"], "0 – 21",
                   [(str(m[0]), m[1], m[2]) for m in majors]))
    grp_en.append((STR["en"]["majors"], "0 – 21",
                   [(str(m[0]), m[4], m[5]) for m in majors]))
    for m in majors:
        pairs.append((f"/tarot/{m[2]}/", f"/en/tarot/{m[5]}/", f"/tarot/{m[2]}/"))

    # ── Arcanos menores, por palo ──
    for prefix, suit_es, suit_en, name_es_suit, name_en_suit, accent in SUITS:
        cards = []  # (rank, name_es, slug_es, data_es, name_en, slug_en, data_en)
        for rank in sorted(RANKS):
            f_es = CORPUS / f"{prefix}-{rank:02d}.es.md"
            r = load(f_es) if f_es.exists() else None
            if not r:
                print(f"  ⚠️ falta corpus para {prefix}-{rank:02d}"); continue
            r_es, r_en = RANKS[rank]
            cards.append((rank, r[0], f"{r_es}-de-{suit_es}", r[1],
                          r[2], f"{r_en}-of-{suit_en}", r[3]))
        seq_es = [(c[2], c[1]) for c in cards]
        seq_en = [(c[5], c[4]) for c in cards]
        k_es = f'{STR["es"]["k_minor"]} · {name_es_suit}'
        k_en = f'{STR["en"]["k_minor"]} · {name_en_suit}'
        for i, (rank, ne, se, de, nn, sn, dn) in enumerate(cards):
            write(None, ne, se, de, nn, sn, dn, accent, k_es, k_en,
                  name_es_suit, seq_es, seq_en, i)
            made += 1
        grp_es.append((name_es_suit, STR["es"]["minors"],
                       [("", c[1], c[2]) for c in cards]))
        grp_en.append((name_en_suit, STR["en"]["minors"],
                       [("", c[4], c[5]) for c in cards]))
        for c in cards:
            pairs.append((f"/tarot/{c[2]}/", f"/en/tarot/{c[5]}/", f"/tarot/{c[2]}/"))

    (ROOT / "tarot").mkdir(exist_ok=True)
    (ROOT / "en/tarot").mkdir(parents=True, exist_ok=True)
    (ROOT / "tarot/index.html").write_text(index("es", grp_es))
    (ROOT / "en/tarot/index.html").write_text(index("en", grp_en))

    # ── sitemap.xml + robots.txt ──
    # homes (x-default = EN root, igual que su <link>) e índices del blog (x-default = ES)
    top = [("/es/", "/", "/"),
           ("/tarot/", "/en/tarot/", "/tarot/")]
    singles = ["/privacy/", "/terms/"]
    (ROOT / "sitemap.xml").write_text(sitemap(top + pairs, singles))
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n")
    print(f"{made} cartas × 2 idiomas + 2 índices · {len(top)+len(pairs)} pares en sitemap · corpus: {CORPUS}")


if __name__ == "__main__":
    main()
