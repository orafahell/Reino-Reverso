#!/usr/bin/env python3
"""Gera html_Reino_Reverso.html e css_Reino_Reverso.css (Roll20, CSE / Legacy Sanitization desligado)."""
import json, os, re

OUT = os.path.dirname(os.path.abspath(__file__))
VERSAO = "1.0.0"  # mudar a cada entrega e registrar no CHANGELOG.md

ATRS = [("forca", "Força", "FOR"), ("agilidade", "Agilidade", "AGI"), ("vitalidade", "Vitalidade", "VIT"),
        ("intelecto", "Intelecto", "INT"), ("carisma", "Carisma", "CAR")]

# chave, nome, atributo padrao, sofre penalidade de armadura
PERICIAS = [
    ("armas_brancas", "Armas Brancas", "forca", False), ("armeiro", "Armeiro", "agilidade", False),
    ("arte", "Arte", "carisma", False), ("atletismo", "Atletismo", "forca", True),
    ("briga", "Briga", "forca", False), ("ciencia_forense", "Ciência Forense", "intelecto", False),
    ("conducao", "Condução", "agilidade", True), ("conhecimento", "Conhecimento", "intelecto", False),
    ("explosivos", "Explosivos", "intelecto", False), ("furto", "Furto", "agilidade", True),
    ("infiltracao", "Infiltração", "agilidade", True), ("informatica", "Informática", "intelecto", False),
    ("interpessoal", "Interpessoal", "carisma", False), ("medicina", "Medicina", "intelecto", True),
    ("obter_informacoes", "Obter Informações", "carisma", False), ("ocultismo", "Ocultismo", "intelecto", False),
    ("percepcao", "Percepção", "intelecto", False), ("pontaria", "Pontaria", "agilidade", False),
    ("profissoes", "Profissões", "intelecto", True), ("reacoes", "Reações", "agilidade", True),
]

CONDICOES = ["Agarrado", "Assustado", "Aterrorizado", "Atordoado", "Caído", "Cercado", "Desatento", "Doente",
             "Embriagado", "Exausto", "Exposto", "Fragilizado", "Indefeso", "Intoxicado", "Ofegante", "Sangramento",
             "Lesão: costas", "Lesão: pernas", "Lesão: braços"]

# tabela de Surtos (p. 22) com os nomes realinhados aos efeitos
SURTOS = ["Fuga Desesperada", "Paralisia do Horror", "Grito Incontrolável", "Desconfiança Absoluta",
          "Alucinação Aterradora", "Ecos na Mente", "Riso da Garganta", "Memória Fragmentada", "Pânico Cego",
          "Catatonia", "Traço Invertido", "Reação Agressiva", "Obsessão Repentina", "Realidade Distorcida",
          "Medo Contagiante", "Ruptura Emocional", "Corpo Estranho", "Verdade Proibida", "A Voz do Outro Lado",
          "Ruptura da Realidade"]

# trilha de niveis conforme o livro 0.9.9.1 (p. 25 a 28)
NIVEIS = [("1", "Criação · Grad. 2 · Espec."), ("2", "Vantagem"), ("3", "Corrupção · Atributo +1 · Grad. 4"),
          ("4", "Vantagem"), ("5", "Espec. · 1 magia I"), ("6", "Corrupção · Atributo +1 · Grad. 6 · Vantagem · 1 magia I"),
          ("7", "Magias I e II"), ("8", "Vantagem · 1 magia II"), ("9", "Corrupção · Atributo +1 · Grad. 8 · Magias II e III"),
          ("10", "Espec. · Vantagem · 1 magia III"), ("11+", "Vantagem · Magias I, II e III")]

LIVRO = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "textos", "livro.json"), encoding="utf-8"))
EXECS = ["Ação Livre", "Ação Padrão", "Rodada Completa", "Várias Rodadas"]


def _exec(x):
    x = x.strip().rstrip(".")
    for e in EXECS:
        if x.lower() == e.lower():
            return e
    return x


LIVRO_JS = {
    "v": dict(LIVRO["vantagens"]),
    "d": dict(LIVRO["desvantagens"]),
    "e": {c["pericia"]: {"p": c["passivo"], "h": [[[h["nome"], _exec(h["exec"]), h["texto"]] for h in et] for et in c["etapas"]]}
          for c in LIVRO["especializacoes"]},
}


def opcoes_livro(nomes, vazio):
    return ('<option value="" selected>%s</option>' % vazio
            + "".join('<option value="%s">%s</option>' % (n, n) for n in nomes)
            + '<option value="-">Outra (escrever)</option>')


PRE = "@{sussurro}&{template:rr} "
SUB = "{{sub=@{character_name}}} "
DADO = "@{dado}cs20cf1"
MOD = " + @{mod_temp}[mod]"


def opcoes_atr(padrao, com_pergunta=True):
    out = []
    for k, _, ab in ATRS:
        sel = " selected" if k == padrao else ""
        out.append('<option value="@{%s}"%s>%s</option>' % (k, sel, ab))
    if com_pergunta:
        q = "?{Atributo|" + "|".join("%s,@{%s}" % (n, k) for k, n, _ in ATRS) + "}"
        sel = " selected" if padrao == "perguntar" else ""
        out.append('<option value="%s"%s>?</option>' % (q, sel))
    return "".join(out)


ROLAGENS = {}


def rolar(nome, titulo, formula, classe="rolar", rotulo=None, extra=""):
    ROLAGENS[nome] = PRE + "{{titulo=%s}} %s{{rolagem=[[%s]]}}%s" % (titulo, SUB, formula, extra)
    return '<button type="action" class="%s" name="act_%s">%s</button>' % (classe, nome, rotulo or titulo)


def tile(rotulo, valor, dica="", largo=False):
    return ('<div class="tile%s"><div class="t-rot">%s</div><div class="t-val">%s</div>%s</div>'
            % (" largo" if largo else "", rotulo, valor, '<div class="t-dica">%s</div>' % dica if dica else ""))


def calc(attr):
    return '<span class="calc" name="attr_%s"></span>' % attr


def linha_atr(k, nome, ab, tiles):
    btn = rolar("atr_" + k, "Teste de " + nome, DADO + " + @{%s}[%s]" % (k, ab) + MOD, rotulo=nome)
    return ('<div class="atr"><div class="atr-id">%s<div class="atr-caixa"><input class="caixa" type="number" name="attr_%s" value="0" min="0" max="5" title="%s (0 a 5)"></div></div>'
            '<div class="seta"></div><div class="tiles">%s</div></div>'
            % (btn, k, nome, "".join(tiles)))


def pericias_html():
    rows = []
    for k, nome, padrao, pen in PERICIAS:
        f = DADO + " + @{grad_%s}[grad] + (@{atr_%s})[atributo] + @{out_%s}[outros]" % (k, k, k)
        if pen:
            f += " - @{prot_pen}[armadura]"
        f += MOD
        rows.append(
            '<div class="per">%s'
            '<span class="per-a">%s</span><select name="attr_atr_%s" title="Atributo da abordagem">%s</select>'
            '<input type="number" name="attr_grad_%s" value="0" min="0" max="8" title="Graduação">'
            '<input type="number" name="attr_out_%s" value="0" title="Outros bônus"></div>'
            % (rolar("per_" + k, nome, f), '<span class="mi" title="Sofre a penalidade do item de proteção">shield</span>' if pen else "", k, opcoes_atr(padrao), k, k))
    return "\n".join(rows)


def reacao(k, nome, atr_formula, dica):
    f = DADO + " + @{grad_reacoes}[grad] + %s + @{out_reacoes}[outros] - @{prot_pen}[armadura]" % atr_formula + MOD
    return '<div class="reacao">%s<div class="reacao-atr">%s</div></div>' % (rolar("reacao_" + k, nome, f, classe="rolar botao"), dica)


def reacoes_html():
    return (reacao("esquiva", "Esquiva", "@{agilidade}[AGI]", "Agilidade")
            + reacao("bloqueio", "Bloqueio", "(@{atr_bloqueio})[atributo]", '<select name="attr_atr_bloqueio" title="Atributo do bloqueio">' + opcoes_atr("perguntar") + '</select>')
            + reacao("contra", "Contra-ataque", "@{forca}[FOR]", "Força"))


def estagio(i, nome, custo):
    ops = "".join('<label class="op"><input type="radio" name="attr_esp_%d_escolha" value="%d"><span name="attr_esp_%d_op%d">—</span></label>' % (i, n, i, n)
                  for n in (1, 2, 3))
    execs = "".join('<option value="%s"%s>%s</option>' % (e, " selected" if e == "Ação Padrão" else "", e) for e in EXECS)
    return ('<div class="estagio estagio-%d">'
            '<div class="estagio-cab"><b>%s</b><small>grad. %d · %d PH</small></div>'
            '<div class="estagio-trava"><span class="mi" aria-hidden="true">lock</span> Libera com %d graduações na perícia</div>'
            '<div class="opcoes" title="Escolha uma das três habilidades do livro para esta etapa">'
            '<input type="radio" class="op-nenhuma" name="attr_esp_%d_escolha" value="0" checked>%s</div>'
            '<div class="estagio-topo"><input type="text" name="attr_esp_%d_nome" placeholder="Nome da habilidade" title="Nome da habilidade">'
            '<select name="attr_esp_%d_exec" title="Tempo de execução">%s</select>'
            '<button type="action" class="rolar botao" name="act_usar%d">Usar</button></div>'
            '<textarea name="attr_esp_%d_texto" placeholder="Benefício" title="Texto da habilidade"></textarea></div>'
            % (i, nome, custo * 2, custo, custo * 2, i, ops, i, i, execs, i, i))


