#!/usr/bin/env python3
"""Genera el blog de significados de tarot para amulet.cards desde el corpus de la app.

Fuente: ../amulet/Resources/ArcanaCorpus/NN-slug.(es|en).md  (un fichero por carta e idioma).
Salida: tarot/<slug-es>/index.html  (ES)  y  en/tarot/<slug-en>/index.html  (EN)
        + tarot/index.html y en/tarot/index.html (índices).

i18n: cada página lleva lang correcto, <link hreflang> a su par, toggle ES/EN y un
script que, la PRIMERA visita, redirige a tu idioma de navegador (no vuelve a molestar).

Uso:  python3 generate_blog.py            # 22 mayores ES+EN
      APP_STORE_URL=https://apps.apple.com/es/app/idXX:  CTA con link real (si no, "próximamente")
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = Path(os.environ.get("CORPUS", ROOT.parent / "amulet" / "Resources" / "ArcanaCorpus"))
APP_STORE_URL = os.environ.get("APP_STORE_URL", "")  # vacío = estado "próximamente"

# número → (slug_es, slug_en). Nombres se leen del propio corpus.
MAJORS = {
    0: ("el-loco", "the-fool"), 1: ("el-mago", "the-magician"),
    2: ("la-sacerdotisa", "the-high-priestess"), 3: ("la-emperatriz", "the-empress"),
    4: ("el-emperador", "the-emperor"), 5: ("el-hierofante", "the-hierophant"),
    6: ("los-enamorados", "the-lovers"), 7: ("el-carro", "the-chariot"),
    8: ("la-fuerza", "strength"), 9: ("el-ermitano", "the-hermit"),
    10: ("la-rueda-de-la-fortuna", "wheel-of-fortune"), 11: ("la-justicia", "justice"),
    12: ("el-colgado", "the-hanged-man"), 13: ("la-muerte", "death"),
    14: ("la-templanza", "temperance"), 15: ("el-diablo", "the-devil"),
    16: ("la-torre", "the-tower"), 17: ("la-estrella", "the-star"),
    18: ("la-luna", "the-moon"), 19: ("el-sol", "the-sun"),
    20: ("el-juicio", "judgement"), 21: ("el-mundo", "the-world"),
}
ACCENTS = ["--vermilion", "--lemon", "--cobalt", "--rose", "--leaf"]

STR = {
    "es": dict(back="Significados del tarot", up="Del derecho", rev="Invertida",
               work="En el trabajo", love="En el amor", self="En ti", note="Ojo:",
               cta_h="Lleva un diario de tus tiradas",
               cta_p="AMULET registra la carta, la pregunta y el contexto de tu mazo físico — y te enseña qué vuelve. Sin cuentas, sin suscripción.",
               soon="Próximamente en el App Store", get="Descargar en el App Store",
               other="English", kicker="Arcano mayor"),
    "en": dict(back="Tarot meanings", up="Upright", rev="Reversed",
               work="At work", love="In love", self="In you", note="Note:",
               cta_h="Keep a journal of your readings",
               cta_p="AMULET logs the card, the question, and the context from your physical deck — and shows you what returns. No account, no subscription.",
               soon="Coming soon to the App Store", get="Download on the App Store",
               other="Español", kicker="Major Arcana"),
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
.crumbs{margin:34px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--faint)}
.crumbs a{text-decoration:none}.crumbs a:hover{color:var(--bone)}
h1.card{margin:.15em 0 0;font-family:"Cormorant",serif;font-weight:300;font-size:clamp(64px,15vw,116px);line-height:.9}
.num{font-family:"Cormorant",serif;color:var(--faint);font-size:22px}
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
.site-footer{border-top:1px solid var(--hairline);padding:28px 0 60px;color:var(--faint);font-size:12px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
.site-footer a{text-decoration:none}
.index-grid{margin:40px 0 60px;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1px;background:var(--hairline);border:1px solid var(--hairline)}
.index-grid a{background:var(--noir);padding:20px;text-decoration:none;display:flex;flex-direction:column;gap:6px}
.index-grid a:hover{background:var(--surface)}
.index-grid .n{color:var(--faint);font-size:12px}
.index-grid .nm{font-family:"Cormorant",serif;font-size:26px}
@media(max-width:600px){.facets{grid-template-columns:1fr}.cta{padding:30px 22px}}
"""


