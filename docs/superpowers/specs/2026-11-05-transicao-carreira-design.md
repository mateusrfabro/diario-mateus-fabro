# Transição de carreira — currículo, LinkedIn, site e GitHub a partir de uma fonte única

**Data:** 05/11/2026 · **Dono:** Mateus Fabro · **Repositório-hub:** `C:\Users\mateu\Projects\portfolio`
(remoto `mateusrfabro/diario-mateus-fabro`; site mateusfabro.vercel.app). Neste documento, "portfolio" e
"diario-mateus-fabro" são o mesmo repositório.

**Revisão 3 (05/11/2026):** três rodadas de revisão. Este documento **não contém nenhum termo da denylist**
(nome de pessoa, cliente, sócio, afiliado, vocabulário do projeto sob NDA, e-mail corporativo): ele mora num repositório
que vai abrir e é varrido pelo mesmo teste que protege o site. Os termos concretos vivem **só** no arquivo local
descrito em U0. A execução se divide em **dois planos**: Plano A (peças geradas, U0–U5 e U7) e Plano B (estado dos
repositórios, U6). A abertura de repositórios no Plano A depende do relatório do Plano B.

## 1. Contexto e objetivo

A Super Nova Gaming (MultiBet, Play4Tune) encerrou a operação em novembro de 2026. O contrato era a renda fixa.
Objetivo: em uma rodada de trabalho, deixar as quatro peças públicas do perfil profissional **verdadeiras,
consistentes entre si e prontas para a busca de vaga** (PJ ou CLT, remoto, via LinkedIn e rede de contatos):

1. **Currículo** PT e EN (PDF e HTML).
2. **Kit LinkedIn** (título, Sobre, experiência, formação, projetos, post de disponibilidade) para colar à mão.
3. **Site** mateusfabro.vercel.app (PT/EN, `resume.json`, `llms.txt`, MCP), republicado uma vez.
4. **GitHub**: perfil público com README, repositórios próprios abertos após varredura, e **todos** os repositórios
   em estado "posso compartilhar a tela agora".

Estado de partida (medido em 05/11/2026): currículo v4 de 10/08/2026 diz "Out/2025 – atual" e só cita Anhembi Morumbi
"em curso"; o site diz "Grupo de iGaming (nome omitido)" e tem números de 23/09; o GitHub tem 24 repositórios (lista
em `gh repo list mateusrfabro`), todos privados, sem nome, bio nem README de perfil; dois testes do site falham porque
o arquivo `C:\Users\mateu\Projects\portfolio-denylist.txt` **não existe** nesta máquina (ficou no notebook anterior).

## 2. Decisões já tomadas (05/11/2026, com o Mateus)

