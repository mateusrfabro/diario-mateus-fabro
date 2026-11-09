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

D, EN, CV = gp.dados("pt"), gp.dados("en"), gp.carregar_cv()   # vista publicável (site.modo)
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
        assert d["experiencia"][0]["empresa"] in h and build.e(CV["titulo_ats"][lang]) in h   # cargo da vaga no topo
        if d["site"]["modo"] == "discreto":
            assert ("10/2025 – atual" if lang == "pt" else "10/2025 – present") in h   # datas MM/AAAA (ATS)
        else:
            assert ("out/2025 – nov/2026" if lang == "pt" else "Oct 2025 – Nov 2026") in h
        for f in d["perfil"]["formacao"]:
            assert f["instituicao"] in h and f["inicio"] in h and f["fim"] in h
        assert tel not in h and re.sub(r"\D", "", tel)[-8:] not in re.sub(r"\D", "", h)


def test_pdfs_publicos_nao_tem_o_telefone():
    from pypdf import PdfReader
    tel = _telefone()
    for lang in ("pt", "en"):
        r = PdfReader(str(RAIZ / "public" / "curriculo" / f"mateus-fabro-{lang}.pdf"))
        texto = "".join(p.extract_text() for p in r.pages)
        assert re.sub(r"\D", "", tel)[-8:] not in re.sub(r"\D", "", texto)


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
    cv = copy.deepcopy(CV)
    cv["titulo_ats"]["pt"] = "x" * 300   # a headline abre com os cargos da vaga (titulo_ats)
    with pytest.raises(ValueError, match="titulo"):
        gp.linkedin_md(D, cv, "pt")


def test_readme_github_tem_projetos_abertos_com_link_e_privados_sem():
    md = gp.github_readme(D, CV)
    repos = json.loads((RAIZ / "scripts" / "github_repos.json").read_text(encoding="utf-8"))
    for r in repos:
        if r.get("mostrar"):
            assert r["nome"] in md
            if r["abre"]:
                assert f"github.com/mateusrfabro/{r['nome']}" in md
    assert D["perfil"]["cargo"] in md and "mateusfabro.vercel.app" in md


def test_curriculo_desatualizado_devolve_nomes_com_prefixo_curriculo(tmp_path, monkeypatch):
    monkeypatch.setattr(gp, "PUBLIC_CV", tmp_path)  # pasta vazia: tudo está desatualizado
    velhos = gp.curriculo_desatualizado()
    assert velhos and all(v.startswith("curriculo/") for v in velhos)


def test_modo_discreto_curriculo_publico_sem_encerramento_e_privado_com_a_verdade_completa():
    for lang in ("pt", "en"):
        bruto = build.carregar() if lang == "pt" else build.carregar_en()
        pub = gp.curriculo_html(build.vista(bruto, "discreto"), CV, lang).lower()
        for proibido in ("nov/2026", "nov 2026", "encerr", "shut down", "busca de vaga", "looking for"):
            assert proibido not in pub, f"[{lang}] {proibido}"
        completo = gp.curriculo_html(gp.dados(lang, "completo"), CV, lang, telefone="x").lower()
        assert ("nov/2026" in completo and "encerramento" in completo) if lang == "pt" else                ("nov 2026" in completo and "shut down" in completo)


def test_kit_e_readme_discretos_sem_anuncio_de_busca():
    for lang in ("pt", "en"):
        d = gp.dados(lang, "discreto")
        kit = gp.linkedin_md(d, CV, lang).lower()
        for proibido in ("encerr", "shut down", "busca de vaga", "open to work (contract", "motivo de saída"):
            assert proibido not in kit
        assert "não publicar em modo discreto" in kit or "do not publish in discreet mode" in kit
    md = gp.github_readme(gp.dados("pt", "discreto"), CV)
    assert "Trabalho atual:" in md and "Trabalho anterior" not in md and "encerr" not in md.lower()


# ------------------------------------------------------------------ ATS: o que a máquina lê
def test_curriculo_publico_passa_no_verificador_de_ats():
    """O PDF publicado é lido como texto, com seções padrão, datas MM/AAAA e URL do LinkedIn visível."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    import ats_check
    for lang in ("pt", "en"):
        erros, avisos, _ = ats_check.checar(RAIZ / "public" / "curriculo" / f"mateus-fabro-{lang}.pdf")
        assert not erros, (lang, erros)
        assert not [a for a in avisos if not a.startswith("telefone")], (lang, avisos)  # público não tem telefone


def test_curriculo_sem_tabela_e_com_cargo_da_vaga_no_topo():
    cv = gp.carregar_cv()
    for lang in ("pt", "en"):
        h = gp.curriculo_html(gp.dados(lang), cv, lang)
        assert "<table" not in h, "tabela: ATS junta as células"
        assert cv["titulo_ats"][lang] in h
        assert "linkedin.com/in/" in h.split("</header>")[0]


def test_docx_tem_uma_coluna_sem_tabela(tmp_path):
    from docx import Document
    cv = gp.carregar_cv()
    alvo = tmp_path / "cv.docx"
    gp.curriculo_docx(gp.dados("pt"), cv, "pt", alvo)
    doc = Document(str(alvo))
    assert not doc.tables
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert cv["titulo_ats"]["pt"] in texto and "Experiência profissional" in texto
