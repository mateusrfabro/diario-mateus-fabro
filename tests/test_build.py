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


def test_home_nao_fala_mais_a_lingua_do_diario():
    """A home fala com gestor e recrutador: o vocabulário de diário oficial saiu (spec de 05/11/2026)."""
    for nome in ("index.html", "en/index.html", "licoes/index.html", "en/licoes/index.html", "404.html"):
        h = GERADO[nome]
        for velho in ("Diário de", "Edição nº", "RETIFICAÇÃO", "Ler como máquina", "Gazette", "Edition no.",
                      ">CORRECTION<", "Read as a machine", 'id="maquina"', "Convocação", "Editais"):
            assert velho not in h, f"{nome}: {velho}"


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


def test_rodape_aponta_para_as_versoes_de_maquina():
    """Sem botão "Ler como máquina": o rodapé linka os formatos que um agente lê direto."""
    for nome, md in (("index.html", "/index.md"), ("en/index.html", "/en/index.md"), ("licoes/index.html", "/index.md")):
        rodape = GERADO[nome].split('<footer class="rodape">')[1]
        for alvo in (md, "/resume.json", "/llms.txt", "/mcp"):
            assert f'href="{alvo}"' in rodape, (nome, alvo)
    assert GERADO["index.md"].startswith(f"# {D['perfil']['nome']}")


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
    """A capa (og.png) traz nome, cargo, frase e endereço desenhados: se o conteúdo mudar e a imagem
    não, este teste pede `python scripts/gerar_og.py`."""
    import struct
    sys.path.insert(0, str(RAIZ / "scripts"))
    import gerar_og
    png = (RAIZ / "public" / "og.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", png[16:24]) == (1200, 630)
    desenhado = json.loads((RAIZ / "public" / "og.json").read_text(encoding="utf-8"))
    assert desenhado == gerar_og.descritor(D), "og.png desatualizada: rode python scripts/gerar_og.py"
    assert set(desenhado) == {"nome", "cargo", "frase", "site"}
    assert desenhado["frase"] == D["perfil"]["frase_hero"] and desenhado["site"] in D["site"]["url"]
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
    assert '<a class="idioma" href="/"' in h and '<a class="idioma" href="/en/"' in GERADO["index.html"]
    le = GERADO["en/licoes/index.html"]
    assert f'<link rel="canonical" href="{D["site"]["url"]}/en/licoes/">' in le
    assert "<dt>Read</dt>" in le and "Onde se lê" not in le
    assert "<dt>Leia-se</dt>" in GERADO["licoes/index.html"] and "<dt>Read</dt>" not in GERADO["licoes/index.html"]
    assert '<a class="idioma" href="/licoes/"' in le and '<a class="idioma" href="/en/licoes/"' in GERADO["licoes/index.html"]


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
    assert r["work"][0]["startDate"] == "2025-10"
    if D["site"]["modo"] == "discreto":
        assert "endDate" not in r["work"][0]            # sem endDate = emprego atual
    else:
        assert r["work"][0]["endDate"] == "2026-11"
    assert D["experiencia"][0]["fim"] == "2026-11"      # a verdade segue nos dados
    assert build.vista(D, "completo")["experiencia"][0]["fim"] == "2026-11"
    assert r["work"][0]["name"] == D["experiencia"][0]["empresa"]
    assert len(r["education"]) == 2 and all(e["startDate"] and e["endDate"] for e in r["education"])


def test_site_nomeia_o_empregador_e_nao_diz_mais_nome_omitido():
    h = GERADO["index.html"]
    assert "nome omitido" not in h and "name omitted" not in GERADO["en/index.html"]
    assert build.e(D["perfil"]["cargo"]) in h and build.e(D["perfil"]["frase_hero"]) in h   # `&` sai como &amp;
    assert "Super Nova" in h
    if D["site"]["modo"] == "discreto":
        assert "nov/2026" not in h.lower() and "encerr" not in h.lower()
    else:
        assert "nov/2026" in h.lower()


