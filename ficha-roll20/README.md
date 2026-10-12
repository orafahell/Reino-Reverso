# Ficha Roll20 · Reino Reverso

Ficha de personagem para o Roll20 (Custom Sheet, **Legacy Sanitization desligado**), baseada no livro 0.9.9.1.

## Instalar ou atualizar no Roll20
1. Configurações do jogo → Character Sheet Template → Custom.
2. Cole `html_Reino_Reverso.html` na aba HTML e `css_Reino_Reverso.css` na aba CSS. Salve.
3. Recarregue a mesa. A versão aparece no topo da ficha, ao lado de "Ficha de personagem".

Fontes e imagens vêm da branch `main` deste repositório (`Doctor Glitch.otf`, `DoctorGlitch-Acentos-teste.ttf` e `assets/`).

## Gerar a ficha a partir do código
Os dois arquivos acima são gerados — não edite à mão.

```
python3 build.py          # gera html_ e css_Reino_Reverso
node test_worker.js       # simula o script da ficha (rolagens, preenchimentos, travas)
```

- `build.py` — fonte única de HTML, CSS, script da ficha e card do chat. A constante `VERSAO` define o número exibido.
- `textos/` — extração dos textos do livro (`extrai.py` → `parse.py` → `gera.py` → `livro.json`).
- `ferramentas/` — render de prévia (`shot.py`), auditoria de acessibilidade (`audit.py`, precisa de `npm install`) e varredura de contraste (`contraste.py`). Use Playwright com Chromium.
- `fonte/acentos.py` — prova de conceito que adiciona acentos à Doctor Glitch.

## Fluxo de versão
1. Cada rodada de ajustes vira uma branch e um PR.
2. Subir `VERSAO` em `build.py`, registrar no `CHANGELOG.md` e gerar a ficha.
3. Ao entregar, criar a tag `ficha-vX.Y.Z`.