def html():
    ini = rolar("iniciativa", "Iniciativa", DADO + " + @{iniciativa}[iniciativa]" + MOD + " &{tracker}")
    ini_b = ini.replace('class="rolar"', 'class="rolar botao"')
    corpo = [
        linha_atr("forca", "Força", "FOR", [
            tile("Carga kg", '<span class="t-num"><span name="attr_carga_leve"></span>/<span name="attr_carga_media"></span>/<span name="attr_carga_pesada"></span></span>', '<span title="leve / média / pesada">L · M · P</span>'),
            tile("Arremesso", calc("arremesso") + "<i>m</i>", "2 + 2×FOR")]),
        linha_atr("agilidade", "Agilidade", "AGI", [
            tile(ini, calc("iniciativa"), "AGI + 1"),
            tile("Movimento", calc("movimento") + "<i>m</i>", "2 + 2×AGI")]),
        linha_atr("vitalidade", "Vitalidade", "VIT", [
            tile("Fôlego · VIT + 1", '<input type="number" class="mini" name="attr_folego" value="1" min="0" title="Fôlego atual"><span class="barra">/</span>' + calc("folego_max")
, '<span title="Gasto por rodada; uma rodada completa recupera tudo">gasto: correr 1 · nadar 2 · escalar 3</span>', largo=True)]),
    ]
    corpo = ('<div class="corpo-topo"><div class="foto"><span class="foto-vazio">Foto 3×4</span><img name="attr_character_avatar" alt=""></div>'
             '<div class="corpo-linhas">' + corpo[0] + corpo[1] + corpo[2] + '</div></div>')
    mente = "\n".join([
        linha_atr("carisma", "Carisma", "CAR", [
            tile("Presença", calc("presenca"), "CAR + 2"),
            tile("Idiomas", calc("idiomas_qtd"), "nativo + INT ÷ 2")]),
        linha_atr("intelecto", "Intelecto", "INT", [
            tile("Memória", calc("memoria"), "INT + 1"),
            tile("Magia Oculta", '<span class="t-txt">Ciclo I 3 · II 6 · III 9 PS</span>', "paga com Sanidade")]),
    ])
    surto_val = (PRE + "{{titulo=Surto}} " + SUB + "{{surto=[[1d20]]}} {{rodadas=[[1d4]]}} "
                 "{{texto=Resgate: 3 sucessos de Interpessoal (DT 15) antes do fim das rodadas.}}")
    morrendo_val = (PRE + "{{titulo=Morrendo}} " + SUB + "{{rolagem=[[1d100]]}} {{dt=@{morrendo_chance}%}} "
                    "{{texto=Continua lutando se o d100 for menor que a chance. Qualquer dano mata.}}")
    esvaecer_val = (PRE + "{{titulo=Esvaecer}} " + SUB + "{{rolagem=[[" + DADO + " + @{intelecto}[INT]" + MOD + "]]}} "
                    "{{dt=[[12 + @{esvaecer_dias}]]}} {{texto=Falhar é perder o controle para a criatura.}}")
    ROLAGENS["esvaecer"] = esvaecer_val
    atk_val = (PRE + "{{titulo=@{atk_nome}}} {{sub=Ataque · @{character_name}}} "
               "{{rolagem=[[@{dado}cs>@{atk_margem}cf1 + @{atk_pericia}[perícia] + (@{atk_atr})[atributo] + @{atk_bonus}[bônus]" + MOD + "]]}} "
               "{{dano=[[@{atk_dano} + @{atk_for}[FOR] + @{atk_dano_bonus}[bônus]]]}} "
               "{{nota=Decisivo @{atk_margem}+ · @{atk_mult} · alcance @{atk_alcance}}}")
    ROLAGENS["__atk"] = atk_val
    mag_val = (PRE + "{{titulo=@{mag_nome}}} {{sub=Magia Oculta · @{mag_escola} · @{character_name}}} "
               "{{custo=@{mag_custo} PS}} {{dt=[[10 + @{mag_custo}*2/3]]}} "
               "{{nota=@{mag_exec} · @{mag_alcance} · @{mag_duracao} · Resist. @{mag_resist} · @{mag_comp}}} {{texto=@{mag_efeito}}}")
    van_val = PRE + "{{titulo=@{van_nome}}} {{sub=Vantagem · @{character_name}}} {{texto=@{van_texto}}}"
    des_val = PRE + "{{titulo=@{des_nome}}} {{sub=Desvantagem · @{character_name}}} {{texto=@{des_texto}}}"

    conds = "".join('<label class="cond"><input type="checkbox" name="attr_cond_%d" value="1"><span>%s</span></label>' % (i, c)
                    for i, c in enumerate(CONDICOES))
    trilha = "".join('<div class="lv lv-%s"><b>%s</b><small>%s</small></div>' % (n.replace("+", ""), n, t) for n, t in NIVEIS)
    surtos_tpl = "".join("{{#rollTotal() surto %d}}%s{{/rollTotal() surto %d}}" % (i + 1, s, i + 1) for i, s in enumerate(SURTOS))

    return f"""<!-- Reino Reverso · ficha base para Roll20 (livro 0.9.9.1). Use com Legacy Sanitization DESLIGADO. -->
<input type="hidden" class="flag-aba" name="attr_aba" value="jogo">
<input type="hidden" class="flag-caminho" name="attr_caminho" value="investigador">
<input type="hidden" class="flag-nivel" name="attr_nivel" value="1">
<input type="hidden" class="flag-carga" name="attr_carga_estado" value="leve">

<div class="topo">
  <div class="marca"><span class="marca-logo" title="Reino Reverso"><span class="ml-1">Reino</span><span class="ml-2">Reverso</span></span><span class="marca-sub">Ficha de personagem · v{VERSAO}</span></div>
  <div class="ident">
    <label class="campo c-nome"><input type="text" name="attr_character_name"><span>Personagem</span></label>
    <label class="campo"><select name="attr_caminho"><option value="investigador" selected>Investigador</option><option value="ocultista">Ocultista</option><option value="sobrevivente">Sobrevivente</option></select><span>Caminho</span></label>
    <label class="campo c-nivel"><input type="number" name="attr_nivel" value="1" min="1"><span>Nível</span></label>
    <label class="campo"><select name="attr_idade"><option value="crianca">Criança</option><option value="adulto" selected>Adulto</option><option value="idoso">Idoso</option></select><span>Idade</span></label>
    <label class="campo"><input type="text" name="attr_jogador"><span>Jogador</span></label>
  </div>
  <div class="mesa">
    <label class="campo"><select name="attr_dado"><option value="1d20" selected>Normal</option><option value="2d20kh1">Vantagem</option><option value="2d20kl1">Desvantagem</option></select><span>Dado</span></label>
    <label class="campo c-nivel"><input type="number" name="attr_mod_temp" value="0"><span>Mod.</span></label>
    <label class="campo"><select name="attr_sussurro"><option value="" selected>Público</option><option value="/w gm ">Só Narrador</option></select><span>Rolagem</span></label>
  </div>
</div>

<div class="abas">
  <button type="action" name="act_aba_jogo" class="aba aba-b-jogo">Em jogo</button>
  <button type="action" name="act_aba_combate" class="aba aba-b-combate">Combate</button>
  <button type="action" name="act_aba_poderes" class="aba aba-b-poderes">Poderes</button>
  <button type="action" name="act_aba_historia" class="aba aba-b-historia">Personagem</button>
  <button type="action" name="act_aba_inventario" class="aba aba-b-inventario">Inventário</button>
  <button type="action" name="act_aba_ajustes" class="aba aba-b-ajustes">Ajustes</button>
</div>

<!-- ============================ EM JOGO ============================ -->
<div class="pagina pg-jogo">
 <div class="duas">
  <div class="col">
   <div class="bloco humano">
    <h3 class="h-glitch">Corpo <small>primário → secundários → recurso</small></h3>
{corpo}
    <div class="recurso">
     <div class="recurso-nome"><b>Vida</b><small>PV · Caminho + VIT</small></div>
     <div class="recurso-valor"><input class="caixa" type="number" name="attr_pv" value="0" title="PV atuais"><span class="barra">/</span><span class="calc alto" name="attr_pv_max"></span></div>
     {tile("RD total", calc("rd_total"), "item + extra")}
     {tile('<button type="roll" class="rolar" name="roll_morrendo" value="' + morrendo_val + '">Morrendo</button>', '<input type="number" class="mini" name="attr_morrendo_chance" value="50" min="0" max="100"><i>%</i>', "d100 por rodada")}
    </div>
   </div>

   <div class="bloco reverso">
    <h3 class="h-glitch">Mente <small>primário → secundários → recurso</small></h3>
{mente}
    <div class="recurso">
     <div class="recurso-nome"><b>Sanidade</b><small>PS · Caminho + INT</small></div>
     <div class="recurso-valor"><input class="caixa" type="number" name="attr_ps" value="0" title="PS atuais"><span class="barra">/</span><span class="calc alto" name="attr_ps_max"></span></div>
     {tile("Pagar magia", '<span class="gastar"><button type="action" name="act_ps_3">−3</button><button type="action" name="act_ps_6">−6</button><button type="action" name="act_ps_9">−9</button></span>', "desconta dos PS")}
     {tile('<button type="roll" class="rolar" name="roll_surto" value="' + surto_val + '">Surto</button>', '<span class="t-txt">PS chegou a 0</span>', "d20 na tabela + 1D4 rodadas")}
    </div>
   </div>

   <div class="par">
    <div class="bloco">
     <h3>Habilidade <small>só do Caminho</small></h3>
     <div class="recurso simples">
      <input class="caixa" type="number" name="attr_ph" value="0" title="PH atuais"><span class="barra">/</span><span class="calc alto" name="attr_ph_max"></span>
      <div class="gastar"><button type="action" name="act_ph_1">−1</button><button type="action" name="act_ph_2">−2</button><button type="action" name="act_ph_3">−3</button><button type="action" name="act_ph_4">−4</button></div>
     </div>
    </div>
    <div class="bloco">
     <h3>Força de Vontade <small>20 natural: +1</small></h3>
     <div class="recurso simples">
      <input class="caixa" type="number" name="attr_fdv" value="2" min="0" title="Pontos atuais"><span class="barra">/</span><input class="caixa fina" type="number" name="attr_fdv_max" value="2" min="0">
      <small class="dica">Rolar de novo · +1D6 · 25% PV · 1D6+2 PH · 1D6+2 PS · movimento</small>
     </div>
    </div>
   </div>

   <div class="bloco conds-bloco">
    <input type="checkbox" class="cond-abrir" name="attr_cond_aberto" value="1" title="Abrir ou fechar a lista de condições">
    <h3>Condições <span class="cond-conta"><span name="attr_cond_qtd">0</span> ativas</span><span class="mi cond-seta">expand_more</span></h3>
    <div class="cond-resumo" name="attr_cond_resumo">Nenhuma</div>
    <div class="conds">{conds}</div>
   </div>
  </div>

  <div class="col">
   <div class="bloco">
    <h3>Perícias <small>grad. máx. <span name="attr_grad_max"></span></small></h3>
    <div class="per per-cab"><span>d20 + grad + atr.</span><span></span><span>Atr</span><span>Grad</span><span>Out</span></div>
{pericias_html()}
    <div class="per-total"><b>Graduações gastas</b><span class="calc" name="attr_grad_total"></span><span>de</span><span class="calc" name="attr_grad_previsto"></span><small>14 na criação + 3 por nível</small></div>
    <small class="dica"><span class="mi">shield</span> sofre a penalidade do item de proteção. Clique no nome para rolar.</small>
   </div>

   <div class="bloco rp-bloco">
    <h3>Reações e proteção</h3>
    <div class="rp-sub">Reagir a um ataque <small>d20 + Reações + atributo − pen.</small></div>
    <div class="reacoes">{reacoes_html()}</div>
    <small class="dica">Alvo indefeso não reage: o ataque acerta com 10 ou mais.</small>
    <div class="rp-sub rp-item">Item de proteção <small>RD total <span name="attr_rd_total"></span></small></div>
    <input type="text" name="attr_prot_nome" placeholder="Nome do item">
    <div class="protecao">
     <label class="campo"><input type="number" name="attr_prot_rd" value="0"><span>RD do item</span></label>
     <label class="campo"><input type="number" name="attr_rd_outros" value="0"><span>RD extra</span></label>
     <label class="campo"><input type="number" name="attr_prot_pen" value="0" min="0"><span>Penalidade</span></label>
     <label class="campo"><input type="number" name="attr_prot_mov" value="0" min="0" step="0.5"><span>Movimento −m</span></label>
    </div>
   </div>
  </div>
 </div>

 <div class="bloco resumo">
  <h3>Ataques <small>resumo para rolar · edite na aba Combate</small></h3>
  <div class="atk-r atk-r-cab"><span></span><span>Arma</span><span>Dano</span><span>Alcance</span><span>Munição</span></div>
  <fieldset class="repeating_ataques">
   <div class="atk-r">
    <button type="action" class="rolar botao" name="act_atk">Atacar</button>
    <span class="atk-r-nome" name="attr_atk_nome"></span>
    <span class="atk-r-val" name="attr_atk_dano"></span>
    <span class="atk-r-val" name="attr_atk_alcance"></span>
    <input type="number" name="attr_atk_municao" value="0" title="Munição restante">
   </div>
  </fieldset>
 </div>

</div>

<!-- ============================ COMBATE ============================ -->
<div class="pagina pg-combate">
 <div class="bloco humano">
  <h3>Na sua vez <small>d20 + bônus, com o modo de dado e o modificador do topo</small></h3>
  <div class="vez">
   <div class="reacao">{ini_b}<div class="reacao-atr">bônus <span name="attr_iniciativa"></span></div></div>
   {reacoes_html()}
  </div>
 </div>
 <div class="bloco">
  <h3>Ataques <small>ataque = d20 + perícia + atributo + bônus</small></h3>
  <fieldset class="repeating_ataques">
   <div class="atk">
    <button type="action" class="rolar botao" name="act_atk">Atacar</button>
    <label class="campo a-arma"><input type="text" name="attr_atk_nome" placeholder="Arma"><span>Arma</span></label>
    <label class="campo a-per"><select name="attr_atk_pericia"><option value="@{{grad_pontaria}}" selected>Pontaria</option><option value="@{{grad_armas_brancas}}">Armas Brancas</option><option value="@{{grad_briga}}">Briga</option><option value="@{{grad_explosivos}}">Explosivos</option><option value="0">Nenhuma</option></select><span>Perícia</span></label>
    <label class="campo"><select name="attr_atk_atr">{opcoes_atr("agilidade", False)}</select><span>Atributo</span></label>
    <label class="campo"><input type="number" name="attr_atk_bonus" value="0"><span>Bônus</span></label>
    <label class="campo"><input type="text" name="attr_atk_dano" value="1d6"><span>Dano</span></label>
    <label class="campo c-check"><input type="checkbox" name="attr_atk_for" value="@{{forca}}"><span>+ Força</span></label>
    <label class="campo"><input type="number" name="attr_atk_dano_bonus" value="0"><span>+ Dano</span></label>
    <label class="campo"><input type="number" name="attr_atk_margem" value="20" min="2" max="20"><span>Decisivo</span></label>
    <label class="campo"><input type="text" name="attr_atk_mult" value="x2"><span>Mult.</span></label>
    <label class="campo"><input type="text" name="attr_atk_alcance" value="-"><span>Alcance</span></label>
    <label class="campo"><input type="number" name="attr_atk_municao" value="0"><span>Munição</span></label>
    <label class="campo"><input type="number" name="attr_atk_integridade" value="0"><span>Integridade</span></label>
   </div>
  </fieldset>
 </div>
</div>

<!-- ============================ PODERES ============================ -->
<div class="pagina pg-poderes">
 <div class="bloco hab-caminho">
  <h3>Habilidade de Caminho <span class="hc-acoes"><label class="uso"><input type="checkbox" name="attr_caminho_usado" value="1"><span>usada na cena</span></label><button type="action" class="rolar botao" name="act_caminho">Usar</button></span></h3>
  <p class="hc hc-investigador"><b>Mente Analítica.</b> Uma vez por cena, ao falhar em Conhecimento, Ciência Forense, Obter Informações ou Percepção, você obtém uma pista parcial.</p>
  <p class="hc hc-ocultista"><b>Arcana Pessoal.</b> Uma magia de Ciclo I desde o nível 1, usável Intelecto + 1 vezes por dia.</p>
  <p class="hc hc-sobrevivente"><b>Instinto de Sobrevivência.</b> Uma vez por cena, quando um ataque ou efeito reduziria seus PV a 0, você fica com 1 PV.</p>
 </div>
 <div class="bloco">
  <h3>Especializações <small>níveis 1, 5 e 10 · etapas liberam com 2, 4, 6 e 8 graduações · a escolha não pode ser desfeita</small></h3>
  <fieldset class="repeating_especializacoes">
   <div class="esp">
    <input type="hidden" class="esp-lib" name="attr_esp_lib" value="0">
    <input type="hidden" class="esp-vaga" name="attr_esp_vaga" value="1">
    <input type="checkbox" class="esp-fechar" name="attr_esp_fechada" value="1" title="Recolher ou abrir esta especialização" aria-label="Recolher especialização">
    <div class="esp-cab"><span class="mi esp-seta" aria-hidden="true">expand_less</span><b class="esp-nome" name="attr_esp_pericia">Nova especialização</b><span class="esp-resumo" name="attr_esp_resumo"></span><span class="esp-grad">grad. <span name="attr_esp_grad">0</span></span></div>
    <div class="esp-aviso">Seu nível ainda não libera esta especialização (níveis 1, 5 e 10: uma por etapa).</div>
    <div class="esp-corpo">
    <div class="esp-topo"><label class="campo"><select name="attr_esp_pericia" title="Perícia especializada">{opcoes_livro([c["pericia"] for c in LIVRO["especializacoes"]], "Escolher perícia")}</select><span>Perícia</span></label>
    <label class="campo c-passivo"><textarea name="attr_esp_passivo" placeholder="Efeito passivo" title="Efeito passivo"></textarea><span>Efeito passivo · recebido ao se especializar</span></label></div>
    {estagio(1, "Inicial", 1)}{estagio(2, "Secundária", 2)}{estagio(3, "Avançada", 3)}{estagio(4, "Final", 4)}
    </div>
   </div>
  </fieldset>
 </div>
 <div class="duas iguais">
  <div class="bloco">
   <h3>Vantagens <small>{len(LIVRO["vantagens"])} no livro</small></h3>
   <fieldset class="repeating_vantagens"><div class="traco">
    <div class="traco-topo"><label class="campo"><select name="attr_van_escolha" title="Vantagem do livro">{opcoes_livro([n for n, _ in LIVRO["vantagens"]], "Escolher do livro")}</select><span>Do livro</span></label>
    <label class="campo"><input type="text" name="attr_van_nome" placeholder="Nome"><span>Nome</span></label>
    <button type="action" class="rolar botao" name="act_van">Chat</button></div>
    <textarea name="attr_van_texto" placeholder="Benefício" title="Texto da vantagem"></textarea></div></fieldset>
  </div>
  <div class="bloco">
   <h3>Desvantagens <small>{len(LIVRO["desvantagens"])} no livro</small></h3>
   <fieldset class="repeating_desvantagens"><div class="traco">
    <div class="traco-topo"><label class="campo"><select name="attr_des_escolha" title="Desvantagem do livro">{opcoes_livro([n for n, _ in LIVRO["desvantagens"]], "Escolher do livro")}</select><span>Do livro</span></label>
    <label class="campo"><input type="text" name="attr_des_nome" placeholder="Nome"><span>Nome</span></label>
    <button type="action" class="rolar botao" name="act_des">Chat</button></div>
    <textarea name="attr_des_texto" placeholder="Penalidade" title="Texto da desvantagem"></textarea></div></fieldset>
  </div>
 </div>
 <div class="bloco reverso">
  <h3>Magias Ocultas <small>Ciclo I 3 PS · DT 12 — Ciclo II 6 PS · DT 14 — Ciclo III 9 PS · DT 16</small></h3>
  <fieldset class="repeating_magias">
   <div class="mag">
    <button type="roll" class="rolar botao" name="roll_mag" value="{mag_val}">Conjurar</button>
    <label class="campo c-largo"><input type="text" name="attr_mag_nome" placeholder="Magia"><span>Magia</span></label>
    <label class="campo"><select name="attr_mag_custo"><option value="3" selected>Ciclo I</option><option value="6">Ciclo II</option><option value="9">Ciclo III</option></select><span>Ciclo</span></label>
    <label class="campo"><input type="text" name="attr_mag_escola" value="-"><span>Escola</span></label>
    <label class="campo"><input type="text" name="attr_mag_exec" value="Ação padrão"><span>Execução</span></label>
    <label class="campo"><input type="text" name="attr_mag_alcance" value="-"><span>Alcance</span></label>
    <label class="campo"><input type="text" name="attr_mag_duracao" value="-"><span>Duração</span></label>
    <label class="campo"><input type="text" name="attr_mag_resist" value="Nenhuma"><span>Resistência</span></label>
    <label class="campo"><input type="text" name="attr_mag_comp" value="-"><span>Componentes</span></label>
    <textarea name="attr_mag_efeito" placeholder="Efeito"></textarea>
   </div>
  </fieldset>
 </div>
</div>

<!-- ============================ INVENTARIO ============================ -->
<div class="pagina pg-inventario">
 <div class="bloco">
  <h3>Equipamento <small>peso total <span name="attr_peso_total"></span> kg · carga <span name="attr_carga_estado"></span></small></h3>
  <div class="aviso av-media">Carga média: −1 em testes físicos e −1,5 m de movimento (já descontado).</div>
  <div class="aviso av-pesada">Carga pesada: −3 em testes físicos, −3 m de movimento (já descontado) e não pode correr.</div>
  <div class="aviso av-acima">Acima da carga pesada: só é possível levantar e arrastar.</div>
  <fieldset class="repeating_itens"><div class="item">
   <input type="text" name="attr_item_nome" placeholder="Item">
   <label class="campo"><input type="number" name="attr_item_qtd" value="1" min="0"><span>Qtd</span></label>
   <label class="campo"><input type="number" name="attr_item_peso" value="0" min="0" step="0.25"><span>Peso kg</span></label>
  </div></fieldset>
  <label class="campo c-dinheiro"><input type="number" name="attr_dinheiro" value="500"><span>Dinheiro ($)</span></label>
 </div>
 <div class="duas iguais">
  <div class="bloco"><h3>Objetos de Poder</h3><textarea class="alto" name="attr_objetos_poder"></textarea></div>
  <div class="bloco"><h3>Local seguro e aliados</h3><textarea class="alto" name="attr_aliados" placeholder="Nome · lealdade 0 a 5"></textarea></div>
 </div>
</div>

<!-- ============================ PERSONAGEM ============================ -->
<div class="pagina pg-historia">
 <div class="bloco">
  <h3>Do humano ao Reverso</h3>
  <div class="trilha">{trilha}</div>
 </div>
 <div class="duas iguais">
  <div class="bloco">
   <h3>Antes do horror</h3>
   <label class="rot">Quem eu era</label><textarea name="attr_quem_era"></textarea>
   <label class="rot">O que temo perder</label><textarea name="attr_temo_perder"></textarea>
   <label class="rot">O que me faz continuar</label><textarea name="attr_continuar"></textarea>
   <label class="rot">Idiomas</label><input type="text" name="attr_idiomas">
  </div>
  <div class="bloco reverso">
   <h3>Corrupção</h3>
   <label class="rot">Mudança física · nível 3</label><textarea name="attr_mudanca_3"></textarea>
   <label class="rot">Mudança física · nível 6</label><textarea name="attr_mudanca_6"></textarea>
   <label class="rot">Mudança física · nível 9</label><textarea name="attr_mudanca_9"></textarea>
   <div class="esvaecer"><button type="action" class="rolar botao" name="act_esvaecer">Esvaecer</button>
   <label class="campo"><input type="number" name="attr_esvaecer_dias" value="0" min="0"><span>Dias</span></label><small>Intelecto, DT 12 + dias</small></div>
  </div>
 </div>
 <div class="bloco"><h3>Anotações e pistas</h3><textarea class="alto" name="attr_anotacoes"></textarea></div>
</div>

<!-- ============================ AJUSTES ============================ -->
<div class="pagina pg-ajustes">
 <div class="bloco">
  <h3>Ajustes manuais <small>somados ao cálculo automático</small></h3>
  <div class="ajustes">
   <label class="campo"><input type="number" name="attr_pv_mod" value="0"><span>PV máximos</span></label>
   <label class="campo"><input type="number" name="attr_ps_mod" value="0"><span>PS máximos</span></label>
   <label class="campo"><input type="number" name="attr_ph_mod" value="0"><span>PH máximos</span></label>
   <label class="campo"><input type="number" name="attr_mov_mod" value="0" step="0.5"><span>Movimento (m)</span></label>
   <label class="campo"><input type="number" name="attr_ini_mod" value="0"><span>Iniciativa</span></label>
  </div>
  <p class="dica">Fórmulas usadas: PV = base do Caminho + VIT, mais (incremento + VIT) por nível acima do 1. PS igual, com INT. PH só do Caminho.
  Investigador 4/+2 PV, 4/+2 PS, 4/+3 PH · Ocultista 4/+2 PV, 8/+4 PS, 2/+1 PH · Sobrevivente 8/+4 PV, 4/+2 PS, 2/+1 PH.
  Graduação máxima: 2 até o nível 2, 4 do nível 3, 6 do nível 6, 8 do nível 9 (livro, p. 26). Graduações previstas: 14 na criação + 3 por nível.</p>
 </div>
</div>

<rolltemplate class="sheet-rolltemplate-rr">
 <div class="sheet-rr">
  <div class="sheet-rr-topo"><div class="sheet-rr-titulo">{{{{titulo}}}}</div>{{{{#sub}}}}<div class="sheet-rr-sub">{{{{sub}}}}</div>{{{{/sub}}}}</div>
  {{{{#modo}}}}<div class="sheet-rr-modo">{{{{modo}}}}</div>{{{{/modo}}}}
  {{{{#atributo}}}}<div class="sheet-rr-linha sheet-rr-atr"><span>Atributo</span><span>{{{{atributo}}}}</span></div>{{{{/atributo}}}}
  {{{{#rolagem}}}}<div class="sheet-rr-linha"><span>Teste</span><span class="sheet-rr-valor">{{{{rolagem}}}}</span></div>{{{{/rolagem}}}}
  {{{{#rollWasCrit() rolagem}}}}<div class="sheet-rr-selo sheet-rr-bom">Sucesso excepcional</div>{{{{/rollWasCrit() rolagem}}}}
  {{{{#rollTotal() computed::fdv 1}}}}<div class="sheet-rr-selo sheet-rr-fdv">20 natural · +1 Força de Vontade</div>{{{{/rollTotal() computed::fdv 1}}}}
  {{{{#rollTotal() computed::fdv 2}}}}<div class="sheet-rr-selo sheet-rr-fdv">20 natural · Força de Vontade já está no máximo</div>{{{{/rollTotal() computed::fdv 2}}}}
  {{{{#rollWasFumble() rolagem}}}}<div class="sheet-rr-selo sheet-rr-ruim">Falha dramática</div>{{{{/rollWasFumble() rolagem}}}}
  {{{{#dano}}}}<div class="sheet-rr-linha"><span>Dano</span><span class="sheet-rr-valor">{{{{dano}}}}</span></div>{{{{/dano}}}}
  {{{{#dt}}}}<div class="sheet-rr-linha"><span>DT</span><span class="sheet-rr-valor">{{{{dt}}}}</span></div>{{{{/dt}}}}
  {{{{#custo}}}}<div class="sheet-rr-linha"><span>Custo</span><span class="sheet-rr-valor">{{{{custo}}}}</span></div>{{{{/custo}}}}
  {{{{#surto}}}}<div class="sheet-rr-linha"><span>d20</span><span class="sheet-rr-valor">{{{{surto}}}}</span></div>
  <div class="sheet-rr-selo sheet-rr-reverso">{surtos_tpl}</div>
  <div class="sheet-rr-linha"><span>Rodadas para o resgate</span><span class="sheet-rr-valor">{{{{rodadas}}}}</span></div>{{{{/surto}}}}
  {{{{#nota}}}}<div class="sheet-rr-nota">{{{{nota}}}}</div>{{{{/nota}}}}
  {{{{#texto}}}}<div class="sheet-rr-texto">{{{{texto}}}}</div>{{{{/texto}}}}
  {{{{#t1}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t1}}}}</div>{{{{/t1}}}}
  {{{{#t2}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t2}}}}</div>{{{{/t2}}}}
  {{{{#t3}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t3}}}}</div>{{{{/t3}}}}
  {{{{#t4}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t4}}}}</div>{{{{/t4}}}}
  {{{{#t5}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t5}}}}</div>{{{{/t5}}}}
  {{{{#t6}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t6}}}}</div>{{{{/t6}}}}
  {{{{#t7}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t7}}}}</div>{{{{/t7}}}}
  {{{{#t8}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t8}}}}</div>{{{{/t8}}}}
  {{{{#t9}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t9}}}}</div>{{{{/t9}}}}
  {{{{#t10}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t10}}}}</div>{{{{/t10}}}}
  {{{{#t11}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t11}}}}</div>{{{{/t11}}}}
  {{{{#t12}}}}<div class="sheet-rr-texto sheet-rr-par">{{{{t12}}}}</div>{{{{/t12}}}}
 </div>
</rolltemplate>

<script type="text/worker">
{WORKER}
</script>
"""


