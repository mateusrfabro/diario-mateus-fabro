# Plano B — Repositórios "prontos para mostrar na tela" Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deixar os 24 repositórios de `gh repo list mateusrfabro` em estado apresentável (branch principal em dia, working tree limpa, README datado, `.env*` ignorado com `.env.example` versionado, sem segredo no histórico) e produzir o relatório que autoriza, repo a repo, a abertura dos 6 escolhidos.

**Architecture:** Um script de varredura (fora do repositório público) percorre o histórico completo de cada clone local contra padrões de segredo e contra a denylist, inclusive mensagens de commit; um relatório Markdown **fora de qualquer repositório** consolida estado e veredito por repo; as arrumações são commits normais em cada repositório. Nada é reescrito na história publicada.

**Tech Stack:** git, `gh` CLI, Python 3.12, PowerShell 5.1 e Git Bash (os comandos `diff`/`ls -R` são do Git Bash; no PowerShell, `diff` é `Compare-Object`).

**Spec:** `docs/superpowers/specs/2026-11-05-transicao-carreira-design.md`, U6. Depende da denylist (Task 0 do Plano A) e roda **depois** do Step 6 da Task 0 do Plano A (`reflog expire` + `gc` no portfolio), senão a varredura `--all` ainda vê revisões antigas da spec.

**Fatos verificados em 05/11/2026 (revisão do plano):**
- No GitHub do Mateus há **24** repos; `multibet-analytics` (remoto do clone `MultiBet`) foi **transferido para a organização da empresa** (conferido com `gh repo view`: dono = org, visibilidade INTERNAL) — nenhuma ação nele. Repositórios de trabalho no GitHub do Mateus: **8** (`play4tune`, `play4tune-analytics`, `pcr-p4t`, `alerta-ftd`, `canonical-assessment`, `startbet-analytics`, `Scripts-usados---Mateus-Fabro`, `radar-demo`). A spec §2/U6.7 dizia 9: a lista verdadeira nasce do inventário (Task 2).
- `medsaas` (nous-clinical): remoto tem `master` e `feat/nous-rebrand-financeiro` (**branch padrão**, 91 commits à frente de `master`); `fix/ajuda-historico-nao-forja-assistente`, `chore/deps-cves-werkzeug-cryptography` e `feat/fiscal-gateway-focusnfe` têm 0 commits além do rebrand. Não existe `main`.
- `cafesaas-cpf` **é worktree** do `cafesaas` (branch `feat/cpf-cnpj-nota`), não cópia. `cafesaas` tem `.claude/worktrees/` untracked e o remoto `feat/fiscal-sefaz-pr` sem decisão; `origin/main..migracao-2026-09-28` = 0.
- `ajudamed` tem 8 worktrees registrados em pastas de scratchpad/`.claude/worktrees/` e 9 branches locais não mergeados.
- `appfotos` já versiona `.env.local.example`.

