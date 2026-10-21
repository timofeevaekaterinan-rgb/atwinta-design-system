"""Собирает index.html — страницу дизайн-системы для GitHub Pages.
Запуск из корня репозитория: python3 tools/build_site.py
Берёт project/README.md, project/tokens.json, превью и README компонентов, ассеты."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
read = lambda *a: open(P(*a), encoding="utf-8").read()

idx = json.loads(read("project", "design-system.json"))
tok = json.loads(read("project", "tokens.json"))

# /_blob/<id> → относительный путь к файлу ассета
blobs = {}
for g, ag in idx["assetGroups"].items():
    for name, r in ag["files"].items():
        blobs["/_blob/" + r["blob"]] = f"project/assets/{g}/{name}"

def unblob(s):
    for k, v in blobs.items():
        s = s.replace(k, v)
    return s

def resolve(v, theme, by):
    if isinstance(v, dict):
        v = v.get(theme, v.get("light"))
    m = re.fullmatch(r"\{(.+)\}", v)
    return resolve(by[m.group(1)]["value"], theme, by) if m else v

colors = tok["color"]["tokens"]
by = {c["name"]: c for c in colors}

def swatch(c):
    lt, dk = resolve(c["value"], "light", by), resolve(c["value"], "dark", by)
    alias = c["value"] if isinstance(c["value"], str) and c["value"].startswith("{") else ""
    two = lt != dk
    chips = f'<span class="chip" style="background:{lt}"></span>' + (f'<span class="chip" style="background:{dk}"></span>' if two else "")
    val = lt + (f" / {dk}" if two else "")
    return (f'<div class="sw"><div class="chips{" two" if two else ""}">{chips}</div>'
            f'<p class="nm">{c["name"]}</p><p class="val">{html.escape(alias or val)}</p>'
            f'<p class="us">{html.escape(c["usage"])}</p></div>')

palette = [c for c in colors if not (isinstance(c["value"], dict) or str(c["value"]).startswith("{"))]
semantic = [c for c in colors if c not in palette]

type_rows = []
for g in tok["type"]["groups"]:
    type_rows.append(f'<h4>{html.escape(g["name"])}</h4>')
    for s in g["styles"]:
        meta = f'{s["fontSize"]} / {s["lineHeight"]} · {s["fontWeight"]} · {s.get("letterSpacing", "0")}'
        type_rows.append(f'<div class="ty"><div class="tm"><p class="nm">{s["name"]}</p><p class="val">{meta}</p>'
                         f'<p class="us">{html.escape(s.get("usage", ""))}</p></div>'
                         f'<p class="{s["name"]} spec">{html.escape(s.get("sample", s["name"]))}</p></div>')

space = "".join(f'<div class="sp"><p class="nm">{t["name"]}</p><span class="bar" style="width:{t["value"]}"></span>'
                f'<p class="val">{t["value"]}</p><p class="us">{html.escape(t["usage"])}</p></div>'
                for t in tok["spacing"]["tokens"])
radius = "".join(f'<div class="rd"><span class="box" style="border-radius:{t["value"]}"></span><p class="nm">{t["name"]}</p>'
                 f'<p class="val">{t["value"]}</p><p class="us">{html.escape(t["usage"])}</p></div>'
                 for t in tok["radius"]["tokens"])
shadows = "".join(f'<div class="sh"><span class="num-demo" style="text-shadow:{t["value"]}">400+</span><p class="nm">{t["name"]}</p>'
                  f'<p class="val">{html.escape(t["value"])}</p><p class="us">{html.escape(t["usage"])}</p></div>'
                  for t in tok["shadow"]["tokens"])
bps = "".join(f'<tr><td class="nm">{t["name"]}</td><td>{t["value"]}</td><td>{html.escape(t["usage"])}</td></tr>'
              for t in tok["breakpoint"]["tokens"])

# компоненты: превью в iframe (srcdoc наследует адрес страницы, пути относительные)
HEAD = '<link rel="stylesheet" href="dist/tokens.css"><link rel="stylesheet" href="project/components/bundle.css">'
order = ["Button", "Chip", "Link", "TextField", "Checkbox", "NumberFact", "ServiceLine", "ProjectCard", "Header"]
comps, nav_c, mds = [], [], {}
for name in order:
    pv = read("project", "components", name, "preview.html")
    m = re.search(r'@dsCard[^>]*height=(\d+)', pv)
    h = int(m.group(1)) + 40 if m else 260
    sub = re.search(r'subtitle="([^"]*)"', pv)
    doc = unblob(pv.split("\n", 1)[1]).replace("<html", '<html data-theme="light"', 1).replace("<head>", "<head>" + HEAD, 1)
    mds[name] = read("project", "components", name, "README.md")
    comps.append(f'<section class="comp" id="c-{name}"><div class="ch"><h3>{name}</h3>'
                 f'<p class="us">{html.escape(sub.group(1)) if sub else ""}</p></div>'
                 f'<iframe title="{name}" loading="lazy" style="height:{h}px" srcdoc="{html.escape(doc, quote=True)}"></iframe>'
                 f'<div class="md" data-md="{name}"></div></section>')
    nav_c.append(f'<a href="#c-{name}">{name}</a>')

cover = unblob(read("project", "components", "Cover", "preview.html").split("\n", 1)[1]).replace("<html", '<html data-theme="light"', 1).replace("<head>", "<head>" + HEAD + "<script>const z=()=>document.documentElement.style.zoom=innerWidth/960;z();addEventListener('resize',z)</script>", 1)
logos = "".join(f'<figure class="{"dark" if "light" in n else ""}"><img src="project/assets/Logos/{n}" alt="{n}"><figcaption>{n}</figcaption></figure>'
                for n in idx["assetGroups"]["Logos"]["order"])
icons = "".join(f'<figure><img src="project/assets/Icons/{n}" alt="{n}"><figcaption>{n[:-4]}</figcaption></figure>'
                for n in idx["assetGroups"]["Icons"]["order"])

md_json = json.dumps({"readme": read("project", "README.md"), **mds}, ensure_ascii=False).replace("</", "<\\/")

page = f"""<!doctype html>
<html lang="ru" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Атвинта — дизайн-система</title>
<meta name="description" content="Дизайн-система по сайту atwinta.ru: цвета, типографика, отступы, компоненты, логотипы и иконки.">
{HEAD}
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:var(--white);color:var(--black);font-family:var(--font-sans);font-weight:300;-webkit-font-smoothing:antialiased}}
a{{color:inherit}}
.wrap{{display:grid;grid-template-columns:240px minmax(0,1fr);max-width:1440px;margin:0 auto}}
nav{{position:sticky;top:0;align-self:start;height:100vh;overflow:auto;padding:40px 30px;border-right:2px solid var(--extra-light-gray)}}
nav img{{width:140px;display:block;margin-bottom:30px}}
nav p{{margin:24px 0 8px;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--dark-gray)}}
nav a{{display:block;padding:5px 0;font-size:16px;text-decoration:none}}
nav a:hover{{color:var(--pink)}}
main{{padding:40px 60px 120px;min-width:0}}
.cover{{width:100%;aspect-ratio:960/288;border:0;display:block;border-radius:0;background:var(--white)}}
section.blk{{padding-top:80px}}
h2{{font-size:50px;line-height:60px;font-weight:400;letter-spacing:-1.5px;margin:0 0 30px}}
h3{{font-size:32px;line-height:40px;font-weight:500;letter-spacing:-.96px;margin:0}}
h4{{font-size:13px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--dark-gray);margin:40px 0 10px}}
.nm{{margin:0;font-weight:500;font-size:15px;color:var(--black)}}
.val{{margin:4px 0 0;font:400 13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--extra-dark-gray)}}
.us{{margin:6px 0 0;font-size:14px;line-height:20px;color:var(--extra-dark-gray)}}
.md{{max-width:820px;font-size:18px;line-height:28px;font-weight:300}}
.md h2{{font-size:32px;line-height:40px;font-weight:500;letter-spacing:-.96px;margin:50px 0 16px}}
.md h1{{display:none}}
.md code{{font:400 15px ui-monospace,Menlo,monospace;background:var(--extra-light-gray);padding:1px 6px;border-radius:6px}}
.md table{{border-collapse:collapse;font-size:15px;margin:16px 0;display:block;overflow-x:auto}}
.md td,.md th{{border-bottom:2px solid var(--extra-light-gray);padding:8px 14px 8px 0;text-align:left;white-space:nowrap}}
.md strong{{font-weight:500}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:30px 24px}}
.chips{{height:96px;display:flex;border-radius:8px;overflow:hidden;border:2px solid var(--extra-light-gray);margin-bottom:12px;
  background:repeating-conic-gradient(#eee 0 25%,#fff 0 50%) 0 0/16px 16px}}
.chip{{flex:1}}
.ty{{display:grid;grid-template-columns:260px minmax(0,1fr);gap:30px;align-items:baseline;padding:24px 0;border-bottom:2px solid var(--extra-light-gray)}}
.spec{{margin:0;overflow-wrap:anywhere}}
.sp{{display:grid;grid-template-columns:180px 200px 70px minmax(0,1fr);gap:20px;align-items:center;padding:10px 0;border-bottom:2px solid var(--extra-light-gray)}}
.sp .bar{{height:20px;background:var(--pink);display:block;max-width:200px}}
.sp .us,.sp .val{{margin:0}}
.rd .box{{display:block;width:120px;height:80px;background:var(--extra-light-gray);border:2px solid var(--light-gray);margin-bottom:12px}}
.num-demo{{display:block;font-family:var(--font-display);font-size:90px;line-height:1;font-weight:700;letter-spacing:-2.7px;margin-bottom:12px}}
table.bp{{border-collapse:collapse;font-size:15px}}
table.bp td{{padding:10px 30px 10px 0;border-bottom:2px solid var(--extra-light-gray)}}
.comp{{padding:50px 0;border-bottom:2px solid var(--extra-light-gray)}}
.comp .ch{{margin-bottom:20px}}
.comp iframe{{width:100%;border:2px solid var(--extra-light-gray);background:var(--white);display:block;margin-bottom:24px}}
.comp .md{{font-size:16px;line-height:24px}}
.comp .md h2{{font-size:20px;line-height:30px;margin:26px 0 8px}}
.assets{{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:16px}}
.assets.logos{{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}}
figure{{margin:0;padding:24px;border:2px solid var(--extra-light-gray);display:flex;flex-direction:column;align-items:center;gap:12px}}
figure.dark{{background:var(--black)}} figure.dark figcaption{{color:var(--gray)}}
figure img{{max-width:100%;height:40px}} .assets:not(.logos) img{{height:30px}}
figcaption{{font-size:12px;color:var(--dark-gray);text-align:center;word-break:break-all}}
.src{{margin-top:12px;font-size:15px;color:var(--dark-gray)}}
@media (max-width:900px){{.wrap{{grid-template-columns:1fr}}nav{{position:static;height:auto;border-right:0;border-bottom:2px solid var(--extra-light-gray);padding:20px}}
  nav a{{display:inline-block;margin-right:14px}}main{{padding:24px 16px 80px}}.ty,.sp{{grid-template-columns:1fr;gap:6px}}h2{{font-size:32px;line-height:40px}}}}
</style>
</head>
<body>
<div class="wrap">
<nav>
  <img src="project/assets/Logos/atwinta-logo-dark.svg" alt="Атвинта">
  <p>Основы</p>
  <a href="#readme">Брендбук</a><a href="#colors">Цвета</a><a href="#type">Типографика</a><a href="#space">Отступы</a><a href="#radius">Скругления</a><a href="#effects">Эффекты</a><a href="#bp">Брейкпоинты</a><a href="#assets">Логотипы и иконки</a>
  <p>Компоненты</p>
  {''.join(nav_c)}
  <p>Исходники</p>
  <a href="https://github.com/timofeevaekaterinan-rgb/atwinta-design-system">GitHub</a><a href="project/tokens.json">tokens.json</a><a href="dist/tokens.css">tokens.css</a><a href="project/components/bundle.css">bundle.css</a>
</nav>
<main>
  <iframe class="cover" title="Обложка" srcdoc="{html.escape(cover, quote=True)}"></iframe>
  <p class="src">Собрано по CSS сайта <a href="https://atwinta.ru/">atwinta.ru</a>. Значения токенов — для ширины от 1680px.</p>

  <section class="blk" id="readme"><h2>Брендбук</h2><div class="md" data-md="readme"></div></section>

  <section class="blk" id="colors"><h2>Цвета</h2>
    <h4>Палитра сайта</h4><div class="grid">{''.join(swatch(c) for c in palette)}</div>
    <h4>Семантические токены · светлая / тёмная тема</h4><div class="grid">{''.join(swatch(c) for c in semantic)}</div>
  </section>

  <section class="blk" id="type"><h2>Типографика</h2>
    <p class="us">Stem — коммерческий шрифт ParaType, в систему не включён; без лицензии крупные заголовки показываются Geologica.</p>
    {''.join(type_rows)}
  </section>

  <section class="blk" id="space"><h2>Отступы и сетка</h2>{space}</section>
  <section class="blk" id="radius"><h2>Скругления</h2><div class="grid">{radius}</div></section>
  <section class="blk" id="effects"><h2>Эффекты</h2><div class="grid">{shadows}</div></section>
  <section class="blk" id="bp"><h2>Брейкпоинты</h2><table class="bp">{bps}</table></section>

  <section class="blk" id="assets"><h2>Логотипы и иконки</h2>
    <div class="assets logos">{logos}</div>
    <h4>Иконки</h4><div class="assets">{icons}</div>
  </section>

  <section class="blk" id="components"><h2>Компоненты</h2>{''.join(comps)}</section>
</main>
</div>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
const MD = {md_json};
document.querySelectorAll('[data-md]').forEach(el => {{
  let src = MD[el.dataset.md] || '';
  src = src.replace(/^# .*\\n/, '');
  el.innerHTML = marked.parse(src);
}});
</script>
</body>
</html>
"""
open(P("index.html"), "w", encoding="utf-8").write(page)
print("index.html", len(page))
