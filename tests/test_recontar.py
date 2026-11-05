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


def test_meu_reconhece_os_dois_nomes_e_exclui_bot():
    assert recontar.meu("Mateus Fabro")
    assert recontar.meu("mateusrfabro")
    assert not recontar.meu("avisa-edital-bot")
    assert not recontar.meu("Outra Pessoa")
    assert recontar.e_bot("dependabot[bot]") and recontar.e_bot("avisa-edital-bot")
    assert not recontar.e_bot("Mateus Botelho") and not recontar.meu("Mateus Botelho")


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


def test_e_fato_commits_e_testes_formatos_reais():
    assert recontar._e_fato_commits("234 commits entre 01/12/2025 e 03/02/2026")
    assert recontar._e_fato_commits("182 of my commits between 01/05 and 03/02/2026")
    assert recontar._e_fato_testes("1.055 funções de teste")
    assert recontar._e_fato_testes("1,055 test functions")
    assert not recontar._e_fato_testes("Python com 3 funções de teste e mais")


def test_funcoes_de_teste_conta_def_e_async_def(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        "def test_um(): pass\ndef test_dois(): pass\nasync def test_tres(): pass\ndef helper(): pass\n",
        encoding="utf-8")
    assert recontar.funcoes_de_teste(tmp_path) == 3
    assert recontar.funcoes_de_teste(tmp_path / "nao_existe") == 0


def _mini(fatos_pt, fatos_en, metodo_pt="66 dos 689 commits meus", metodo_en="66 of my 689 commits"):
    def proj(f):
        return {"slug": "avisa-edital", "tipo": "produto", "fatos": list(f)}
    return (
        {"projetos": [proj(fatos_pt)], "numeros": [{}, {}, {}], "metodo": [{"texto": metodo_pt}]},
        {"projetos": [proj(fatos_en)], "numeros": [{}, {}, {}], "metodo": [{"texto": metodo_en}]},
    )


def test_aplicar_com_contagens_injetadas(monkeypatch):
    monkeypatch.setattr(recontar, "REPOS", {"avisa-edital": []})
    c = {"avisa-edital": {"humanos": 1055, "bot": 0, "inicio": "2026-01-05", "fim": "2026-02-03", "testes": 2000}}
    d, d_en = _mini(["1 commits meus entre 01/01 e 02/01/2026", "5 funções de teste"],
                    ["1 of my commits between 01/01 and 01/02/2026", "5 test functions"])
    r = recontar.aplicar(d, d_en, c, 125, 70)
    assert r["commits"] == 1055 and r["testes"] == 2000
    assert d["projetos"][0]["fatos"][1] == "2.000 funções de teste"
    assert d_en["projetos"][0]["fatos"][1] == "2,000 test functions"
    assert d["metodo"][0]["texto"] == "70 dos 1.055 commits meus"
    assert d_en["metodo"][0]["texto"] == "70 of my 1,055 commits"
    assert d["numeros"][0]["valor"] == "125"


def test_aplicar_falha_alto_sem_fato_ou_sem_metodo(monkeypatch):
    import pytest
    monkeypatch.setattr(recontar, "REPOS", {"avisa-edital": []})
    c = {"avisa-edital": {"humanos": 10, "bot": 0, "inicio": "2026-01-05", "fim": "2026-02-03", "testes": 5}}
    d, d_en = _mini(["texto qualquer"], ["any text"])
    with pytest.raises(SystemExit, match="nenhum fato"):
        recontar.aplicar(d, d_en, c, 1, 1)
    d, d_en = _mini(["1 commits meus entre a e b", "5 funções de teste"],
                    ["1 of my commits between a", "5 test functions"], metodo_pt="sem frase")
    with pytest.raises(SystemExit, match="metodo"):
        recontar.aplicar(d, d_en, c, 1, 1)