WORKER = r"""
const RR_CAMINHOS = {
  investigador: { pv: [4, 2], ps: [4, 2], ph: [4, 3] },
  ocultista:    { pv: [4, 2], ps: [8, 4], ph: [2, 1] },
  sobrevivente: { pv: [8, 4], ps: [4, 2], ph: [2, 1] }
};
const RR_CARGA = [[15, 30, 45], [19, 38, 58], [25, 50, 75], [33, 66.5, 100], [43, 86.5, 130], [57, 100, 150]];
const RR_BASE = ["forca", "agilidade", "vitalidade", "intelecto", "carisma", "caminho", "nivel", "idade",
  "pv_mod", "ps_mod", "ph_mod", "mov_mod", "ini_mod", "rd_outros", "prot_rd", "prot_mov", "peso_total"];

const rrNum = (v) => { const n = parseFloat(v); return isNaN(n) ? 0 : n; };
const rrLimite = (v, min, max) => Math.max(min, Math.min(max, v));

const rrRecalcular = () => {
  getAttrs(RR_BASE, (v) => {
    const forca = rrLimite(Math.floor(rrNum(v.forca)), 0, 5);
    const agi = rrNum(v.agilidade), vit = rrNum(v.vitalidade), intel = rrNum(v.intelecto), car = rrNum(v.carisma);
    const nivel = Math.max(1, Math.floor(rrNum(v.nivel) || 1));
    const cam = RR_CAMINHOS[v.caminho] || RR_CAMINHOS.investigador;
    const acima = nivel - 1;
    const carga = RR_CARGA[forca];
    const peso = rrNum(v.peso_total);
    let estado = "leve", perdaCarga = 0;
    if (peso > carga[2]) { estado = "acima"; perdaCarga = 3; }
    else if (peso > carga[1]) { estado = "pesada"; perdaCarga = 3; }
    else if (peso > carga[0]) { estado = "media"; perdaCarga = 1.5; }
    const perdaIdade = v.idade === "crianca" ? 2 : 0;
    const movimento = Math.max(0, 2 + 2 * agi - rrNum(v.prot_mov) - perdaCarga - perdaIdade + rrNum(v.mov_mod));
    setAttrs({
      iniciativa: agi + 1 + rrNum(v.ini_mod),
      movimento: movimento,
      arremesso: 2 + 2 * forca,
      carga_leve: carga[0], carga_media: carga[1], carga_pesada: carga[2],
      carga_estado: estado,
      folego_max: vit + 1,
      memoria: intel + 1,
      idiomas_qtd: 1 + Math.floor(intel / 2),
      presenca: car + 2,
      pv_max: cam.pv[0] + vit + acima * (cam.pv[1] + vit) + rrNum(v.pv_mod),
      ps_max: cam.ps[0] + intel + acima * (cam.ps[1] + intel) + rrNum(v.ps_mod),
      ph_max: cam.ph[0] + acima * cam.ph[1] + rrNum(v.ph_mod),
      rd_total: rrNum(v.prot_rd) + rrNum(v.rd_outros),
      grad_max: nivel >= 9 ? 8 : nivel >= 6 ? 6 : nivel >= 3 ? 4 : 2,
      grad_previsto: 14 + 3 * acima
    });
  });
};

const rrPeso = () => {
  getSectionIDs("repeating_itens", (ids) => {
    const campos = [];
    ids.forEach((id) => { campos.push("repeating_itens_" + id + "_item_qtd", "repeating_itens_" + id + "_item_peso"); });
    getAttrs(campos, (v) => {
      let total = 0;
      ids.forEach((id) => { total += rrNum(v["repeating_itens_" + id + "_item_qtd"]) * rrNum(v["repeating_itens_" + id + "_item_peso"]); });
      setAttrs({ peso_total: Math.round(total * 100) / 100 });
    });
  });
};

const rrGastar = (attr, valor) => {
  getAttrs([attr], (v) => { const novo = {}; novo[attr] = Math.max(0, rrNum(v[attr]) - valor); setAttrs(novo); });
};

const RR_ROLAGENS = /*ROLAGENS*/;
const RR_ATAQUE = /*ATAQUE*/;

// rola pelo servidor, confere 20 natural e devolve o aviso de Forca de Vontade ao cartao
const RR_ATRS = /*ATRS*/;
const RR_MODO = { "2d20kh1": "Com vantagem · 2d20, fica o maior", "2d20kl1": "Com desvantagem · 2d20, fica o menor" };
// fonte do atributo de cada rolagem: campo de selecao ou atributo fixo
const rrFonteAtr = (nome) => {
  let m = /^per_(.+)$/.exec(nome); if (m) return { campo: "atr_" + m[1] };
  m = /^atr_(.+)$/.exec(nome); if (m) return { fixo: m[1] };
  if (nome === "reacao_esquiva") return { fixo: "agilidade" };
  if (nome === "reacao_contra") return { fixo: "forca" };
  if (nome === "reacao_bloqueio") return { campo: "atr_bloqueio" };
  return null;
};
const rrRotuloAtr = (chave, v) => {
  const a = RR_ATRS[chave];
  return a ? a[0] + " · " + a[1] + " " + (rrNum(v[chave]) >= 0 ? "+" : "") + rrNum(v[chave]) : "";
};
// acrescenta ao cartao o modo do dado (vantagem/desvantagem) e o atributo usado
const rrCabecalho = (fonte, cb) => {
  const pedir = ["dado"].concat(Object.keys(RR_ATRS));
  if (fonte && fonte.campo) pedir.push(fonte.campo);
  getAttrs(pedir, (v) => {
    let extra = "";
    if (RR_MODO[v.dado]) extra += " {{modo=" + RR_MODO[v.dado] + "}}";
    if (fonte) {
      let chave = fonte.fixo || "";
      if (fonte.campo) {
        const val = v[fonte.campo] || "";
        const m = /^@\{(\w+)\}$/.exec(val.trim());
        if (m) chave = m[1];
        else if (val.indexOf("?{") === 0) extra += " {{atributo=escolhido na pergunta}}";
      }
      if (chave) extra += " {{atributo=" + rrRotuloAtr(chave, v) + "}}";
    }
    cb(extra);
  });
};
const rrRolar = (modelo, fonte) => {
  rrCabecalho(fonte, (extra) => rrRolarDireto(modelo + extra));
};
const rrRolarDireto = (modelo) => {
  startRoll(modelo + " {{fdv=[[0]]}}", (r) => {
    const rolagem = r.results.rolagem || {};
    const dados = rolagem.dice || [];
    getAttrs(["dado", "fdv", "fdv_max"], (v) => {
      let natural = false;
      if (dados.length) {
        if (v.dado === "2d20kl1") natural = dados.every((d) => d === 20);
        else if (v.dado === "2d20kh1") natural = dados.some((d) => d === 20);
        else natural = dados[0] === 20;
      }
      let aviso = 0;
      if (natural) {
        const atual = rrNum(v.fdv), max = rrNum(v.fdv_max);
        if (atual < max) { setAttrs({ fdv: atual + 1 }); aviso = 1; } else { aviso = 2; }
      }
      finishRoll(r.rollId, { fdv: aviso });
    });
  });
};

Object.keys(RR_ROLAGENS).forEach((nome) => {
  on("clicked:" + nome, () => { rrRolar(RR_ROLAGENS[nome], rrFonteAtr(nome)); });
});
on("clicked:repeating_ataques:atk", (ev) => {
  const achou = /^repeating_ataques_(.+)_atk$/i.exec(ev.sourceAttribute || "");
  if (!achou) return;
  rrRolar(RR_ATAQUE.split("@{atk_").join("@{repeating_ataques_" + achou[1] + "_atk_"), { campo: "repeating_ataques_" + achou[1] + "_atk_atr" });
});

on("sheet:opened " + RR_BASE.map((a) => "change:" + a).join(" "), rrRecalcular);
on("sheet:opened change:repeating_itens remove:repeating_itens", rrPeso);

const RR_GRADS = /*GRADS*/;
const rrGraduacoes = () => {
  getAttrs(RR_GRADS, (v) => {
    let total = 0;
    RR_GRADS.forEach((a) => { total += rrNum(v[a]); });
    setAttrs({ grad_total: total });
  });
};
const RR_LIVRO = /*LIVRO*/;
const rrSeguro = (t) => String(t || "").replace(/[{}]/g, (c) => (c === "{" ? "(" : ")")).replace(/\[\[/g, "[ [").replace(/\]\]/g, "] ]").replace(/[@%&]\{/g, (c) => c[0] + " (");
const rrCartao = (dados) => {
  getAttrs(["sussurro", "character_name"], (v) => {
    const pars = String(dados.texto || "").split(/\n+/).map((x) => x.trim()).filter((x) => x);
    while (pars.length > 12) { const ult = pars.pop(); pars[11] += " " + ult; }
    let t = (v.sussurro || "") + "&{template:rr} {{titulo=" + rrSeguro(dados.titulo || "—") + "}} {{sub=" + rrSeguro(dados.sub + " · " + (v.character_name || "")) + "}}";
    if (dados.custo) t += " {{custo=" + rrSeguro(dados.custo) + "}}";
    if (dados.nota) t += " {{nota=" + rrSeguro(dados.nota) + "}}";
    pars.forEach((x, n) => { t += " {{t" + (n + 1) + "=" + rrSeguro(x) + "}}"; });
    startRoll(t, (r) => finishRoll(r.rollId, {}));
  });
};
const rrLinha = (ev, secao, campo) => {
  const m = new RegExp("^(repeating_" + secao + "_.+)_" + campo + "$", "i").exec(ev.sourceAttribute || "");
  return m ? m[1] : null;
};
[["vantagens", "van", "v", "Vantagem"], ["desvantagens", "des", "d", "Desvantagem"]].forEach(([secao, k, fonte, rotulo]) => {
  on("change:repeating_" + secao + ":" + k + "_escolha", (ev) => {
    const p = rrLinha(ev, secao, k + "_escolha"), nome = ev.newValue;
    if (!p || !RR_LIVRO[fonte][nome]) return;
    setAttrs({ [p + "_" + k + "_nome"]: nome, [p + "_" + k + "_texto"]: RR_LIVRO[fonte][nome] });
  });
  on("clicked:repeating_" + secao + ":" + k, (ev) => {
    const p = rrLinha(ev, secao, k);
    if (!p) return;
    getAttrs([p + "_" + k + "_nome", p + "_" + k + "_texto"], (v) => {
      rrCartao({ titulo: v[p + "_" + k + "_nome"], sub: rotulo, texto: v[p + "_" + k + "_texto"] });
    });
  });
});
const RR_ETAPAS = ["Inicial", "Secundária", "Avançada", "Final"];
const rrEspAplicar = (p, pericia, etapa, escolha) => {
  const livro = RR_LIVRO.e[pericia];
  const saida = {};
  if (!livro) return saida;
  const h = livro.h[etapa - 1][escolha - 1];
  if (h) { saida[p + "_esp_" + etapa + "_nome"] = h[0]; saida[p + "_esp_" + etapa + "_exec"] = h[1]; saida[p + "_esp_" + etapa + "_texto"] = h[2]; }
  return saida;
};
on("change:repeating_especializacoes:esp_pericia", (ev) => {
  const p = rrLinha(ev, "especializacoes", "esp_pericia");
  const livro = RR_LIVRO.e[ev.newValue];
  if (!p || !livro) return;
  getAttrs([1, 2, 3, 4].map((n) => p + "_esp_" + n + "_escolha"), (v) => {
    const saida = { [p + "_esp_passivo"]: livro.p };
    [1, 2, 3, 4].forEach((n) => {
      livro.h[n - 1].forEach((h, i) => { saida[p + "_esp_" + n + "_op" + (i + 1)] = h[0]; });
      Object.assign(saida, rrEspAplicar(p, ev.newValue, n, parseInt(v[p + "_esp_" + n + "_escolha"], 10) || 0));
    });
    setAttrs(saida);
  });
});
[1, 2, 3, 4].forEach((n) => {
  on("change:repeating_especializacoes:esp_" + n + "_escolha", (ev) => {
    const p = rrLinha(ev, "especializacoes", "esp_" + n + "_escolha");
    if (!p) return;
    getAttrs([p + "_esp_pericia"], (v) => setAttrs(rrEspAplicar(p, v[p + "_esp_pericia"], n, parseInt(ev.newValue, 10) || 0)));
  });
  // botao de acao em secao repetida: nome sem sublinhado, senao o Roll20 nao dispara o evento
  on("clicked:repeating_especializacoes:usar" + n, (ev) => {
    const p = rrLinha(ev, "especializacoes", "usar" + n);
    if (!p) return;
    const c = [p + "_esp_pericia", p + "_esp_" + n + "_nome", p + "_esp_" + n + "_exec", p + "_esp_" + n + "_texto"];
    getAttrs(c, (v) => rrCartao({ titulo: v[c[1]], sub: (v[c[0]] || "Especialização") + " · " + RR_ETAPAS[n - 1], custo: n + " PH", nota: v[c[2]], texto: v[c[3]] }));
  });
});

// Habilidade de Caminho no chat, marcando "usada na cena"
const RR_CAMINHO = /*CAMINHOS*/;
on("clicked:caminho", () => {
  getAttrs(["caminho"], (v) => {
    const c = RR_CAMINHO[v.caminho] || RR_CAMINHO.investigador;
    setAttrs({ caminho_usado: "1" });
    rrCartao({ titulo: c[0], sub: "Habilidade de Caminho · " + c[1], texto: c[2] });
  });
});

// especializacoes: etapas liberam por graduacao na pericia (2, 4, 6, 8); vagas por nivel (1, 5, 10)
const RR_PER_GRAD = /*PERGRAD*/;
const rrEsp = () => {
  getSectionIDs("repeating_especializacoes", (ids) => {
    const campos = ["nivel"].concat(Object.values(RR_PER_GRAD));
    ids.forEach((id) => {
      const p = "repeating_especializacoes_" + id + "_";
      campos.push(p + "esp_pericia", p + "esp_1_nome", p + "esp_2_nome", p + "esp_3_nome", p + "esp_4_nome");
    });
    getAttrs(campos, (v) => {
      const nivel = rrNum(v.nivel) || 1;
      const vagas = nivel >= 10 ? 3 : nivel >= 5 ? 2 : 1;
      const saida = {};
      ids.forEach((id, i) => {
        const p = "repeating_especializacoes_" + id + "_";
        const g = rrNum(v[RR_PER_GRAD[v[p + "esp_pericia"]]]);
        const lib = Math.max(0, Math.min(4, Math.floor(g / 2)));
        const nomes = [1, 2, 3, 4].filter((n) => n <= lib).map((n) => v[p + "esp_" + n + "_nome"]).filter((x) => x);
        saida[p + "esp_lib"] = lib;
        saida[p + "esp_grad"] = g;
        saida[p + "esp_vaga"] = i < vagas ? 1 : 0;
        saida[p + "esp_resumo"] = nomes.length ? nomes.join(" · ") : (lib ? "nenhuma habilidade escolhida" : "precisa de 2 graduações");
      });
      setAttrs(saida);
    });
  });
};
on("sheet:opened change:nivel remove:repeating_especializacoes change:repeating_especializacoes:esp_pericia "
  + [1, 2, 3, 4].map((n) => "change:repeating_especializacoes:esp_" + n + "_nome").join(" ") + " "
  + Object.values(RR_PER_GRAD).map((a) => "change:" + a).join(" "), rrEsp);

// versao da ficha gravada no personagem: base para migracoes de dados em versoes futuras
on("sheet:opened", () => { setAttrs({ versao_ficha: "/*VERSAO*/" }, { silent: true }); });

const RR_CONDS = /*CONDS*/;
const rrCondicoes = () => {
  const nomes = RR_CONDS.map((c, i) => "cond_" + i);
  getAttrs(nomes, (v) => {
    const ativas = RR_CONDS.filter((c, i) => v["cond_" + i] === "1");
    setAttrs({ cond_qtd: ativas.length, cond_resumo: ativas.length ? ativas.join(" · ") : "Nenhuma" });
  });
};
on("sheet:opened " + RR_CONDS.map((c, i) => "change:cond_" + i).join(" "), rrCondicoes);

on("sheet:opened " + RR_GRADS.map((a) => "change:" + a).join(" "), rrGraduacoes);

["jogo", "combate", "poderes", "historia", "inventario", "ajustes"].forEach((aba) => {
  on("clicked:aba_" + aba, () => { setAttrs({ aba: aba }); });
});
[3, 6, 9].forEach((n) => { on("clicked:ps_" + n, () => { rrGastar("ps", n); }); });
[1, 2, 3, 4].forEach((n) => { on("clicked:ph_" + n, () => { rrGastar("ph", n); }); });
"""


