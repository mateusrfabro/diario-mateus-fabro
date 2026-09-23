"""Reconta os números do diário direto na fonte e (com --aplicar) atualiza conteudo/dados.json.

Sem isto os números começam a envelhecer no dia seguinte à publicação. Roda na máquina do
Mateus, porque é lá que moram os repositórios dos produtos e a memória global. Na nuvem não
há o que recontar.

O que reconta:
  • commits humanos (sem os automáticos, cujo autor contém "bot"), primeira e última data;
  • funções de teste (`def test_`) em tests/;
  • lições registradas (global_index.json);
  • no Avisa Edital, quantos commits humanos registram teste de mutação.

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
PROJETOS = Path.home() / "Projects"
REPOS = {"avisa-edital": "ajudamed", "pingado": "cafesaas", "nous-clinical": "medsaas",
         "aggron": "poolcompras", "dumpai": "appfotos"}
INDICE_LICOES = Path.home() / ".claude" / "memory-global" / "global_index.json"
FLASK = ("avisa-edital", "pingado", "nous-clinical", "aggron")   # os que têm suíte pytest


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def contar(slug: str) -> dict:
    repo = PROJETOS / REPOS[slug]
    linhas = [l.split("\t") for l in git(repo, "log", "--format=%an\t%ad\t%s", "--date=short").splitlines()]
    humanos = [l for l in linhas if "bot" not in l[0].lower()]
    datas = sorted(l[1] for l in humanos)
    testes = 0
    for f in (repo / "tests").rglob("*.py") if (repo / "tests").exists() else []:
        testes += len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M))
    return {"humanos": len(humanos), "bot": len(linhas) - len(humanos), "inicio": datas[0],
            "fim": datas[-1], "testes": testes}


def contar_mutacao(slug: str) -> int:
    repo = PROJETOS / REPOS[slug]
    blocos = git(repo, "log", "--format=%an%x00%B%x01").split("\x01")
    return sum(1 for b in blocos if "\x00" in b and "bot" not in b.split("\x00")[0].lower()
               and re.search(r"muta[cç]", b.split("\x00")[1], re.I))


def br(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fato_commits(c: dict) -> str:
    ini, fim = date.fromisoformat(c["inicio"]), date.fromisoformat(c["fim"])
    faixa = f"{ini:%d/%m} e {fim:%d/%m/%Y}"
    if c["bot"]:
        return f"{c['humanos']} commits meus entre {faixa}, fora {c['bot']} automáticos do bot"
    return f"{c['humanos']} commits entre {faixa}"


DADOS_EN = RAIZ / "conteudo" / "dados.en.json"


def en(n: int) -> str:
    return f"{n:,}"


def fato_commits_en(c: dict) -> str:
    ini, fim = date.fromisoformat(c["inicio"]), date.fromisoformat(c["fim"])
    faixa = f"{ini:%m/%d} and {fim:%m/%d/%Y}"
    if c["bot"]:
        return f"{c['humanos']} of my commits between {faixa}, plus {c['bot']} automated bot commits"
    return f"{c['humanos']} commits between {faixa}"


def atualizar_en(contagens: dict, licoes: int, total_c: int, total_t: int, mut: int, humanos_avisa: int) -> dict:
    """A versão em inglês recebe os MESMOS números — o teste de paridade exige."""
    d = json.loads(DADOS_EN.read_text(encoding="utf-8"))
    por_slug = {p["slug"]: p for p in d["projetos"]}
    for slug, c in contagens.items():
        fatos = por_slug[slug]["fatos"]
        fatos[:] = [fato_commits_en(c) if " commits" in f else f for f in fatos]
        if slug in FLASK:
            fatos[:] = [f"{en(c['testes'])} test functions" if f.endswith("test functions") else f for f in fatos]
    for n in d["numeros"]:
        if "lessons" in n["rotulo"]:
            n["valor"] = str(licoes)
        elif "commits" in n["rotulo"]:
            n["valor"] = en(total_c)
        elif "test functions" in n["rotulo"]:
            n["valor"] = en(total_t)
    for m in d["metodo"]:
        m["texto"] = re.sub(r"\d+ of my \d+ commits", f"{mut} of my {humanos_avisa} commits", m["texto"])
    return d


def main() -> int:
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    antes = json.dumps(d, ensure_ascii=False)
    antes_en = DADOS_EN.read_text(encoding="utf-8")
    contagens = {}
    por_slug = {p["slug"]: p for p in d["projetos"]}
    total_c = total_t = 0
    for slug in REPOS:
        c = contar(slug)
        contagens[slug] = c
        total_c += c["humanos"]
        fatos = por_slug[slug]["fatos"]
        fatos[:] = [fato_commits(c) if " commits" in f else f for f in fatos]
        if slug in FLASK:
            total_t += c["testes"]
            fatos[:] = [f"{br(c['testes'])} funções de teste" if f.endswith("funções de teste") else f
                        for f in fatos]
        print(f"{slug:14} commits {c['humanos']:4} (+{c['bot']} bot)  testes {c['testes']:5}  {c['inicio']}..{c['fim']}")

    licoes = len(json.loads(INDICE_LICOES.read_text(encoding="utf-8"))["lessons"])
    for n in d["numeros"]:
        if "lições" in n["rotulo"]:
            n["valor"] = str(licoes)
        elif "commits" in n["rotulo"]:
            n["valor"] = br(total_c)
        elif "funções de teste" in n["rotulo"]:
            n["valor"] = br(total_t)

    avisa = contar("avisa-edital")
    mut = contar_mutacao("avisa-edital")
    for m in d["metodo"]:
        m["texto"] = re.sub(r"\d+ dos \d+ commits meus", f"{mut} dos {avisa['humanos']} commits meus", m["texto"])
    print(f"lições {licoes} · commits {total_c} · testes {total_t} · mutação no Avisa {mut}/{avisa['humanos']}")

    d_en = atualizar_en(contagens, licoes, total_c, total_t, mut, avisa["humanos"])
    novo_en = json.dumps(d_en, ensure_ascii=False, indent=2) + "\n"
    if json.dumps(d, ensure_ascii=False) == antes and json.loads(novo_en) == json.loads(antes_en):
        print("nada mudou")
        return 0
    if "--aplicar" not in sys.argv:
        print("há números novos — rode com --aplicar para gravar")
        return 1
    hoje = date.today().isoformat()
    d["site"]["medido_em"] = d_en["site"]["medido_em"] = hoje
    DADOS.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    DADOS_EN.write_text(json.dumps(d_en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(RAIZ / "build.py")], check=True)
    print("gravado. Se a edição mudou, rode também: python scripts/gerar_og.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
