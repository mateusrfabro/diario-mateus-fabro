# Site profissional — nova pele sobre o mesmo gerador

**Data:** 05/11/2026 · **Decisões do Mateus:** retificações/atos saem da home para `/licoes`; visual limpo, claro, corporativo, sem metáfora de diário; a home fala primeiro com gestor/recrutador de vaga de dados. Modo discreto continua valendo.

## O que muda
- `build.py`: nova `pagina()` (home) e nova `pagina_licoes()`; novo `CSS`; `T` sem vocabulário de diário ("Editais", "Edição nº", "Convocação", "Ler como máquina", "RETIFICAÇÃO" na home). JSON-LD, `index.md`, `llms*.txt`, `resume.json`, MCP e `app.js` (WebMCP) continuam; `<script id="dados">` permanece (invisível).
- Home, nesta ordem: hero (nome, `perfil.cargo`, `perfil.frase_hero`, botões Currículo (PDF) e E-mail, linha Londrina · remoto · GitHub · LinkedIn) → prova (`numeros`, com "medidos em") → 3 pilares (`pilares`: Dados · Produto · Agentes de IA, texto sem dígito) → experiência (`experiencia` + `igaming-dados.fatos` no item atual) + formação → projetos (cards: nome, linha, status com bolinha, stack em chips, link; `avisa-edital` primeiro) → stack (`curriculo.json.stack`) → como trabalho (`metodo` + link "N lições de casos reais →") → contato → rodapé com links para máquinas.
- `/licoes/` (`public/licoes/index.html` e `en/licoes/index.html`): retificações (onde se lê / leia-se / regra) e atos, mesmo visual.
- Capa OG nova: nome, cargo, frase, site (sem retificação). `gerar_og.descritor` muda; `og.json` regerado.
- Kit e README: "retificações dos meus erros" → "lições de casos reais"; FAQ "O que são as retificações" → "O que são as lições".
- Dados novos em `dados.json`/`dados.en.json`: `perfil.frase_hero` (1 frase), `pilares` (3 × {titulo, texto}); `site.titulo` = "Mateus Fabro — Engenheiro de Dados & Analytics"; `site.descricao` sem "retificações".
- Testes: remover os de carimbo/edição/pre#maquina; adicionar: home tem h1 único com o nome, dois CTAs (href do PDF e mailto), 5 números, 3 pilares, seção de experiência com o empregador, cards com todos os `projetos`, link para `/licoes/`; `/licoes/` tem todas as retificações; capa em dia; denylist; paridade PT/EN mantida; modo discreto mantido.

## Fora de escopo
Mudar dados/fatos (exceto os campos novos); mudar `recontar.py`; trocar fontes externas (CSP `style-src 'self'`: fonte de sistema ou woff2 próprio).

## Aceite
`pytest -q` verde; render a 412 px e 1280 px revisado por `ux-review`; `curl` do site no ar sem "Diário", "Edição", "RETIFICAÇÃO" na home; `/licoes/` 200; `resume.json`/`llms.txt`/`/mcp` iguais em conteúdo.