def css():
    regras_aba = "\n".join(
        ".charsheet .flag-aba[value=\"%s\"] ~ .pg-%s { display: block; animation: rr-abrir 0.18s ease-out; }\n"
        ".charsheet .flag-aba[value=\"%s\"] ~ .abas button[type=\"action\"].aba-b-%s, .charsheet .flag-aba[value=\"%s\"] ~ .abas button[type=\"action\"].aba-b-%s:hover { height: 38px; background: #E6E7E3; color: #0F1112; border-bottom-color: #E6E7E3; box-shadow: inset 0 5px 0 #F0A21C; }"
        % (a, a, a, a, a, a) for a in ["jogo", "combate", "poderes", "historia", "inventario", "ajustes"])
    regras_cam = "\n".join(".charsheet .flag-caminho[value=\"%s\"] ~ .pagina .hc-%s { display: block; }" % (c, c)
                           for c in ["investigador", "ocultista", "sobrevivente"])
    sel_nivel = []
    for n in range(1, 11):
        sel_nivel.append(".charsheet .flag-nivel[value=\"%d\"] ~ .pagina .lv-%d" % (n, n))
    for n in range(11, 31):
        sel_nivel.append(".charsheet .flag-nivel[value=\"%d\"] ~ .pagina .lv-11" % n)
    regras_nivel = ",\n".join(sel_nivel) + " { background: #0F1112; color: #E6E7E3; border-color: #0F1112; }"
    regras_carga = "\n".join(".charsheet .flag-carga[value=\"%s\"] ~ .pagina .av-%s { display: block; }" % (c, c)
                             for c in ["media", "pesada", "acima"])
    return CSS.replace("/*ABAS*/", regras_aba).replace("/*CAMINHO*/", regras_cam) \
              .replace("/*NIVEL*/", regras_nivel).replace("/*CARGA*/", regras_carga)


