# Plano A — Peças geradas (currículo, kit LinkedIn, site, perfil GitHub) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gerar, de `conteudo/dados.json` + `dados.en.json` + `conteudo/curriculo.json`, o site atualizado, o currículo PT/EN (HTML + PDF), o kit LinkedIn e o README do perfil GitHub, com empregador nomeado, formação correta e nenhum termo da denylist.

**Architecture:** O gerador existente (`build.py`) continua dono de `public/`; um script novo (`scripts/gerar_pecas.py`) lê os mesmos JSONs e produz currículo, kit e README. `scripts/recontar.py` passa a conhecer todos os repositórios (lista de caminhos absolutos por slug) e a contar commits por autor. Tudo que não pode ser público (denylist, telefone, relatório de repositórios) mora **fora** do repositório, em `C:\Users\mateu\Projects\`.

**Tech Stack:** Python 3.12 (`py -3.12`), pytest, Playwright/Chromium 145 (PDF), pypdf 6.10, `gh` CLI, Vercel CLI 61, PowerShell 5.1.

**Spec:** `docs/superpowers/specs/2026-11-05-transicao-carreira-design.md` (rev. 3). **Plano B** (repositórios) é `2026-11-05-plano-b-repositorios.md`; a Task 18 deste plano depende do relatório dele.

**Regras de execução (valem para TODAS as tasks):**
- Diretório de trabalho: `C:\Users\mateu\Projects\portfolio`. Python sempre `py -3.12`. Antes de qualquer Python que imprima acento: `$env:PYTHONIOENCODING="utf-8"` (PowerShell) ou `export PYTHONIOENCODING=utf-8` (bash).
- `git add` arquivo por arquivo. Commits na branch `migracao-2026-09-28`. Mensagens sem nenhum nome de pessoa, cliente ou sócio (o teste de denylist lê o `git log`).
- **Nunca** escrever num arquivo do repositório um termo da denylist. Os nomes concretos só existem em `C:\Users\mateu\Projects\portfolio-denylist.txt`. Se um passo precisar olhar um nome (ex.: achar o nome completo do sócio), o passo lê o arquivo-fonte e grava **direto** na denylist, sem ecoar no terminal nem no plano.
- Depois de editar `conteudo/*.json`: `py -3.12 build.py` e `py -3.12 -m pytest -q` antes do commit.

---

## Chunk 1: Pré-requisitos locais e dados (U0, U1)

### Task 0: Denylist, arquivo privado, hook, branch master

**Files:**
- Create (fora do repo): `C:\Users\mateu\Projects\portfolio-denylist.txt`, `C:\Users\mateu\Projects\portfolio-privado.json`
- Modify: config git do repo (hooksPath), branch local `master`

- [ ] **Step 1: Levantar os termos da denylist sem ecoar no terminal**

Abrir cada fonte abaixo com o Read tool, copiar o nome **completo** e gravar na denylist (um por linha). Não colar nenhum nome no chat, no commit, nem em arquivo do repositório.

| Categoria (spec §4) | Onde achar o nome completo |
|---|---|
| cliente da cafeteria (nome da cafeteria e da dona) | `C:\Users\mateu\Projects\cafesaas\README.md` (1ª linha) e `docs/PROJETO.md` |
| sócio do radar de editais (nome completo; o apelido de 2 letras **não** entra: casaria em nomes de arquivo) | em `C:\Users\mateu\Projects\ajudamed\docs\`, o arquivo de handoff cujo nome termina com o apelido do sócio (cabeçalho); se só houver o apelido, o arquivo de decisões de vendas de 11/10 |
| sócio do projeto sob NDA | `C:\Users\mateu\Projects\credito-saas\docs\publicacao.md` ("admin = ...") |
| 3 colegas do squad de dados | `C:\Users\mateu\OneDrive - PGX\Projetos - Super Nova\play4tune\CLAUDE.md` ("Quem sou eu") — primeiro nome; sobrenome em `git log --format=%an` do `MultiBet` se existir. Se só houver o primeiro nome de 5 letras, gravar assim mesmo e aceitar falso positivo (o teste nunca imprime o termo). |
| afiliados | `C:\Users\mateu\.claude\projects\c--Users-mateu-OneDrive---PGX-Projetos---Super-Nova-play4tune\memory\MEMORY_afiliados.md` (nomes de afiliado citados no índice) |
| vocabulário e identidade do projeto sob NDA | `credito-saas/docs/auditoria-sistema-2026-10-22.md`: o nome do grupo nas 2 grafias, a **cidade** do grupo como aparece no nome, a sigla de 3 letras, a palavra do domínio no singular e no plural, e as duas palavras que o documento usa para as partes do contrato (quem empresta e quem deve) |
| e-mails corporativos (os dois, inteiros) | `git -C "C:\Users\mateu\OneDrive - PGX\Projetos - Super Nova\MultiBet" log --format=%ae \| sort -u` (o do grupo antigo) e `git config --global user.email` (o atual) |

Formato do arquivo: UTF-8 **sem BOM** (gravar com o Write tool; `Set-Content -Encoding utf8` do PowerShell 5.1 põe BOM e o 1º termo nasceria com `\ufeff`, nunca casando), uma linha por termo, linhas `#` são comentário. Mínimo 10 termos (o teste exige). Conferir: `py -3.12 -c "print(open(r'C:\Users\mateu\Projects\portfolio-denylist.txt','rb').read(3))"` não começa com `\xef\xbb\xbf`.

- [ ] **Step 2: Criar o arquivo privado** — o telefone **não** se escreve neste plano nem em nenhum arquivo do repo: o executor digita o número (está no currículo v4 em `OneDrive - PGX/7. Projetos Pessoais/Curriculo_Mateus_Fabro_v4_conteudo_PT.md`, linha 5) direto no comando, no terminal: Se o placeholder ficar, `test_curriculo_publico...` **falha** de propósito (o número vazio sempre "aparece" no HTML) — não é bug do teste.

```powershell
py -3.12 -c "import json,pathlib;pathlib.Path(r'C:\Users\mateu\Projects\portfolio-privado.json').write_text(json.dumps({'telefone': '<digitar aqui>'}), encoding='utf-8')"
```

- [ ] **Step 3: Hook e e-mail do autor**

```powershell
cd C:\Users\mateu\Projects\portfolio
git config user.email mateusrfabro@hotmail.com
git config core.hooksPath scripts/hooks
git config --get core.hooksPath   # esperado: scripts/hooks
```

- [ ] **Step 4: Branch master local**

```powershell
git fetch origin
git branch master origin/master      # cria sem trocar de branch
git branch -a                        # esperado: master, * migracao-2026-09-28, remotes/...
```

- [ ] **Step 5: Suíte verde ANTES de mexer no conteúdo**

Run: `py -3.12 -m pytest -q`
Expected: `40 passed` (os 2 testes de denylist passam porque o arquivo agora existe). Se `test_nenhum_nome_confidencial_sai_publicado` falhar, o índice do termo aponta um nome que já está publicado em `public/` — abrir o termo na denylist e decidir: nome de empresa encerrada não entra na lista (spec §4); nome de pessoa que já estava no site é bug do site e se corrige em Task 2.

- [ ] **Step 6: Limpar reflog (spec U6.5) e confirmar que a história não tem termo**

```powershell
git reflog expire --expire=now --all; git gc --prune=now --quiet
py -3.12 -m pytest -q -k "confidencial or vermelha"
```
Expected: `2 passed`. Se o teste acusar índice de termo **em `docs/superpowers/`**, o spec ou um plano ainda contém um termo: corrigir o texto (categoria no lugar do termo), `git commit --amend` (os commits de spec/plano são locais) e repetir.

Nada a commitar nesta task.

- [ ] **Step 7: Ordem obrigatória das tasks** — Task 4 (`curriculo.json`) **antes** da Task 5 (`gerar_pecas.py`): o `try/except ImportError` da Task 3 cobre módulo ausente, não `FileNotFoundError` do JSON.

---

### Task 1: `recontar.py` com repositórios absolutos e filtro por autor

**Files:**
- Rewrite: `scripts/recontar.py`
- Test: `tests/test_recontar.py` (novo)

- [ ] **Step 1: Escrever o teste**

```python
"""recontar.py: contrato de REPOS, filtro de autor e formas dos fatos."""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import recontar  # noqa: E402


def test_repos_sao_listas_de_caminhos_absolutos_existentes():
    for slug, caminhos in recontar.REPOS.items():
        assert isinstance(caminhos, list) and caminhos, slug
        for c in caminhos:
            assert c.is_absolute() and (c / ".git").exists(), f"{slug}: {c}"


def test_meu_reconhece_os_dois_emails_e_exclui_bot():
    assert recontar.meu("Mateus Fabro")
    assert recontar.meu("mateusrfabro")
    assert not recontar.meu("avisa-edital-bot")
    assert not recontar.meu("Outra Pessoa")


def test_fato_commits_cobre_ano_diferente():
    c = {"humanos": 12, "bot": 0, "inicio": "2025-12-01", "fim": "2026-02-03", "testes": 0}
    assert recontar.fato_commits(c) == "12 commits meus entre 01/12/2025 e 03/02/2026"
    c["inicio"] = "2026-01-05"
    assert recontar.fato_commits(c) == "12 commits meus entre 05/01 e 03/02/2026"
    c["bot"] = 3
    assert recontar.fato_commits(c).endswith(", fora 3 automáticos do bot")


def test_produtos_com_repo_e_com_pytest_sao_derivados():
    d = recontar.carregar()
    produtos = recontar.produtos_com_repo(d)
    assert set(produtos) <= set(recontar.REPOS) and "igaming-dados" not in produtos
    assert len(produtos) == 8
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `py -3.12 -m pytest -q tests/test_recontar.py`
Expected: FAIL (`AttributeError: ... 'meu'` / `REPOS` com `Path` único).

- [ ] **Step 3: Reescrever `scripts/recontar.py`**

```python
"""Reconta os números do diário direto na fonte e (com --aplicar) atualiza conteudo/dados*.json.

Sem isto os números começam a envelhecer no dia seguinte à publicação. Roda na máquina do
Mateus, porque é lá que moram os repositórios e a memória global.

O que reconta, por projeto (REPOS: slug → lista de repositórios, caminhos absolutos):
  • commits MEUS (autor "Mateus" ou "mateusrfabro", nunca "bot"), primeira e última data;
  • funções de teste (`def test_`) em tests/**/*.py;
  • lições registradas (global_index.json);
  • no Avisa Edital, quantos commits meus registram teste de mutação.

Os rótulos de numeros[1] e numeros[2] são derivados: "N produtos" é o número de projetos do tipo
produto com repositório; "N produtos em Python" é o subconjunto com suíte pytest.

Uso:
  python scripts/recontar.py            # mostra o que mudou
  python scripts/recontar.py --aplicar  # grava, atualiza medido_em e roda o build
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "conteudo" / "dados.json"
DADOS_EN = RAIZ / "conteudo" / "dados.en.json"
CASA = Path.home()
PROJETOS = CASA / "Projects"
SUPER_NOVA = CASA / "OneDrive - PGX" / "Projetos - Super Nova"
PORTAIS = ["portal-br-beneficios", "portal-br-credito", "portal-br-invest", "portal-eua", "portal-us-money"]
REPOS: dict[str, list[Path]] = {
    "avisa-edital": [PROJETOS / "ajudamed"],
    "pingado": [PROJETOS / "cafesaas"],
    "nous-clinical": [PROJETOS / "medsaas"],
    "aggron": [PROJETOS / "poolcompras"],
    "dumpai": [PROJETOS / "appfotos"],
    "atendimento-whatsapp": [PROJETOS / "secretaria-ia"],
    "credito-nda": [PROJETOS / "credito-saas"],
    "portais-conteudo": [PROJETOS / p for p in PORTAIS],
    "igaming-dados": [SUPER_NOVA / "play4tune", SUPER_NOVA / "MultiBet", CASA / "Repos" / "play4tune-analytics"],
}
INDICE_LICOES = CASA / ".claude" / "memory-global" / "global_index.json"
AUTOR = re.compile(r"mateus", re.I)


def carregar() -> dict:
    return json.loads(DADOS.read_text(encoding="utf-8"))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def meu(autor: str) -> bool:
    return "bot" not in autor.lower() and AUTOR.search(autor) is not None


def funcoes_de_teste(repo: Path) -> int:
    pasta = repo / "tests"
    if not pasta.exists():
        return 0
    return sum(len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M))
               for f in pasta.rglob("*.py"))


def contar(slug: str) -> dict:
    datas, bots = [], 0
    for repo in REPOS[slug]:
        for linha in git(repo, "log", "--format=%an\t%ad", "--date=short").splitlines():
            autor, data = linha.split("\t")
            if "bot" in autor.lower():
                bots += 1
            elif meu(autor):
                datas.append(data)
    datas.sort()
    if not datas:
        raise SystemExit(f"{slug}: nenhum commit meu — conferir `git -C <repo> log --format=%an | sort -u`")
    return {"humanos": len(datas), "bot": bots, "inicio": datas[0], "fim": datas[-1],
            "testes": sum(funcoes_de_teste(r) for r in REPOS[slug])}


def contar_mutacao(slug: str) -> int:
    total = 0
    for repo in REPOS[slug]:
        blocos = git(repo, "log", "--format=%an%x00%B%x01").split("\x01")
        total += sum(1 for b in blocos if "\x00" in b and meu(b.split("\x00")[0])
                     and re.search(r"muta[cç]", b.split("\x00")[1], re.I))
    return total


def produtos_com_repo(d: dict) -> list[str]:
    return [p["slug"] for p in d["projetos"] if p["tipo"] == "produto" and p["slug"] in REPOS]