def test_modo_discreto_igual_nos_dois_jsons_e_vista_troca_os_campos():
    en = build.carregar_en()
    assert D["site"]["modo"] == en["site"]["modo"] in ("discreto", "completo")
    for d in (D, en):
        v = build.vista(d, "discreto")
        assert v["experiencia"][0]["fim"] is None and v["site"]["modo"] == "discreto"
        assert v["perfil"]["resumo"] == d["perfil"]["resumo_discreto"]
        assert v["disponibilidade"] == d["disponibilidade_discreta"]
        assert v["faq"][3]["resposta"] == d["faq"][3]["resposta_discreta"]
        c = build.vista(d, "completo")
        assert c["experiencia"][0]["fim"] == "2026-11" and c["perfil"]["resumo"] == d["perfil"]["resumo"]
        for x in (v, c):
            assert "_discret" not in json.dumps(x)       # as variantes nunca vazam na vista


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


# ------------------------------------------------------------------ a home nova (spec 05/11/2026)
def _secao(h: str, ident: str) -> str:
    """Trecho do HTML da seção `id=ident` até a próxima seção."""
    return h.split(f'id="{ident}"', 1)[1].split("<section", 1)[0]


@pytest.mark.parametrize("nome,dd", [("index.html", D), ("en/index.html", EN)])
def test_home_tem_h1_unico_com_o_nome(nome, dd):
    h = GERADO[nome]
    assert h.count("<h1") == 1
    assert re.search(r"<h1>([^<]*)</h1>", h).group(1) == dd["perfil"]["nome"]


@pytest.mark.parametrize("nome,t", [("index.html", build.T["pt"]), ("en/index.html", build.T["en"])])
def test_dois_ctas_no_hero_e_no_contato(nome, t):
    """Currículo (PDF) e e-mail com assunto aparecem na abertura E no contato."""
    h = GERADO[nome]
    hero = h.split('class="hero"', 1)[1].split("</section>", 1)[0]
    contato = _secao(h, "contato")
    pdf = f'href="/curriculo/{t["cv_arquivo"]}"'
    mailto = f'href="mailto:{D["perfil"]["email"]}?subject={t["assunto"]}"'
    for trecho in (hero, contato):
        assert pdf in trecho and mailto in trecho
        assert f">{t['cv']}<" in trecho and f">{t['email_btn']}<" in trecho
    assert 'href="#projetos"' in hero and t["ver_proj"] in hero


def test_cinco_numeros_com_data_de_medicao():
    h = GERADO["index.html"]
    v = build.vista(D)
    assert len(v["numeros"]) == 5 and h.count('<div class="numero">') == 5
    for n in v["numeros"]:
        assert f"<b>{build.e(n['valor'])}</b>" in h and build.e(n["fonte"]) in h
    assert build.data_curta(D["site"]["medido_em"]) in h.split('class="prova"', 1)[1].split("</aside>", 1)[0]


def test_tres_pilares_sem_digito_e_com_provas_lidas_dos_dados():
    cv = build.carregar_cv()
    for dd, nome, t in ((D, "index.html", build.T["pt"]), (EN, "en/index.html", build.T["en"])):
        v = build.vista(dd)
        assert len(v["pilares"]) == 3
        for p in v["pilares"]:
            assert p["titulo"] and p["texto"] and not re.search(r"\d", p["titulo"] + p["texto"]), p["titulo"]
        h = GERADO[nome]
        assert h.count('<article class="pilar">') == 3
        provas = build.provas_pilares(v, cv, t)
        assert [len(x) for x in provas] == [2, 2, 2]
        for pv in provas:
            for x in pv:
                assert build.e(x) in h
    assert [p["titulo"] for p in D["pilares"]] == ["Dados", "Produto", "Agentes de IA"]


def test_experiencia_tem_o_empregador_e_os_fatos_do_trabalho_atual():
    exp = _secao(GERADO["index.html"], "experiencia")
    v = build.vista(D)
    for x in v["experiencia"]:
        assert build.e(x["empresa"]) in exp and build.e(x["cargo"]) in exp
    trabalho = next(pr for pr in v["projetos"] if pr["tipo"] == "trabalho")
    commits = [f for f in trabalho["fatos"] if build.FATO_COMMITS.match(f)]
    assert len(commits) == 1                                  # o fato existe nos dados...
    for f in trabalho["fatos"]:
        assert (build.e(build.inicial(f)) in exp) == (f not in commits)   # ...mas não na página
    form = _secao(GERADO["index.html"], "formacao")
    for f in v["perfil"]["formacao"]:
        assert build.e(f["instituicao"]) in form and f["inicio"] in form


