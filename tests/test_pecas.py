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


def test_curriculo_desatualizado_devolve_nomes_com_prefixo_curriculo(tmp_path, monkeypatch):
    monkeypatch.setattr(gp, "PUBLIC_CV", tmp_path)  # pasta vazia: tudo está desatualizado
    velhos = gp.curriculo_desatualizado()
    assert velhos and all(v.startswith("curriculo/") for v in velhos)