CSS = r"""/* Reino Reverso · ficha Roll20 (CSE) · versao em VERSAO no build.py. Paleta do moodboard:
   asfalto #0F1112 · concreto #6F7573 · papel #E6E7E3 · sodio #F0A21C · verdete #1F6F6B / #4FB3A5 */
@import url('https://fonts.googleapis.com/css?family=Archivo+Black|IBM+Plex+Mono:400,500,600|IBM+Plex+Sans:400,500,600|Material+Icons&display=swap');

/* Fonte do logo, servida pelo repositorio do projeto. Se o Roll20 recusar este bloco ao salvar, apague-o:
   os titulos passam a usar Archivo Black. */
@font-face { font-family: 'Doctor Glitch'; src: url('https://raw.githubusercontent.com/orafahell/Reino-Reverso/main/Doctor%20Glitch.otf') format('opentype'); font-weight: 400; font-style: normal; }
/* Versao com acentos, servida pelo repositorio (DoctorGlitch-Acentos-teste.ttf). */
@font-face { font-family: 'Doctor Glitch Acentos'; src: url('https://raw.githubusercontent.com/orafahell/Reino-Reverso/main/DoctorGlitch-Acentos-teste.ttf') format('truetype'); font-weight: 400; font-style: normal; font-display: swap; }

.charsheet { background: #1F1F1F; color: #0F1112; font-family: 'IBM Plex Sans', Arial, sans-serif; font-size: 13px; line-height: 1.3; padding: 10px; min-width: 840px; box-sizing: border-box; }
.charsheet * { box-sizing: border-box; }
.charsheet small { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #4A4F4D; font-weight: 400; }
.charsheet b { font-weight: 600; }
.charsheet label, .charsheet span, .charsheet div, .charsheet p { color: inherit; }
.charsheet p { margin: 0; }

/* ---------- campos ---------- */
.charsheet input[type="text"], .charsheet input[type="number"], .charsheet select, .charsheet textarea {
  width: 100%; height: 26px; margin: 0; padding: 2px 6px; border: 1px solid #0F1112; border-radius: 0; background: #FFFFFF; color: #0F1112;
  box-shadow: none; font-family: 'IBM Plex Sans', Arial, sans-serif; font-size: 13px; line-height: 1.2; }
.charsheet input[type="number"] { font-family: 'IBM Plex Mono', monospace; text-align: center; padding: 2px; -moz-appearance: textfield; }
.charsheet input[type="number"]::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.charsheet select { padding: 2px 2px; }
.charsheet textarea { height: 52px; resize: vertical; display: block; }
.charsheet textarea.alto { height: 130px; }
.charsheet input[type="checkbox"] { width: 14px; height: 14px; margin: 0; accent-color: #0F1112; }
.charsheet input:focus, .charsheet select:focus, .charsheet textarea:focus { outline: 2px solid #F0A21C; outline-offset: 0; }
.charsheet input[disabled] { display: none; }
.charsheet .campo { display: flex; flex-direction: column; gap: 2px; margin: 0; min-width: 0; }
.charsheet .campo > span, .charsheet .rot { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: #4A4F4D; font-weight: 400; margin: 0; }
.charsheet .rot { display: block; margin: 8px 0 2px; }
.charsheet input[type="number"].caixa { width: 58px; height: 44px; border: 2px solid #0F1112; font-size: 20px; font-weight: 600; flex-shrink: 0; }
.charsheet input[type="number"].caixa.fina { width: 44px; border-width: 1px; background: #D9DBD6; }
.charsheet input[type="number"].mini { width: 44px; height: 28px; flex-shrink: 0; }
.charsheet .calc { display: inline-flex; align-items: center; justify-content: center; min-width: 40px; height: 28px; padding: 0 6px; border: 1px dashed #6F7573; background: #D9DBD6;
  font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 500; flex-shrink: 0; }
.charsheet .calc.alto { min-width: 46px; height: 44px; font-size: 18px; }
.charsheet .calc.largo { min-width: 104px; gap: 2px; }
.charsheet .barra { font-size: 20px; color: #6F7573; }
.charsheet .dica { display: block; margin-top: 6px; }

/* ---------- botoes ---------- */
.charsheet button[type="roll"]::before, .charsheet button[type="action"]::before { content: none; display: none; }
.charsheet button[type].rolar { background: none; border: 0; border-bottom: 1px dashed #0F1112; border-radius: 0; box-shadow: none; padding: 0 1px; margin: 0; color: inherit;
  font-family: 'IBM Plex Sans', Arial, sans-serif; font-size: 13px; font-weight: 600; line-height: 1.3; text-align: left; text-shadow: none; cursor: pointer; }
.charsheet button[type].rolar:hover { background: #F0A21C; color: #0F1112; }
.charsheet button[type].rolar.botao { border: 2px solid #0F1112; background: #0F1112; color: #E6E7E3; padding: 4px 10px; height: 28px; text-align: center;
  font-family: 'Archivo Black', Arial, sans-serif; font-weight: 400; font-size: 11px; letter-spacing: 0.04em; text-transform: uppercase; }
.charsheet button[type].rolar.botao:hover { background: #F0A21C; border-color: #F0A21C; color: #0F1112; }
.charsheet .gastar { display: flex; align-items: center; gap: 4px; font-size: 12px; }
.charsheet .gastar button[type="action"] { height: 24px; min-width: 30px; padding: 0 4px; margin: 0; border: 1px solid #0F1112; border-radius: 0; background: #FFFFFF; color: #0F1112; box-shadow: none; text-shadow: none;
  font-family: 'IBM Plex Mono', monospace; font-size: 12px; cursor: pointer; }
.charsheet .gastar button[type="action"]:hover { background: #F0A21C; }

/* ---------- topo ---------- */
.charsheet .topo { display: flex; gap: 14px; align-items: flex-end; background: #1F1F1F; color: #E6E7E3; padding: 12px 2px; }
.charsheet .marca-logo { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; font-family: 'Doctor Glitch Acentos', 'Doctor Glitch', 'Archivo Black', Arial, sans-serif; text-transform: uppercase; color: #FFFFFF; white-space: nowrap; }
.charsheet .ml-1 { font-size: 27px; line-height: 0.86; }
.charsheet .ml-2 { font-size: 27px; line-height: 0.86; transform: scaleY(-1); }
.charsheet .marca-sub { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: #F0A21C; display: block; margin-top: 7px; white-space: nowrap; }
.charsheet .ident { flex: 1; display: grid; grid-template-columns: 1.5fr 1.5fr 0.6fr 1.1fr 1fr; gap: 8px; min-width: 0; }
.charsheet .mesa { display: grid; grid-template-columns: 1.3fr 0.6fr 1.3fr; gap: 8px; width: 212px; flex-shrink: 0; padding-left: 12px; border-left: 2px solid #F0A21C; }

/* ---------- abas: orelhas de pasta de arquivo ---------- */
.charsheet .abas { display: flex; align-items: flex-end; gap: 3px; margin: 12px 0 0; padding: 0 10px; border-bottom: 1px solid #0F1112; }
.charsheet .abas button[type="action"].aba { flex: 1; height: 28px; margin: 0 0 -1px; padding: 0 6px; background: #B9BDB8; color: #3A3F3D; border: 1px solid #0F1112; border-radius: 3px 12px 0 0;
  box-shadow: none; text-shadow: none; font-family: 'Archivo Black', Arial, sans-serif; font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; cursor: pointer;
  transition: height 0.15s ease-out, background-color 0.15s ease-out, color 0.15s ease-out; }
.charsheet .abas button[type="action"].aba:hover { background: #D5D7D2; color: #0F1112; height: 31px; }
.charsheet .pagina { display: none; background: #E6E7E3; border: 1px solid #0F1112; border-top: 0; padding: 12px 10px 2px; }
@keyframes rr-abrir { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .charsheet .pagina { animation: none !important; } .charsheet .abas button[type="action"].aba { transition: none; } }
/*ABAS*/

/* ---------- estrutura ---------- */
.charsheet .duas { display: grid; grid-template-columns: minmax(0, 1fr) 332px; gap: 10px; align-items: start; }
.charsheet .duas { margin-bottom: 10px; }
.charsheet .duas.iguais { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
.charsheet .par { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10px; }
.charsheet .col { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.charsheet .bloco { border: 1.5px solid #0F1112; background: #E6E7E3; padding: 10px; margin-bottom: 10px; min-width: 0; }
.charsheet .col > .bloco, .charsheet .par > .bloco, .charsheet .col > .par { margin-bottom: 0; }
.charsheet h3 { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin: 0 0 8px; padding: 0; font-family: 'Archivo Black', Arial, sans-serif; font-size: 12px; font-weight: 400; letter-spacing: 0.05em; text-transform: uppercase; color: #0F1112; line-height: 1.2; }
.charsheet h3 small { text-transform: none; letter-spacing: 0; }
.charsheet h3.h-glitch { font-family: 'Doctor Glitch Acentos', 'Doctor Glitch', 'Archivo Black', Arial, sans-serif; font-size: 26px; line-height: 1; letter-spacing: 0; margin-bottom: 10px; }
.charsheet h3.h-glitch small { font-family: 'IBM Plex Mono', monospace; font-size: 11px; }

/* bloco do Reverso: cores invertidas */
.charsheet .reverso { background: #0F1112 url("https://raw.githubusercontent.com/orafahell/Reino-Reverso/main/assets/texturas/estatica-escura.jpg") repeat; color: #E6E7E3; border-color: #0F1112; }
.charsheet .reverso h3 { color: #4FB3A5; }
.charsheet .reverso small, .charsheet .reverso .campo > span, .charsheet .reverso .rot { color: #C9CCC8; }
.charsheet .reverso input[type="text"], .charsheet .reverso input[type="number"], .charsheet .reverso select, .charsheet .reverso textarea { background: #1A1D1E; color: #E6E7E3; border-color: #4FB3A5; }
.charsheet .reverso input[type="number"].caixa { border-color: #4FB3A5; }
.charsheet .reverso .calc { background: #1A1D1E; border-color: #6F7573; color: #E6E7E3; }
.charsheet .reverso button[type].rolar { border-bottom-color: #4FB3A5; }
.charsheet .reverso button[type].rolar.botao { background: #4FB3A5; border-color: #4FB3A5; color: #0F1112; }
.charsheet .reverso .gastar button[type="action"] { background: #1A1D1E; color: #E6E7E3; border-color: #4FB3A5; }
.charsheet .reverso .gastar button[type="action"]:hover { background: #4FB3A5; color: #0F1112; }
.charsheet .reverso .seta { background: #C9CCC8; }
.charsheet .reverso .seta::after { border-left-color: #C9CCC8; }
.charsheet .reverso .chip { border-color: #3A3F3D; }
.charsheet .reverso .recurso { border-top-color: #4FB3A5; }

.charsheet .humano { background: #0F1112; color: #E6E7E3; border-color: #0F1112; }
.charsheet .humano h3 { color: #F0A21C; }
.charsheet .humano small, .charsheet .humano .campo > span, .charsheet .humano .rot { color: #C9CCC8; }
.charsheet .humano input[type="text"], .charsheet .humano input[type="number"], .charsheet .humano select, .charsheet .humano textarea { background: #1A1D1E; color: #E6E7E3; border-color: #F0A21C; }
.charsheet .humano input[type="number"].caixa { border-color: #F0A21C; }
.charsheet .humano .calc { background: #1A1D1E; border-color: #6F7573; color: #E6E7E3; }
.charsheet .humano button[type].rolar { border-bottom-color: #F0A21C; }
.charsheet .humano button[type].rolar.botao { background: #F0A21C; border-color: #F0A21C; color: #0F1112; }
.charsheet .humano .gastar button[type="action"] { background: #1A1D1E; color: #E6E7E3; border-color: #F0A21C; }
.charsheet .humano .gastar button[type="action"]:hover { background: #F0A21C; color: #0F1112; }
.charsheet .humano .seta { background: #C9CCC8; }
.charsheet .humano .seta::after { border-left-color: #C9CCC8; }
.charsheet .humano .chip { border-color: #3A3F3D; }
.charsheet .humano .recurso { border-top-color: #F0A21C; }
.charsheet .reverso .tile, .charsheet .humano .tile { border-color: #3A3F3D; }
.charsheet .reverso .tile { background: rgba(15, 17, 18, 0.86); }
.charsheet .reverso .t-dica, .charsheet .humano .t-dica { color: #9BA19F; }
.charsheet .reverso .recurso-nome b { color: #4FB3A5; }
.charsheet .humano .recurso-nome b { color: #F0A21C; }
.charsheet .reverso .reacao-atr, .charsheet .humano .reacao-atr { border-color: #3A3F3D; }
.charsheet .humano .recurso { border-top-color: #F0A21C; }

/* ---------- atributos: primario, seta, secundarios ---------- */
.charsheet .atr { display: grid; grid-template-columns: 92px 14px minmax(0, 1fr); gap: 8px; align-items: center; padding: 8px 0; border-top: 1px solid #3A3F3D; }
.charsheet h3 + .atr, .charsheet .corpo-linhas .atr:first-child { border-top: 0; padding-top: 0; }
.charsheet .corpo-linhas .atr:last-child { padding-bottom: 0; }
.charsheet .atr-id { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
.charsheet .atr-id button[type].rolar { font-size: 15px; }
.charsheet .atr-caixa { display: flex; align-items: flex-end; gap: 6px; }
.charsheet .corpo-topo { display: grid; grid-template-columns: 132px minmax(0, 1fr); gap: 12px; align-items: stretch; padding-bottom: 8px; }
.charsheet .foto { position: relative; align-self: stretch; width: 132px; min-height: 176px; border: 2px solid #F0A21C; background: #1A1D1E; overflow: hidden; }
.charsheet .foto img { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; object-position: center top; border: 0; }
.charsheet .foto-vazio { position: absolute; left: 0; right: 0; top: 50%; margin-top: -7px; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #9BA19F; }
.charsheet .t-num { font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 600; white-space: nowrap; }
.charsheet .seta { position: relative; height: 1.5px; background: #0F1112; }
.charsheet .seta::after { content: ""; position: absolute; right: -1px; top: -4px; border: 4.5px solid rgba(0,0,0,0); border-left-color: #0F1112; border-right-width: 0; }
.charsheet .tiles { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.charsheet .tile { display: grid; grid-template-columns: minmax(0, 1fr); gap: 4px; align-content: start; padding: 6px 8px; border: 1px solid #9BA19F; min-width: 0; }
.charsheet .t-rot { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; }
.charsheet .t-rot button[type].rolar { font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; }
.charsheet .t-val { display: flex; align-items: center; gap: 5px; min-height: 28px; }
.charsheet .t-val i { font-style: normal; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
.charsheet .t-txt { font-size: 12px; font-weight: 600; line-height: 1.25; }
.charsheet .t-dica { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #4A4F4D; }
.charsheet .recurso { display: grid; grid-template-columns: 120px auto minmax(0, 1fr) minmax(0, 1fr); gap: 10px; align-items: stretch; border-top: 2px solid #0F1112; padding-top: 10px; margin-top: 2px; }
.charsheet .recurso.simples { display: flex; align-items: center; gap: 8px; border-top: 0; padding-top: 0; margin-top: 0; flex-wrap: wrap; }
.charsheet .recurso-nome { display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.charsheet .recurso-nome b { font-family: 'Doctor Glitch Acentos', 'Doctor Glitch', 'Archivo Black', Arial, sans-serif; font-weight: 400; font-size: 21px; line-height: 1; text-transform: uppercase; }
.charsheet .recurso-valor { display: flex; align-items: center; gap: 6px; }
.charsheet .hab-caminho .hc { display: none; font-size: 12px; }
.charsheet .uso { display: inline-flex; align-items: center; gap: 5px; margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 10px; text-transform: none; letter-spacing: 0; font-weight: 400; }
/*CAMINHO*/

/* ---------- pericias ---------- */
.charsheet .per { display: grid; grid-template-columns: minmax(0, 1fr) 16px 52px 40px 40px; gap: 6px; align-items: center; min-height: 28px; border-bottom: 1px solid #C9CCC8; }
.charsheet .per-cab { min-height: 18px; border-bottom: 1.5px solid #0F1112; font-family: 'IBM Plex Mono', monospace; font-size: 10px; text-transform: uppercase; color: #4A4F4D; }
.charsheet .per button[type].rolar { border-bottom: 0; justify-self: start; }
.charsheet .per-a { display: flex; align-items: center; }
.charsheet .mi { display: inline-block; width: 14px; height: 14px; overflow: hidden; vertical-align: -2px; font-family: 'Material Icons'; font-size: 14px; line-height: 1; font-weight: 400; font-style: normal;
  letter-spacing: normal; text-transform: none; white-space: nowrap; word-wrap: normal; direction: ltr; -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; color: #4A4F4D; }
.charsheet .per-total { display: flex; align-items: center; gap: 8px; margin-top: 8px; padding: 8px; border: 1.5px solid #0F1112; background: #FFFFFF; font-size: 13px; }
.charsheet .per-total small { margin-left: auto; text-align: right; }
.charsheet .per input[type="number"], .charsheet .per select { height: 22px; font-size: 12px; }

/* ---------- reacoes, ataques, condicoes ---------- */
.charsheet .rp { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0; }
.charsheet .rp-col { display: flex; flex-direction: column; gap: 8px; min-width: 0; padding-right: 14px; }
.charsheet .rp-col + .rp-col { padding: 0 0 0 14px; border-left: 1.5px solid #0F1112; }
.charsheet .rp-sub { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; font-weight: 600; font-size: 13px; }
.charsheet .reacoes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.charsheet .vez { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
.charsheet .reacao { display: grid; grid-template-rows: 34px 24px; gap: 4px; }
.charsheet .reacao button[type].rolar.botao { width: 100%; height: 34px; }
.charsheet .reacao-atr { display: flex; align-items: center; justify-content: center; gap: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; border: 1px solid #9BA19F; }
.charsheet .reacao-atr select { height: 22px; border: 0; font-size: 11px; background: none; }
.charsheet .protecao { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; align-items: end; }
.charsheet .atk-r { display: grid; grid-template-columns: 84px minmax(0, 2fr) minmax(0, 1fr) minmax(0, 1fr) 64px; gap: 10px; align-items: center; padding: 5px 0; border-bottom: 1px solid #C9CCC8; }
.charsheet .atk-r-cab { padding: 0 0 3px; border-bottom: 1.5px solid #0F1112; font-family: 'IBM Plex Mono', monospace; font-size: 10px; text-transform: uppercase; color: #4A4F4D; }
.charsheet .atk-r-nome { font-weight: 600; font-size: 14px; }
.charsheet .atk-r-val { font-family: 'IBM Plex Mono', monospace; }
.charsheet .resumo .repcontrol { display: none; }
.charsheet .atk, .charsheet .mag { display: grid; gap: 6px; align-items: end; padding: 6px 0; border-bottom: 1px solid #9BA19F; }
.charsheet .atk { grid-template-columns: 84px repeat(8, minmax(0, 1fr)); padding: 10px 0; }
.charsheet .atk > button[type].rolar.botao { grid-row: span 2; align-self: stretch; height: auto; }
.charsheet .atk .a-arma { grid-column: span 4; }
.charsheet .atk .a-per { grid-column: span 2; }
.charsheet .mag { grid-template-columns: 84px 2fr 1fr 1fr 1.1fr 1fr 1fr 1.1fr 1.1fr; }
.charsheet .mag textarea { grid-column: 1 / -1; }
.charsheet .c-check { align-items: center; }
.charsheet .c-check input { margin: 6px 0; }
.charsheet .conds-bloco { position: relative; }
.charsheet .conds-bloco h3 { display: flex; align-items: center; gap: 10px; margin-bottom: 0; }
.charsheet .cond-conta { margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0; text-transform: none; font-weight: 400; color: #4A4F4D; }
.charsheet .cond-seta { width: 20px; height: 20px; font-size: 20px; color: #0F1112; transition: transform 0.15s ease-out; }
.charsheet input[type="checkbox"].cond-abrir { position: absolute; top: 0; left: 0; z-index: 2; width: 100%; height: 40px; margin: 0; opacity: 0; cursor: pointer; }
.charsheet .cond-resumo { margin-top: 8px; padding: 6px 8px; background: #0F1112; color: #F0A21C; font-family: 'IBM Plex Mono', monospace; font-size: 11px; }
.charsheet .conds { display: none; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px 8px; margin-top: 10px; }
.charsheet .cond-abrir:checked ~ .conds { display: grid; }
.charsheet .cond-abrir:checked ~ h3 .cond-seta { transform: rotate(180deg); }
.charsheet .col > .conds-bloco { margin-top: 10px; }
.charsheet .rp-bloco { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
.charsheet .rp-bloco h3 { margin-bottom: 0; }
.charsheet .rp-item { margin-top: 6px; padding-top: 10px; border-top: 1.5px solid #0F1112; }
.charsheet .rp-bloco .protecao { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.charsheet .cond { display: flex; align-items: center; gap: 6px; margin: 0; font-size: 12px; font-weight: 400; color: #0F1112; cursor: pointer; }
.charsheet .cond span { padding: 2px 6px; color: #0F1112; border: 1px solid rgba(0,0,0,0); }
.charsheet .cond input:checked + span { background: #0F1112; color: #F0A21C; border-color: #0F1112; font-weight: 600; }

/* ---------- poderes ---------- */
.charsheet .esp { border-bottom: 2px solid #0F1112; padding: 6px 0 10px; }
.charsheet .esp-topo { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 10px; margin-bottom: 10px; align-items: start; }
.charsheet .c-passivo textarea { height: 64px; }
.charsheet .estagio { display: grid; grid-template-columns: 120px minmax(0, 1fr); gap: 4px 12px; padding: 10px 0; border-top: 1px solid #9BA19F; }
.charsheet .estagio-cab { grid-row: span 3; display: flex; flex-direction: column; gap: 2px; }
.charsheet .estagio-cab b { font-size: 14px; }
.charsheet .estagio-cab small { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #3A3F3D; }
.charsheet .opcoes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
.charsheet .opcoes input.op-nenhuma { display: none; }
.charsheet .op { position: relative; display: flex; margin: 0; min-width: 0; cursor: pointer; }
.charsheet .op input[type="radio"] { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; opacity: 0; cursor: pointer; }
.charsheet .op span { display: flex; align-items: center; width: 100%; min-height: 32px; padding: 5px 10px; border: 1px solid #0F1112; background: #FFFFFF; color: #0F1112; font-size: 12px; line-height: 16px; }
.charsheet .op input:checked + span { background: #0F1112; color: #F0A21C; font-weight: 600; }
.charsheet .op input:focus-visible + span { outline: 2px solid #F0A21C; outline-offset: 2px; }
.charsheet .estagio-topo { display: grid; grid-template-columns: minmax(0, 1fr) 150px 72px; gap: 6px; align-items: center; }
.charsheet .estagio textarea { height: 72px; }
.charsheet .traco { display: flex; flex-direction: column; gap: 6px; padding: 10px 0; border-bottom: 1px solid #9BA19F; }
.charsheet .traco-topo { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 64px; gap: 6px; align-items: start; }
.charsheet .traco textarea { height: 96px; }

/* ---------- inventario ---------- */
.charsheet .item { display: grid; grid-template-columns: minmax(0, 1fr) 70px 80px; gap: 6px; align-items: end; padding: 4px 0; border-bottom: 1px solid #C9CCC8; }
.charsheet .c-dinheiro { width: 140px; margin-top: 10px; }
.charsheet .aviso { display: none; background: #F0A21C; color: #0F1112; font-weight: 600; padding: 4px 8px; margin-bottom: 8px; font-size: 12px; }
/*CARGA*/

/* ---------- personagem ---------- */
.charsheet .trilha { display: grid; grid-template-columns: repeat(11, minmax(0, 1fr)); gap: 4px; }
.charsheet .lv { border: 1.5px solid #0F1112; padding: 5px; min-height: 104px; display: flex; flex-direction: column; gap: 3px; }
.charsheet .lv b { font-family: 'IBM Plex Mono', monospace; font-size: 15px; }
.charsheet .lv small { font-family: 'IBM Plex Sans', Arial, sans-serif; font-size: 10px; line-height: 1.2; color: inherit; }
.charsheet .lv-3, .charsheet .lv-6, .charsheet .lv-9 { border-bottom: 6px solid #1F6F6B; }
/*NIVEL*/
.charsheet .esvaecer { display: flex; align-items: flex-end; gap: 8px; margin-top: 10px; }
.charsheet .esvaecer .campo { width: 64px; }
.charsheet .ajustes { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }

/* ---------- secoes repetiveis ---------- */
.charsheet .repcontrol { margin-top: 6px; }
.charsheet .repcontrol .btn { border-radius: 0; background: #FFFFFF; border: 1px solid #0F1112; color: #0F1112; text-shadow: none; box-shadow: none; font-size: 11px; }
.charsheet .repcontainer .repitem { margin: 0; }

@media only screen and (max-width: 820px) {
  .charsheet .duas, .charsheet .duas.iguais { grid-template-columns: minmax(0, 1fr); }
  .charsheet .topo { flex-wrap: wrap; }
}

/* ---------- cartao no chat ---------- */
.sheet-rolltemplate-rr .sheet-rr { border: 2px solid #0F1112; background: #E6E7E3; color: #0F1112; font-family: 'IBM Plex Sans', Arial, sans-serif; font-size: 13px; }
.sheet-rolltemplate-rr .sheet-rr-topo { background-color: #0F1112; background-image: repeating-linear-gradient(0deg, rgba(255,255,255,0.05) 0, rgba(255,255,255,0.05) 1px, rgba(0,0,0,0) 1px, rgba(0,0,0,0) 3px); color: #E6E7E3; padding: 6px 8px; border-bottom: 3px solid #F0A21C; }
.sheet-rolltemplate-rr .sheet-rr-titulo { font-family: 'Archivo Black', Arial, sans-serif; font-size: 16px; text-transform: uppercase; line-height: 1.15; }
.sheet-rolltemplate-rr .sheet-rr-sub { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #C9CCC8; }
.sheet-rolltemplate-rr .sheet-rr-linha { display: flex; justify-content: space-between; align-items: center; padding: 5px 8px; border-bottom: 1px solid #C9CCC8; }
.sheet-rolltemplate-rr .sheet-rr-valor { font-family: 'IBM Plex Mono', monospace; font-size: 16px; font-weight: 600; }
.sheet-rolltemplate-rr .sheet-rr-valor .inlinerollresult { background: #FFFFFF; border: 1.5px solid #0F1112; padding: 1px 6px; font-size: 16px; }
.sheet-rolltemplate-rr .sheet-rr-valor .inlinerollresult.fullcrit { border-color: #1F6F6B; color: #1F6F6B; }
.sheet-rolltemplate-rr .sheet-rr-valor .inlinerollresult.fullfail { border-color: #0F1112; background: #F0A21C; }
.sheet-rolltemplate-rr .sheet-rr-selo { padding: 4px 8px; font-family: 'Archivo Black', Arial, sans-serif; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
.sheet-rolltemplate-rr .sheet-rr-bom { background: #1F6F6B; color: #FFFFFF; }
.sheet-rolltemplate-rr .sheet-rr-ruim { background: #F0A21C; color: #0F1112; }
.sheet-rolltemplate-rr .sheet-rr-fdv { background: #0F1112; color: #F0A21C; border-left: 6px solid #F0A21C; }
.sheet-rolltemplate-rr .sheet-rr-reverso { background: #0F1112; color: #4FB3A5; }
.sheet-rolltemplate-rr .sheet-rr-nota { padding: 4px 8px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #4A4F4D; border-bottom: 1px solid #C9CCC8; }
.sheet-rolltemplate-rr .sheet-rr-modo { padding: 4px 8px; background: #F0A21C; color: #0F1112; font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.sheet-rolltemplate-rr .sheet-rr-atr span + span { font-family: 'IBM Plex Mono', monospace; font-size: 12px; font-weight: 600; }
.sheet-rolltemplate-rr .sheet-rr-texto { padding: 6px 8px; font-size: 12px; }
"""

