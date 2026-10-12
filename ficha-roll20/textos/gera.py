import sys, re, json
def plano(txt):
    out = []
    for p in txt.split('\n'):
        so_negrito = re.fullmatch(r'\*\*[^*]+\*\*', p) is not None
        if so_negrito and out and out[-1][1]: out[-1] = (out[-1][0] + ' · ' + p, True)
        else: out.append((p, so_negrito))
    return '\n'.join(p.replace('**', '') for p, _ in out)
sys.path.insert(0, '.')
from parse import limpa, paragrafos

def lista(L, inicio, fim):
    i = [n for n, (k, t) in enumerate(L) if k == 'H11' and t == inicio][0] + 1
    j = [n for n, (k, t) in enumerate(L) if n > i and k == 'H20' and t == fim]
    j = j[0] if j else len(L)
    itens, cur = [], None
    for k, t in L[i:j]:
        if k == 'H11': cur = [t, []]; itens.append(cur)
        elif cur: cur[1].append(t)
    return [(n, plano('\n'.join(paragrafos(ls)))) for n, ls in itens]

V = limpa('vd.txt')
van = lista(V, 'Lista de Vantagens', 'Escolhendo Desvantagens')
des = lista(V, 'Lista de Desvantagens', None)

E = limpa('esp.txt')
esp, cur, est, hab, alvo = [], None, None, None, None
ETAPAS = ['Habilidade Inicial', 'Habilidade Secundária', 'Habilidade Avançada', 'Habilidade Final']
for k, t in E:
    if k == 'H18':
        cur = {'pericia': t, 'descricao': [], 'passivo': [], 'etapas': []}; esp.append(cur); alvo = cur['descricao']; continue
    if cur is None: continue
    if k == 'H11' and t == 'Efeito Passivo': alvo = cur['passivo']; continue
    if k == 'H11' and t in ETAPAS: est = []; cur['etapas'].append(est); alvo = None; continue
    if k == 'H11': hab = {'nome': t.rstrip('. '), 'linhas': []}; est.append(hab); alvo = hab['linhas']; continue
    if alvo is not None: alvo.append(t)
for c in esp:
    c['descricao'] = plano('\n'.join(paragrafos(c['descricao'])))
    c['passivo'] = plano('\n'.join(paragrafos(c['passivo'])))
    for est in c['etapas']:
        for h in est:
            ps = paragrafos(h.pop('linhas'))
            ex = ''
            if ps and ps[0].startswith('**Tempo de Execução**'):
                p0 = ps.pop(0).split(':', 1)[1].strip()
                m = re.match(r'\(([^)]*)\)\s*(.*)', p0)
                ex, resto = (m.group(1).strip(), m.group(2).strip()) if m else (p0, '')
                if resto: ps.insert(0, resto)
            h['exec'] = ex; h['texto'] = plano('\n'.join(ps))
    assert len(c['etapas']) == 4 and all(len(e) == 3 for e in c['etapas']), c['pericia']
json.dump({'vantagens': van, 'desvantagens': des, 'especializacoes': esp}, open('livro.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(van), len(des), len(esp), len(json.dumps({'v': van, 'd': des, 'e': esp}, ensure_ascii=False)))
semexec = [(c['pericia'], h['nome']) for c in esp for e in c['etapas'] for h in e if not h['exec']]
print('sem tempo de execucao:', semexec)
