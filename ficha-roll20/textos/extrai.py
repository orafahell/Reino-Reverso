import sys, pymupdf
d = pymupdf.open("../Reino Reverso 0.9.9.1.pdf")
a, b = int(sys.argv[1]), int(sys.argv[2])
out = []
for pn in range(a, b + 1):
    out.append("@@@ %d" % pn)
    pg = d[pn - 1]
    W = pg.rect.width
    blocos = [bl for bl in pg.get_text("dict", sort=False)["blocks"] if bl.get("lines")]
    blocos.sort(key=lambda bl: (0 if bl["bbox"][0] < W / 2 - 10 else 1, bl["bbox"][1]))
    for bl in blocos:
        for l in bl["lines"]:
            linha = ""
            for s in l["spans"]:
                t = s["text"]
                if not t.strip(): linha += t; continue
                f = s["font"]
                if "Impact" in f or "Glitch" in f: t = "<H%d>%s</H>" % (round(s["size"]), t)
                elif "Bold" in f: t = "<b>%s</b>" % t
                linha += t
            out.append(linha.replace("</b><b>", "").replace("</H><H11>", ""))
print("\n".join(out))
