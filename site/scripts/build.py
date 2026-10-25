"""Build a portable static website using only Python's standard library."""
from pathlib import Path
import json
import shutil
import hashlib
from html import escape as esc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
s = json.loads((ROOT / 'content/site.json').read_text())
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
E = lambda value: esc(str(value), quote=True)

def asset(name):
    """Give changed assets a new URL so previews and published pages refresh."""
    version = hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()[:10]
    return f"assets/{name}?v={version}"

def pub(p, compact=False):
    tags = '<ul class="publication-tags" aria-label="Research topics">' + ''.join(f'<li class="publication-tag">{E(tag)}</li>' for tag in p.get('tags', [])) + '</ul>'
    authors = '' if compact else f'<p class="authors">{E(p["authors"])}</p>'
    return f'<article class="pub"><span class="year">{E(p["year"])}</span><div><h3><a href="{E(p["url"])}">{E(p["title"])}</a></h3>{authors}<p class="journal">{E(p["journal"])}</p>{tags}</div></article>'

def themes():
    return '<div class="themes">' + ''.join(f'<article><h3 class="theme-heading"><span class="theme-number">{i+1}</span><span>{E(t["title"])}</span></h3><p>{E(t["text"])}</p></article>' for i,t in enumerate(s['themes'])) + '</div>'

def page(title, content, slug=''):
    base = '../' if slug else './'
    nav = ''.join(f'<a href="{base}{path}"' + (' aria-current="page"' if key==slug else '') + f'>{label}</a>' for key,path,label in [('', '', 'Home'), ('research','research/','Research'), ('cv','cv/','CV')])
    full_title = f'{title} | {s["name"]}' if title else s['name']
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(full_title)}</title><meta name="description" content="{E(s['intro'])}"><meta name="theme-color" content="#142d43"><meta property="og:title" content="{E(full_title)}"><meta property="og:description" content="{E(s['intro'])}"><meta property="og:type" content="website"><link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{base}{asset('style.css')}"></head>
<body class="page-{E(slug or 'home')}"><a class="skip" href="#main">Skip to content</a><header><div class="wrap nav"><a class="brand" href="{base}">{E(s['name'])}</a><nav aria-label="Main navigation">{nav}<a href="mailto:{E(s['email'])}">Contact <span aria-hidden="true">↗</span></a></nav></div></header>
<main id="main">{content}</main>
<div class="wrap contact"><div><h2>Contact me</h2><p>For research, teaching, and collaboration inquiries.</p></div><a href="mailto:{E(s['email'])}">{E(s['email'])} <span aria-hidden="true">↗</span></a></div>
<footer><div class="wrap footer-inner"><span>{E(s['name'])} · {E(s['institution'])}</span><div class="footer-links"><a href="{E(s['scholar'])}">Google Scholar</a><a href="{E(s['github'])}">GitHub</a></div></div></footer></body></html>'''
    dest = OUT / slug if slug else OUT
    dest.mkdir(exist_ok=True)
    (dest / 'index.html').write_text(doc)

home = f'''<div class="wrap hero"><div><h1 class="visually-hidden">{E(s['name'])}</h1><h2 class="about-title">About</h2><p class="lead">{E(s['about'])}</p><p class="lead">{E(s['background'])}</p><div class="buttons"><a class="button" href="./research/">Research <span aria-hidden="true">→</span></a><a class="text-link" href="./cv/">View CV</a></div></div><figure class="portrait"><img src="./{asset('portrait.jpg')}" alt="Marika Mae Cusick" width="2176" height="1920" fetchpriority="high"><figcaption><strong>{E(s['name'])}, PhD</strong>{E(s['role'])}<br>{E(s['institution'])}</figcaption></figure></div>
<section class="wrap section" aria-labelledby="focus"><div class="section-head"><h2 id="focus">Areas of Research Focus</h2><a class="text-link" href="./research/">More about my work <span aria-hidden="true">→</span></a></div>{themes()}</section>
<section class="wrap section" aria-labelledby="selected"><div class="section-head"><h2 id="selected">Selected research</h2><a class="text-link" href="./research/#publications">View publications <span aria-hidden="true">→</span></a></div>{''.join(pub(p, True) for p in sorted((item for item in s['publications'] if 'selected_order' in item), key=lambda item: item['selected_order']))}</section>
'''
page('', home)
research = f'''<div class="wrap"><div class="page-intro"><h1>Research</h1></div><section class="section" aria-label="Research themes">{themes()}</section><section class="section" aria-labelledby="publications"><div class="section-head"><h2 id="publications">Selected publications</h2><a class="text-link" href="{E(s['scholar'])}">Full list on Google Scholar <span aria-hidden="true">↗</span></a></div>{''.join(pub(p) for p in s['publications'])}</section><section class="section" aria-labelledby="media"><div class="section-head"><h2 id="media">Policy &amp; media</h2></div><div class="media">{''.join(f'<article><p class="eyebrow">{E(m["source"])}</p><h3><a href="{E(m["url"])}">{E(m["title"])} <span aria-hidden="true">↗</span></a></h3></article>' for m in s['media'])}</div></section></div>'''
page('Research', research, 'research')
cv = f'''<div class="wrap"><div class="page-intro"><p class="eyebrow">Background &amp; experience</p><h1>Curriculum vitae</h1></div><div class="cv-layout"><div><p class="lead">{E(s['role'])}<br>{E(s['department'])}<br>{E(s['institution'])}</p><a class="button" href="../assets/marika-cusick-cv.pdf" download>Download CV <span aria-hidden="true">↓</span></a><p class="note">PDF · Updated {E(s['cv_date'])}</p><a class="text-link" href="../assets/marika-cusick-cv.pdf">Open PDF in browser <span aria-hidden="true">↗</span></a></div><section class="cv-summary" aria-labelledby="education"><h2 id="education">Education</h2><div class="degree"><strong>PhD, Health Policy</strong><p>Stanford University · 2025<br>Decision Science</p></div><div class="degree"><strong>MS, Information Science</strong><p>Cornell University / Cornell Tech · 2019<br>Health Tech</p></div><div class="degree"><strong>BA, Statistical Science</strong><p>Cornell University · 2017</p></div></section></div></div>'''
page('CV', cv, 'cv')
(OUT / '.nojekyll').touch()
(OUT / '404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found | Marika Mae Cusick</title><body style="font-family:Georgia,serif;font-size:19px;max-width:650px;margin:15vh auto;padding:25px"><h1 style="font-size:32px">Page not found</h1><p>This page may have moved.</p><a href="/">Return to the homepage</a></body></html>')
print(f'Built Home, Research, CV, and 404 pages in {OUT}')