| Tema | Decisão |
|---|---|
| Posicionamento | **Um** título que junta as duas frentes. No `perfil`: `cargo` = *Engenheiro de Dados & Analytics* (curto: cabe em `<title>`, `og:title`, JSON-LD `jobTitle`, `resume.json.label` e na capa OG 1200×630) e `subtitulo` = *Construo o pipeline e o produto em volta dele — Python · SQL · TypeScript*. Não há campo novo. A tese: entregar o dado até virar aviso, painel ou produto com cliente real. Sem claim de liderança: membro do squad (correção do Mateus em 05/11). |
| Empregador | Nomeado em **todas** as peças: *Super Nova Gaming / MultiBet (Grupo PGX)*, **Out/2025 – Nov/2026**, cargo *Analista de Dados*, motivo de saída *encerramento da operação*. Tudo que hoje diz "trabalho atual" vai para o passado: `igaming-dados.status`, `numeros[3].fonte`, `perfil.resumo[0]`, FAQ. |
| Formação | `perfil.formacao` muda de **string para lista** de 2 objetos `{curso, instituicao, inicio, fim, status}`: *Administração — Universidade Anhembi Morumbi, 2022–2025, concluído* e *Ciências Contábeis — UEL, 2018–2021, incompleto*. Mesma mudança em `dados.en.json`. |
| GitHub: abrir | `diario-mateus-fabro`, `dumpai`, `lab-ia`, `secretaria-ia`, `poolcompras`, `nous-clinical` — só após varredura de segredos no histórico completo (Plano B) e OK final do Mateus na lista. |
| GitHub: privados, mas 100% apresentáveis | `cafesaas`, `avisa-edital`, `avisa-pedidos`, `credito-saas`, `flashmed`, os 5 portais Astro (`central-do-trabalhador`, `guiadocredito`, `radardoinvestidor`, `mydollarpilot`, `usmoneybrasil`) e os 8 repositórios de trabalho. Total 6 + 10 + 8 = 24 (conferido em `gh repo list` na revisão do Plano B). O remoto do clone local `MultiBet` (`multibet-analytics`) foi **transferido para a organização da empresa** no GitHub: não é do Mateus e fica fora de qualquer ação. "Apresentável" está definido em U6. |
| credito-saas | Entra em todas as peças **mascarado**: nome genérico *SaaS multi-tenant de gestão de crédito (sob NDA)*, só stack e práticas técnicas. O vocabulário do domínio, o nome e a cidade do grupo, sócio e cliente ficam na **denylist** (fora do repo). Não existe lista de mascaramento versionada. |
| Telefone | **Não entra em nada versionado.** O site, o `resume.json`, o kit e o currículo publicado em `public/curriculo/` levam e-mail, LinkedIn, GitHub e site. O telefone só aparece na cópia local do currículo gerada com `--privado`, que lê `C:\Users\mateu\Projects\portfolio-privado.json` (fora do repo, como a denylist) e grava **apenas** em `OneDrive - PGX/7. Projetos Pessoais/`. |
| Disponibilidade | *Em busca de vaga (PJ ou CLT, remoto). Converso também sobre projeto fechado.* |
| Fonte única | Fatos (datas, nomes, números, formação, experiências, projetos) moram em `conteudo/dados.json` e `dados.en.json`. Prosa específica do currículo mora em `conteudo/curriculo.json`. Nenhum número é digitado em duas peças. |

## 3. Arquitetura: uma fonte, cinco saídas

```
conteudo/dados.json ──┬── build.py ──────────► public/ (site PT/EN, resume.json, llms*.txt, projetos/*.md)
conteudo/dados.en.json│                        api/mcp.py lê o mesmo JSON
conteudo/curriculo.json (prosa do CV) ─┐
                      ├── scripts/gerar_pecas.py curriculo ──► public/curriculo/mateus-fabro-{pt,en}.{html,pdf}
                      │                        (--privado: + telefone, só para OneDrive)
                      ├── scripts/gerar_pecas.py linkedin  ──► docs/linkedin/kit-2026-11-{pt,en}.md
                      └── scripts/gerar_pecas.py github    ──► docs/github/README.md (copiado para o repo de perfil)
scripts/recontar.py ── reconta commits/testes nos repos locais e grava em dados*.json (contrato de REPOS muda, U1)
fora do repo (C:\Users\mateu\Projects\): portfolio-denylist.txt · portfolio-privado.json · _fora-do-git\ (relatórios e cópias)
```

### U0 — Pré-requisitos locais (tarefa, não fato)
- Criar `C:\Users\mateu\Projects\portfolio-denylist.txt` (≥ 10 termos; **categorias** na seção 4; os termos em si só
  lá). Nomes de pessoa entram **completos** (nome e sobrenome), porque termo de 5 letras casa como substring.
- Criar `C:\Users\mateu\Projects\portfolio-privado.json` com `{"telefone": "..."}`.
- `git config user.email mateusrfabro@hotmail.com` no repo (feito em 05/11) e `git config core.hooksPath scripts/hooks`
  para o pré-commit voltar a rodar.
- Criar o branch local `master` a partir de `origin/master` (hoje só existe `migracao-2026-09-28` localmente).
- Histórico: os commits desta spec existem só localmente (nunca foram enviados); antes de qualquer push, eles são
  refeitos como **um** commit sem termo proibido. Isso não é reescrita de história publicada.
- Aceite: `pytest -q` do portfolio verde (40 testes) com a denylist presente, **antes** de qualquer mudança de conteúdo.

