import re,sys
from playwright.sync_api import sync_playwright
h=open('html_Reino_Reverso.html',encoding='utf-8').read()
h=re.sub(r'<script type="text/worker">.*?</script>','',h,flags=re.S); h=re.sub(r'<rolltemplate.*?</rolltemplate>','',h,flags=re.S)
css=open('css_Reino_Reverso.css',encoding='utf-8').read().replace('https://raw.githubusercontent.com/orafahell/Reino-Reverso/main/','file://'+__import__('os').path.abspath('..')+'/')
h=h.replace('https://raw.githubusercontent.com/orafahell/Reino-Reverso/main/','file://'+__import__('os').path.abspath('..')+'/')
page="<html><head><meta charset='utf-8'><style>body{margin:0;font-family:Arial;font-size:13px}fieldset{border:0;padding:0;margin:0}button{font-size:13px}"+css+"</style></head><body><div class='charsheet' style='width:860px'>"+h+"</div></body></html>"
vals={'pv_max':11,'ps_max':7,'ph_max':4,'iniciativa':3,'movimento':6,'arremesso':4,'carga_leve':19,'carga_media':38,'carga_pesada':58,'folego_max':2,'memoria':3,'idiomas_qtd':2,'presenca':3,'grad_max':2,'rd_total':3,'grad_total':14,'grad_previsto':20,'peso_total':21.5,'atk_nome':'Glock','atk_dano':'2d6','atk_alcance':'9 m','carga_estado':'media'}
import json
with sync_playwright() as p:
    b=p.chromium.launch(); 
    for tab in sys.argv[1:]:
        pg=b.new_page(viewport={'width':880,'height':900}); open('_prev.html','w',encoding='utf-8').write(page); pg.goto('file://'+__import__('os').path.abspath('_prev.html')); pg.wait_for_timeout(400)
        pg.evaluate("""([tab,vals])=>{document.querySelector('.flag-aba').setAttribute('value',tab);document.querySelector('.flag-carga').setAttribute('value','media');document.querySelector('.flag-nivel').setAttribute('value','3');
        for(const k in vals)document.querySelectorAll('span[name="attr_'+k+'"]').forEach(s=>s.textContent=vals[k]);}""",[tab,vals])
        pg.wait_for_timeout(450); pg.screenshot(path='shot_'+tab+'.png',full_page=True); 
        print(tab,pg.evaluate("document.documentElement.scrollWidth"))
    b.close()