# ---------- camada de sistema: tokens, tipografia, espaco e acessibilidade ----------
TOKENS = [  # (hex, token) — paleta do moodboard e tons de apoio
    ("#0F1112", "--rr-asfalto"), ("#1F1F1F", "--rr-fundo"), ("#E6E7E3", "--rr-papel"), ("#FFFFFF", "--rr-branco"),
    ("#F0A21C", "--rr-sodio"), ("#4FB3A5", "--rr-verdete"), ("#1F6F6B", "--rr-verdete-escuro"),
    ("#4A4F4D", "--rr-texto-suave"), ("#C9CCC8", "--rr-texto-suave-escuro"), ("#9BA19F", "--rr-linha"),
    ("#3A3F3D", "--rr-linha-escura"), ("#6F7573", "--rr-concreto"), ("#1A1D1E", "--rr-campo-escuro"),
    ("#D9DBD6", "--rr-calculado"), ("#B9BDB8", "--rr-aba"), ("#D5D7D2", "--rr-aba-hover"),
]

SISTEMA = """
/* =================== SISTEMA (tokens · tipografia · espacos · acessibilidade) =================== */
.charsheet {
""" + "\n".join("  %s: %s;" % (t, h) for h, t in TOKENS) + """
  --rr-e1: 4px; --rr-e2: 8px; --rr-e3: 12px; --rr-e4: 16px;
  --rr-t-micro: 11px; --rr-t-peq: 12px; --rr-t-corpo: 13px; --rr-t-titulo: 18px; --rr-t-num: 20px; --rr-t-display: 26px;
  --rr-foco: 0 0 0 2px var(--rr-sodio);
}
/* hierarquia: titulo de secao > rotulo > dica */
.charsheet h3 { font-size: var(--rr-t-titulo); margin-bottom: var(--rr-e3); }
.charsheet h3.h-glitch { font-size: var(--rr-t-display); }
.charsheet small, .charsheet .t-dica, .charsheet .dica { font-size: var(--rr-t-micro); line-height: 1.35; }
.charsheet .campo > span, .charsheet .rot, .charsheet .t-rot { letter-spacing: 0.04em; }
/* espacos em escala de 4 */
.charsheet .bloco { padding: var(--rr-e3); margin-bottom: var(--rr-e3); }
.charsheet .duas, .charsheet .par, .charsheet .col { gap: var(--rr-e3); }
.charsheet .duas { margin-bottom: var(--rr-e3); }
.charsheet .pagina { padding: var(--rr-e3) var(--rr-e3) 0; }
/* contraste: rotulos do topo e separadores */
.charsheet .topo .campo > span { color: var(--rr-linha); }
.charsheet .barra { color: var(--rr-texto-suave); }
.charsheet .humano .barra, .charsheet .reverso .barra { color: var(--rr-linha); }
/* foco visivel em fundo claro e escuro: anel duplo asfalto + sodio */
.charsheet input:focus, .charsheet select:focus, .charsheet textarea:focus { outline: 0; }
.charsheet input:focus-visible, .charsheet select:focus-visible, .charsheet textarea:focus-visible, .charsheet button:focus-visible {
  outline: 2px solid var(--rr-asfalto); outline-offset: 2px; box-shadow: var(--rr-foco); }
.charsheet .humano :focus-visible, .charsheet .reverso :focus-visible, .charsheet .topo :focus-visible { outline-color: var(--rr-branco); }
.charsheet .cond-abrir:focus-visible ~ h3 { outline: 2px solid var(--rr-asfalto); outline-offset: 2px; box-shadow: var(--rr-foco); }
/* alvos de clique: minimo de 24 px (WCAG 2.5.8) */
.charsheet button[type].rolar { min-height: 24px; display: inline-flex; align-items: center; }
.charsheet button[type].rolar.botao { justify-content: center; min-height: 28px; }
.charsheet input[type="checkbox"] { width: 16px; height: 16px; }
.charsheet .uso, .charsheet .cond { min-height: 24px; }
/* titulos de aba e de card na fonte do logo (versao com acentos) */
.charsheet .abas button[type="action"].aba { font-family: 'Doctor Glitch Acentos', 'Archivo Black', Arial, sans-serif; font-size: 15px; letter-spacing: 0.02em; line-height: 1; }
.charsheet h3 { font-family: 'Doctor Glitch Acentos', 'Archivo Black', Arial, sans-serif; font-size: 18px; letter-spacing: 0.01em; line-height: 1.05; align-items: center; }
.charsheet h3 small, .charsheet h3 .uso, .charsheet h3 .cond-conta { font-family: 'IBM Plex Mono', monospace; letter-spacing: 0; }
.charsheet h3.h-glitch { font-size: var(--rr-t-display); }
.charsheet .par h3 { flex-direction: column; align-items: flex-start; gap: 4px; }
/* especializacoes: cabecalho recolhivel, vaga por nivel e etapas travadas */
.charsheet .esp { position: relative; padding: 0 0 12px; }
.charsheet input[type="checkbox"].esp-fechar { position: absolute; top: 0; left: 0; z-index: 2; width: 100%; height: 40px; margin: 0; opacity: 0; cursor: pointer; }
.charsheet .esp-cab { display: flex; align-items: center; gap: 10px; min-height: 40px; padding: 0 8px; background: var(--rr-asfalto); color: var(--rr-papel); }
.charsheet .esp-nome { font-family: 'Doctor Glitch Acentos', 'Archivo Black', Arial, sans-serif; font-weight: 400; font-size: 17px; color: var(--rr-sodio); white-space: nowrap; }
.charsheet .esp-resumo { flex: 1; min-width: 0; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--rr-texto-suave-escuro); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.charsheet .esp-grad { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--rr-texto-suave-escuro); white-space: nowrap; }
.charsheet .esp-seta { width: 20px; height: 20px; font-size: 20px; color: var(--rr-papel); transition: transform 0.15s ease-out; }
.charsheet .esp-fechar:checked ~ .esp-cab .esp-seta { transform: rotate(180deg); }
.charsheet .esp-fechar:checked ~ .esp-corpo { display: none; }
.charsheet .esp-fechar:focus-visible ~ .esp-cab { outline: 2px solid var(--rr-asfalto); outline-offset: 2px; box-shadow: var(--rr-foco); }
.charsheet .esp-corpo { padding-top: 10px; }
.charsheet .esp-aviso { display: none; margin-top: 6px; padding: 6px 8px; border-left: 4px solid var(--rr-sodio); background: var(--rr-branco); font-size: 12px; }
.charsheet .esp-vaga[value="0"] ~ .esp-aviso { display: block; }
.charsheet .estagio-trava { display: none; grid-column: 2; align-items: center; gap: 6px; padding: 6px 8px; border: 1px dashed var(--rr-texto-suave); font-size: 12px; color: var(--rr-texto-suave); }
.charsheet .estagio-trava .mi { color: var(--rr-texto-suave); }
.charsheet .hc-acoes { display: inline-flex; align-items: center; gap: 10px; }
.charsheet .hc-acoes button[type].rolar.botao { font-family: 'Archivo Black', Arial, sans-serif; }
/*TRAVAS*/
/* atributos condensados: Forca e Agilidade ocupam a altura da foto 3x4 (132 x 176) */
.charsheet .atr { grid-template-columns: 76px 12px minmax(0, 1fr); gap: 8px; padding: 6px 0; }
.charsheet .atr-id { gap: 2px; }
.charsheet .atr-id button[type].rolar { min-height: 22px; font-size: 14px; }
.charsheet input[type="number"].caixa { width: 52px; height: 40px; font-size: 19px; }
.charsheet .tiles { gap: 6px; }
.charsheet .tile { gap: 2px; padding: 4px 8px; }
.charsheet .corpo-linhas .t-rot button[type].rolar { min-height: 18px; }
.charsheet .t-val { min-height: 24px; gap: 4px; }
.charsheet .tile .calc { height: 24px; min-width: 34px; }
.charsheet .tile input[type="number"].mini { height: 24px; }
.charsheet .t-dica { line-height: 1.2; }
.charsheet .corpo-linhas .t-dica { white-space: nowrap; }
.charsheet .t-txt { font-size: 12px; line-height: 1.2; }
.charsheet .corpo-topo { align-items: start; padding-bottom: 6px; }
.charsheet .corpo-topo { grid-template-columns: 156px minmax(0, 1fr); }
.charsheet .corpo-topo { align-items: stretch; }
.charsheet .foto { align-self: stretch; width: 156px; height: auto; min-height: 208px; }
.charsheet .corpo-linhas { display: flex; flex-direction: column; justify-content: space-between; min-height: 208px; }
.charsheet .corpo-linhas .atr { padding: 0; }
.charsheet .corpo-linhas .atr + .atr { padding-top: 4px; }
.charsheet .corpo-linhas .tile { padding: 3px 8px; }
.charsheet .tile.largo { grid-column: 1 / -1; }
.charsheet .corpo-linhas .tile.largo .t-dica { white-space: normal; }
/* texto so para leitor de tela */
.charsheet .gastar { gap: 3px; }
.charsheet .gastar button[type="action"] { min-width: 26px; padding: 0 3px; }
.charsheet .sr { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
"""


