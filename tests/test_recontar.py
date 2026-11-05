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