@pytest.mark.parametrize("nome,dd", [("index.html", D), ("en/index.html", EN)])
def test_cards_com_todos_os_produtos_avisa_edital_primeiro_e_bolinha_de_status(nome, dd):
    proj = _secao(GERADO[nome], "projetos")
    cards = re.findall(r'<article class="card[^"]*" id="([a-z0-9-]+)"', proj)
    produtos = [pr for pr in dd["projetos"] if pr["tipo"] == "produto"]
    assert sorted(cards) == sorted(pr["slug"] for pr in produtos) and cards[0] == "avisa-edital"
    assert "igaming-dados" not in cards                       # o trabalho mora na experiência
    assert proj.count('class="dot vivo"') == sum(build.status_vivo(pr) for pr in produtos)
    for pr in produtos:
        for s_ in pr["stack"]:
            assert f"<li>{build.e(s_)}</li>" in proj
        if pr.get("url"):
            assert f'href="{pr["url"]}"' in proj
        card = proj.split(f'id="{pr["slug"]}"', 1)[1].split("</article>", 1)[0]
        for f in pr["fatos"]:
            if build.FATO_COMMITS.match(f):
                assert build.e(f) not in card, pr["slug"]   # o de commits já está na faixa de números
        assert build.e(build.inicial(build.sem_commits(pr["fatos"])[0])) in card
    avisa = next(pr for pr in produtos if pr["slug"] == "avisa-edital")
    card = proj.split('id="avisa-edital"', 1)[1].split("</article>", 1)[0]
    assert build.e(build.inicial(avisa["fatos"][2])) in card and build.e(avisa["fatos"][0]) not in card
    assert build.FATO_COMMITS.match(avisa["fatos"][0])
    md = GERADO["index.md" if dd is D else "en/index.md"]
    assert all(f in md for f in avisa["fatos"])               # o Markdown segue com todos os fatos


def test_stack_vem_do_curriculo_json():
    cv = build.carregar_cv()
    st = _secao(GERADO["index.html"], "stack")
    for c in cv["stack"]["pt"]:
        assert f"<dt>{build.e(c['categoria'])}</dt>" in st
        for item in c["itens"].split(" · "):
            assert f"<li>{build.e(item)}</li>" in st


@pytest.mark.parametrize("nome,t,pref", [("index.html", build.T["pt"], ""), ("en/index.html", build.T["en"], "/en")])
def test_como_trabalho_tem_o_metodo_e_o_link_para_as_licoes(nome, t, pref):
    dd = D if pref == "" else EN
    met = _secao(GERADO[nome], "metodo")
    for m in dd["metodo"]:
        assert build.e(m["titulo"]) in met
    assert f'href="{pref}/licoes/"' in met
    assert build.e(t["link_licoes"].format(n=len(dd["atos"]))) in met


@pytest.mark.parametrize("nome,dd", [("licoes/index.html", D), ("en/licoes/index.html", EN)])
def test_pagina_de_licoes_tem_todas_as_retificacoes_e_atos(nome, dd):
    h = GERADO[nome]
    assert h.count("<h1") == 1
    assert sorted(re.findall(r'<article class="ret" id="(ret-[0-9a-z-]+)"', h)) == \
        sorted(r["protocolo"].lower() for r in dd["retificacoes"])
    for r in dd["retificacoes"]:
        for campo in ("onde_se_le", "leia_se", "regra", "contexto"):
            assert build.e(r[campo]) in h, (r["protocolo"], campo)
    for a in dd["atos"]:
        assert build.e(a["titulo"]) in h
    assert h.count("<script") == 0                           # página só de leitura
    pref = "" if dd is D else "/en"
    assert f'<link rel="canonical" href="{D["site"]["url"]}{pref}/licoes/">' in h


def test_sitemap_e_llms_conhecem_as_licoes():
    for u in ("/licoes/", "/en/licoes/"):
        assert f"<loc>{D['site']['url']}{u}</loc>" in GERADO["sitemap.xml"]
    assert f"({D['site']['url']}/licoes/)" in GERADO["llms.txt"]


def test_app_js_nao_depende_de_elemento_que_saiu_da_pagina():
    """O botão de alternar saiu; um getElementById dele derrubaria o WebMCP antes de registrar."""
    js = GERADO["app.js"]
    for id_ in re.findall(r"getElementById\('([a-z]+)'\)", js):
        assert f'id="{id_}"' in GERADO["index.html"], id_
    assert "registerTool" in js