def travas_css():
    sels_t, sels_b = [], []
    for lib in range(0, 4):
        for n in range(lib + 1, 5):
            base = '.charsheet .esp-lib[value="%d"] ~ .esp-corpo .estagio-%d' % (lib, n)
            sels_t.append(base + " .estagio-trava")
            sels_b.append(base + " .opcoes, " + base + " .estagio-topo, " + base + " textarea")
    return (",\n".join(sels_t) + " { display: flex; }\n" + ",\n".join(sels_b) + " { display: none; }\n"
            + ",\n".join('.charsheet .esp-lib[value="%d"] ~ .esp-corpo .estagio-%d .estagio-cab' % (lib, n) for lib in range(0, 4) for n in range(lib + 1, 5))
            + " { opacity: 0.55; }")


def tokens_css(c):
    i = c.index("/* ---------- cartao no chat")
    folha, chat = c[:i], c[i:]
    corpo_ini = folha.index(".charsheet {")
    cab, corpo = folha[:corpo_ini], folha[corpo_ini:]
    for hx, tk in TOKENS:
        corpo = re.sub(re.escape(hx) + r"\b", "var(%s)" % tk, corpo, flags=re.I)
    corpo = corpo.replace("font-size: 10px", "font-size: var(--rr-t-micro)")
    chat = chat.replace("font-size: 10px", "font-size: 11px")
    chat = chat.replace(".sheet-rolltemplate-rr .sheet-rr-texto { padding: 6px 8px; font-size: 12px; }",
                        ".sheet-rolltemplate-rr .sheet-rr-texto { padding: 6px 8px; font-size: 13px; line-height: 1.4; }\n.sheet-rolltemplate-rr .sheet-rr-par + .sheet-rr-par { padding-top: 0; }")
    # o cartao do chat vai logo depois das fontes: assim nenhuma regra da ficha mais abaixo pode afetar o chat
    return cab + chat + "\n" + corpo + SISTEMA.replace("/*TRAVAS*/", travas_css())


