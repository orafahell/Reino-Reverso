import re, sys, json
from playwright.sync_api import sync_playwright
exec(open('ferramentas/shot.py').read().split('import json')[0].split('from playwright')[1].split('\n',1)[1])  # reaproveita page/vals
axe = open('node_modules/axe-core/axe.min.js').read()
abas = ['jogo', 'combate', 'poderes', 'historia', 'inventario', 'ajustes']
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 880, 'height': 900})
    open('_prev.html', 'w', encoding='utf-8').write(page)
    pg.goto('file://'+__import__('os').path.abspath('_prev.html')); pg.wait_for_timeout(300)
    pg.add_script_tag(content=axe)
    for tab in abas:
        pg.evaluate("""(tab)=>{document.querySelector('.flag-aba').setAttribute('value',tab);}""", tab)
        r = pg.evaluate("""async()=>{const r=await axe.run(document.querySelector('.charsheet'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']},resultTypes:['violations']});
          return r.violations.map(v=>({id:v.id,impact:v.impact,help:v.help,tags:v.tags.filter(t=>/^wcag\\d/.test(t)),n:v.nodes.length,ex:v.nodes.slice(0,3).map(n=>n.target.join(' ')+' :: '+(n.any[0]&&n.any[0].message||'').slice(0,110))}))}""")
        res[tab] = r
    b.close()
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else 'audit.json', 'w'), ensure_ascii=False, indent=1)
tot = {}
for tab, r in res.items():
    for v in r:
        t = tot.setdefault(v['id'], [v['impact'], v['tags'], 0, v['help'], v['ex']]); t[2] += v['n']
for k, (imp, tags, n, h, ex) in sorted(tot.items(), key=lambda x: -x[1][2]):
    print(f"{k:28} {imp:9} {','.join(tags):18} {n:4}  {h}")
    for e in ex[:2]: print('      ', e)
