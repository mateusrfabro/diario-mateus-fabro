"""O site publicado é o que o gerador produz, e o gerador só publica o que pode ser público."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import build  # noqa: E402

D = build.carregar()
GERADO = build.gerar(D)


def _num(s: str) -> int:
    return int(re.sub(r"\D", "", s))


# ------------------------------------------------------------------ public/ em dia
def test_public_e_exatamente_o_que_o_gerador_produz():
    r = subprocess.run([sys.executable, str(RAIZ / "build.py"), "--check"],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout


# ------------------------------------------------------------------ nomes que não saem
# A lista NÃO mora no repositório: uma denylist versionada de clientes seria ela mesma o
# vazamento ("o guard de PII é o vetor"). Fica um nível acima da pasta do projeto. Pelo mesmo
# motivo a falha NUNCA imprime o termo — só o índice dele na lista e o arquivo.
DENYLIST = Path(os.environ.get("PORTFOLIO_DENYLIST", RAIZ.parent / "portfolio-denylist.txt"))


def _termos() -> list[str]:
    if not DENYLIST.exists():
        if os.environ.get("PORTFOLIO_SEM_DENYLIST") == "1":
            pytest.skip("denylist dispensada explicitamente (PORTFOLIO_SEM_DENYLIST=1)")
        pytest.fail(f"denylist ausente em {DENYLIST}: sem ela este teste não protege nada")
    termos = [t.strip() for t in DENYLIST.read_text(encoding="utf-8").splitlines()]
    termos = [t for t in termos if t and not t.startswith("#")]
    assert len(termos) >= 10, "denylist curta demais para ser a lista real"
    return termos


def _dobrar(s: str) -> str:
    """Minúsculas, sem acento, NFKC (pega forma 'larga'/acentuada do mesmo nome)."""
    s = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _compacto(s: str) -> str:
    return re.sub(r"[\s._\-]+", "", s)


def vazamentos(textos: dict[str, str], termos: list[str]) -> list[tuple[str, int]]:
    """(arquivo, índice do termo) de cada termo achado. Termo de 5+ caracteres casa como
    substring — pega a forma colada ('<termo>2025', 'x<termo>' numa URL) — nas formas normal
    e compacta (sem espaço/ponto/hífen). Termo curto (sigla de 3 letras) casa só com
    fronteira, senão casaria dentro de palavra inocente."""
    achados = []
    for i, termo in enumerate(termos):
        t = _dobrar(termo)
        for nome, texto in textos.items():
            alvo = _dobrar(texto)
            if len(_compacto(t)) >= 5:
                hit = t in alvo or _compacto(t) in _compacto(alvo)
            else:
                hit = re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", alvo) is not None
            if hit:
                achados.append((nome, i))
    return achados


def _publicaveis() -> dict[str, str]:
    """TUDO que vai para um repositório público: cada arquivo versionável (não só o gerado),
    mais as mensagens e os autores dos commits."""
    textos = dict(GERADO)
    ignorar = {".git", "__pycache__", ".pytest_cache", ".vercel"}
    for f in RAIZ.rglob("*"):
        if f.is_file() and not (ignorar & set(f.relative_to(RAIZ).parts)) and f.suffix != ".pyc":
            try:
                textos[str(f.relative_to(RAIZ))] = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    r = subprocess.run(["git", "-C", str(RAIZ), "log", "--all", "--format=%an %ae %cn %ce %s %b"],
                       capture_output=True, text=True, encoding="utf-8")
    textos["<git log>"] = r.stdout if r.returncode == 0 else ""
    textos["<git config user.email>"] = subprocess.run(
        ["git", "-C", str(RAIZ), "config", "user.email"], capture_output=True, text=True).stdout
    return textos


def test_nenhum_nome_confidencial_sai_publicado():
    achados = vazamentos(_publicaveis(), _termos())
    # só índice e arquivo: o log de CI de um repo público é público
    assert not achados, f"termo(s) da denylist publicados (índice, arquivo): {[(i, n) for n, i in achados][:10]}"


def _variantes(termo: str) -> list[str]:
    base = termo.strip()
    v = [base.upper(), f"https://x.com/{base}", base.title(), f"({base})"]
    if len(_compacto(base)) >= 5:          # sigla curta não casa colada — de propósito
        v += [f"{base}2025", f"xx{base}"]
    if " " in base:
        v += [base.replace(" ", "-"), base.replace(" ", "")]
    return v


def test_a_guarda_sabe_ficar_vermelha_para_cada_termo_e_variante():
    """Controle que não pode falhar não é controle: cada termo da lista, em cada variante
    realista, injetado numa cópia do conteúdo publicável, tem de ser pego pela MESMA função
    que o teste de verdade usa."""
    termos = _termos()
    base = {"index.html": GERADO["index.html"]}
    assert vazamentos(base, termos) == []
    for i, termo in enumerate(termos):
        for var in _variantes(termo):
            texto = {"index.html": GERADO["index.html"] + f" trabalhei na {var} ."}
            assert ("index.html", i) in vazamentos(texto, termos), f"variante do termo #{i} passou"


# ------------------------------------------------------------------ números derivados
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


def test_edicao_e_o_numero_de_licoes():
    assert build.edicao(D) == D["numeros"][0]["valor"]   # o valor real vem do recontar.py
    assert "lições" in D["numeros"][0]["rotulo"]
    assert f"Edição nº {build.edicao(D)}" in GERADO["index.html"]


def test_metodo_cita_os_mesmos_commits_do_projeto():
    avisa = next(pr for pr in D["projetos"] if pr["slug"] == "avisa-edital")
    total = _num(next(f for f in avisa["fatos"] if "commits" in f).split(" commits")[0])
    assert any(f"dos {total} commits" in m["texto"] for m in D["metodo"])


# ------------------------------------------------------------------ o que agentes leem
def test_json_ld_valido_com_pessoa_site_perfil_e_faq():
    bloco = re.search(r'<script type="application/ld\+json">(.*?)</script>', GERADO["index.html"], re.S)
    ld = json.loads(bloco.group(1))
    tipos = {n["@type"] for n in ld["@graph"]}
    assert {"Person", "WebSite", "ProfilePage", "FAQPage", "ItemList"} <= tipos
    pessoa = next(n for n in ld["@graph"] if n["@type"] == "Person")
    assert pessoa["sameAs"] == [D["perfil"]["github"], D["perfil"]["linkedin"]]


def test_uma_h1_canonical_e_open_graph():
    h = GERADO["index.html"]
    assert h.count("<h1") == 1
    assert f'<link rel="canonical" href="{D["site"]["url"]}/">' in h
    for tag in ('property="og:title"', 'property="og:description"', 'name="twitter:card"',
                'rel="alternate" type="text/markdown"'):
        assert tag in h


def test_robots_libera_os_buscadores_de_ia_pelo_nome():
    r = GERADO["robots.txt"]
    for bot in ("OAI-SearchBot", "Claude-SearchBot", "PerplexityBot", "GPTBot", "ClaudeBot", "Googlebot"):
        assert f"User-agent: {bot}\nAllow: /" in r
    assert "Disallow" not in r
    assert f"Sitemap: {D['site']['url']}/sitemap.xml" in r


def test_llms_txt_segue_o_formato():
    linhas = GERADO["llms.txt"].splitlines()
    assert linhas[0] == f"# {D['perfil']['nome']}"
    assert linhas[2].startswith("> ")
    assert "## Optional" in linhas
    for pr in D["projetos"]:
        assert f"/projetos/{pr['slug']}.md" in GERADO["llms.txt"]
        assert f"projetos/{pr['slug']}.md" in GERADO


def test_resume_json_tem_o_basico_do_schema():
    r = json.loads(GERADO["resume.json"])
    assert r["basics"]["name"] == D["perfil"]["nome"]
    assert r["basics"]["location"]["countryCode"] == "BR"
    assert {p["name"] for p in r["projects"]} == {pr["nome"] for pr in D["projetos"] if pr["tipo"] == "produto"}


def test_versao_maquina_e_o_mesmo_markdown():
    """O botão "Ler como máquina" mostra exatamente o /index.md — não uma cópia que envelhece."""
    import html
    pre = re.search(r'<pre id="maquina"[^>]*>(.*?)</pre>', GERADO["index.html"], re.S).group(1)
    assert html.unescape(pre) == GERADO["index.md"]


def test_json_embutido_nao_fecha_a_tag_script():
    """Um campo com `</script><!--<script>` não pode quebrar o HTML. A versão anterior deste
    teste era cega: a regex não-gulosa parava justamente no `</script>` injetado."""
    import copy
    d = copy.deepcopy(D)
    d["perfil"]["tese"] = 'x </script><!--<script>alert(1)</script> & "y"'
    d["projetos"][0]["nome"] = "</SCRIPT>"
    h = build.pagina(d, build.markdown(d))
    assert h.count("<script") == h.count("</script>")
    for bloco in re.findall(r'<script type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', h, re.S):
        json.loads(bloco)                       # atravessa inteiro
        assert "<" not in bloco and ">" not in bloco


def test_retificacoes_tem_onde_se_le_e_leia_se_e_datas_validas():
    from datetime import date
    for r in D["retificacoes"]:
        assert r["onde_se_le"] and r["leia_se"] and r["regra"]
        date.fromisoformat(r["data"])
        base = f"RET-{r['data'][:4]}-{r['data'][5:7]}{r['data'][8:10]}"
        assert r["protocolo"] == base or re.fullmatch(re.escape(base) + r"-[A-Z]", r["protocolo"])
    assert len({r["protocolo"] for r in D["retificacoes"]}) == len(D["retificacoes"])


def test_url_sem_https_no_conteudo_derruba_o_build():
    """`e()` escapa aspas, não impede `javascript:` num href vindo do conteúdo."""
    import copy
    d = copy.deepcopy(D)
    d["projetos"][0]["url"] = "javascript:alert(1)"
    with pytest.raises(ValueError, match="https"):
        build.gerar(d)
    d = copy.deepcopy(D)
    d["perfil"]["linkedin"] = "http://exemplo.com"
    with pytest.raises(ValueError):
        build.gerar(d)


def test_imagem_de_compartilhamento_existe_e_nao_envelheceu():
    """A capa (og.png) traz edição e números desenhados: se o conteúdo mudar e a imagem não,
    este teste pede `python scripts/gerar_og.py`."""
    import struct
    sys.path.insert(0, str(RAIZ / "scripts"))
    import gerar_og
    png = (RAIZ / "public" / "og.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630)
    desenhado = json.loads((RAIZ / "public" / "og.json").read_text(encoding="utf-8"))
    assert desenhado == gerar_og.descritor(D), "og.png desatualizada: rode python scripts/gerar_og.py"
    h = GERADO["index.html"]
    assert f'<meta property="og:image" content="{D["site"]["url"]}/og.png">' in h
    assert 'name="twitter:card" content="summary_large_image"' in h


# ------------------------------------------------------------------ as duas línguas dizem o mesmo
EN = build.carregar_en()


def _digitos(s: str) -> list[str]:
    """Os números de uma frase, em qualquer ordem e formato: '1.055' e '1,055' dão os mesmos;
    '12/08' (pt) e '08/12' (en) também."""
    return sorted(re.findall(r"\d+", s))


def test_versao_em_ingles_tem_os_mesmos_fatos_e_numeros():
    """A tradução é outra cópia do conteúdo — e cópia envelhece. Mudou um número em português,
    este teste exige o mesmo número em inglês."""
    assert EN["site"]["medido_em"] == D["site"]["medido_em"]
    assert EN["site"]["url"] == D["site"]["url"] and EN["perfil"]["email"] == D["perfil"]["email"]
    assert [_digitos(n["valor"]) for n in EN["numeros"]] == [_digitos(n["valor"]) for n in D["numeros"]]
    assert [p["slug"] for p in EN["projetos"]] == [p["slug"] for p in D["projetos"]]
    for pt, en in zip(D["projetos"], EN["projetos"]):
        assert [_digitos(f) for f in en["fatos"]] == [_digitos(f) for f in pt["fatos"]], pt["slug"]
        assert (en["url"], en["tipo"]) == (pt["url"], pt["tipo"])
    assert sorted((r["protocolo"], r["data"]) for r in EN["retificacoes"]) == \
           sorted((r["protocolo"], r["data"]) for r in D["retificacoes"])
    en_por_prot = {r["protocolo"]: r for r in EN["retificacoes"]}
    for r in D["retificacoes"]:
        assert _digitos(en_por_prot[r["protocolo"]]["leia_se"]) == _digitos(r["leia_se"]), r["protocolo"]
    assert len(EN["atos"]) == len(D["atos"]) and len(EN["metodo"]) == len(D["metodo"])
    assert [_digitos(m["texto"]) for m in EN["metodo"]] == [_digitos(m["texto"]) for m in D["metodo"]]


def test_pagina_em_ingles_aponta_para_si_e_para_a_portuguesa():
    h = GERADO["en/index.html"]
    assert '<html lang="en">' in h and f'<link rel="canonical" href="{D["site"]["url"]}/en/">' in h
    assert 'hreflang="pt-BR"' in h and 'hreflang="en"' in GERADO["index.html"]
    assert ">CORRECTION<" in h and ">Read<" in h and "Onde se lê" not in h
    assert "RETIFICAÇÃO" in GERADO["index.html"] and "CORRECTION" not in GERADO["index.html"]
    import html as _h
    pre = re.search(r'<pre id="maquina"[^>]*>(.*?)</pre>', h, re.S).group(1)
    assert _h.unescape(pre) == GERADO["en/index.md"]


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