def page(lang, num, name, slug, other_url, data):
    t = STR[lang]
    accent = ACCENTS[num % len(ACCENTS)]
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

    cta_link = (f'<a href="{APP_STORE_URL}">{t["get"]}</a>' if APP_STORE_URL
                else f'<p class="soon">{t["soon"]}</p>')

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0908">
<title>{esc(name)} — significado en el tarot | AMULET</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://amulet.cards{'/tarot/'+slug+'/' if lang=='es' else '/en/tarot/'+slug+'/'}">
<link rel="alternate" hreflang="es" href="https://amulet.cards/tarot/{MAJORS[num][0]}/">
<link rel="alternate" hreflang="en" href="https://amulet.cards/en/tarot/{MAJORS[num][1]}/">
<link rel="alternate" hreflang="x-default" href="https://amulet.cards/tarot/{MAJORS[num][0]}/">
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

  <p class="crumbs"><a href="{back_url}">{t['back']}</a> · {t['kicker']}</p>
  <span class="num">{num}</span>
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
    if(isES&&here==='en'){{location.replace('https://amulet.cards/tarot/{MAJORS[num][0]}/');}}
    else if(!isES&&here==='es'){{location.replace('https://amulet.cards/en/tarot/{MAJORS[num][1]}/');}}
  }}catch(e){{}}
}})();
document.querySelector('.lang')&&document.querySelector('.lang').addEventListener('click',function(){{
  try{{localStorage.setItem('lang-choice','1');}}catch(e){{}}
}});
</script>
</body>
</html>"""


def index(lang, cards):
    t = STR[lang]
    items = "".join(
        f'<a href="{("/tarot/" if lang=="es" else "/en/tarot/")+slug+"/"}"><span class="n">{num}</span>'
        f'<span class="nm">{esc(name)}</span></a>'
        for num, name, slug in cards)
    other = "/en/tarot/" if lang == "es" else "/tarot/"
    h = "Significados del tarot" if lang == "es" else "Tarot meanings"
    sub = ("Cada arcano mayor, del derecho y del revés — la carta, lo que pide, y qué anotar cuando aparece."
           if lang == "es" else
           "Every major arcana, upright and reversed — the card, what it asks, and what to note when it shows up.")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b0908">
<title>{h} — los 22 arcanos mayores | AMULET</title>
<meta name="description" content="{sub}">
<link rel="canonical" href="https://amulet.cards{'/tarot/' if lang=='es' else '/en/tarot/'}">
<link rel="alternate" hreflang="es" href="https://amulet.cards/tarot/">
<link rel="alternate" hreflang="en" href="https://amulet.cards/en/tarot/">
<link rel="icon" href="/assets/app-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300;0,400;1,400&amp;family=Hanken+Grotesk:wght@300;400;500&amp;display=swap" rel="stylesheet">
<style>{CSS}:root{{--accent:var(--cobalt)}}</style>
</head>
<body><div class="wrap">
<header class="site-header"><a class="brand" href="/">AMULET</a><a class="lang" href="{other}">{t['other']}</a></header>
<p class="crumbs">{t['kicker']}</p>
<h1 class="card" style="font-size:clamp(48px,10vw,80px)">{h}</h1>
<p class="lede">{sub}</p>
<div class="index-grid">{items}</div>
<footer class="site-footer"><span>AMULET / TAROT JOURNAL</span>
<span><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="mailto:esthersarasua.dev@gmail.com">Contact</a></span></footer>
</div></body></html>"""


def main():
    files = {int(f.name[:2]): f for f in CORPUS.glob("[0-9][0-9]-*.es.md")}
    cards_es, cards_en = [], []
    made = 0
    for num, (slug_es, slug_en) in MAJORS.items():
        f_es = files.get(num)
        f_en = CORPUS / f_es.name.replace(".es.md", ".en.md") if f_es else None
        if not f_es or not f_en.exists():
            print(f"  ⚠️ falta corpus para {num}"); continue
        name_es, data_es = parse(f_es.read_text())
        name_en, data_en = parse(f_en.read_text())
        url_es = f"/tarot/{slug_es}/"
        url_en = f"/en/tarot/{slug_en}/"
        (ROOT / f"tarot/{slug_es}").mkdir(parents=True, exist_ok=True)
        (ROOT / f"en/tarot/{slug_en}").mkdir(parents=True, exist_ok=True)
        (ROOT / f"tarot/{slug_es}/index.html").write_text(page("es", num, name_es, slug_es, url_en, data_es))
        (ROOT / f"en/tarot/{slug_en}/index.html").write_text(page("en", num, name_en, slug_en, url_es, data_en))
        cards_es.append((num, name_es, slug_es))
        cards_en.append((num, name_en, slug_en))
        made += 1
    (ROOT / "tarot").mkdir(exist_ok=True)
    (ROOT / "en/tarot").mkdir(parents=True, exist_ok=True)
    (ROOT / "tarot/index.html").write_text(index("es", sorted(cards_es)))
    (ROOT / "en/tarot/index.html").write_text(index("en", sorted(cards_en)))
    print(f"{made} cartas × 2 idiomas + 2 índices · corpus: {CORPUS}")


if __name__ == "__main__":
    main()
