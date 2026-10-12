# Ficha Roll20 · Reino Reverso — histórico de versões

Versão no formato `MAIOR.MENOR.CORREÇÃO`:
- **MAIOR** muda quando a ficha deixa de ser compatível com personagens já criados (campos renomeados ou removidos).
- **MENOR** sobe a cada rodada de ajustes (layout, recursos novos).
- **CORREÇÃO** sobe quando só conserta algo que quebrou.

Cada versão entregue fica congelada em `versoes/vX.Y.Z/` (HTML e CSS prontos para colar). Para voltar a uma versão, copie os dois arquivos da pasta dela para o Roll20. O código-fonte de cada versão está no commit correspondente do histórico.

## 1.0.0 — 12/10/2026 · linha de base

Primeira versão registrada. Reúne tudo o que foi construído até aqui:

- **Estrutura:** abas Em jogo, Combate, Poderes, Personagem, Inventário e Ajustes; topo com identificação, modo do dado (normal, vantagem, desvantagem), modificador e rolagem pública ou só para o Narrador.
- **Em jogo:** Corpo com foto 3×4 e Força, Agilidade e Vitalidade alinhadas à altura da foto; Vida e Morrendo; Mente com Carisma, Intelecto e Sanidade; Habilidade e Força de Vontade; Condições em lista recolhível; Perícias com total de graduações; Reações e item de proteção na coluna direita; resumo de Ataques.
- **Regras do livro 0.9.9.1:** atributos derivados, PV/PS/PH por Caminho, graduação máxima por nível, custo e DT de magia, carga, evolução por nível.
- **Força de Vontade:** +1 automático no 20 natural (respeita vantagem e desvantagem), com aviso no chat.
- **Poderes:** textos completos do livro para 74 vantagens, 54 desvantagens e 20 especializações; especializações recolhíveis, com etapas liberadas por graduação (2, 4, 6, 8) e vagas por nível (1, 5, 10); Habilidade de Caminho enviada ao chat.
- **Chat:** card próprio com título, modo do dado, atributo usado, resultado, decisivo/falha e textos em parágrafos.
- **Visual e acessibilidade:** tokens de cor, escala tipográfica e de espaços; Doctor Glitch com acentos em abas e títulos; zero violações automáticas de WCAG 2.2 AA (axe-core) na data.
