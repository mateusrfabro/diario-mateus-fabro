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
        resumo_exp = f"<p>{e(x['resumo'])}</p>" if blocos and "bloco" in blocos[0] else ""  # flat: o bullet ja diz o mesmo
        nota = f" · {e(x['nota'])}" if x.get("nota") else ""
        exp.append(f'<div class="exp"><div class="topo"><h3>{e(x["empresa"])}</h3>'
                   f'<span class="quando">{e(periodo(x, lang))} · {e(x["local"])}{nota}</span></div>'
                   f'<p class="cargo-exp">{e(x["cargo"])}</p>{resumo_exp}{corpo}</div>')
    produtos = []
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        link = f' · <a href="{e(pr["url"])}">{e(pr["url"].split("//")[1])}</a>' if pr.get("url") else ""
        fatos = "; ".join(pr["fatos"][:1])
        produtos.append(f'<p class="produto"><b>{e(pr["nome"])}</b> — {e(pr["linha"])} '
                        f'<span class="status">({e(pr["status"])})</span>{link}</p>')
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
    """Nomes dos arquivos de public/curriculo/ ausentes ou diferentes do gerado, sempre com prefixo `curriculo/`
    (ex.: `curriculo/mateus-fabro-pt.html`), para o `build.py --check` distinguir do site."""
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


def cmd_linkedin(a): return 2  # Task 6


def cmd_github(a): return 2  # Task 7


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("curriculo", "linkedin", "github"):
        print(__doc__)
        return 2
    return {"curriculo": cmd_curriculo, "linkedin": cmd_linkedin, "github": cmd_github}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