### U1 — Dados (`conteudo/dados.json`, `dados.en.json`, `conteudo/curriculo.json`)
- **Faz:** guarda todo fato publicável.
  - `perfil.cargo`, `perfil.subtitulo`, `perfil.formacao` (lista), `perfil.resumo` reescritos (seção 2).
  - **Novo** `experiencia`: lista de 3 objetos `{id, empresa, cargo, inicio, fim, local, resumo, nota?}` — `super-nova`
    (2025-10 → 2026-11), `costa-oeste` (2025-07 → 2025-09), `adama` (2020-10 → 2024-09; `nota`: "estágio 2019–2020").
    É a **única** fonte de empregador/datas; `resume.json.work` passa a sair daqui (hoje é hardcoded em `build.py`):
    `summary` = `resumo`; `highlights` só no `super-nova`, vindos de `igaming-dados.fatos`.
  - `conteudo/curriculo.json`: **só prosa do currículo**, chaveada por `experiencia.id` (bullets por bloco: dados &
    plataforma, sistemas, antifraude & ML, IA aplicada; 1–2 bullets para as anteriores) e a tabela de stack, em PT e EN.
    Não contém datas nem nomes de empresa. Cada bullet é `{"texto": ..., "fonte": ...}`: **um bullet que cita número
    tem `fonte` obrigatória e não vazia** (o repositório, o script ou o relatório de onde o número saiu); bullet sem
    dígito pode ter `fonte` vazia. **Exceção explícita:** versão de tecnologia na tabela `stack` ("Next.js 16",
    "PostgreSQL 15") é permitida sem fonte.
  - Projetos: atualizar os 7 existentes; **adicionar** `credito-nda` e `portais-conteudo` (ambos `tipo: produto`).
    `lab-ia` **não entra no site** (é estudo, não produto): aparece só na linha "IA aplicada" do currículo e no README
    do GitHub. Nenhum `tipo` novo é criado.
  - `numeros`: os 5 tiles continuam, com rótulos derivados: `numeros[1]` = "commits meus em N produtos" e
    `numeros[2]` = "funções de teste nos N produtos em Python", N calculado de `REPOS`; `numeros[3]` vai para o passado
    ("3 operações de iGaming, out/2025 – nov/2026").
- **`scripts/recontar.py` (contrato novo):** `REPOS: dict[slug, list[Path]]` com caminhos **absolutos**; entram
  `avisa-edital`, `pingado`, `nous-clinical`, `aggron`, `dumpai`, `atendimento-whatsapp` (`secretaria-ia`, hoje fora),
  `credito-nda`, `portais-conteudo` (5 pastas somadas) e `igaming-dados` (`OneDrive - PGX/Projetos - Super Nova/play4tune`
  + `.../MultiBet` + `~/Repos/play4tune-analytics`). Logo N = 8 produtos. Commit "meu" = autor cujo nome contém "Mateus" ou "mateusrfabro" (cobre o
  e-mail pessoal e o corporativo) e não contém "bot". Projeto "com pytest" = tem `tests/**/*.py` com `def test_`
  (`credito-nda`, e2e em TS, fica fora da contagem de testes). O fato de commits do `igaming-dados` segue a forma de
  `fato_commits()`: datas de início e fim saem do `git log`, nunca digitadas.
- **Teste:** paridade PT/EN estendida a `experiencia` (mesmos `id`, `inicio`, `fim`) e `formacao` (mesmos anos);
  `test_numeros_agregados_batem_com_os_fatos_dos_projetos` passa a derivar o conjunto de `recontar.REPOS` em vez das
  constantes `CINCO`/`QUATRO_FLASK`; em `curriculo.json`, todo bullet com dígito tem `fonte` não vazia (teste).

### U2 — Site (`build.py` → `public/`)
- **Faz:** o que já faz, mais: `resume.json.work` e `education` gerados de `experiencia` e `formacao` (com
  `startDate`/`endDate`); cabeçalho e `llms.txt` ganham link para `/curriculo/mateus-fabro-pt.pdf` e `-en.pdf`;
  disponibilidade nova; projetos novos. O projeto `igaming-dados` passa a se chamar "Super Nova Gaming / MultiBet" com
  `status: "Encerrado em nov/2026 (fim da operação)"`.
- **OG:** `scripts/gerar_og.py` continua desenhando `cargo`; com o cargo curto cabe. Regerar `og.png` após o build.
- **Interface:** `python build.py` e `python build.py --check`; o `--check` passa a chamar também a checagem do
  currículo (U3), de modo que `test_public_e_exatamente_o_que_o_gerador_produz` e o pré-commit cobrem `public/curriculo/*.html`
  sem hook novo.
- **Teste:** suíte existente verde; novos: `resume.json` tem `work[0].endDate == "2026-11"` e 2 itens de `education`
  com `startDate`/`endDate`; `index.html` contém `perfil.cargo` e `perfil.subtitulo`; `index.html` **não** contém
  "nome omitido".

