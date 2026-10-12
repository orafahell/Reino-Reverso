import re, json
def limpa(path):
    L = []
    for l in open(path, encoding='utf-8').read().split('\n'):
        s = l.strip()
        if not s or s.startswith('@@@') or re.fullmatch(r'\d{1,3}', s): continue
        s = re.sub(r'</H>\s*<H(\d+)>', ' ', s)
        if re.fullmatch(r'<H11>\s*REINO REVERSO\s*</H>', s): continue
        if s == 'REINO REVERSO': continue
        m = re.fullmatch(r'<H(\d+)>(.*?)</H>\s*', s)
        if m: L.append(('H' + m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip())); continue
        L.append(('T', s))
    # junta titulos consecutivos do mesmo tamanho
    out = []
    for k, t in L:
        if out and k.startswith('H') and out[-1][0] == k and k != 'H11X': out[-1] = (k, out[-1][1] + ' ' + t)
        else: out.append((k, t))
    return out

def paragrafos(linhas):
    """junta linhas de texto em paragrafos; quebra em rotulos em negrito e marcadores"""
    ps = []
    for t in linhas:
        novo = t.startswith('<b>') or t.startswith('•') or t.startswith('<H11>')
        if not ps or novo or ps[-1].endswith('•'): ps.append(t)
        else:
            a = ps[-1]
            ps[-1] = (a[:-1] + t) if a.endswith('-') and not a.endswith(' -') else (a.rstrip() + ' ' + t)
    r = []
    for p in ps:
        p = re.sub(r'<H11>(.*?)</H>', r'\1', p)
        p = re.sub(r'<b>\s*(.*?)\s*</b>', r'**\1**', p)
        p = re.sub(r'\s+', ' ', p).strip()
        p = p.replace('** :', '**:').replace(' ,', ',').replace(' .', '.')
        if p and p != '•': r.append(p)
    # marcador sozinho seguido de texto
    o = []
    for p in r:
        if o and o[-1] == '•': o[-1] = '• ' + p
        else: o.append(p)
    return o
