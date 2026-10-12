"""Prova de conceito: adiciona acentos (agudo, grave, circunflexo, til, trema, cedilha) a Doctor Glitch
como glifos compostos (letra base + acento), no estilo de fatias deslocadas da fonte. Nao distribuir sem licenca."""
import unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables._g_l_y_f import GlyphComponent

f = TTFont('../Doctor Glitch.otf')
glyf, hmtx, gs = f['glyf'], f['hmtx'], f.getGlyphSet()
B = 1700  # base dos acentos, logo acima das maiusculas (1643)

def area(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))

def desenha(polis):
    pen = TTGlyphPen(None)
    for p in polis:
        if area(p) > 0: p = p[::-1]  # TrueType: contorno externo no sentido horario
        pen.moveTo(p[0]); [pen.lineTo(q) for q in p[1:]]; pen.closePath()
    return pen.glyph()

def para(x0, y0, x1, y1, inc):  # fatia inclinada (paralelogramo)
    return [(x0, y0), (x1, y0), (x1 + inc, y1), (x0 + inc, y1)]

ACENTOS = {
    'acute': [para(120, B, 330, B + 150, 120), para(270, B + 150, 480, B + 300, 120)],
    'grave': [para(360, B, 570, B + 150, -120), para(210, B + 150, 420, B + 300, -120)],
    'circumflex': [para(40, B, 230, B + 170, 170), para(450, B, 640, B + 170, -170), [(250, B + 170), (450, B + 170), (420, B + 300), (280, B + 300)]],
    'tilde': [[(0, B), (230, B), (230, B + 110), (0, B + 110)], [(130, B + 110), (420, B + 110), (420, B + 220), (130, B + 220)],
              [(300, B), (640, B), (640, B + 110), (300, B + 110)], [(470, B + 110), (690, B + 110), (690, B + 260), (470, B + 260)]],
    'dieresis': [[(0, B), (210, B), (210, B + 200), (0, B + 200)], [(430, B + 30), (640, B + 30), (640, B + 230), (430, B + 230)]],
    'cedilla': [[(160, -240), (330, -240), (330, -330), (160, -330)], [(220, -330), (470, -330), (470, -440), (220, -440)],
                [(60, -440), (430, -440), (430, -540), (60, -540)]],
}
for nome, polis in ACENTOS.items():
    glyf[nome] = desenha(polis)
    hmtx[nome] = (hmtx[nome][0] if nome in hmtx.metrics else 700, 0)

def caixa(n):
    bp = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[n].draw(bp); return bp.bounds

MARCA = {'0301': 'acute', '0300': 'grave', '0302': 'circumflex', '0303': 'tilde', '0308': 'dieresis', '0327': 'cedilla'}
cmap = f.getBestCmap(); feitos = []
for cp, gname in sorted(cmap.items()):
    d = unicodedata.decomposition(chr(cp)).split()
    if len(d) != 2 or d[1] not in MARCA or d[0].startswith('<'): continue
    base = cmap.get(int(d[0], 16)); marca = MARCA[d[1]]
    if not base or glyf[base].isComposite(): continue
    bx0, _, bx1, _ = caixa(base); mx0, _, mx1, _ = caixa(marca)
    dx = round((bx0 + bx1) / 2 - (mx0 + mx1) / 2)
    g = glyf[gname]; g.__dict__.clear(); g.numberOfContours = -1; g.components = []
    for n, x in ((base, 0), (marca, dx)):
        c = GlyphComponent(); c.glyphName = n; c.x, c.y = x, 0; c.flags = 0x4 if n == base else 0; g.components.append(c)
    hmtx[gname] = hmtx[base]
    feitos.append(chr(cp))
# espaco vertical para os acentos e a cedilha
f['hhea'].ascent = f['OS/2'].sTypoAscender = 2100; f['OS/2'].usWinAscent = 2150
f['hhea'].descent = f['OS/2'].sTypoDescender = -560; f['OS/2'].usWinDescent = 600
f['maxp'].maxComponentElements = max(getattr(f['maxp'], 'maxComponentElements', 0), 2)
for r in f['name'].names:
    if r.nameID in (1, 4): r.string = 'Doctor Glitch Acentos'
    if r.nameID == 6: r.string = 'DoctorGlitchAcentos'
f.save('DoctorGlitch-Acentos-teste.ttf')
print(len(feitos), ''.join(feitos))