### U3 — Currículo (`scripts/gerar_pecas.py curriculo`)
- **Faz:** renderiza HTML (template em `scripts/templates/curriculo.html`, estilo do
  `Curriculo_Mateus_Fabro_v4_WEB_FINAL.html`, 1 coluna, **alvo 2 páginas A4, limite 3**) e PDF via Playwright/Chromium
  (instalado: 145). Saída em `public/curriculo/mateus-fabro-{pt,en}.{html,pdf}`.
- **Interface:** `python scripts/gerar_pecas.py curriculo [--sem-pdf] [--privado] [--check]`. Lê U1 e, com
  `--privado`, o `portfolio-privado.json`; `--privado` grava em
  `OneDrive - PGX/7. Projetos Pessoais/Curriculo_Mateus_Fabro_v5_{PT,EN}.{html,pdf}` e **nunca** em `public/`.
  `--check` regenera o HTML em memória e compara com o de `public/curriculo/` (chamado por `build.py --check`).
- **Conteúdo fixo:** cabeçalho (nome, cargo, subtítulo, Londrina/remoto, e-mail, GitHub, LinkedIn, site), resumo de
  4 linhas, 5 tiles de `numeros`, experiência (3 itens de `experiencia` com bullets de `curriculo.json`), produtos
  próprios (um parágrafo por projeto `produto`, com `status`), stack (tabela), formação (2 linhas), idiomas.
- **Frescor:** HTML coberto pelo `--check`; o PDF é artefato versionado, regenerado no mesmo comando, sem checagem de
  frescor além da contagem de páginas.
- **Teste:** HTML gerado contém o nome do empregador, "out/2025 – nov/2026", as duas formações com anos, `cargo`, e
  **nenhum** termo da denylist (o `_publicaveis()` já varre `RAIZ` inteira, então `public/curriculo/` é coberto);
  PDF tem ≤ 3 páginas (`pypdf`, disponível); o HTML público **não contém o telefone** lido de `portfolio-privado.json`
  — sem o arquivo, o teste **falha** (como a denylist), salvo `PORTFOLIO_SEM_PRIVADO=1` explícito.

### U4 — Kit LinkedIn (`scripts/gerar_pecas.py linkedin`)
- **Faz:** gera um Markdown com seções na ordem em que o LinkedIn pede, cada uma dentro do limite da plataforma:
  título (220), Sobre (2.600), cada experiência (2.000), formação (2 entradas), projetos (até 6, com link),
  competências (lista de 50 para marcar), e o **post de disponibilidade** (PT, ≤ 1.300 caracteres, sem nome de cliente).
- **Interface:** `python scripts/gerar_pecas.py linkedin` → `docs/linkedin/kit-2026-11-pt.md` e `-en.md`
  (dentro de `RAIZ`: coberto pela denylist).
- **Teste:** cada seção respeita o limite (o script falha, não corta); mesmo empregador/datas/formação de U1.
- **Fora da automação:** colar no LinkedIn é manual; o kit traz, por seção, "onde colar" e "o que marcar".

### U5 — Perfil GitHub (`scripts/gerar_pecas.py github` + `scripts/github_perfil.ps1`)
- **Faz:** gera `docs/github/README.md` (cargo, subtítulo, 3 linhas de tese, tabela de projetos com status e link,
  links para site/currículo/LinkedIn, badge "em busca de vaga"). Fica dentro de `RAIZ`, logo coberto pela denylist.
- **`scripts/github_repos.json`**: tabela dos **24** repositórios (`nome`, `descricao`, `topics`, `abre: bool`);
  os 9 de trabalho entram com descrição "(Super Nova Gaming, out/2025 – nov/2026 — confidencial)" e `abre: false`.
  Não contém termo da denylist (descrição genérica basta).
- **`github_perfil.ps1`** (idempotente, imprime antes/depois):
  1. `gh repo create mateusrfabro/mateusrfabro --public` se não existir, clona em `C:\Users\mateu\Projects\mateusrfabro`,
     copia `docs/github/README.md`, commita e faz push;
  2. `gh api user` ajusta `name`, `bio`, `blog`, `location`;
  3. `gh repo edit` aplica descrição e topics dos 24 repositórios de `github_repos.json`;
  4. só com `-Abrir`: `gh repo edit --visibility public` nos que têm `abre: true`, e **só se** o relatório do Plano B
     (`C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md`) marcar `ABRE` na linha do repo;
     o script lê esse arquivo e recusa sem a marca.
