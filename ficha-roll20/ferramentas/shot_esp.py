import re, json, shutil, os
from playwright.sync_api import sync_playwright
exec(open('ferramentas/shot.py').read().split('import json')[0].split('from playwright')[1].split('\n',1)[1])
open('_prev.html','w',encoding='utf-8').write(page)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':880,'height':900})
    pg.goto('file://'+__import__('os').path.abspath('_prev.html')); pg.wait_for_timeout(300)
    pg.evaluate("""()=>{document.querySelector('.flag-aba').setAttribute('value','poderes');
    const esp=document.querySelector('.repeating_especializacoes .esp');
    esp.querySelector('.esp-lib').setAttribute('value','2');
    esp.querySelector('[name=attr_esp_pericia]').value='Medicina';
    esp.querySelector('b.esp-nome').textContent='Medicina';
    esp.querySelector('.esp-resumo').textContent='Bandagem · Injeção de Vigor';
    esp.querySelector('[name=attr_esp_grad]').textContent='5';
    const ops=[['Bandagem','Frutas Saudáveis','Injeção de Adrenalina'],['Não no meu Turno','Ervas Revitalizantes','Injeção de Vigor'],['Tratamentos Agressivos','Antídoto Natural','Potência Aumentada'],['Reanimação','Médico','Injeção Final']];
    ops.forEach((l,i)=>l.forEach((n,j)=>{esp.querySelector('[name=attr_esp_'+(i+1)+'_op'+(j+1)+']').textContent=n;}));
    esp.querySelector('[name=attr_esp_1_escolha][value="1"]').checked=true;esp.querySelector('[name=attr_esp_2_escolha][value="3"]').checked=true;
    esp.querySelector('[name=attr_esp_1_nome]').value='Bandagem';esp.querySelector('[name=attr_esp_2_nome]').value='Injeção de Vigor';}""")
    pg.wait_for_timeout(500); pg.screenshot(path='previa_poderes.png',full_page=True)
    pg.evaluate("()=>{document.querySelector('.esp-fechar').checked=true;}"); pg.wait_for_timeout(200)
    pg.screenshot(path='previa_poderes_recolhida.png',clip={'x':0,'y':60,'width':880,'height':360})
    b.close()
from PIL import Image
a=Image.open('previa_poderes.png'); a.crop((0,60,880,1000)).save('c3.png')
