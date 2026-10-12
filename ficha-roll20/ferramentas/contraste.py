import re, json, sys
from playwright.sync_api import sync_playwright
exec(open('ferramentas/shot.py').read().split('import json')[0].split('from playwright')[1].split('\n',1)[1])
JS = r"""()=>{
const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(m[0])+0.7152*f(m[1])+0.0722*f(m[2])};
const bg=el=>{for(let e=el;e;e=e.parentElement){const s=getComputedStyle(e);const c=s.backgroundColor;const m=c.match(/[\d.]+/g);if(m&&(m.length<4||+m[3]>0.5))return c;}return 'rgb(255,255,255)'};
const hex=c=>'#'+c.match(/[\d.]+/g).slice(0,3).map(v=>(+v).toString(16).padStart(2,'0')).join('');
const out={};
document.querySelectorAll('.charsheet *').forEach(el=>{
 const s=getComputedStyle(el); if(s.visibility==='hidden'||!el.offsetParent&&s.position!=='fixed')return;
 const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())||['INPUT','SELECT','TEXTAREA'].includes(el.tagName)&&el.type!=='checkbox'&&el.type!=='radio';
 if(!own)return; const r=el.getBoundingClientRect(); if(r.width<2)return;
 const fg=s.color,b=bg(el); const L1=lum(fg),L2=lum(b); const cr=(Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
 const size=parseFloat(s.fontSize),bold=+s.fontWeight>=700; const large=size>=24||(size>=18.66&&bold);
 const k=hex(fg)+' on '+hex(b)+' '+size+'px'; const o=out[k]||(out[k]={cr:+cr.toFixed(2),need:large?3:4.5,n:0,ex:(el.className||el.tagName)+'|'+(el.textContent||el.value||'').trim().slice(0,30)}); o.n++;
});
return out}"""
abas = ['jogo','combate','poderes','historia','inventario','ajustes']
tot = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 880, 'height': 900})
    open('_prev.html','w',encoding='utf-8').write(page); pg.goto('file://'+__import__('os').path.abspath('_prev.html')); pg.wait_for_timeout(300)
    for tab in abas:
        pg.evaluate("(t)=>document.querySelector('.flag-aba').setAttribute('value',t)", tab)
        for k, v in pg.evaluate(JS).items():
            t = tot.setdefault(k, dict(v, n=0)); t['n'] += v['n']
    b.close()
falha = {k: v for k, v in tot.items() if v['cr'] < v['need']}
print(len(tot), 'pares;', len(falha), 'reprovados')
for k, v in sorted(falha.items(), key=lambda x: x[1]['cr']): print(f"{v['cr']:5} <{v['need']}  {k:34} x{v['n']:3}  {v['ex']}")
json.dump(tot, open(sys.argv[1], 'w'), indent=1)