- **Teste:** README gerado não contém termo da denylist; `--online` opcional confere que os links respondem 200.

### U6 — Repositórios "prontos para mostrar na tela" (**Plano B**, separado)
Checklist aplicado a **cada um dos 24** repositórios de `gh repo list mateusrfabro` (a lista nasce do comando, não
desta spec), com resultado em `C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md` — **fora
do repositório**, porque o relatório cita nomes de pasta e de achado que não podem ser publicados:

1. Branch principal contém o trabalho; branches `migracao-2026-09-28` e `feat/*`/`fix/*` concluídas são mergeadas
   (merge, nunca reescrita de história publicada) ou apagadas; a **mensagem do commit HEAD** não é "WIP". Histórico
   antigo com WIP fica. O **branch padrão do remoto** é `main`/`master` (`gh repo edit --default-branch`): em
   `nous-clinical` hoje aponta para um `feat/*`, e há `fix/ajuda-historico-nao-forja-assistente`,
   `chore/deps-cves-werkzeug-cryptography` e `feat/fiscal-gateway-focusnfe` abertos.
2. Working tree limpa (sem arquivo untracked que não seja `.gitignore`ável). Em `lab-ia`, as pastas e arquivos não
   versionados que não pertencem ao laboratório (ferramentas de funil/cloaker, páginas de oferta, `.wrangler/`)
   **saem do repositório** para `C:\Users\mateu\Projects\_fora-do-git\lab-ia\` antes de qualquer commit — o repo vai abrir.
3. `README.md` com: o que é, para quem, stack, como rodar, **estado real com data** (inclusive "parado desde").
4. `.env.example` quando há `.env`; `.env*` no `.gitignore`.
5. Varredura de segredos no **histórico completo** (`git log -p --all` contra padrões: `AKIA[0-9A-Z]{16}`,
   `gh[pousr]_[A-Za-z0-9]{36}`, `sk-[A-Za-z0-9]{20,}`, `xox[bp]-`, `://[^/\s]+:[^@\s]+@`, `BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY`,
   os domínios de e-mail corporativo e os termos da denylist). Achado = NÃO ABRE; o relatório lista commit e arquivo,
   nunca o valor. No `portfolio`, antes da varredura: `git reflog expire --expire=now --all && git gc --prune=now`
   (as revisões 1 e 2 desta spec, nunca publicadas, ainda existem no reflog).
6. Descrição e topics no GitHub (via `github_repos.json`, U5); licença MIT nos 6 que abrem.
7. Os 8 repositórios de trabalho no GitHub (`play4tune`, `play4tune-analytics`, `pcr-p4t`, `alerta-ftd`,
   `canonical-assessment`, `startbet-analytics`, `Scripts-usados---Mateus-Fabro`, `radar-demo`) permanecem
   **privados**. O clone local `MultiBet` aponta para um repositório da organização da empresa (transferido):
   nenhuma ação nele; o `recontar.py` só lê o clone. **Arquivar é opcional e fica para decisão do Mateus.**
