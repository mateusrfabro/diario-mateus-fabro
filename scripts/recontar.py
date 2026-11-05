"""Reconta os números do diário direto na fonte e (com --aplicar) atualiza conteudo/dados*.json.

Sem isto os números começam a envelhecer no dia seguinte à publicação. Roda na máquina do
Mateus, porque é lá que moram os repositórios e a memória global.

O que reconta, por projeto (REPOS: slug → lista de repositórios, caminhos absolutos):
  • commits MEUS (autor "Mateus Fabro" ou "mateusrfabro"; bot = a palavra "bot" no autor), primeira
    e última data. Todas as branches (`git log --all`), commit contado uma vez (dedup por hash,
    então dois clones do mesmo projeto não somam o mesmo commit duas vezes);
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
AUTOR = re.compile(r"mateus fabro|mateusrfabro", re.I)
BOT = re.compile(r"\bbot\b|\[bot\]$", re.I)


def carregar() -> dict:
    return json.loads(DADOS.read_text(encoding="utf-8"))


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", check=True).stdout
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"{repo.name}: git falhou em {repo}: {(e.stderr or '').strip()}") from e


def e_bot(autor: str) -> bool:
    return BOT.search(autor) is not None


def meu(autor: str) -> bool:
    return not e_bot(autor) and AUTOR.search(autor) is not None


def funcoes_de_teste(repo: Path) -> int:
    pasta = repo / "tests"
    if not pasta.exists():
        return 0
    return sum(len(re.findall(r"^\s*(?:async\s+)?def test_", f.read_text(encoding="utf-8", errors="replace"), re.M))
               for f in pasta.rglob("*.py"))


def contar(slug: str) -> dict:
    datas, bots, vistos = [], 0, set()
    for repo in REPOS[slug]:
        if not (repo / ".git").exists():
            raise SystemExit(f"{slug}: repositório ausente em {repo}")
        for linha in git(repo, "log", "--all", "--format=%H%x09%an%x09%ad", "--date=short").splitlines():
            h, autor, data = linha.split("\t")
            if h in vistos:
                continue
            vistos.add(h)
            if e_bot(autor):
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
        blocos = git(repo, "log", "--all", "--format=%an%x00%B%x01").split("\x01")
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


def aplicar(d: dict, d_en: dict, contagens: dict, licoes: int, mut: int) -> dict:
    """Grava as contagens nos dois JSONs (em memória) e devolve o resumo impresso."""
    por_slug = {p["slug"]: p for p in d["projetos"]}
    por_slug_en = {p["slug"]: p for p in d_en["projetos"]}
    produtos_do_total = set(produtos_com_repo(d))  # só estes entram no total de testes; igaming-dados não tem fato de teste
    for slug, c in contagens.items():
        for proj, fato_c, fato_t in ((por_slug[slug], fato_commits, f"{br(c['testes'])} funções de teste"),
                                     (por_slug_en[slug], fato_commits_en, f"{en(c['testes'])} test functions")):
            fatos = proj["fatos"]
            if not any(_e_fato_commits(f) for f in fatos) or (c["testes"] and slug in produtos_do_total and not any(_e_fato_testes(f) for f in fatos)):
                raise SystemExit(f"{slug}: nenhum fato de commits/testes para substituir")
            fatos[:] = [fato_c(c) if _e_fato_commits(f) else f for f in fatos]
            if c["testes"]:
                fatos[:] = [fato_t if _e_fato_testes(f) else f for f in fatos]
        print(f"{slug:20} commits {c['humanos']:4} (+{c['bot']} bot)  testes {c['testes']:5}  {c['inicio']}..{c['fim']}")

    produtos = produtos_com_repo(d)
    com_py = [s for s in produtos if contagens[s]["testes"]]
    total_c = sum(contagens[s]["humanos"] for s in produtos)
    total_t = sum(contagens[s]["testes"] for s in com_py)
    avisa = contagens["avisa-edital"]

    d["numeros"][0]["valor"] = d_en["numeros"][0]["valor"] = str(licoes)
    d["numeros"][1].update(valor=br(total_c), rotulo=f"commits meus em {len(produtos)} produtos próprios, em 2026")
    d_en["numeros"][1].update(valor=en(total_c), rotulo=f"of my commits across {len(produtos)} own products, in 2026")
    d["numeros"][2].update(valor=br(total_t), rotulo=f"funções de teste nos {len(com_py)} produtos em Python")
    d_en["numeros"][2].update(valor=en(total_t), rotulo=f"test functions in the {len(com_py)} Python products")
    for lista, rx, novo_txt in (
            (d["metodo"], r"\d[\d.]* dos \d[\d.]* commits meus", f"{br(mut)} dos {br(avisa['humanos'])} commits meus"),
            (d_en["metodo"], r"\d[\d,]* of my \d[\d,]* commits", f"{en(mut)} of my {en(avisa['humanos'])} commits")):
        n = 0
        for m in lista:
            m["texto"], k = re.subn(rx, novo_txt, m["texto"])
            n += k
        if n < 1:
            raise SystemExit("metodo: nenhuma frase de mutação para substituir")
    return {"licoes": licoes, "commits": total_c, "testes": total_t, "mutacao": mut, "avisa": avisa["humanos"]}


def main() -> int:
    d, d_en = carregar(), json.loads(DADOS_EN.read_text(encoding="utf-8"))
    antes, antes_en = json.dumps(d, ensure_ascii=False), json.dumps(d_en, ensure_ascii=False)
    contagens = {s: contar(s) for s in REPOS}
    licoes = len(json.loads(INDICE_LICOES.read_text(encoding="utf-8"))["lessons"])
    r = aplicar(d, d_en, contagens, licoes, contar_mutacao("avisa-edital"))
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