def br(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def en(n: int) -> str:
    return f"{n:,}"


def _faixa(c: dict, fmt_curto: str, fmt_longo: str) -> str:
    ini, fim = date.fromisoformat(c["inicio"]), date.fromisoformat(c["fim"])
    primeiro = ini.strftime(fmt_longo if ini.year != fim.year else fmt_curto)
    return f"{primeiro} e {fim.strftime(fmt_longo)}"


def fato_commits(c: dict) -> str:
    base = f"{c['humanos']} commits meus entre {_faixa(c, '%d/%m', '%d/%m/%Y')}"
    return base + (f", fora {c['bot']} automáticos do bot" if c["bot"] else "")


def fato_commits_en(c: dict) -> str:
    faixa = _faixa(c, "%m/%d", "%m/%d/%Y").replace(" e ", " and ")
    base = f"{c['humanos']} of my commits between {faixa}"
    return base + (f", plus {c['bot']} automated bot commits" if c["bot"] else "")


def _e_fato_commits(f: str) -> bool:
    return re.match(r"\d[\d.,]* (commits|of my commits)", f) is not None


def _e_fato_testes(f: str) -> bool:
    return re.match(r"\d[\d.,]* (funções de teste|test functions)$", f) is not None


def aplicar(d: dict, d_en: dict) -> dict:
    """Grava as contagens nos dois JSONs (em memória) e devolve o resumo impresso."""
    por_slug = {p["slug"]: p for p in d["projetos"]}
    por_slug_en = {p["slug"]: p for p in d_en["projetos"]}
    contagens = {slug: contar(slug) for slug in REPOS}
    for slug, c in contagens.items():
        for proj, fato_c, fato_t in ((por_slug[slug], fato_commits, f"{br(c['testes'])} funções de teste"),
                                     (por_slug_en[slug], fato_commits_en, f"{en(c['testes'])} test functions")):
            fatos = proj["fatos"]
            fatos[:] = [fato_c(c) if _e_fato_commits(f) else f for f in fatos]
            if c["testes"]:
                fatos[:] = [fato_t if _e_fato_testes(f) else f for f in fatos]
        print(f"{slug:20} commits {c['humanos']:4} (+{c['bot']} bot)  testes {c['testes']:5}  {c['inicio']}..{c['fim']}")

    produtos = produtos_com_repo(d)
    com_py = [s for s in produtos if contagens[s]["testes"]]
    total_c = sum(contagens[s]["humanos"] for s in produtos)
    total_t = sum(contagens[s]["testes"] for s in com_py)
    licoes = len(json.loads(INDICE_LICOES.read_text(encoding="utf-8"))["lessons"])
    avisa, mut = contagens["avisa-edital"], contar_mutacao("avisa-edital")

    d["numeros"][0]["valor"] = d_en["numeros"][0]["valor"] = str(licoes)
    d["numeros"][1].update(valor=br(total_c), rotulo=f"commits meus em {len(produtos)} produtos próprios, em 2026")
    d_en["numeros"][1].update(valor=en(total_c), rotulo=f"of my commits across {len(produtos)} own products, in 2026")
    d["numeros"][2].update(valor=br(total_t), rotulo=f"funções de teste nos {len(com_py)} produtos em Python")
    d_en["numeros"][2].update(valor=en(total_t), rotulo=f"test functions in the {len(com_py)} Python products")
    for m in d["metodo"]:
        m["texto"] = re.sub(r"\d+ dos \d+ commits meus", f"{mut} dos {avisa['humanos']} commits meus", m["texto"])
    for m in d_en["metodo"]:
        m["texto"] = re.sub(r"\d+ of my \d+ commits", f"{mut} of my {avisa['humanos']} commits", m["texto"])
    return {"licoes": licoes, "commits": total_c, "testes": total_t, "mutacao": mut, "avisa": avisa["humanos"]}


def main() -> int:
    d, d_en = carregar(), json.loads(DADOS_EN.read_text(encoding="utf-8"))
    antes, antes_en = json.dumps(d, ensure_ascii=False), json.dumps(d_en, ensure_ascii=False)
    r = aplicar(d, d_en)
    print(f"lições {r['licoes']} · commits {r['commits']} · testes {r['testes']} · mutação no Avisa {r['mutacao']}/{r['avisa']}")
    if json.dumps(d, ensure_ascii=False) == antes and json.dumps(d_en, ensure_ascii=False) == antes_en:
        print("nada mudou")
        return 0
    if "--aplicar" not in sys.argv:
        print("há números novos — rode com --aplicar para gravar")
        return 1
    hoje = date.today().isoformat()
    d["site"]["medido_em"] = d_en["site"]["medido_em"] = hoje
    for caminho, dados in ((DADOS, d), (DADOS_EN, d_en)):
        caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(RAIZ / "build.py")], check=True)
    print("gravado. Se a edição mudou, rode também: python scripts/gerar_og.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar o teste (ainda falha em `produtos_com_repo`: 8 — os projetos novos só entram na Task 2)**

Run: `py -3.12 -m pytest -q tests/test_recontar.py`
Expected: 3 passed, 1 failed (`len(produtos) == 8` → 6). Aceitável até a Task 2.

- [ ] **Step 5: Commit**

```powershell
git add scripts/recontar.py tests/test_recontar.py
git commit -m "recontar: REPOS com caminhos absolutos por slug, commits por autor, rotulos derivados"
```

---

### Task 2: Conteúdo novo em `dados.json` e `dados.en.json`

**Files:**
- Modify: `conteudo/dados.json`, `conteudo/dados.en.json`
- Test: `tests/test_build.py` (testes novos; ver Step 1)

- [ ] **Step 1: Testes novos em `tests/test_build.py` (acrescentar ao fim da seção "números derivados" e à seção das duas línguas)**

Substituir a função `test_numeros_agregados_batem_com_os_fatos_dos_projetos` e as constantes `QUATRO_FLASK`/`CINCO` por:

```python
def _fato_num(f: str, sufixo: str) -> int | None:
    m = re.match(r"(\d[\d.]*) " + sufixo, f)
    return _num(m.group(1)) if m else None


def test_numeros_agregados_batem_com_os_fatos_dos_projetos():
    """Os agregados são SOMAS dos fatos de cada produto com repositório (recontar.REPOS) — se um
    produto for atualizado e o agregado não, o teste acusa (número fora do código envelhece)."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    import recontar
    commits = testes = 0
    for pr in D["projetos"]:
        if pr["tipo"] != "produto" or pr["slug"] not in recontar.REPOS:
            continue
        for f in pr["fatos"]:
            commits += _fato_num(f, "commits") or 0
            testes += _fato_num(f, "funções de teste") or 0
    por_rotulo = {n["rotulo"]: n["valor"] for n in D["numeros"]}
    assert _num(next(v for r, v in por_rotulo.items() if "commits" in r)) == commits
    assert _num(next(v for r, v in por_rotulo.items() if "funções de teste" in r)) == testes
```

Acrescentar ao fim do arquivo:

```python
# ------------------------------------------------------------------ empregador, datas e formação
def test_experiencia_e_formacao_sao_a_fonte_unica_e_batem_nas_duas_linguas():
    assert [x["id"] for x in D["experiencia"]] == ["super-nova", "costa-oeste", "adama"]
    for pt, en in zip(D["experiencia"], EN["experiencia"]):
        assert (pt["id"], pt["inicio"], pt["fim"]) == (en["id"], en["inicio"], en["fim"])
    assert D["experiencia"][0]["fim"] == "2026-11" and D["experiencia"][0]["inicio"] == "2025-10"
    assert isinstance(D["perfil"]["formacao"], list) and len(D["perfil"]["formacao"]) == 2
    for pt, en in zip(D["perfil"]["formacao"], EN["perfil"]["formacao"]):
        assert (pt["inicio"], pt["fim"]) == (en["inicio"], en["fim"])
    anos = {(f["inicio"], f["fim"]) for f in D["perfil"]["formacao"]}
    assert anos == {("2022", "2025"), ("2018", "2021")}


def test_resume_json_tem_trabalho_datado_e_formacao_com_anos():
    r = json.loads(GERADO["resume.json"])
    assert r["work"][0]["endDate"] == "2026-11" and r["work"][0]["startDate"] == "2025-10"
    assert r["work"][0]["name"] == D["experiencia"][0]["empresa"]
    assert len(r["education"]) == 2 and all(e["startDate"] and e["endDate"] for e in r["education"])


def test_site_nomeia_o_empregador_e_nao_diz_mais_nome_omitido():
    h = GERADO["index.html"]
    assert "nome omitido" not in h and "name omitted" not in GERADO["en/index.html"]
    assert build.e(D["perfil"]["cargo"]) in h and build.e(D["perfil"]["subtitulo"]) in h   # `&` sai como &amp;
    assert "Super Nova" in h and "nov/2026" in h.lower()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `py -3.12 -m pytest -q tests/test_build.py -k "experiencia or resume_json_tem_trabalho or nomeia"`
Expected: 3 failed (`KeyError: 'experiencia'`, `KeyError: 'endDate'`, `AssertionError`).

- [ ] **Step 3: Editar `conteudo/dados.json`** — aplicar exatamente estas mudanças (Edit tool, um trecho por vez; o restante do arquivo fica igual)

`site.descricao`:
```
"Mateus Fabro, engenheiro de dados e analytics em Londrina (PR): sistemas de dados, produtos próprios e as retificações de cada erro que virou regra verificável."
```

`perfil.cargo`, `perfil.subtitulo`, `perfil.resumo`, `perfil.formacao`:
```json
"cargo": "Engenheiro de Dados & Analytics",
"subtitulo": "Construo o pipeline e o produto em volta dele — Python · SQL · TypeScript",
"resumo": [
  "Trabalhei com dados em iGaming de outubro de 2025 a novembro de 2026, quando a operação encerrou: três casas, três países e três moedas. membro do squad de quatro pessoas.",
  "Fora do expediente, construí produtos próprios e opero os que estão no ar: um radar de concursos e convocações de saúde (PR e SP), um sistema de cafeteria com cliente real em produção, um SaaS de clínicas, uma plataforma de compra cooperativa, um app de fotos com IA, cinco portais de conteúdo com dados oficiais e um SaaS de crédito sob NDA.",
  "Trabalho em par com agentes de IA (Claude Code) e com um sistema de memória próprio: cada erro corrigido que vale para outro projeto vira uma lição com origem, motivo e forma de aplicar — e um script prova que o índice não esqueceu nenhuma."
],
"formacao": [
  {"curso": "Administração", "instituicao": "Universidade Anhembi Morumbi", "inicio": "2022", "fim": "2025", "status": "concluído"},
  {"curso": "Ciências Contábeis", "instituicao": "Universidade Estadual de Londrina (UEL)", "inicio": "2018", "fim": "2021", "status": "incompleto"}
],
```

Inserir a chave `experiencia` logo depois de `perfil` (antes de `numeros`):
```json
"experiencia": [
  {"id": "super-nova", "empresa": "Super Nova Gaming / MultiBet (Grupo PGX)", "cargo": "Analista de Dados", "inicio": "2025-10", "fim": "2026-11", "local": "remoto",
   "resumo": "Squad de dados de 4 pessoas para três operações de iGaming (Brasil/BRL, Paquistão/PKR, Colômbia/COP). membro do squad de quatro pessoas. Saída pelo encerramento da operação em novembro de 2026."},
  {"id": "costa-oeste", "empresa": "Costa Oeste / Terceirize", "cargo": "Analista Administrativo", "inicio": "2025-07", "fim": "2025-09", "local": "Londrina, PR",
   "resumo": "KPIs operacionais e dashboards em Power BI; rotinas de governança de dados administrativos."},
  {"id": "adama", "empresa": "ADAMA", "cargo": "Assistente de Crédito e Cobrança", "inicio": "2020-10", "fim": "2024-09", "local": "Londrina, PR", "nota": "estágio em 2019–2020",
   "resumo": "Contas a receber e operações de FIDC; análise de crédito PJ/PF com garantias (CPR, alienação fiduciária, caução); dashboards Power BI para os times Brasil e Global; atuação no Portal de Crédito."}
],
```

`numeros[1]`, `numeros[2]`, `numeros[3]` (o `recontar` sobrescreve `valor` e `rotulo` de [1] e [2]; `fonte` é texto):
```json
{"valor": "820", "rotulo": "commits meus em 8 produtos próprios, em 2026", "fonte": "git log dos repositórios dos produtos, só commits de minha autoria, sem os automáticos de bot"},
{"valor": "2.675", "rotulo": "funções de teste nos 4 produtos em Python", "fonte": "contagem de def test_ em tests/ dos produtos com suíte pytest"},
{"valor": "3", "rotulo": "operações de iGaming, em 3 países e 3 moedas", "fonte": "Super Nova Gaming, out/2025 – nov/2026"},
```

Projeto `avisa-edital` — trocar `linha`, `para_quem`, `fatos`, `status`:
```json
"linha": "Alerta no Telegram quando sai concurso, convocação ou nomeação para médicos no Paraná e em São Paulo.",
"para_quem": "Médicos que prestaram concurso ou PSS e não podem perder o prazo de uma convocação — em geral de 3 a 5 dias úteis.",
"fatos": [
  "182 commits meus entre 12/08 e 21/09/2026, fora 27 automáticos do bot",
  "1.055 funções de teste",
  "PR e SP: diários oficiais municipais e estaduais, bancas e fontes de convocação, coletados numa VM com systemd e complementados por GitHub Actions",
  "assinatura pela Kiwify com teste grátis de 7 dias sem cartão, pelo próprio bot"
],
"status": "No ar desde agosto de 2026; operação diária desde outubro",
```

Projeto `pingado` — trocar `papel`, `fatos`, `status`:
```json
"papel": "Desenvolvedor e dono do produto: reuniões com a cliente e cada versão entregue em até um dia após a reunião, da v0.2 em diante.",
"fatos": ["234 commits entre 06/07 e 18/09/2026", "772 funções de teste", "cliente real com duas lojas em produção"],
"status": "Em produção desde setembro de 2026, evoluindo com a cliente",
```

Projeto `nous-clinical` — `status`: `"Última versão em 06/10/2026"`.

Projeto `atendimento-whatsapp` — acrescentar como **primeiro** fato: `"8 commits entre 16/09 e 30/10/2026"` (o `recontar` corrige).

Projeto `igaming-dados` — trocar `nome`, `para_quem`, `papel`, `fatos`, `status`, `historia`:
```json
"nome": "Super Nova Gaming / MultiBet (Grupo PGX)",
"para_quem": "Squad de dados de 4 pessoas atendendo três operações de iGaming; membro do squad de quatro pessoas.",
"papel": "Analista de dados de out/2025 a nov/2026, com trabalho de engenharia de ponta a ponta.",
"fatos": [
  "855 commits meus entre 04/06 e 23/10/2026",
  "migração de data lake (3,07 bi de registros, 234 tabelas): camada de conexão com fonte única e rollback por uma variável, preservando a interface dos ~71 pipelines consumidores",
  "custo de mídia (Meta, Google Ads, TikTok) num tracker de atribuição multi-tenant, substituindo um fornecedor pago",
  "serviço diário de risco e score de crédito de jogador",
  "linter multi-tenant que falha fechado: lista de exceções de 43 para 3",
  "consulta crítica de 240 s para 21 s, com equivalência provada por conjunto"
],
"status": "Encerrado em nov/2026 (fim da operação)",
"historia": "A maior parte das retificações deste diário nasceu aqui. Os números são reais; os nomes de cliente ficam de fora."
```

Inserir **antes** de `igaming-dados` (depois de `atendimento-whatsapp`) os dois projetos novos:
```json
{
  "slug": "credito-nda",
  "nome": "SaaS de crédito (sob NDA)",
  "tipo": "produto",
  "linha": "Gestão de crédito multi-tenant para operadores pequenos: painel da equipe e portal do tomador como PWA.",
  "para_quem": "Operadores de crédito de pequeno porte. Detalhes de negócio sob acordo de confidencialidade.",
  "papel": "Arquitetura e implementação de ponta a ponta, com um sócio como dono do produto.",
  "stack": ["Next.js 16 + TypeScript", "PWA com branding por tenant", "PostgreSQL (Supabase) com RLS por tenant", "GitHub Actions", "Docker (e2e em contêiner)", "Vercel"],
  "fatos": [
    "65 commits entre 13/10 e 28/10/2026",
    "backup diário restaurado num banco descartável e conferido em CI: contagens, migrações e políticas de isolamento",
    "auto-cadastro público com checagem antifraude e aprovação em um clique"
  ],
  "status": "Piloto no ar desde outubro de 2026",
  "url": "",
  "historia": "Quando o controle de aplicativos do sistema bloqueou o binário nativo de hash de senha, o ambiente de desenvolvimento foi para um contêiner — e o e2e junto."
},
{
  "slug": "portais-conteudo",
  "nome": "Portais de conteúdo com dados oficiais",
  "tipo": "produto",
  "linha": "Cinco portais estáticos de finanças e direitos, com indicadores que se atualizam sozinhos a partir de fontes oficiais.",
  "para_quem": "Leitores brasileiros (crédito, renda fixa, direitos trabalhistas, finanças em dólar) e um público dos EUA (finanças pessoais).",
  "papel": "Construí os cinco: coleta dos indicadores, build, revisão editorial assistida por IA com aprovação humana e publicação em domínio próprio.",
  "stack": ["Astro 7", "TypeScript", "GitHub Actions", "APIs oficiais (Banco Central/SGS, FRED, IBGE, Tesouro, ANP)", "Vercel"],
  "fatos": [
    "40 commits entre 20/10 e 03/11/2026",
    "33 a 45 guias por portal, cada um com fonte primária",
    "indicadores recalculados por workflow, não digitados"
  ],
  "status": "No ar desde outubro de 2026; monetização em avaliação",
  "url": "https://guiadocredito.com.br",
  "historia": "A primeira versão de um deles trazia foto e credenciais de um autor que não existia, geradas por IA. Saíram antes da publicação: texto assinado por pessoa, ou não assinado."
},
```

`disponibilidade`:
```json
{"status": "em busca de vaga", "texto": "Em busca de vaga de engenharia de dados, analytics engineering ou desenvolvimento de produto — PJ ou CLT, remoto. Converso também sobre projeto fechado. O jeito mais rápido é o e-mail.", "canal": "mateusrfabro@hotmail.com"}
```

`faq[0].resposta` e `faq[3].resposta`:
```
"Engenheiro de dados e analytics em Londrina (PR). Trabalhou com dados de três operações de iGaming até novembro de 2026 e constrói produtos próprios: Avisa Edital, Pingado, Nous Clinical, Aggron, DumpAI e cinco portais de conteúdo."
"Sim: em busca de vaga, PJ ou CLT, remoto. Contato por e-mail: mateusrfabro@hotmail.com."
```

- [ ] **Step 4: Editar `conteudo/dados.en.json`** com os equivalentes (mesmos slugs na mesma ordem, mesmos números):

`site.descricao`: `"Mateus Fabro, data & analytics engineer in Londrina, Brazil: data systems, his own products and the corrections for every mistake that became a checkable rule."`

`perfil`:
```json
"cargo": "Data & Analytics Engineer",
"subtitulo": "I build the pipeline and the product around it — Python · SQL · TypeScript",
"resumo": [
  "I worked with data in iGaming from October 2025 to November 2026, when the operation shut down: three brands, three countries and three currencies. member of the four-person squad.",
  "Outside work, I built my own products and run the ones that are live: an alert service for public-health job calls (PR and SP), a café management system with a real customer in production, a clinic SaaS, a group-buying platform, an AI photo app, five content portals fed by official data and a credit SaaS under NDA.",
  "I work paired with AI agents (Claude Code) and with a memory system of my own: every fixed mistake that applies to another project becomes a lesson with an origin, a reason and a way to apply it — and a script proves the index forgot none."
],
"formacao": [
  {"curso": "Business Administration", "instituicao": "Universidade Anhembi Morumbi", "inicio": "2022", "fim": "2025", "status": "completed"},
  {"curso": "Accounting", "instituicao": "Universidade Estadual de Londrina (UEL)", "inicio": "2018", "fim": "2021", "status": "incomplete"}
],
```

`experiencia` (mesmos `id`, `inicio`, `fim`):
```json
"experiencia": [
  {"id": "super-nova", "empresa": "Super Nova Gaming / MultiBet (PGX Group)", "cargo": "Data Analyst", "inicio": "2025-10", "fim": "2026-11", "local": "remote",
   "resumo": "Four-person data squad serving three iGaming operations (Brazil/BRL, Pakistan/PKR, Colombia/COP). member of the four-person squad. Left when the operation shut down in November 2026."},
  {"id": "costa-oeste", "empresa": "Costa Oeste / Terceirize", "cargo": "Administrative Analyst", "inicio": "2025-07", "fim": "2025-09", "local": "Londrina, Brazil",
   "resumo": "Operational KPIs and Power BI dashboards; administrative data governance routines."},
  {"id": "adama", "empresa": "ADAMA", "cargo": "Credit & Collections Assistant", "inicio": "2020-10", "fim": "2024-09", "local": "Londrina, Brazil", "nota": "internship in 2019–2020",
   "resumo": "Accounts receivable and FIDC operations; corporate and retail credit analysis with collateral; Power BI dashboards for the Brazil and Global teams; Credit Portal."}
],
```

`numeros[1..3]`:
```json
{"valor": "820", "rotulo": "of my commits across 8 own products, in 2026", "fonte": "git log of the product repositories, my commits only, excluding automated bot commits"},
{"valor": "2,675", "rotulo": "test functions in the 4 Python products", "fonte": "count of def test_ under tests/ in the products with a pytest suite"},
{"valor": "3", "rotulo": "iGaming operations, in 3 countries and 3 currencies", "fonte": "Super Nova Gaming, Oct 2025 – Nov 2026"},
```

Projetos EN — `avisa-edital`: `linha` `"Telegram alert when a public exam, job call or appointment for physicians is published in Paraná or São Paulo."`, `para_quem` `"Physicians who sat a public exam or selection process and cannot miss a job-call deadline — usually 3 to 5 business days."`, `fatos` `["182 of my commits between 08/12 and 09/21/2026, plus 27 automated bot commits", "1,055 test functions", "PR and SP: municipal and state official gazettes, exam boards and job-call sources, collected on a VM with systemd and complemented by GitHub Actions", "Kiwify subscription with a 7-day free trial, no card, from the bot itself"]`, `status` `"Live since August 2026; daily operation since October"`.
`pingado`: `papel` `"Developer and product owner: meetings with the customer and each version delivered within a day of the meeting, from v0.2 on."`, `fatos` `["234 commits between 07/06 and 09/18/2026", "772 test functions", "real customer with two stores in production"]`, `status` `"In production since September 2026, evolving with the customer"`.
`nous-clinical`: `status` `"Last version on 10/06/2026"`.
`atendimento-whatsapp`: primeiro fato `"8 commits between 09/16 and 10/30/2026"`.
Novos (antes de `igaming-dados`):
```json
{"slug": "credito-nda", "nome": "Credit SaaS (under NDA)", "tipo": "produto",
 "linha": "Multi-tenant credit management for small lenders: a staff panel and a borrower portal as a PWA.",
 "para_quem": "Small credit operators. Business details under a non-disclosure agreement.",
 "papel": "End-to-end architecture and implementation, with a partner as product owner.",
 "stack": ["Next.js 16 + TypeScript", "PWA with per-tenant branding", "PostgreSQL (Supabase) with per-tenant RLS", "GitHub Actions", "Docker (e2e in a container)", "Vercel"],
 "fatos": ["65 commits between 10/13 and 10/28/2026", "daily backup restored into a throwaway database and checked in CI: row counts, migrations and isolation policies", "public self-signup with anti-fraud checks and one-click approval"],
 "status": "Pilot live since October 2026", "url": "",
 "historia": "When the OS application control blocked the native password-hashing binary, development moved into a container — and the e2e suite with it."},
{"slug": "portais-conteudo", "nome": "Content portals fed by official data", "tipo": "produto",
 "linha": "Five static portals on finance and labor rights, with indicators that refresh themselves from official sources.",
 "para_quem": "Brazilian readers (credit, fixed income, labor rights, dollar finance) and a U.S. audience (personal finance).",
 "papel": "Built all five: indicator collection, build, AI-assisted editorial review with human approval, and publication on their own domains.",
 "stack": ["Astro 7", "TypeScript", "GitHub Actions", "Official APIs (Central Bank/SGS, FRED, IBGE, Treasury, ANP)", "Vercel"],
 "fatos": ["40 commits between 10/20 and 11/03/2026", "33 to 45 guides per portal, each with a primary source", "indicators recomputed by workflow, never typed in"],
 "status": "Live since October 2026; monetization under evaluation", "url": "https://guiadocredito.com.br",
 "historia": "The first version of one of them carried the photo and credentials of an author who did not exist, generated by AI. They came out before publication: text signed by a person, or unsigned."},
```
`igaming-dados` EN: `nome` `"Super Nova Gaming / MultiBet (PGX Group)"`, `para_quem` `"Four-person data squad serving three iGaming operations; member of the four-person squad."`, `papel` `"Data analyst from Oct 2025 to Nov 2026, with end-to-end engineering work."`, `fatos` = `["855 of my commits between 06/04 and 10/23/2026"] + os 5 fatos EN atuais`, `status` `"Ended in Nov 2026 (operation shut down)"`, `historia` `"Most of this gazette's corrections were born here. The numbers are real; client names are left out."`
`disponibilidade`: `{"status": "looking for a role", "texto": "Looking for a data engineering, analytics engineering or product development role — contractor or employee, remote. Also open to fixed-scope projects. Email is the fastest way.", "canal": "mateusrfabro@hotmail.com"}`
`faq[0]`: `"A data and analytics engineer in Londrina, Brazil. He worked with data for three iGaming operations until November 2026 and builds his own products: Avisa Edital, Pingado, Nous Clinical, Aggron, DumpAI and five content portals."`; `faq[3]`: `"Yes: looking for a role, contractor or employee, remote. Contact by email: mateusrfabro@hotmail.com."`

- [ ] **Step 5: Validar JSON e rodar o recontar (sem gravar) para ver os números reais**

```powershell
py -3.12 -c "import json;json.load(open('conteudo/dados.json',encoding='utf-8'));json.load(open('conteudo/dados.en.json',encoding='utf-8'));print('json ok')"
py -3.12 scripts/recontar.py
```
Expected: tabela com 9 slugs e "há números novos". Conferir que `igaming-dados` tem centenas de commits (não zero: se der zero, o filtro de autor não casou — ver `git -C <repo> log --format=%an | sort -u`).

- [ ] **Step 6: Gravar os números, regenerar e testar**

```powershell
py -3.12 scripts/recontar.py --aplicar
py -3.12 -m pytest -q
```
Expected: todos verdes **exceto** `test_imagem_de_compartilhamento_existe_e_nao_envelheceu` (og.png fica para a Task 3) e os 3 novos de resume/empregador (ficam para a Task 3). Se `test_metodo_cita_os_mesmos_commits_do_projeto` falhar, o regex do método não casou: conferir o texto de `metodo[2]`.

- [ ] **Step 7: Commit**

```powershell
git add conteudo/dados.json conteudo/dados.en.json tests/test_build.py
git commit -m "conteudo: empregador nomeado (out/2025 - nov/2026), formacao em lista, experiencia, 2 projetos novos, disponibilidade e numeros recontados"
```
(O hook roda `--check`; se acusar `public/` desatualizado, rodar `py -3.12 build.py` e `git add public/` arquivo a arquivo — ou `git add public` é aceitável aqui porque é saída gerada? **Não**: o hook global bloqueia diretório. Usar `git add (git ls-files -m -o --exclude-standard public)` no PowerShell: `git ls-files -m -o --exclude-standard public | % { git add $_ }`.)

---

### Task 3: `build.py` lê `experiencia`/`formacao`, linka o currículo e nomeia

**Files:**
- Modify: `build.py` (funções `T`, `markdown`, `llms_txt`, `resume_json`, `pagina`, `main`)
- Modify: `api/mcp.py:35` (descrição)
- Modify: `scripts/gerar_og.py` (só rodar)

- [ ] **Step 1: Editar `build.py`**

Em `T["pt"]` acrescentar as chaves (dentro do dicionário, após `"p_fatos"`):
```python
        "cv": "Currículo (PDF)", "md_cv": "Currículo em PDF", "cv_arquivo": "mateus-fabro-pt.pdf",
```
e trocar `l_ret` para terminar em `"... Nomes de cliente ficam de fora."` (remover "de empresa e").
Em `T["en"]`:
```python
        "cv": "Résumé (PDF)", "md_cv": "Résumé as PDF", "cv_arquivo": "mateus-fabro-en.pdf",
```
e `l_ret` → `"... Client names are left out."`.

Em `markdown()`, na lista `md_agentes`, acrescentar depois da linha do resume:
```python
          f"- {t['md_cv']}: {s['url']}/curriculo/{t['cv_arquivo']}",
```

Em `llms_txt()`, após a linha do JSON Resume:
```python
         f"- [Currículo em PDF]({s['url']}/curriculo/mateus-fabro-pt.pdf): para imprimir (English: {s['url']}/curriculo/mateus-fabro-en.pdf)",
```

Substituir `resume_json()` inteira:
```python
def resume_json(d: dict) -> dict:
    p, s = d["perfil"], d["site"]
    trabalho = next(pr for pr in d["projetos"] if pr["tipo"] == "trabalho")
    work = []
    for x in d["experiencia"]:
        item = {"name": x["empresa"], "position": x["cargo"], "startDate": x["inicio"], "endDate": x["fim"],
                "summary": x["resumo"] + (f" ({x['nota']})" if x.get("nota") else "")}
        if x["id"] == "super-nova":
            item["highlights"] = trabalho["fatos"]
        work.append(item)
    return {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {
            "name": p["nome"], "label": p["cargo"], "email": p["email"], "url": s["url"],
            "summary": " ".join(p["resumo"]),
            "location": {"city": p["cidade"], "region": p["estado"], "countryCode": "BR"},
            "profiles": [{"network": "GitHub", "username": "mateusrfabro", "url": p["github"]},
                         {"network": "LinkedIn", "url": p["linkedin"]}],
        },
        "work": work,
        "projects": [{"name": pr["nome"], "description": pr["linha"], "highlights": pr["fatos"],
                      "keywords": pr["stack"], **({"url": pr["url"]} if pr.get("url") else {})}
                     for pr in d["projetos"] if pr["tipo"] == "produto"],
        "education": [{"institution": f["instituicao"], "area": f["curso"],
                       "studyType": f"Graduação ({f['status']})", "startDate": f["inicio"], "endDate": f["fim"]}
                      for f in p["formacao"]],
        "languages": [{"language": i.split(" (")[0], "fluency": i.split("(")[1].rstrip(")")}
                      for i in p["idiomas"]],
        "meta": {"lastModified": s["medido_em"], "version": f"edicao-{edicao(d)}"},
    }
```

Em `pagina()`, na linha do `<p class="contato-topo">`, inserir antes do `<a href="#convocacao">`:
```python
<a href="/curriculo/{t['cv_arquivo']}">{t['cv']}</a>
```
e, na lista `<ul>` da seção `maquinas`, acrescentar um item:
```python
      <li><a href="/curriculo/{t['cv_arquivo']}"><code>/curriculo/{t['cv_arquivo']}</code></a> · <a href="/resume.json"><code>/resume.json</code></a></li>
```
(e remover `/resume.json` do item anterior para não duplicar).

Em `json_ld()`, `knowsAbout`: manter a lista e acrescentar `"Next.js"`, `"Flask"` ao fim.

Em `main()`, dentro do `if "--check"`, logo após calcular `velhos`:
```python
        sys.path.insert(0, str(RAIZ / "scripts"))
        import gerar_pecas
        velhos += gerar_pecas.curriculo_desatualizado()
```
e trocar a mensagem de erro por:
```python
            dica = "python scripts/gerar_pecas.py curriculo" if all(v.startswith("curriculo/") for v in velhos) else "python build.py"
            print(f"public/ desatualizado — rode `{dica}`:", ", ".join(velhos))
```
(`gerar_pecas` nasce na Task 5; até lá, proteger com `try: ... except ImportError: pass` e **remover** o `try` na Task 5.)

- [ ] **Step 2: `api/mcp.py`** — descrição de `listar_projetos`: `"Projetos (produtos próprios e o trabalho em iGaming, 2025–2026), com status real. Filtro opcional tipo = 'produto' ou 'trabalho'."`

- [ ] **Step 3: Regenerar, capa OG e testes**

```powershell
py -3.12 build.py
py -3.12 scripts/gerar_og.py
py -3.12 -m pytest -q
```
Expected: tudo verde (47 testes: 40 + 4 de `test_recontar.py` + 3 novos). Abrir `public/og.png` com o Read tool e conferir que o cargo cabe na linha.

- [ ] **Step 4: Commit**

```powershell
git add build.py api/mcp.py
git ls-files -m -o --exclude-standard public | % { git add $_ }
git commit -m "site: resume.json com experiencia e formacao datadas, link para o curriculo, empregador nomeado, capa OG regerada"
```

---

### Task 4: `conteudo/curriculo.json` (prosa do currículo, PT e EN)

**Files:**
- Create: `conteudo/curriculo.json`
- Test: `tests/test_build.py` (1 teste novo)

- [ ] **Step 1: Teste**

```python
def test_curriculo_json_bullet_com_numero_tem_fonte():
    cv = json.loads((RAIZ / "conteudo" / "curriculo.json").read_text(encoding="utf-8"))
    for lang in ("pt", "en"):
        for bloco in cv["experiencia"]["super-nova"][lang] + [{"itens": cv["experiencia"][k][lang]} for k in ("costa-oeste", "adama")]:
            for item in bloco["itens"]:
                assert item["texto"].strip()
                if re.search(r"\d", item["texto"]):
                    assert item.get("fonte", "").strip(), f"[{lang}] sem fonte: {item['texto'][:60]}"
        assert len(cv["resumo"][lang]) <= 4
        assert {c["categoria"] for c in cv["stack"][lang]}
```

- [ ] **Step 2: Rodar e ver falhar** — `py -3.12 -m pytest -q -k curriculo_json` → FileNotFoundError.

- [ ] **Step 3: Criar `conteudo/curriculo.json`**

```json
{
  "resumo": {
    "pt": [
      "Engenheiro de dados e analytics: projeto, construo e opero sistemas de dados de ponta a ponta — pipelines, antifraude, atribuição de mídia, APIs e painéis — e também o produto em volta do dado, em Python e TypeScript.",
      "De out/2025 a nov/2026, num squad de dados de 4 pessoas, atendi três operações de iGaming em três países e três moedas num squad de dados de quatro pessoas.",
      "Fora do expediente, construí e opero produtos próprios com cliente real em produção, cobertos por testes e com status honesto — inclusive os que pararam.",
      "Uso agentes de IA (Claude Code) como multiplicador, com memória em camadas e gates de qualidade próprios; cada erro corrigido vira regra escrita e, quando dá, um teste."
    ],
    "en": [
      "Data and analytics engineer: I design, build and run end-to-end data systems — pipelines, anti-fraud, media attribution, APIs and dashboards — and the product around the data, in Python and TypeScript.",
      "From Oct 2025 to Nov 2026, in a four-person data squad, I served three iGaming operations in three countries and three currencies in a four-person data squad, until the operation shut down.",
      "Outside work, I built and run my own products with real customers in production, covered by tests and with an honest status — including the ones that stopped.",
      "I use AI agents (Claude Code) as a multiplier, with layered memory and my own quality gates; every fixed mistake becomes a written rule and, when possible, a test."
    ]
  },
  "experiencia": {
    "super-nova": {
      "pt": [
        {"bloco": "Engenharia de dados e plataforma", "itens": [
          {"texto": "Fiz a camada de consumo da migração do data lake (Athena legado → S3 Tables/Iceberg, 234 tabelas, 3,07 bi de registros): camada de conexão bi-ambiente com fonte única e rollback por uma variável de ambiente, sem quebrar os ~71 pipelines consumidores.", "fonte": "inventário do catálogo Iceberg ($snapshots) e lista de pipelines do repositório MultiBet (clone local), ago/2026"},
          {"texto": "Retrofit multi-tenant do analytics (duas operações nas mesmas tabelas): registry tipado de tenants, escopo obrigatório no runner de queries e linter fail-closed com allowlist-ratchet (43 → 3 exceções) e hook no editor — nascido de um incidente real de escopo de moeda.", "fonte": "repositório play4tune, scripts/lint_tenant_scope e histórico da allowlist"},
          {"texto": "Camada gold de torneios juntando três fontes (PostgreSQL, MongoDB Atlas, postgres_fdw) num contrato só, fail-closed: fonte fora do ar vira estado UNREACHABLE, nunca zero falso.", "fonte": ""},
          {"texto": "Padrão de deploy git-first em EC2 via AWS SSM com smoke test remoto e timers systemd; otimizei a consulta crítica de 240 s (timeout) para 21 s, com equivalência provada por conjunto.", "fonte": "medição antes/depois registrada no repositório play4tune, set/2026"}
        ]},
        {"bloco": "Sistemas e aplicações", "itens": [
          {"texto": "Evoluí e operei o tracker de atribuição multi-tenant (NestJS 11 + Next.js 15): postbacks de conversão, despacho para as APIs de conversão dos canais e junção de custo com receita → CAC, ROAS e LTV por campanha e criativo.", "fonte": "package.json do repositório do tracker (versões), out/2026"},
          {"texto": "Entreguei do zero o módulo de administração e autenticação (sessões opacas com hash de token, guards, audit log) e toda a camada de custo de mídia — Meta Graph API multi-BM, Google Ads e TikTok, 6 cron jobs — substituindo um fornecedor pago.", "fonte": "repositório do tracker, módulos admin/ e cost/, jun–out/2026"},
          {"texto": "Dashboards e serviços web em produção: Flask (Central de Bônus, CRM), Dash/Plotly com Docker, FastAPI e uma malha de alertas operacionais em WhatsApp (Evolution API self-hosted), Slack e Telegram com dead-man's switches de frescor.", "fonte": ""}
        ]},
        {"bloco": "Antifraude e ML", "itens": [
          {"texto": "Construí o serviço diário de risco da operação do Paquistão: 5 detectores (cluster de carteira, bônus → saque, anel de indicação, burst de e-mail, retenção de saque), delta contra snapshot e digest HTML + Telegram.", "fonte": "repositório play4tune, risk_daily, ago/2026"},
          {"texto": "PCR — score de crédito de jogador em 7 tiers com janela rolling de 90 dias, publicado de forma atômica no CRM; corrigi em pós-produção uma feature que contaminava 25% do peso do score.", "fonte": "repositório pcr-p4t e relatório de correção, ago/2026"},
          {"texto": "Inferência de gênero por primeiro nome com dicionário treinado na própria base: 99,4% de acurácia em holdout 70/30, funil auditável de 1,38 M para 208.958 classificados.", "fonte": "notebook de avaliação no repositório MultiBet (clone local), jul/2026"}
        ]},
        {"bloco": "IA aplicada", "itens": [
          {"texto": "Squad de agentes Claude Code especializados com gate obrigatório (extração → boas práticas → auditoria → entrega), skills próprias e hooks de lint; memória em três camadas (projeto → global → export) com script que prova que o índice não esqueceu nenhuma lição.", "fonte": ""},
          {"texto": "Laboratório local de modelos (Ollama + PyTorch numa RTX 4060): agente com ferramentas, fine-tuning QLoRA e baseline tabular — para saber o que roda sem API.", "fonte": "repositório lab-ia, log de 04–06/10/2026 (hardware)"}
        ]}
      ],
      "en": [
        {"bloco": "Data engineering and platform", "itens": [
          {"texto": "Built the consumer layer of the data lake migration (legacy Athena → S3 Tables/Iceberg, 234 tables, 3.07 bn records): a dual-environment connection layer with a single source and one-variable rollback, without breaking the ~71 consumer pipelines.", "fonte": "Iceberg catalog inventory ($snapshots) and pipeline list in the MultiBet repository (local clone), Aug 2026"},
          {"texto": "Multi-tenant retrofit of the analytics (two operations on the same tables): typed tenant registry, mandatory scope in the query runner and a fail-closed linter with an allowlist ratchet (43 → 3 exceptions) plus an editor hook — born from a real currency-scope incident.", "fonte": "play4tune repository, scripts/lint_tenant_scope and the allowlist history"},
          {"texto": "Gold layer for tournaments joining three sources (PostgreSQL, MongoDB Atlas, postgres_fdw) under one contract, fail-closed: a source that is down becomes UNREACHABLE, never a false zero.", "fonte": ""},
          {"texto": "Git-first EC2 deployment pattern via AWS SSM with remote smoke tests and systemd timers; optimized the critical query from 240 s (timeout) to 21 s, with set-based equivalence proof.", "fonte": "before/after measurement recorded in the play4tune repository, Sep 2026"}
        ]},
        {"bloco": "Systems and applications", "itens": [
          {"texto": "Evolved and operated the multi-tenant attribution tracker (NestJS 11 + Next.js 15): conversion postbacks, dispatch to the channels' conversion APIs and cost joined with revenue → CAC, ROAS and LTV per campaign and creative.", "fonte": "package.json of the tracker repository (versions), Oct 2026"},
          {"texto": "Delivered from scratch the admin/auth module (opaque sessions with hashed tokens, guards, audit log) and the whole media-cost layer — Meta Graph API multi-BM, Google Ads and TikTok, 6 cron jobs — replacing a paid vendor.", "fonte": "tracker repository, admin/ and cost/ modules, Jun–Oct 2026"},
          {"texto": "Dashboards and web services in production: Flask (bonus center, CRM), Dash/Plotly with Docker, FastAPI, and an operational alert mesh on WhatsApp (self-hosted Evolution API), Slack and Telegram with freshness dead-man's switches.", "fonte": ""}
        ]},
        {"bloco": "Anti-fraud and ML", "itens": [
          {"texto": "Built the daily risk service for the Pakistan operation: 5 detectors (wallet cluster, bonus → withdrawal, referral ring, e-mail burst, withdrawal retention), delta against a snapshot and an HTML + Telegram digest.", "fonte": "play4tune repository, risk_daily, Aug 2026"},
          {"texto": "PCR — player credit score in 7 tiers over a rolling 90-day window, published atomically to the CRM; fixed in post-production a feature that polluted 25% of the score's weight.", "fonte": "pcr-p4t repository and correction report, Aug 2026"},
          {"texto": "First-name gender inference with a dictionary trained on the company's own base: 99.4% accuracy on a 70/30 holdout, auditable funnel from 1.38 M down to 208,958 classified.", "fonte": "evaluation notebook in the MultiBet repository (local clone), Jul 2026"}
        ]},
        {"bloco": "Applied AI", "itens": [
          {"texto": "Squad of specialized Claude Code agents with a mandatory gate (extraction → best practices → audit → delivery), custom skills and lint hooks; three-layer memory (project → global → export) with a script that proves the index forgot no lesson.", "fonte": ""},
          {"texto": "Local model lab (Ollama + PyTorch on an RTX 4060): tool-using agent, QLoRA fine-tuning and a tabular baseline — to know what runs without an API.", "fonte": "lab-ia repository, log of Oct 4–6, 2026 (hardware)"}
        ]}
      ]
    },
    "costa-oeste": {
      "pt": [{"texto": "KPIs operacionais e dashboards em Power BI; rotinas de governança de dados administrativos.", "fonte": ""}],
      "en": [{"texto": "Operational KPIs and Power BI dashboards; administrative data governance routines.", "fonte": ""}]
    },
    "adama": {
      "pt": [
        {"texto": "Contas a receber e operações de FIDC; análise de crédito PJ/PF com garantias (CPR, alienação fiduciária, caução).", "fonte": ""},
        {"texto": "Dashboards Power BI para os times Brasil e Global; atuação no Portal de Crédito.", "fonte": ""}
      ],
      "en": [
        {"texto": "Accounts receivable and FIDC operations; corporate and retail credit analysis with collateral.", "fonte": ""},
        {"texto": "Power BI dashboards for the Brazil and Global teams; Credit Portal.", "fonte": ""}
      ]
    }
  },
  "stack": {
    "pt": [
      {"categoria": "Linguagens", "itens": "Python (pandas, SQLAlchemy, boto3, psycopg2, pytest) · TypeScript (NestJS, Next.js, React, Prisma, Jest) · SQL avançado (PostgreSQL 15, Trino/Athena) · Bash · PowerShell"},
      {"categoria": "Dados e cloud", "itens": "AWS (Athena, S3 Tables/Iceberg, EC2, RDS, SSM, IAM) · PostgreSQL (particionamento, FDW, matviews) · MongoDB Atlas · Redis · Supabase · Prefect 3 · systemd"},
      {"categoria": "Backend e web", "itens": "Flask · FastAPI · NestJS 11 · Next.js 15/16 + React 19 · Astro 7 · Tailwind · Docker/Compose · nginx/Caddy · Vercel · Render"},
      {"categoria": "Integrações", "itens": "Meta Marketing/Graph API · Google Ads · TikTok Ads · Smartico CRM · WhatsApp (Cloud API + Evolution) · Telegram · Slack · Google Calendar · Kiwify · Focus NFe · APIs do Banco Central e FRED"},
      {"categoria": "IA aplicada", "itens": "Claude Code (squads de agentes, skills, hooks, memória em camadas) · Anthropic API (multimodal, em produção) · LangChain/n8n · Ollama + PyTorch (QLoRA)"},
      {"categoria": "Segurança e práticas", "itens": "Argon2 · 2FA/TOTP · CSP · CSRF · rate-limit · RLS por tenant · sessões opacas · audit logs · LGPD/PII · git-first + smoke test · testes como gate de deploy · fail-closed por padrão · backup restaurado em CI"}
    ],
    "en": [
      {"categoria": "Languages", "itens": "Python (pandas, SQLAlchemy, boto3, psycopg2, pytest) · TypeScript (NestJS, Next.js, React, Prisma, Jest) · advanced SQL (PostgreSQL 15, Trino/Athena) · Bash · PowerShell"},
      {"categoria": "Data and cloud", "itens": "AWS (Athena, S3 Tables/Iceberg, EC2, RDS, SSM, IAM) · PostgreSQL (partitioning, FDW, matviews) · MongoDB Atlas · Redis · Supabase · Prefect 3 · systemd"},
      {"categoria": "Backend and web", "itens": "Flask · FastAPI · NestJS 11 · Next.js 15/16 + React 19 · Astro 7 · Tailwind · Docker/Compose · nginx/Caddy · Vercel · Render"},
      {"categoria": "Integrations", "itens": "Meta Marketing/Graph API · Google Ads · TikTok Ads · Smartico CRM · WhatsApp (Cloud API + Evolution) · Telegram · Slack · Google Calendar · Kiwify · Focus NFe · Central Bank and FRED APIs"},
      {"categoria": "Applied AI", "itens": "Claude Code (agent squads, skills, hooks, layered memory) · Anthropic API (multimodal, in production) · LangChain/n8n · Ollama + PyTorch (QLoRA)"},
      {"categoria": "Security and practices", "itens": "Argon2 · 2FA/TOTP · CSP · CSRF · rate limiting · per-tenant RLS · opaque sessions · audit logs · LGPD/PII · git-first + smoke tests · tests as deploy gate · fail-closed by default · backup restored in CI"}
    ]
  },
  "rotulos": {
    "pt": {"resumo": "Resumo", "numeros": "Em números", "experiencia": "Experiência", "produtos": "Produtos próprios", "stack": "Stack", "formacao": "Formação", "idiomas": "Idiomas", "remoto": "remoto", "gerado": "Gerado de conteudo/dados.json em", "status": "status", "incompleto": "incompleto", "concluido": "concluído"},
    "en": {"resumo": "Summary", "numeros": "In numbers", "experiencia": "Experience", "produtos": "Own products", "stack": "Stack", "formacao": "Education", "idiomas": "Languages", "remoto": "remote", "gerado": "Generated from conteudo/dados.en.json on", "status": "status", "incompleto": "incomplete", "concluido": "completed"}
  }
}
```

**Antes de gravar**, conferir cada `fonte` citada: o executor abre o repositório/arquivo nomeado e confirma que o número existe lá (ex.: `grep -r "43" play4tune/scripts/lint*` para o ratchet; `99,4` no notebook). Fonte que não se confirma → o bullet perde o número (reescrever sem dígito) ou sai.

- [ ] **Step 4: Rodar o teste** — `py -3.12 -m pytest -q -k curriculo_json` → PASS.

- [ ] **Step 5: Commit**

```powershell
git add conteudo/curriculo.json tests/test_build.py
git commit -m "conteudo: prosa do curriculo (PT/EN) com fonte por bullet numerico"
```

---

## Chunk 2: Gerador de peças (U3, U4, U5)

### Task 5: `scripts/gerar_pecas.py` — currículo HTML + PDF

**Files:**
- Create: `scripts/gerar_pecas.py`, `scripts/templates/curriculo.html`
- Create: `tests/test_pecas.py`
- Modify: `build.py:main` (remover o `try` da Task 3), `.vercelignore` (acrescentar `docs/`), `.gitignore` (nada: `public/curriculo/` é versionado)

- [ ] **Step 1: Testes (`tests/test_pecas.py`)**

```python
"""Currículo, kit LinkedIn e README do GitHub saem dos mesmos JSONs do site."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))
import build  # noqa: E402
import gerar_pecas as gp  # noqa: E402

D, EN, CV = build.carregar(), build.carregar_en(), gp.carregar_cv()
PRIVADO = Path(os.environ.get("PORTFOLIO_PRIVADO", RAIZ.parent / "portfolio-privado.json"))


def _telefone() -> str:
    if not PRIVADO.exists():
        if os.environ.get("PORTFOLIO_SEM_PRIVADO") == "1":
            pytest.skip("arquivo privado dispensado explicitamente")
        pytest.fail(f"arquivo privado ausente em {PRIVADO}: sem ele o teste do telefone não protege nada")
    return json.loads(PRIVADO.read_text(encoding="utf-8"))["telefone"]


def test_curriculo_publico_tem_empregador_datas_formacao_e_cargo_e_nao_tem_telefone():
    tel = _telefone()
    for lang, d in (("pt", D), ("en", EN)):
        h = gp.curriculo_html(d, CV, lang)
        assert d["experiencia"][0]["empresa"] in h and build.e(d["perfil"]["cargo"]) in h   # `&` sai como &amp;
        assert ("out/2025 – nov/2026" if lang == "pt" else "Oct 2025 – Nov 2026") in h
        for f in d["perfil"]["formacao"]:
            assert f["instituicao"] in h and f["inicio"] in h and f["fim"] in h
        assert tel not in h and re.sub(r"\D", "", tel)[-8:] not in re.sub(r"\D", "", h)


def test_curriculo_privado_tem_telefone_e_nunca_vai_para_public():
    tel = _telefone()
    h = gp.curriculo_html(D, CV, "pt", telefone=tel)
    assert tel in h
    assert not any(RAIZ in p.parents for p in gp.saidas_privadas()), "saída privada dentro do repositório"


def test_curriculo_em_public_esta_em_dia():
    assert gp.curriculo_desatualizado() == [], "rode: py -3.12 scripts/gerar_pecas.py curriculo"


def test_pdf_existe_e_tem_no_maximo_3_paginas():
    from pypdf import PdfReader
    for lang in ("pt", "en"):
        pdf = RAIZ / "public" / "curriculo" / f"mateus-fabro-{lang}.pdf"
        assert pdf.exists(), "rode: py -3.12 scripts/gerar_pecas.py curriculo"
        assert len(PdfReader(str(pdf)).pages) <= 3


def test_kit_linkedin_respeita_os_limites_e_tem_os_mesmos_fatos():
    for lang, d in (("pt", D), ("en", EN)):
        secoes = gp.linkedin_secoes(d, CV, lang)
        for nome, texto in secoes.items():
            limite = gp.LIMITES[nome.split(":")[0]]
            assert len(texto) <= limite, f"{lang} {nome}: {len(texto)} > {limite}"
        md = gp.linkedin_md(d, CV, lang)
        assert d["experiencia"][0]["empresa"] in md and d["perfil"]["formacao"][1]["instituicao"] in md


def test_kit_linkedin_estoura_limite_falha_em_vez_de_cortar():
    import copy
    d = copy.deepcopy(D)
    d["perfil"]["cargo"] = "x" * 300
    with pytest.raises(ValueError, match="titulo"):
        gp.linkedin_md(d, CV, "pt")


def test_readme_github_tem_projetos_abertos_com_link_e_privados_sem():
    md = gp.github_readme(D, CV)
    repos = json.loads((RAIZ / "scripts" / "github_repos.json").read_text(encoding="utf-8"))
    for r in repos:
        if r.get("mostrar"):
            assert r["nome"] in md
            if r["abre"]:
                assert f"github.com/mateusrfabro/{r['nome']}" in md
    assert D["perfil"]["cargo"] in md and "mateusfabro.vercel.app" in md
```

- [ ] **Step 2: Rodar e ver falhar** — `py -3.12 -m pytest -q tests/test_pecas.py` → `ModuleNotFoundError: gerar_pecas`.

- [ ] **Step 3: Template `scripts/templates/curriculo.html`**

```html
<!doctype html>
<html lang="{{lang_html}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{nome}} — {{cargo}}</title>
<meta name="robots" content="noindex">
<style>
:root{--paper:#F6F8F9;--ink:#14232B;--muted:#56676F;--accent:#0E5A63;--rule:#D9E0E3;--tile:#EDF1F2}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:10.6pt/1.42 "Segoe UI",-apple-system,Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--accent);text-decoration:none}
.folha{max-width:820px;margin:0 auto;padding:28px 20px 40px}
header{border-bottom:2px solid var(--ink);padding-bottom:10px;margin-bottom:12px}
h1{font-size:22pt;margin:0;line-height:1.1;letter-spacing:-.01em}
.cargo{font-size:12.5pt;color:var(--accent);margin:4px 0 2px;font-weight:600}
.sub{color:var(--muted);margin:0 0 8px}
.contato{font-size:9.2pt;color:var(--muted);display:flex;flex-wrap:wrap;gap:4px 14px}
h2{font-size:9.2pt;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);border-bottom:1px solid var(--rule);padding-bottom:3px;margin:16px 0 8px}
p{margin:0 0 6px}
.resumo p{max-width:72ch}
.numeros{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}
.numero{background:var(--tile);padding:7px 9px;border-radius:3px}
.numero b{display:block;font-size:14pt;line-height:1.1}
.numero span{font-size:8.2pt;color:var(--muted);line-height:1.25;display:block;margin-top:2px}
.exp{margin-bottom:10px;break-inside:avoid-page}
.exp .topo{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:baseline}
.exp h3{font-size:11.5pt;margin:0}
.exp .quando{font-size:9.2pt;color:var(--muted);white-space:nowrap}
.exp .cargo-exp{color:var(--accent);font-weight:600;margin:0 0 3px}
.exp h4{font-size:9.4pt;margin:7px 0 2px;color:var(--muted);font-weight:600}
ul{margin:0 0 4px 16px;padding:0}
li{margin:0 0 3px}
.produto{margin:0 0 5px}
.produto b{color:var(--ink)}
.produto .status{color:var(--muted);font-style:italic}
table{border-collapse:collapse;width:100%;font-size:9.4pt}
td{vertical-align:top;padding:3px 6px 3px 0;border-bottom:1px solid var(--rule)}
td:first-child{font-weight:600;white-space:nowrap;width:1%;color:var(--accent)}
.rodape{margin-top:14px;font-size:8pt;color:var(--muted);border-top:1px solid var(--rule);padding-top:6px}
@page{size:A4;margin:12mm 13mm}
@media print{body{background:#fff;font-size:10pt}.folha{max-width:none;padding:0}.numeros{gap:5px}}
@media (max-width:520px){.numeros{grid-template-columns:1fr 1fr}.exp .quando{white-space:normal}}
</style>
</head>
<body><div class="folha">
<header>
<h1>{{nome}}</h1>
<p class="cargo">{{cargo}}</p>
<p class="sub">{{subtitulo}}</p>
<div class="contato">{{contato}}</div>
</header>
<section class="resumo"><h2>{{r_resumo}}</h2>{{resumo}}</section>
<section><h2>{{r_numeros}}</h2><div class="numeros">{{numeros}}</div></section>
<section><h2>{{r_experiencia}}</h2>{{experiencia}}</section>
<section><h2>{{r_produtos}}</h2>{{produtos}}</section>
<section><h2>{{r_stack}}</h2><table>{{stack}}</table></section>
<section><h2>{{r_formacao}}</h2>{{formacao}}</section>
<section><h2>{{r_idiomas}}</h2><p>{{idiomas}}</p></section>
<p class="rodape">{{rodape}}</p>
</div></body></html>
```

- [ ] **Step 4: `scripts/gerar_pecas.py`** (parte 1: currículo; as funções do kit e do README entram nas Tasks 6 e 7 no mesmo arquivo)

```python
"""Gera as peças que não são o site, dos MESMOS JSONs: currículo (HTML + PDF), kit LinkedIn e README do GitHub.

  python scripts/gerar_pecas.py curriculo [--sem-pdf] [--privado] [--check]
  python scripts/gerar_pecas.py linkedin
  python scripts/gerar_pecas.py github

O currículo público (public/curriculo/) nunca tem telefone. `--privado` lê
C:\\Users\\mateu\\Projects\\portfolio-privado.json (fora do repo) e grava a cópia com telefone SÓ no OneDrive.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import build  # noqa: E402

CV = RAIZ / "conteudo" / "curriculo.json"
TEMPLATE = RAIZ / "scripts" / "templates" / "curriculo.html"
PUBLIC_CV = RAIZ / "public" / "curriculo"
PRIVADO = Path(os.environ.get("PORTFOLIO_PRIVADO", RAIZ.parent / "portfolio-privado.json"))
ONEDRIVE = Path.home() / "OneDrive - PGX" / "7. Projetos Pessoais"
MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
e = build.e


def carregar_cv() -> dict:
    return json.loads(CV.read_text(encoding="utf-8"))


def dados(lang: str) -> dict:
    return build.carregar() if lang == "pt" else build.carregar_en()


def mes_ano(iso: str, lang: str) -> str:
    y, m = iso.split("-")
    return f"{(MESES_PT if lang == 'pt' else MESES_EN)[int(m) - 1]}/{y}" if lang == "pt" \
        else f"{MESES_EN[int(m) - 1]} {y}"


def periodo(x: dict, lang: str) -> str:
    return f"{mes_ano(x['inicio'], lang)} – {mes_ano(x['fim'], lang)}"


def _bullets(itens: list[dict]) -> str:
    return "<ul>" + "".join(f"<li>{e(i['texto'])}</li>" for i in itens) + "</ul>"


def curriculo_html(d: dict, cv: dict, lang: str, telefone: str | None = None) -> str:
    p, s, r = d["perfil"], d["site"], cv["rotulos"][lang]
    contato = [f"{e(p['cidade'])}, {e(p['estado'])} · {r['remoto']}", f'<a href="mailto:{e(p["email"])}">{e(p["email"])}</a>']
    if telefone:
        contato.append(e(telefone))
    contato += [f'<a href="{e(p["github"])}">github.com/mateusrfabro</a>', f'<a href="{e(p["linkedin"])}">LinkedIn</a>',
                f'<a href="{e(s["url"])}">{e(s["url"].split("//")[1])}</a>']
    numeros = "".join(f'<div class="numero"><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in d["numeros"])
    exp = []
    for x in d["experiencia"]:
        blocos = cv["experiencia"][x["id"]][lang]
        corpo = ("".join(f"<h4>{e(b['bloco'])}</h4>{_bullets(b['itens'])}" for b in blocos)
                 if blocos and "bloco" in blocos[0] else _bullets(blocos))
        nota = f" · {e(x['nota'])}" if x.get("nota") else ""
        exp.append(f'<div class="exp"><div class="topo"><h3>{e(x["empresa"])}</h3>'
                   f'<span class="quando">{e(periodo(x, lang))} · {e(x["local"])}{nota}</span></div>'
                   f'<p class="cargo-exp">{e(x["cargo"])}</p><p>{e(x["resumo"])}</p>{corpo}</div>')
    produtos = []
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        link = f' · <a href="{e(pr["url"])}">{e(pr["url"].split("//")[1])}</a>' if pr.get("url") else ""
        fatos = "; ".join(pr["fatos"][:2])
        produtos.append(f'<p class="produto"><b>{e(pr["nome"])}</b> — {e(pr["linha"])} '
                        f'<span class="status">({e(pr["status"]).lower()})</span>{link}<br>'
                        f'{e(fatos)}. {e(", ".join(pr["stack"]))}.</p>')
    stack = "".join(f"<tr><td>{e(c['categoria'])}</td><td>{e(c['itens'])}</td></tr>" for c in cv["stack"][lang])
    formacao = "".join(f"<p><b>{e(f['curso'])}</b> — {e(f['instituicao'])} · {e(f['inicio'])}–{e(f['fim'])} ({e(f['status'])})</p>"
                       for f in p["formacao"])
    campos = {
        "lang_html": "pt-BR" if lang == "pt" else "en", "nome": e(p["nome"]), "cargo": e(p["cargo"]),
        "subtitulo": e(p["subtitulo"]), "contato": " · ".join(contato),
        "resumo": "".join(f"<p>{e(par)}</p>" for par in cv["resumo"][lang]), "numeros": numeros,
        "experiencia": "".join(exp), "produtos": "".join(produtos), "stack": stack, "formacao": formacao,
        "idiomas": e(" · ".join(p["idiomas"])),
        "rodape": f"{e(r['gerado'])} {e(s['medido_em'])} · {e(s['url'])}",
        **{f"r_{k}": e(v) for k, v in r.items()},
    }
    texto = TEMPLATE.read_text(encoding="utf-8")
    for k, v in campos.items():
        texto = texto.replace("{{" + k + "}}", v)
    sobrou = re.findall(r"{{\w+}}", texto)
    if sobrou:
        raise ValueError(f"placeholder sem valor no template: {sobrou}")
    return texto


def curriculo_arquivos() -> dict[str, str]:
    cv = carregar_cv()
    return {f"mateus-fabro-{lang}.html": curriculo_html(dados(lang), cv, lang) for lang in ("pt", "en")}


def curriculo_desatualizado() -> list[str]:
    return [f"curriculo/{n}" for n, c in curriculo_arquivos().items()
            if not (PUBLIC_CV / n).exists() or (PUBLIC_CV / n).read_text(encoding="utf-8") != c]


def saidas_privadas() -> list[Path]:
    return [ONEDRIVE / f"Curriculo_Mateus_Fabro_v5_{lang.upper()}.{ext}" for lang in ("pt", "en") for ext in ("html", "pdf")]


def pdf(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        try:
            nav = pw.chromium.launch(channel="msedge")
        except Exception:  # noqa: BLE001 — sem Edge, o Chromium do Playwright
            nav = pw.chromium.launch()
        pg = nav.new_page()
        pg.goto(html_path.resolve().as_uri())
        pg.emulate_media(media="print")
        pg.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
        nav.close()


def cmd_curriculo(args: list[str]) -> int:
    if "--check" in args:
        velhos = curriculo_desatualizado()
        print("curriculo em dia" if not velhos else f"desatualizado: {velhos}")
        return 1 if velhos else 0
    PUBLIC_CV.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in curriculo_arquivos().items():
        alvo = PUBLIC_CV / nome
        alvo.write_text(conteudo, encoding="utf-8", newline="\n")
        if "--sem-pdf" not in args:
            pdf(alvo, alvo.with_suffix(".pdf"))
        print(f"public/curriculo/{nome}{'' if '--sem-pdf' in args else ' + .pdf'}")
    if "--privado" in args:
        if not PRIVADO.exists():
            print(f"arquivo privado ausente: {PRIVADO}")
            return 1
        tel = json.loads(PRIVADO.read_text(encoding="utf-8"))["telefone"]
        cv = carregar_cv()
        ONEDRIVE.mkdir(parents=True, exist_ok=True)
        for lang in ("pt", "en"):
            alvo = ONEDRIVE / f"Curriculo_Mateus_Fabro_v5_{lang.upper()}.html"
            alvo.write_text(curriculo_html(dados(lang), cv, lang, telefone=tel), encoding="utf-8", newline="\n")
            if "--sem-pdf" not in args:
                pdf(alvo, alvo.with_suffix(".pdf"))
            print(f"privado: {alvo}")
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("curriculo", "linkedin", "github"):
        print(__doc__)
        return 2
    return {"curriculo": cmd_curriculo, "linkedin": cmd_linkedin, "github": cmd_github}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
```

(Enquanto `cmd_linkedin`/`cmd_github` não existem, definir no fim do arquivo `def cmd_linkedin(a): return 2` e `def cmd_github(a): return 2`; as Tasks 6 e 7 substituem.)

- [ ] **Step 5: Gerar, olhar, ajustar para caber em 2 páginas**

```powershell
py -3.12 scripts/gerar_pecas.py curriculo
py -3.12 -c "from pypdf import PdfReader;print([len(PdfReader(f'public/curriculo/mateus-fabro-{l}.pdf').pages) for l in ('pt','en')])"
```
Expected: `[2, 2]`. Se der 3, reduzir: `body` 10pt → 9.6pt no `@media print`, ou cortar o 3º bullet de "Sistemas e aplicações" no `curriculo.json`. Abrir o PDF com o Read tool (página 1 e 2) e conferir cabeçalho, tiles e que nenhum bloco quebrou feio.

- [ ] **Step 6: `.vercelignore`** — acrescentar linha `docs/`. **`build.py:main`** — remover o `try/except ImportError` da Task 3.

- [ ] **Step 7: Testes** — `py -3.12 -m pytest -q` → os de currículo e `--check` passam; os de LinkedIn/README ainda falham (Tasks 6–7).

- [ ] **Step 8: Commit**

```powershell
git add scripts/gerar_pecas.py scripts/templates/curriculo.html tests/test_pecas.py build.py .vercelignore
git add public/curriculo/mateus-fabro-pt.html public/curriculo/mateus-fabro-en.html public/curriculo/mateus-fabro-pt.pdf public/curriculo/mateus-fabro-en.pdf
git commit -m "curriculo: gerador HTML+PDF (PT/EN) dos mesmos JSONs do site; publico sem telefone; --privado so no OneDrive"
```

---

### Task 6: Kit LinkedIn

**Files:**
- Modify: `scripts/gerar_pecas.py` (acrescentar)
- Create (gerado): `docs/linkedin/kit-2026-11-pt.md`, `docs/linkedin/kit-2026-11-en.md`

- [ ] **Step 1: Acrescentar ao `gerar_pecas.py`** (antes de `main`)

```python
# ============================================================================ LinkedIn
LIMITES = {"titulo": 220, "sobre": 2600, "experiencia": 2000, "projeto": 2000, "post": 1300, "competencias": 50}
DOCS_LI = RAIZ / "docs" / "linkedin"

COMPETENCIAS = ["Python", "SQL", "PostgreSQL", "TypeScript", "Engenharia de Dados", "Analytics Engineering",
    "Data Pipelines", "ETL", "AWS", "Amazon Athena", "Apache Iceberg", "Amazon EC2", "Prefect", "MongoDB", "Redis",
    "Supabase", "NestJS", "Next.js", "React", "Flask", "FastAPI", "Astro", "Docker", "Linux", "systemd", "Git",
    "GitHub Actions", "CI/CD", "pytest", "Jest", "Prisma", "Playwright", "Antifraude", "Detecção de Fraude",
    "Credit Scoring", "Atribuição de Marketing", "Meta Ads API", "Google Ads API", "CRM", "Power BI", "Dash (Plotly)",
    "pandas", "Machine Learning", "LLM", "Claude Code", "Anthropic API", "LangChain", "n8n", "Automação", "LGPD"]


def _check(nome: str, texto: str) -> str:
    chave = nome.split(":")[0]
    if len(texto) > LIMITES[chave]:
        raise ValueError(f"{nome}: {len(texto)} caracteres, limite {LIMITES[chave]}")
    return texto


def linkedin_secoes(d: dict, cv: dict, lang: str) -> dict[str, str]:
    p, x0 = d["perfil"], d["experiencia"][0]
    pt = lang == "pt"
    titulo = (f"{p['cargo']} | Python · SQL · TypeScript | pipelines, antifraude e atribuição em iGaming · "
              f"produtos próprios com cliente real | em busca de vaga (PJ/CLT, remoto)" if pt else
              f"{p['cargo']} | Python · SQL · TypeScript | pipelines, anti-fraud and attribution in iGaming · "
              f"own products with real customers | open to work (contractor/employee, remote)")
    sobre = "\n\n".join(cv["resumo"][lang] + [
        ("Produtos próprios no ar: " if pt else "Own products live: ") + ", ".join(
            pr["nome"] for pr in d["projetos"] if pr["tipo"] == "produto" and build.status_vivo(pr)) + ".",
        (f"Site com projetos, números medidos e as retificações dos meus erros: {d['site']['url']}\n"
         f"Currículo: {d['site']['url']}/curriculo/mateus-fabro-{lang}.pdf\n"
         f"Contato: {p['email']}")])
    secoes = {"titulo": titulo, "sobre": sobre}
    for x in d["experiencia"]:
        blocos = cv["experiencia"][x["id"]][lang]
        itens = [i for b in blocos for i in b["itens"]] if blocos and "bloco" in blocos[0] else blocos
        corpo = x["resumo"] + "\n\n" + "\n".join(f"• {i['texto']}" for i in itens)
        secoes[f"experiencia:{x['id']}"] = corpo
    fora_do_kit = {"atendimento-whatsapp", "credito-nda"}          # piloto parado; sob NDA — ficam 6 (limite do LinkedIn)
    for pr in d["projetos"]:
        if pr["tipo"] == "produto" and pr["slug"] not in fora_do_kit:
            secoes[f"projeto:{pr['slug']}"] = f"{pr['linha']}\n{pr['status']}.\n" + "\n".join(f"• {f}" for f in pr["fatos"][:3])
    produtos = [pr for pr in d["projetos"] if pr["tipo"] == "produto"]
    no_ar = sum(1 for pr in produtos if build.status_vivo(pr))      # derivado do status, não digitado
    secoes["post"] = (
        f"A operação em que trabalhei desde outubro de 2025 encerrou em novembro. Estou em busca de vaga de "
        f"engenharia de dados, analytics engineering ou desenvolvimento de produto — PJ ou CLT, remoto.\n\n"
        f"O que eu levo: {len(produtos)} produtos próprios construídos de ponta a ponta ({no_ar} no ar hoje), "
        f"migração de data lake, antifraude e atribuição de mídia em três operações de iGaming, e um site onde "
        f"publico os meus erros com a regra que ficou de cada um.\n\n"
        f"Site e currículo: {d['site']['url']}\nSe souber de uma vaga ou quiser conversar: {p['email']}" if pt else
        f"The operation I worked at since October 2025 shut down in November. I'm looking for a data engineering, "
        f"analytics engineering or product development role — contractor or employee, remote.\n\n"
        f"What I bring: {len(produtos)} own products built end to end ({no_ar} live today), a data lake migration, "
        f"anti-fraud and media attribution across three iGaming operations, and a site where I publish my mistakes "
        f"with the rule each one left.\n\n"
        f"Site and résumé: {d['site']['url']}\nIf you know of a role or want to talk: {p['email']}")
    return {k: _check(k, v) for k, v in secoes.items()}


def linkedin_md(d: dict, cv: dict, lang: str) -> str:
    s = linkedin_secoes(d, cv, lang)
    p = d["perfil"]
    pt = lang == "pt"
    L = [f"# Kit LinkedIn — {p['nome']} — {date.today().isoformat()} ({lang})", "",
         ("Cada seção abaixo cabe no limite do LinkedIn. Colar na ordem. Depois de colar, ligar o "
          "\"Open to work\" (Cargos: Engenheiro de Dados, Analytics Engineer, Desenvolvedor Python; remoto; PJ e CLT)."
          if pt else "Each section fits LinkedIn's limit. Paste in order."), "",
         "## 1. Título (Intro → Headline)", "", "```", s["titulo"], "```", "",
         "## 2. Sobre (About)", "", "```", s["sobre"], "```", ""]
    L += ["## 3. Experiência (uma entrada por bloco; cargo, empresa, datas, local, descrição)", ""]
    for x in d["experiencia"]:
        nota = f" · {x['nota']}" if x.get("nota") else ""
        L += [f"### {x['cargo']} — {x['empresa']}", f"- Datas: {periodo(x, lang)} · {x['local']}{nota}",
              ("- Motivo de saída (se perguntarem): encerramento da operação." if x["id"] == "super-nova" and pt else ""),
              "", "```", s[f"experiencia:{x['id']}"], "```", ""]
    L += ["## 4. Formação (Education)", ""]
    for f in p["formacao"]:
        L += [f"- {f['instituicao']} — {f['curso']} — {f['inicio']}–{f['fim']} ({f['status']})"]
    L += ["", "## 5. Projetos (Projects, até 6; link = site ou URL do projeto)", ""]
    for k, v in s.items():
        if k.startswith("projeto:"):
            pr = next(x for x in d["projetos"] if x["slug"] == k.split(":")[1])
            L += [f"### {pr['nome']}", f"- Link: {pr.get('url') or d['site']['url'] + '/projetos/' + pr['slug'] + '.md'}",
                  "", "```", v, "```", ""]
    L += ["## 6. Competências (Skills) — marcar estas 50", "", ", ".join(COMPETENCIAS), "",
          "## 7. Post de disponibilidade (publicar depois de atualizar o perfil)", "", "```", s["post"], "```", ""]
    return "\n".join(L)


def cmd_linkedin(args: list[str]) -> int:
    cv = carregar_cv()
    DOCS_LI.mkdir(parents=True, exist_ok=True)
    for lang in ("pt", "en"):
        alvo = DOCS_LI / f"kit-2026-11-{lang}.md"          # nome fixo: o git add do plano aponta para ele
        alvo.write_text(linkedin_md(dados(lang), cv, lang), encoding="utf-8", newline="\n")
        print(alvo.relative_to(RAIZ))
    return 0
```

- [ ] **Step 2: Gerar e testar**

```powershell
py -3.12 scripts/gerar_pecas.py linkedin
py -3.12 -m pytest -q tests/test_pecas.py -k linkedin
```
Expected: 2 passed. Se `ValueError` por limite (provável em `experiencia:super-nova`, 12 bullets ≈ 2.600 caracteres), reduzir no `linkedin_secoes`: para a experiência principal usar só o **primeiro** bullet de cada bloco (`itens = [b["itens"][0] for b in blocos]`) e repetir o teste.

- [ ] **Step 3: Commit**

```powershell
git add scripts/gerar_pecas.py docs/linkedin/kit-2026-11-pt.md docs/linkedin/kit-2026-11-en.md
git commit -m "linkedin: kit gerado com limites da plataforma (titulo, sobre, experiencias, projetos, post)"
```

---

### Task 7: README do perfil GitHub e `github_repos.json`

**Files:**
- Create: `scripts/github_repos.json`
- Modify: `scripts/gerar_pecas.py` (acrescentar)
- Create (gerado): `docs/github/README.md`

- [ ] **Step 1: `scripts/github_repos.json`** (24 entradas = exatamente `gh repo list mateusrfabro`; o remoto do clone `MultiBet` pertence à organização da empresa e **não** entra; `abre` = vai abrir; `mostrar` = aparece na tabela do README; descrições sem nome de pessoa/cliente)

```json
[
  {"nome": "diario-mateus-fabro", "abre": true, "mostrar": true, "descricao": "Portfólio em formato de diário oficial, para pessoas e agentes de IA: site, JSON Resume, llms.txt e servidor MCP de um JSON só", "topics": ["portfolio", "python", "vercel", "mcp", "llms-txt"]},
  {"nome": "nous-clinical", "abre": true, "mostrar": true, "descricao": "Nous Clinical — SaaS de gestão de clínicas: agenda, prontuário, financeiro, NFS-e, 2FA, chatbot. Flask + PostgreSQL", "topics": ["flask", "saas", "healthcare", "postgresql", "python"]},
  {"nome": "poolcompras", "abre": true, "mostrar": true, "descricao": "Aggron — compra cooperativa para hamburguerias: rodadas, cotação de fornecedores, bot Telegram. Flask. MVP parado desde mai/2026", "topics": ["flask", "marketplace", "telegram-bot", "python"]},
  {"nome": "dumpai", "abre": true, "mostrar": true, "descricao": "DumpAI — IA multimodal escolhe as 10 melhores fotos para um photo dump. Next.js 16 + Claude + Kiwify", "topics": ["nextjs", "anthropic", "typescript", "vercel"]},
  {"nome": "secretaria-ia", "abre": true, "mostrar": true, "descricao": "Secretária virtual de WhatsApp com agenda real (n8n + Evolution API + LangChain). Piloto parado", "topics": ["n8n", "whatsapp", "langchain", "automation"]},
  {"nome": "lab-ia", "abre": true, "mostrar": true, "descricao": "Laboratório local de IA: Ollama + PyTorch numa RTX 4060 — agente com ferramentas, QLoRA, ML tabular", "topics": ["ollama", "pytorch", "qlora", "llm"]},
  {"nome": "avisa-edital", "abre": false, "mostrar": true, "descricao": "Avisa Edital — alertas de concurso, convocação e nomeação para médicos (PR/SP) no Telegram. Python, Vercel, Upstash. Privado (negócio com sócio)", "topics": ["python", "telegram-bot", "vercel", "scraping"]},
  {"nome": "cafesaas", "abre": false, "mostrar": true, "descricao": "Pingado — gestão de cafeteria: balcão, comanda, fiado, estoque, NFC-e. Flask + PostgreSQL. Cliente em produção. Privado", "topics": ["flask", "pos", "saas", "python"]},
  {"nome": "credito-saas", "abre": false, "mostrar": true, "descricao": "SaaS multi-tenant de gestão de crédito (sob NDA). Next.js 16, Supabase/RLS, PWA", "topics": ["nextjs", "supabase", "pwa", "typescript"]},
  {"nome": "guiadocredito", "abre": false, "mostrar": true, "descricao": "Portal de crédito, cartões e score com indicadores do Banco Central atualizados por workflow. Astro 7", "topics": ["astro", "typescript", "content"]},
  {"nome": "radardoinvestidor", "abre": false, "mostrar": false, "descricao": "Portal de renda fixa e indicadores oficiais (BCB, Tesouro, IBGE). Astro 7", "topics": ["astro", "typescript", "content"]},
  {"nome": "central-do-trabalhador", "abre": false, "mostrar": false, "descricao": "Portal de direitos trabalhistas, FGTS, INSS e seguro-desemprego com tabelas de 2026. Astro 7", "topics": ["astro", "typescript", "content"]},
  {"nome": "usmoneybrasil", "abre": false, "mostrar": false, "descricao": "Portal sobre câmbio, remessas e contas globais para brasileiros. Astro 7", "topics": ["astro", "typescript", "content"]},
  {"nome": "mydollarpilot", "abre": false, "mostrar": false, "descricao": "U.S. personal finance portal with official data (FRED, BLS). Astro 7", "topics": ["astro", "typescript", "content"]},
  {"nome": "avisa-pedidos", "abre": false, "mostrar": false, "descricao": "Backlog do Avisa Edital: pedidos, problemas e ideias do sócio", "topics": []},
  {"nome": "flashmed", "abre": false, "mostrar": false, "descricao": "Flashcards médicos — especificação inicial (out/2026)", "topics": []},
  {"nome": "play4tune", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — analytics multi-tenant. Confidencial", "topics": []},
  {"nome": "play4tune-analytics", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — relatórios RTP/GGR. Confidencial", "topics": []},
  {"nome": "pcr-p4t", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — score de crédito de jogador. Confidencial", "topics": []},
  {"nome": "alerta-ftd", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — alertas de FTD. Confidencial", "topics": []},
  {"nome": "canonical-assessment", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — tabelas canônicas. Confidencial", "topics": []},
  {"nome": "startbet-analytics", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — matriz de receita. Confidencial", "topics": []},
  {"nome": "Scripts-usados---Mateus-Fabro", "abre": false, "mostrar": false, "descricao": "Super Nova Gaming (out/2025 – nov/2026) — extrações e queries. Confidencial", "topics": []},
  {"nome": "radar-demo", "abre": false, "mostrar": false, "descricao": "Demo de radar de editais (ago/2026). Privado", "topics": []}
]
```

- [ ] **Step 2: Acrescentar ao `gerar_pecas.py`**

```python
# ============================================================================ GitHub
REPOS_GH = RAIZ / "scripts" / "github_repos.json"
DOCS_GH = RAIZ / "docs" / "github"


def github_readme(d: dict, cv: dict) -> str:
    p, s = d["perfil"], d["site"]
    repos = json.loads(REPOS_GH.read_text(encoding="utf-8"))
    L = [f"# {p['nome']} — {p['cargo']}", "", f"**{p['subtitulo']}**", "",
         f"🟢 **{d['disponibilidade']['status'].capitalize()}** — {d['disponibilidade']['texto']}", "",
         f"- Site (projetos, números medidos e retificações): {s['url']}",
         f"- Currículo: [PT]({s['url']}/curriculo/mateus-fabro-pt.pdf) · [EN]({s['url']}/curriculo/mateus-fabro-en.pdf)",
         f"- LinkedIn: {p['linkedin']}", f"- E-mail: {p['email']}", "",
         "## O que eu faço", ""] + [f"- {par}" for par in cv["resumo"]["pt"]] + ["",
         "## Projetos", "", "| Projeto | O que é | Status | Código |", "|---|---|---|---|"]
    por_nome = {r["nome"]: r for r in repos}
    pares = {"avisa-edital": "avisa-edital", "pingado": "cafesaas", "nous-clinical": "nous-clinical",
             "aggron": "poolcompras", "dumpai": "dumpai", "atendimento-whatsapp": "secretaria-ia",
             "credito-nda": "credito-saas", "portais-conteudo": "guiadocredito"}
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        r = por_nome[pares[pr["slug"]]]
        codigo = f"[{r['nome']}](https://github.com/mateusrfabro/{r['nome']})" if r["abre"] else f"`{r['nome']}` (privado)"
        L.append(f"| **{pr['nome']}** | {pr['linha']} | {pr['status']} | {codigo} |")
    extra = [r for r in repos if r["mostrar"] and r["nome"] not in pares.values()]
    for r in extra:
        codigo = f"[{r['nome']}](https://github.com/mateusrfabro/{r['nome']})" if r["abre"] else f"`{r['nome']}` (privado)"
        L.append(f"| **{r['nome']}** | {r['descricao']} | — | {codigo} |")
    L += ["", f"Trabalho anterior: {d['experiencia'][0]['empresa']}, {periodo(d['experiencia'][0], 'pt')} — "
          "repositórios privados (dados da empresa).", "",
          "## Como eu trabalho", ""] + [f"- **{m['titulo']}.** {m['texto']}" for m in d["metodo"]] + ["",
          f"_README gerado de `conteudo/dados.json` em {s['medido_em']} pelo repositório "
          f"[diario-mateus-fabro](https://github.com/mateusrfabro/diario-mateus-fabro)._", ""]
    return "\n".join(L)


def cmd_github(args: list[str]) -> int:
    DOCS_GH.mkdir(parents=True, exist_ok=True)
    alvo = DOCS_GH / "README.md"
    alvo.write_text(github_readme(build.carregar(), carregar_cv()), encoding="utf-8", newline="\n")
    print(alvo.relative_to(RAIZ))
    return 0
```

- [ ] **Step 3: Gerar e testar**

```powershell
py -3.12 scripts/gerar_pecas.py github
py -3.12 -m pytest -q
```
Expected: tudo verde (inclusive a denylist sobre `docs/github/README.md` e `scripts/github_repos.json`).

- [ ] **Step 4: Commit**

```powershell
git add scripts/github_repos.json scripts/gerar_pecas.py docs/github/README.md
git commit -m "github: README do perfil gerado e tabela dos 24 repositorios (descricao, topics, abre)"
```

---

### Task 8: `scripts/github_perfil.ps1`

**Files:**
- Create: `scripts/github_perfil.ps1`

- [ ] **Step 1: Escrever o script** (PowerShell 5.1: sem `&&`, sem `?.`)

```powershell
<#
.SYNOPSIS
  Aplica no GitHub o que docs/github/README.md e scripts/github_repos.json descrevem. Idempotente.
  Sem -Abrir: perfil (nome, bio, blog, local), repositório mateusrfabro/mateusrfabro com o README,
  descrição e topics dos 24 repositórios. Com -Abrir: muda a visibilidade para public SÓ dos repos com
  abre=true E marcados "ABRE" no relatório do Plano B.
.PARAMETER Abrir
  Abre os repositórios (irreversível na prática: histórico fica público).
#>
param([switch]$Abrir, [switch]$SoMostrar)
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$repos = Get-Content (Join-Path $raiz "scripts\github_repos.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$relatorio = "C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md"
$perfilRepo = "C:\Users\mateu\Projects\mateusrfabro"

function Passo($msg) { Write-Host ("== " + $msg) -ForegroundColor Cyan }

Passo "1. Perfil"
$antes = gh api user --jq '{name,bio,blog,location}'
Write-Host "antes:  $antes"
if (-not $SoMostrar) {
  gh api -X PATCH /user -f name="Mateus Fabro" `
    -f bio="Engenheiro de Dados & Analytics - construo o pipeline e o produto em volta dele (Python, SQL, TypeScript). Em busca de vaga." `
    -f blog="https://mateusfabro.vercel.app" -f location="Londrina, PR - Brasil" | Out-Null
  Write-Host "depois: $(gh api user --jq '{name,bio,blog,location}')"
}

Passo "2. Repositório de perfil mateusrfabro/mateusrfabro"
$existe = $true
try { gh repo view mateusrfabro/mateusrfabro --json name | Out-Null } catch { $existe = $false }
if (-not $SoMostrar) {
  if (-not $existe) { gh repo create mateusrfabro/mateusrfabro --public --description "Perfil" | Out-Null }
  if (-not (Test-Path $perfilRepo)) { git clone https://github.com/mateusrfabro/mateusrfabro.git $perfilRepo | Out-Null }
  Copy-Item (Join-Path $raiz "docs\github\README.md") (Join-Path $perfilRepo "README.md") -Force
  Push-Location $perfilRepo
  git config user.email mateusrfabro@hotmail.com
  git add README.md
  $mudou = git status --porcelain
  if ($mudou) { git commit -q -m "perfil: README gerado de diario-mateus-fabro"; git push -q origin HEAD }
  Pop-Location
  Write-Host "README publicado: https://github.com/mateusrfabro"
} else { Write-Host "repo existe: $existe" }

Passo "3. Descrição e topics dos $($repos.Count) repositórios"
foreach ($r in $repos) {
  $atual = gh repo view "mateusrfabro/$($r.nome)" --json description,repositoryTopics,visibility | ConvertFrom-Json
  $topicsAtuais = @($atual.repositoryTopics | ForEach-Object { $_.name })
  Write-Host ("{0,-32} {1,-8} '{2}'" -f $r.nome, $atual.visibility, $atual.description)
  if ($SoMostrar) { continue }
  if ($atual.description -ne $r.descricao) { gh repo edit "mateusrfabro/$($r.nome)" --description $r.descricao | Out-Null }
  foreach ($t in $r.topics) { if ($topicsAtuais -notcontains $t) { gh repo edit "mateusrfabro/$($r.nome)" --add-topic $t | Out-Null } }
}

if ($Abrir) {
  Passo "4. Abrir repositórios"
  if (-not (Test-Path $relatorio)) { throw "relatório do Plano B ausente: $relatorio" }
  $linhas = Get-Content $relatorio -Encoding UTF8
  foreach ($r in $repos | Where-Object { $_.abre }) {
    $marca = $linhas | Where-Object { $_ -match ("^\|\s*" + [regex]::Escape($r.nome) + "\s*\|.*\|\s*ABRE\s*\|") }
    if (-not $marca) { Write-Host "NÃO ABRE (sem marca ABRE no relatório): $($r.nome)" -ForegroundColor Yellow; continue }
    gh repo edit "mateusrfabro/$($r.nome)" --visibility public --accept-visibility-change-consequences | Out-Null
    Write-Host "ABERTO: https://github.com/mateusrfabro/$($r.nome)" -ForegroundColor Green
  }
}
Write-Host "fim."
```

- [ ] **Step 2: Rodar só leitura**

Run: `powershell -File scripts/github_perfil.ps1 -SoMostrar`
Expected: lista dos 24 repos com visibilidade PRIVATE e descrição atual; nenhum erro de nome (se um nome não existir, `gh repo view` falha: conferir contra `gh repo list`).

- [ ] **Step 3: Commit**

```powershell
git add scripts/github_perfil.ps1
git commit -m "github: script idempotente de perfil, README, descricoes/topics e abertura condicionada ao relatorio"
```

---

## Chunk 3: Revisão por agentes e publicação (U7)

### Task 9: Revisão de conteúdo (agentes `copywriter` e `revisor-conteudo`)

- [ ] **Step 1: `copywriter`** — prompt: ler `docs/linkedin/kit-2026-11-pt.md`, seções 2 (Sobre) e 7 (post). Regras: honesto, sem promessa, sem adjetivo vazio, primeira pessoa, limites `LIMITES` (2.600 e 1.300), **não inventar número**, não citar nome de cliente ou pessoa. Devolver o texto proposto. O executor aplica as mudanças **no código** (`linkedin_secoes` ou `curriculo.json["resumo"]`), nunca no `.md` gerado; regenera e roda os testes.
- [ ] **Step 2: `revisor-conteudo`** — prompt: revisar `public/curriculo/mateus-fabro-pt.html` e `-en.html` e os dois kits: gramática, consistência de termos (PT), inglês de currículo direto e sem adjetivo (EN). Correções voltam para `curriculo.json`/`dados*.json`, nunca para a saída. Regenerar (`gerar_pecas.py curriculo && linkedin && github`), `pytest -q` verde, commit `"conteudo: revisao de texto (copy e revisor)"`.

### Task 10: Gate de números (agente `auditor`, eixo "o número é possível?")

- [ ] **Step 1:** Prompt ao `auditor`: ler o spec §4 e §9; para cada número em `public/curriculo/mateus-fabro-pt.html` e em `public/index.html`, apontar a fonte (`numeros[].fonte`, `fatos`, `curriculo.json[].fonte`) e dizer se é possível; conferir que empregador, datas e formação são iguais nas 4 peças (site, currículo, kit, README). Saída: tabela número × fonte × veredito.
- [ ] **Step 2:** Corrigir bloqueios na fonte, regenerar, testar, commit `"conteudo: ajustes do auditor"`.

### Task 11: Publicar o site

- [ ] **Step 1: Última recontagem e regeneração completa**

```powershell
py -3.12 scripts/recontar.py --aplicar
py -3.12 build.py
py -3.12 scripts/gerar_pecas.py curriculo
py -3.12 scripts/gerar_pecas.py linkedin
py -3.12 scripts/gerar_pecas.py github
py -3.12 scripts/gerar_og.py
py -3.12 -m pytest -q
```
Expected: verde. Commit do que mudou (`git ls-files -m -o --exclude-standard | % { git add $_ }` só depois de ler a lista) com `"publicacao: numeros recontados em <data>"`.

- [ ] **Step 2: Render mobile** — gravar em `C:\Users\mateu\Projects\_fora-do-git\ferramentas\screenshot_412.py`:

```python
"""Screenshot do site local a 412 px (celular). Uso: py -3.12 screenshot_412.py <pasta public> <saida.png>"""
import functools, http.server, sys, threading
from playwright.sync_api import sync_playwright
pasta, saida = sys.argv[1], sys.argv[2]
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=pasta)
h.log_message = lambda *a, **k: None
s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
threading.Thread(target=s.serve_forever, daemon=True).start()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 412, "height": 915})
    pg.goto(f"http://127.0.0.1:{s.server_address[1]}/")
    pg.wait_for_timeout(500)
    pg.screenshot(path=saida, full_page=True)
    b.close()
print(saida)
```
Rodar `py -3.12 C:\Users\mateu\Projects\_fora-do-git\ferramentas\screenshot_412.py public C:\Users\mateu\Projects\_fora-do-git\site-412.png` → abrir a imagem com o Read tool; agente `ux-review` recebe o caminho e aponta fricções. Corrigir só o que for conteúdo/link (design fora de escopo). O agente `tester` (spec §6) está coberto pelo `pytest -q` do Step 1: pytest verde, PDF ≤ 3 páginas e kit nos limites são testes da suíte.

- [ ] **Step 3: Refazer os commits locais de spec/plano e fazer merge + push**

Os commits desta branch ainda não foram enviados. Prova de que nenhum deles leva termo proibido: `py -3.12 -m pytest -q -k "confidencial or vermelha"` (lê `git log --all`). Se acusar índice num commit local: `git reset --soft origin/migracao-2026-09-28` e recommitar em 2 commits (docs; código + conteúdo). Nunca `rebase -i` (interativo).

```powershell
git checkout master
git merge --no-ff migracao-2026-09-28 -m "merge: transicao de carreira (site, curriculo, kit LinkedIn, README GitHub)"
py -3.12 -m pytest -q      # verde no master
git push origin master
git push origin migracao-2026-09-28
```

- [ ] **Step 4: Deploy e verificação empírica**

```powershell
vercel --prod --yes
curl.exe -s https://mateusfabro.vercel.app/resume.json | py -3.12 -c "import json,sys;r=json.load(sys.stdin);print(r['work'][0]['name'],r['work'][0]['endDate'],[e['institution'] for e in r['education']])"
curl.exe -s -o NUL -w "%{http_code}`n" https://mateusfabro.vercel.app/curriculo/mateus-fabro-pt.pdf
curl.exe -s https://mateusfabro.vercel.app/llms.txt | findstr /i "curriculo"
curl.exe -s https://mateusfabro.vercel.app/ | findstr /c:"nome omitido"
```
Expected: empregador e `2026-11`, 2 instituições; `200`; linha do currículo; **nenhuma** linha com "nome omitido".

- [ ] **Step 5: Cópia privada do currículo** — `py -3.12 scripts/gerar_pecas.py curriculo --privado` → conferir que `OneDrive - PGX/7. Projetos Pessoais/Curriculo_Mateus_Fabro_v5_PT.pdf` existe e tem o telefone (abrir com Read).

### Task 12: GitHub (sem abrir) e entrega do kit

- [ ] **Step 1:** `powershell -File scripts/github_perfil.ps1` (sem `-Abrir`). Conferir `https://github.com/mateusrfabro` no navegador ou `gh api users/mateusrfabro --jq '{name,bio,blog}'`.
- [ ] **Step 2:** Entregar ao Mateus: caminho dos dois kits, dos PDFs públicos e privados, e a lista de checagens feitas. **Abertura dos 6 repositórios só na Task 18 (Plano B), após o OK dele.**

### Task 18 (depende do Plano B): abrir os repositórios

- [ ] Pré-condição: relatório `C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md` com `ABRE` nas 6 linhas e **mensagem do Mateus autorizando** (não inferir).
- [ ] `powershell -File scripts/github_perfil.ps1 -Abrir` → conferir `gh repo list mateusrfabro --visibility public` = 7 (6 + perfil).
- [ ] Regerar README (`gerar_pecas.py github`, links agora válidos), rodar o `.ps1` de novo sem `-Abrir` para republicar o README, commit no portfolio.