8. Pastas de `~/Projects` sem git ou sem remoto (há 7; a lista nasce de `git remote` em cada pasta e vai no relatório):
   verificar com `diff -rq` contra o repo-fonte; se nada único, mover para `C:\Users\mateu\Projects\_fora-do-git\`
   (não apagar).

### U7 — Publicação (Plano A, última etapa)
- Site: `python scripts/recontar.py --aplicar` → `python build.py` → `python scripts/gerar_pecas.py curriculo` →
  `pytest -q` verde → `python scripts/gerar_og.py` → commit em `migracao-2026-09-28` → `git checkout master && git merge
  migracao-2026-09-28` → `git push origin master` → `vercel --prod` (CLI 61, logado como mateusrfabro).
  Verificação empírica: `curl` em `/`, `/resume.json`, `/curriculo/mateus-fabro-pt.pdf`, `/llms.txt` com o nome do
  empregador e as datas; screenshot Playwright a 412 px revisado pelo agente `ux-review`.
- GitHub: `github_perfil.ps1` sem `-Abrir` → relatório do Plano B → **OK do Mateus** → `-Abrir`.
- LinkedIn: entrega do kit; nada automatizado.
- Currículo: `gerar_pecas.py curriculo --privado` gera a cópia v5 com telefone no OneDrive.

## 4. Regras de conteúdo

- **Denylist** (`C:\Users\mateu\Projects\portfolio-denylist.txt`, fora do repositório, criada em U0). **Categorias**
  (os termos ficam só no arquivo): nome completo do cliente da cafeteria; nome completo do sócio do radar de editais;
  nome completo do sócio do projeto sob NDA; nomes completos dos 3 colegas do squad de dados; nomes de afiliados;
  vocabulário do domínio do projeto sob NDA e o nome e a cidade do grupo dele; os dois e-mails corporativos (inteiros).
  **Não** entram: Super Nova, MultiBet, PGX, Play4Tune, Play4 Colômbia, Londrina (cidade do Mateus, está no perfil).
  O e-mail corporativo inteiro na lista não conflita com "PGX" fora dela: o termo é o e-mail completo.
  O teste `test_nenhum_nome_confidencial_sai_publicado` volta a valer e, por varrer `RAIZ`, cobre `public/curriculo/`,
  `docs/linkedin/`, `docs/github/` e esta spec.
- **credito-saas**, texto permitido (PT): *SaaS multi-tenant de gestão de crédito (sob NDA): Next.js 16 + TypeScript,
  PWA com branding por tenant, Postgres/Supabase com RLS por tenant, backup diário restaurado em banco descartável e
  conferido em CI, e2e em contêiner. 65 commits, out/2026.*
- **Números**: todo número em qualquer peça vem de `numeros`, de `fatos` de projeto, de `experiencia` ou de um bullet
  de `curriculo.json` com `fonte` preenchida (exceção: versão de tecnologia em `stack`). `recontar.py` roda antes de
  publicar e a diferença aparece no commit.
- **Status honesto**: cada projeto diz se está no ar, em produção com cliente, parado (desde quando) ou piloto.
  "Faturamento baixo" (DumpAI) e "piloto parado" (Secretária) **continuam** — é a marca do site.
- **Idioma**: PT é a fonte; EN é tradução com os mesmos números (teste de paridade). Inglês do currículo revisado pelo
  agente `revisor-conteudo` com a instrução "inglês de currículo, direto, sem adjetivo".

## 5. Projetos: o que entra e onde

| Projeto (slug) | Repo(s) local(is) | Site | Currículo | LinkedIn | Abre? | Observação |
|---|---|---|---|---|---|---|
| Super Nova Gaming / MultiBet (`igaming-dados`) | `OneDrive - PGX/Projetos - Super Nova/play4tune` + `.../MultiBet` | sim (tipo trabalho, nomeado) | sim (experiência principal) | sim (experiência) | não | out/2025 – nov/2026; commits recontados por autor |
| Avisa Edital / AjudaMed (`avisa-edital`) | `~/Projects/ajudamed` (main) | sim (atualizar: PR e SP, commits e testes recontados, estado 05/11) | sim | sim (projeto) | não (sócio) | `avisa-pontagrossa` é clone do mesmo remoto; usar `ajudamed` |
| Pingado (`pingado`) | `~/Projects/cafesaas` | sim (atualizar: 2 lojas, versões até 04/11) | sim | sim | não (cliente) | branch `migracao-2026-09-28` → main (Plano B) |
| Nous Clinical (`nous-clinical`) | `~/Projects/medsaas` | sim | sim | sim | **sim** | branch `fix/ajuda-historico-nao-forja-assistente` → main (Plano B) |
| Aggron (`aggron`) | `~/Projects/poolcompras` | sim | sim | sim | **sim** | parado desde 28/05/2026 |
| DumpAI (`dumpai`) | `~/Projects/appfotos` | sim | sim | sim | **sim** | branch migração → master (Plano B) |
| Secretária de WhatsApp (`atendimento-whatsapp`) | `~/Projects/secretaria-ia` | sim | sim (1 linha) | não | **sim** | piloto parado; README já honesto; entra em `REPOS` |
| **Crédito (NDA)** (`credito-nda`) — novo | `~/Projects/credito-saas` | sim (mascarado) | sim (mascarado) | sim (mascarado) | não | regra da seção 4 |
| **Portais de conteúdo** (`portais-conteudo`) — novo, 1 entrada | 5 pastas `portal-*` | sim | sim (1 parágrafo) | sim (1 projeto) | não | "5 portais estáticos Astro 7 com indicadores oficiais (BCB/SGS, FRED, IBGE) atualizados por workflow, 33–45 guias cada, domínio próprio; lançados out/2026" — sem citar AdSense |
| lab-ia | `~/Projects/lab-ia` | **não** | 1 linha em "IA aplicada" | não | **sim** | "laboratório local: Ollama + PyTorch em RTX 4060, QLoRA, agente com ferramentas"; limpar pastas estranhas (U6.2) |
| Diário (`portfolio`) | `~/Projects/portfolio` | é o site | link | link | **sim** | hub |
| flashmed, meu-site, planos43, cópias sem git | — | não | não | não | não | U6.8 |

## 6. Agentes e gates (ordem)

| Momento | Agente | Entrada | Saída exigida |
|---|---|---|---|
| Plano B, antes de abrir qualquer repo | `cybersecurity` | lista de repos + script de varredura | tabela repo × achado (commit, arquivo, tipo) sem o valor; veredito ABRE / NÃO ABRE |
| Prosa do Sobre e do post | `copywriter` | `dados.json` + limites do LinkedIn | texto honesto, sem promessa, dentro do limite |
| Currículo PT/EN e kit | `revisor-conteudo` | arquivos gerados | correções in-place + relatório; inglês direto |
| Site publicado | `ux-review` | URL de preview + screenshot 412 px | fricções e correções |
| Suíte e geração | `tester` | repo portfolio | pytest verde, PDF ≤ 3 páginas, kit dentro dos limites |
| Fechamento | `auditor` (eixo "o número é possível?") | todas as peças + saída do `recontar.py` | cada número com fonte; datas e empregador iguais nas 4 peças |

## 7. Fora de escopo

- Postar no LinkedIn ou alterar o perfil por automação.
- Reescrever o design visual do site (só conteúdo e links novos).
- Migrar repositórios de trabalho para outra organização ou apagá-los.
- Tradução do site para espanhol.
- Banner novo do LinkedIn (o de 10/08 segue; se o título mudar no banner, é tarefa à parte).
- Tipo novo de projeto no gerador (`estudo`): não é necessário, lab-ia não entra no site.

## 8. Riscos e tratamento

| Risco | Tratamento |
|---|---|
| Abrir repo com segredo no histórico | varredura do Plano B é gate; achado bloqueia; abertura só com `-Abrir` após OK |
| Número velho em alguma peça | todas geradas da mesma fonte na mesma execução; `medido_em` único; teste de paridade |
| Nome de cliente/sócio vazar junto com o nome da empresa | denylist criada em U0, **antes** de qualquer geração; teste varre `RAIZ` inteira, inclusive esta spec |
| Telefone vazar | não existe em arquivo versionado; teste de U3 confere que o HTML público não o contém |
| Merge de `migracao-2026-09-28` apagar algo | merge, nunca reset; `git log` antes/depois no relatório |
| PDF com 4+ páginas | teste conta páginas; prosa do CV corta antes |
| Currículo "inflado" | regra: fato com fonte ou não entra; status honesto; auditor confere |
| Capa OG com título cortado | `cargo` curto; regerar `og.png` e olhar |

## 9. Critérios de aceite

1. `pytest` do portfólio verde, com a denylist e o `portfolio-privado.json` presentes (sem variáveis de dispensa).
2. Site no ar com empregador nomeado, datas out/2025–nov/2026, duas formações, disponibilidade nova, 9 projetos
   (7 atuais + 2 novos), PDFs PT/EN acessíveis, `resume.json` válido com `work` e `education` datados, `medido_em` =
   data da publicação, `og.png` regerado.
3. Currículo PT e EN em PDF (≤ 3 páginas, alvo 2) e HTML em `public/curriculo/`, sem telefone; cópia v5 com telefone
   em `OneDrive - PGX/7. Projetos Pessoais/`.
4. Kit LinkedIn PT e EN em `docs/linkedin/`, cada seção dentro do limite, com instruções de onde colar.
5. Perfil GitHub com nome, bio, link e README; 6 repositórios abertos após varredura e OK; 24 repositórios com README
   datado, branch principal em dia e working tree limpa; relatório do Plano B preenchido fora do repo.
6. Nenhum arquivo do repositório, inclusive esta spec, contém termo da denylist.