**Regras:** nunca imprimir o valor de um segredo (só commit, arquivo e tipo; em grep manual, só o **nome da chave**). Nunca `git push --force`, `rebase` ou `filter-branch` em branch que está no remoto. Merge, nunca reset. Nada se apaga: pasta sai para `C:\Users\mateu\Projects\_fora-do-git\` e o relatório diz o que ela tinha de único.

---

## Chunk 1: Ferramenta de varredura e inventário

### Task 1: Pastas fora do git e script de varredura

**Files:**
- Create: `C:\Users\mateu\Projects\_fora-do-git\ferramentas\varrer_segredos.py`
- Create: `C:\Users\mateu\Projects\_fora-do-git\relatorios\` (pasta)

- [ ] **Step 1: Criar as pastas**

```powershell
New-Item -ItemType Directory -Force C:\Users\mateu\Projects\_fora-do-git\ferramentas, C:\Users\mateu\Projects\_fora-do-git\relatorios, C:\Users\mateu\Projects\_fora-do-git\lab-ia | Out-Null
```

- [ ] **Step 2: Script**

```python
"""Varre o histórico COMPLETO de um repositório git (diffs E mensagens de commit) contra padrões de
segredo e contra a denylist.

Uso: py -3.12 varrer_segredos.py <caminho-do-repo> [<caminho-do-repo> ...]
Saída: uma linha por achado: repo | commit | arquivo | tipo — NUNCA o valor.
Exit 0 = nada; 1 = achado. Pré-condição: C:\\Users\\mateu\\Projects\\portfolio-denylist.txt existe.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DENYLIST = Path.home() / "Projects" / "portfolio-denylist.txt"
PADROES = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),
    "openai_anthropic_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "slack_token": re.compile(r"xox[bp]-[A-Za-z0-9-]{10,}"),
    "url_com_senha": re.compile(r"://[^/\s:@]+:[^@\s]+@"),
    "chave_privada": re.compile(r"BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY"),
    "email_corporativo": re.compile(r"@(pgx-group\.com|grupo-pgs\.com)", re.I),
}
ENV_VERSIONADO = re.compile(r"^\+\+\+ b/(.*/)?\.env(?!\.(example|sample|template)$)(\.[a-z]+)?$")
IGNORAR_ARQ = re.compile(r"(package-lock\.json|uv\.lock|\.min\.js|\.woff2?|\.png|\.jpg|\.pdf)$")


def _dobrar(s: str) -> str:
    s = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def termos() -> list[str]:
    if not DENYLIST.exists():
        sys.exit(f"denylist ausente: {DENYLIST}")
    return [t.strip() for t in DENYLIST.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")]


def _bate_denylist(baixa: str, deny: list[tuple[int, str]]) -> list[int]:
    hits = []
    for i, t in deny:
        if (len(t) >= 5 and t in baixa) or (len(t) < 5 and re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", baixa)):
            hits.append(i)
    return hits


def varrer(repo: Path) -> list[tuple[str, str, str, str]]:
    repo = repo.resolve()
    log = subprocess.run(["git", "-C", str(repo), "log", "--all", "-p", "--no-color",
                          "--format=COMMIT %h%nMSG %s%nMSG %b%nENDMSG"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    achados, commit, arquivo = [], "?", "?"
    deny = [(i, _dobrar(t)) for i, t in enumerate(termos())]
    em_msg = False
    for linha in log.splitlines():
        if linha.startswith("COMMIT "):
            commit, arquivo, em_msg = linha[7:], "<mensagem>", True
            continue
        if linha == "ENDMSG":
            em_msg = False
            continue
        if em_msg:                                   # %s e %b inteiros, inclusive corpo multilinha
            for i in _bate_denylist(_dobrar(linha[4:] if linha.startswith("MSG ") else linha), deny):
                achados.append((repo.name, commit, "<mensagem>", f"denylist#{i}"))
            continue
        if linha.startswith("+++ b/"):
            arquivo = linha[6:]
            if ENV_VERSIONADO.match(linha):
                achados.append((repo.name, commit, arquivo, "env_versionado"))
            continue
        if not linha.startswith("+") or IGNORAR_ARQ.search(arquivo):
            continue
        for tipo, rx in PADROES.items():
            if rx.search(linha):
                achados.append((repo.name, commit, arquivo, tipo))
        for i in _bate_denylist(_dobrar(linha), deny):
            achados.append((repo.name, commit, arquivo, f"denylist#{i}"))
    return sorted(set(achados))


def main() -> int:
    total = 0
    for caminho in sys.argv[1:]:
        for a in varrer(Path(caminho)):
            print(" | ".join(a))
            total += 1
    print(f"-- {total} achado(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Controle positivo (o script sabe ficar vermelho)** — pré-condição: a denylist da Task 0 do Plano A já existe.

```powershell
cd C:\Users\mateu\Projects\_fora-do-git
git init -q controle; cd controle; git config user.email t@t; git config user.name t
Set-Content a.txt "AKIAABCDEFGHIJKLMNOP"; Set-Content .env "X=1"; git add a.txt .env; git commit -q -m x
py -3.12 ..\ferramentas\varrer_segredos.py .
cd ..; Remove-Item -Recurse -Force controle
```
Expected: duas linhas `controle | <hash> | .env | env_versionado` e `controle | <hash> | a.txt | aws_access_key`, depois `-- 2 achado(s)`, exit 1. Controle negativo: repetir com `Set-Content .env.example "X="` no lugar de `.env` → só o achado do `a.txt`.

### Task 2: Inventário e varredura dos 6 que abrem

- [ ] **Step 1: Inventário (a lista de 24 nasce daqui, não da spec)**

```powershell
gh repo list mateusrfabro --limit 60 --json name,visibility,pushedAt --jq '.[] | "\(.name)\t\(.visibility)\t\(.pushedAt[:10])"' | Out-File -Encoding utf8 C:\Users\mateu\Projects\_fora-do-git\relatorios\inventario.tsv
(Get-Content C:\Users\mateu\Projects\_fora-do-git\relatorios\inventario.tsv).Count   # esperado: 24
```

- [ ] **Step 2: Varredura dos 6** (clones: `portfolio`, `medsaas`, `poolcompras`, `appfotos`, `secretaria-ia`, `lab-ia`)

```powershell
cd C:\Users\mateu\Projects
[Console]::OutputEncoding = [Text.Encoding]::UTF8
py -3.12 _fora-do-git\ferramentas\varrer_segredos.py portfolio medsaas poolcompras appfotos secretaria-ia lab-ia | Out-File -Encoding utf8 _fora-do-git\relatorios\varredura-6.txt
Get-Content _fora-do-git\relatorios\varredura-6.txt | Select-Object -Last 5
```

- [ ] **Step 3: Agente `cybersecurity`** — prompt com o caminho do `varredura-6.txt` e do script. Pedir: (a) classificar cada achado (segredo real / falso positivo / dado pessoal); (b) segunda varredura manual nos arquivos **atuais** dos 6, imprimindo **só arquivo, linha e nome da chave**, nunca o valor: `grep -rnoE "^[A-Za-z_]*(PASSWORD|SENHA|TOKEN|SECRET|API_KEY)[A-Za-z_]*=" --include=*.env* --include=*.py --include=*.ts .` e, para JSON, `grep -rnoiE '"[a-z_]*(password|senha|token|secret|api_key)[a-z_]*"\s*:' --include=*.json .`; (c) veredito **ABRE / NÃO ABRE** por repo com motivo. Achado real em repo da lista = NÃO ABRE até remoção **e** rotação do segredo (histórico público não se limpa; se exigir reescrever história, o repo sai da lista de abertura).

### Task 3: Varredura dos privados (inventário, não bloqueia)

- [ ] Rodar o script nos clones locais que existem: `ajudamed`, `cafesaas`, `credito-saas`, os 5 `portal-*`, `flashmed`, e nos de trabalho `OneDrive - PGX/Projetos - Super Nova/{play4tune,MultiBet}` e `~/Repos/play4tune-analytics`. Saída em `varredura-privados.txt`. Registrar no relatório `git remote -v` de `MultiBet` (remoto transferido para a org da empresa) e a existência de `~/Repos/Supernova-Dashboard` (org da empresa, fora da lista). Achado em repo de trabalho vira **nota** (segredo da empresa encerrada; rotação não é nossa; nunca abrir).

## Chunk 2: Arrumação repo a repo

Para cada repo dos 6 que abrem, os steps são sempre: (1) branch, (2) working tree, (3) README datado, (4) `.gitignore` com `.env*` + `!.env.example` e `.env.example` sem valores, (5) `LICENSE` MIT, (6) branch padrão no GitHub, (7) push, (8) `git status --short` vazio e `git log -1 --format=%s` sem "WIP".

### Task 4: `portfolio` (diario-mateus-fabro)

- [ ] **Step 1:** Já mergeado em `master` e enviado no Plano A (Task 11). Conferir `git status --short` vazio e HEAD não-WIP.
- [ ] **Step 2:** README: acrescentar 3 linhas à tabela "Uma fonte, seis formas" (`curriculo/*.html|pdf`, `docs/linkedin/`, `docs/github/`) e a frase "Código sob licença MIT; o conteúdo (textos e dados) é do autor."
- [ ] **Step 3:** `LICENSE` MIT (texto padrão, "Copyright (c) 2026 Mateus Fabro"). Commit `"docs: licenca MIT e pecas geradas no README"`, push `master`.

### Task 5: `appfotos` (dumpai)

- [ ] **Step 1:** `git checkout master` (criar de `origin/master` se não existir local) → `git merge --no-ff migracao-2026-09-28 -m "merge: estado da migracao de notebook"`.
- [ ] **Step 2:** README: seção "Estado (05/11/2026)": no ar em https://dumpai-omega.vercel.app; vendas perto de zero; sem desenvolvimento desde 22/06/2026.
- [ ] **Step 3:** `.gitignore`: garantir `.env*` e `!.env.local.example`; conferir que `.env.local.example` lista as mesmas chaves de `.env.local` (comparar só os nomes: `cut -d= -f1`), sem valores.
- [ ] **Step 4:** `LICENSE` MIT. Commit `"docs: estado em 05/11/2026, licenca MIT"`. `gh repo edit mateusrfabro/dumpai --default-branch master`. Push `master`; apagar `migracao-2026-09-28` local e remoto depois do merge.

### Task 6: `medsaas` (nous-clinical) — não existe `main`

- [ ] **Step 1:** `git fetch --all`; `git checkout -b master origin/master`; `git merge --no-ff origin/feat/nous-rebrand-financeiro -m "merge: rebrand e financeiro"` (91 commits).
- [ ] **Step 2:** Para `fix/ajuda-historico-nao-forja-assistente`, `chore/deps-cves-werkzeug-cryptography`, `feat/fiscal-gateway-focusnfe`: `git log master..<branch> --oneline`; vazio (esperado) → `git branch -D <branch>` e `git push origin --delete <branch>` se existir no remoto; não vazio → merge.
- [ ] **Step 3:** `git diff CLAUDE.md` → commitar se for só texto; `.claude/` e `.env*` + `!.env.example` no `.gitignore`.
- [ ] **Step 4:** README: "Estado (05/11/2026): última versão em 06/10/2026, sem cliente pagante, deploy no Render". `.env.example` com os nomes de `.env` sem valores. `LICENSE` MIT. Commit.
- [ ] **Step 5:** `git push origin master`; `gh repo edit mateusrfabro/nous-clinical --default-branch master`; depois `git push origin --delete feat/nous-rebrand-financeiro` (já mergeado; só após o default mudar).
- [ ] **Step 6:** `gh pr list` (dependabot, 7 aqui e 7 no `poolcompras`): mergear os de segurança que passam CI, fechar os demais; registrar no relatório.

### Task 7: `poolcompras` (aggron)

- [ ] **Step 1:** `git diff CLAUDE.md` → commitar se texto; `.claude/` e `.env*` + `!.env.example` no `.gitignore`.
- [ ] **Step 2:** README: "Estado (05/11/2026): MVP completo, parado desde 28/05/2026; sócio como PO". `.env.example` conferido. `LICENSE` MIT. Commit, push `main`.

### Task 8: `secretaria-ia`

- [ ] **Step 1:** README: atualizar o bloco "Estado em 16/09/2026" para "Estado em 05/11/2026: piloto parado; sem cliente pagante".
- [ ] **Step 2:** `.gitignore` com `.env*` + `!.env.example`; `.env.example` para `n8n/` e `tenants/` (nomes das chaves, sem valor). `LICENSE` MIT. Commit, push `master`.

### Task 9: `lab-ia` — pastas estranhas saem ANTES de qualquer commit

- [ ] **Step 1:** Mover para `C:\Users\mateu\Projects\_fora-do-git\lab-ia\` tudo que não é do laboratório: as pastas `*cloaker*`, as pastas `rewarded-tasks*`, os arquivos `*_offer.html`, `scripts/audit_funnel_cloaker.py` e `.wrangler/`. `git status --short` tem de ficar vazio. Acrescentar `.wrangler/` ao `.gitignore`.
- [ ] **Step 2:** README: trocar "RTX 4050 de 6 GB" pelo hardware atual (log de 06/10: RTX 4060 8 GB) e acrescentar "Estado (05/11/2026): trilhas agent/finetune/tabular; sem resultado publicado ainda".
- [ ] **Step 3:** `.gitignore` com `.env*` + `!.env.example`. `LICENSE` MIT. Commit, push `main`. O grep manual da Task 2 Step 3 é o que cobre os arquivos atuais (a varredura só vê histórico).

### Task 10: Privados que ficam, mas apresentáveis

- [ ] **`cafesaas`:** `git checkout -b main origin/main`; `git log origin/main..migracao-2026-09-28` (esperado vazio → nada a mergear; se não, `merge --no-ff`). Worktree `cafesaas-cpf` (branch `feat/cpf-cnpj-nota`): `git log main..feat/cpf-cnpj-nota --oneline` → merge se tiver commits; **primeiro** `git worktree remove --force C:\Users\mateu\Projects\cafesaas-cpf` (caminho absoluto; o git recusa apagar branch em uso), **depois** `git branch -d feat/cpf-cnpj-nota`. Mesma ordem para `.claude/worktrees/agent-*` (`git worktree list` → `remove` → `branch -d`); `.claude/` no `.gitignore`. Remoto `feat/fiscal-sefaz-pr`: `git log main..origin/feat/fiscal-sefaz-pr` → merge ou `push --delete`. `reports/` e `research_notes/` untracked: `ls` → saídas de análise vão para `_fora-do-git/cafesaas/`; documentação se commita. README: "Estado (05/11/2026): em produção na cliente com 2 lojas; última versão 04/11". `.env.example` conferido. Push `main`.
- [ ] **`ajudamed`:** `git worktree list` → para cada worktree em pasta de scratchpad ou `.claude/worktrees/`: `git worktree remove --force <caminho>` (se a pasta não existir, `git worktree prune`). Branches locais não mergeados (`vendas-*`, `links-bio`, `grupo-whatsapp`, `voz-ato`, `backup/main-local-07-10`): `git log main..<branch> --oneline`; registrar no relatório o que cada um tem e **deixar a decisão (merge/apagar) para o Mateus** — é negócio vivo com sócio. `avisa-pontagrossa`: se `git status` limpo e `git log -1` igual ao `origin/main`, mover a pasta para `_fora-do-git/`. README: acrescentar a data de hoje no cabeçalho de "Operação".
- [ ] **`credito-saas`:** criar README mínimo na raiz: o que é em 2 linhas (texto permitido do spec §4), stack, como rodar (apontar `docs/desenvolvimento.md`), estado 28/10/2026. **Sem** nome de grupo, cidade ou sócio.
- [ ] **5 portais, `flashmed`, `avisa-pedidos`, `radar-demo`:** `git status` limpo; descrição no GitHub vem do `github_perfil.ps1` (Plano A).

### Task 11: Repositórios de trabalho (8 no GitHub)

- [ ] Nada no conteúdo. Descrição via `github_perfil.ps1`. Registrar no relatório que ficam privados e que **arquivar** (`gh repo archive`, reversível) é decisão do Mateus.

### Task 12: Pastas de `~/Projects` sem git ou sem remoto

- [ ] **Step 1 (enumerar, Git Bash):** `for d in ~/Projects/*/; do echo "$d $(git -C "$d" remote get-url origin 2>/dev/null || echo SEM-REMOTO)"; done`. Critério: pasta **duplicada** de um repo-fonte, tenha remoto ou não. Hoje: `ajudamed-wt` e `planos43` sem git; `meu-site` com git e sem remoto; `nous-stable` e a pasta `*-demo` (nome da cliente da cafeteria) são **clones do `nous-clinical` com alteração local** (`M CLAUDE.md` e untracked próprios) — entram mesmo tendo remoto.
- [ ] **Step 2 (registrar o único, Git Bash):** para os clones (`nous-stable`, `*-demo`): `git -C <copia> status --short` e `git -C <copia> log -1 --format=%h` comparado a `git -C medsaas rev-parse --short origin/master`. Para `ajudamed-wt` (sem git): `diff -rq -x .git -x node_modules -x .venv ajudamed-wt ajudamed | head`. Anotar no relatório o que a cópia tem de único (ex.: `.bat`, `proposta-*.html`, `CLAUDE.md` alterado).
- [ ] **Step 3 (mover sempre, nunca apagar, Git Bash):** `mv ~/Projects/<copia> ~/Projects/_fora-do-git/`. `planos43` e `meu-site`: `ls` do conteúdo → uma linha no relatório dizendo o que são; mover.

## Chunk 3: Relatório e entrega

### Task 13: Relatório `2026-11-repos-estado.md`

- [ ] **Step 1:** Escrever `C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md`. A coluna `repo` é o nome **no GitHub** (igual a `scripts/github_repos.json` do Plano A), uma linha por repo do `inventario.tsv` (24). **O `github_perfil.ps1 -Abrir` lê exatamente este formato** (regex `^\|\s*<repo>\s*\|.*\|\s*ABRE\s*\|`):

```
| repo | pasta local | visibilidade hoje | branch padrão | HEAD é WIP? | tree limpa | README datado | .env.example | varredura | veredito |
|---|---|---|---|---|---|---|---|---|---|
| diario-mateus-fabro | portfolio | PRIVATE | master | não | sim | sim | n/a | 0 achados | ABRE |
| nous-clinical | medsaas | PRIVATE | master | não | sim | sim | sim | 0 achados | ABRE |
| play4tune | play4tune (OneDrive) | PRIVATE | main | não | — | — | — | nota | FICA PRIVADO |
```

- [ ] **Step 2:** Seções abaixo da tabela: "Achados da varredura (commit, arquivo, tipo — sem valor)"; "Pastas movidas para `_fora-do-git` e o que tinham de único"; "Branches sem decisão (ajudamed)"; "Decisões pendentes do Mateus: arquivar os 8 de trabalho? branches do ajudamed?".
- [ ] **Step 3:** Entregar ao Mateus o caminho do relatório e pedir o OK explícito para a Task 18 do Plano A.