def acessivel_html(h):
    # rotulo visivel ligado ao campo por nome acessivel (title)
    h = re.sub(r'(<label class="rot">([^<]+)</label>\s*<(?:textarea|input)(?![^>]*title=))', lambda m: m.group(1) + ' title="%s"' % m.group(2).strip(), h)
    extras = {"attr_morrendo_chance": "Chance de morrer por rodada (%)", "attr_fdv_max": "Força de Vontade máxima",
              "attr_objetos_poder": "Objetos de Poder", "attr_aliados": "Local seguro e aliados", "attr_anotacoes": "Anotações",
              "attr_idiomas": "Idiomas"}
    for nome, t in extras.items():
        h = re.sub(r'(<(?:input|textarea)(?![^>]*title=)[^>]*name="%s")' % nome, r'\1 title="%s"' % t, h)
    # icones de ligadura: escondidos do leitor de tela, com texto equivalente
    h = h.replace('<span class="mi" title="Sofre a penalidade do item de proteção">shield</span>',
                  '<span class="mi" aria-hidden="true" title="Sofre a penalidade do item de proteção">shield</span><span class="sr">sofre penalidade de proteção</span>')
    h = re.sub(r'<span class="mi(?: [^"]*)?"(?![^>]*aria-hidden)', lambda m: m.group(0) + ' aria-hidden="true"', h)
    h = h.replace('<span class="barra">', '<span class="barra" aria-hidden="true">')
    h = h.replace('<span class="marca-logo" title="Reino Reverso">', '<span class="marca-logo" role="img" aria-label="Reino Reverso">')
    h = h.replace('<div class="pagina ', '<div lang="pt-BR" class="pagina ').replace('<div class="topo">', '<div lang="pt-BR" class="topo">')
    h = h.replace('<div class="abas">', '<div class="abas" role="group" aria-label="Abas da ficha">')
    h = h.replace('class="cond-abrir" name="attr_cond_aberto" value="1" title="Abrir ou fechar a lista de condições"',
                  'class="cond-abrir" name="attr_cond_aberto" value="1" title="Abrir ou fechar a lista de condições" aria-label="Mostrar todas as condições"')
    return h


if __name__ == "__main__":
    import json
    h = html()
    atk = ROLAGENS.pop("__atk")
    h = h.replace("/*VERSAO*/", VERSAO)
    h = "<!-- Reino Reverso · ficha Roll20 v" + VERSAO + " -->\n" + h
    h = h.replace("/*ATRS*/", json.dumps({k: [n, ab] for k, n, ab in ATRS}, ensure_ascii=False))
    h = h.replace("/*PERGRAD*/", json.dumps({n: "grad_" + k for k, n, _, _ in PERICIAS}, ensure_ascii=False))
    h = h.replace("/*CAMINHOS*/", json.dumps({
        "investigador": ["Mente Analítica", "Investigador", "Uma vez por cena, ao falhar em Conhecimento, Ciência Forense, Obter Informações ou Percepção, você obtém uma pista parcial."],
        "ocultista": ["Arcana Pessoal", "Ocultista", "Uma magia de Ciclo I desde o nível 1, usável Intelecto + 1 vezes por dia."],
        "sobrevivente": ["Instinto de Sobrevivência", "Sobrevivente", "Uma vez por cena, quando um ataque ou efeito reduziria seus PV a 0, você fica com 1 PV."]}, ensure_ascii=False))
    h = h.replace("/*LIVRO*/", json.dumps(LIVRO_JS, ensure_ascii=False))
    h = h.replace("/*CONDS*/", json.dumps(CONDICOES, ensure_ascii=False))
    h = h.replace("/*GRADS*/", json.dumps(["grad_" + k for k, _, _, _ in PERICIAS]))
    h = h.replace("/*ROLAGENS*/", json.dumps(ROLAGENS, ensure_ascii=False, indent=1)).replace("/*ATAQUE*/", json.dumps(atk, ensure_ascii=False))
    c = tokens_css(css())
    h = acessivel_html(h)
    # palavras bloqueadas pelo filtro de seguranca do Roll20
    import re
    for nome, txt in (("html", h), ("css", c)):
        for ruim in ("data:", "eval", "cookie", "window", "expression", "behavior", "behaviour", "moz-binding"):
            assert ruim not in txt.lower(), (nome, ruim)
        assert not re.search(r"\b(this|parent)\b", txt), nome
    open(os.path.join(OUT, "html_Reino_Reverso.html"), "w", encoding="utf-8").write(h)
    open(os.path.join(OUT, "css_Reino_Reverso.css"), "w", encoding="utf-8").write(c)
    print(len(h), len(c))
