"""Gera as peças que não são o site, dos MESMOS JSONs: currículo (HTML + PDF), kit LinkedIn e README do GitHub.

  python scripts/gerar_pecas.py curriculo [--sem-pdf] [--privado] [--check]
  python scripts/gerar_pecas.py linkedin
  python scripts/gerar_pecas.py github

O currículo público (public/curriculo/) nunca tem telefone. `--privado` gera SÓ a cópia com telefone: lê o
arquivo privado e grava no OneDrive, ambos fora do repositório (caminhos em PORTFOLIO_PRIVADO / PORTFOLIO_ONEDRIVE).
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
ONEDRIVE = Path(os.environ.get("PORTFOLIO_ONEDRIVE", Path.home() / "OneDrive - PGX" / "7. Projetos Pessoais"))
LANGS = ("pt", "en")
MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
e = build.e


def carregar_cv() -> dict:
    return json.loads(CV.read_text(encoding="utf-8"))


def dados(lang: str) -> dict:
    return build.carregar() if lang == "pt" else build.carregar_en()


def mes_ano(iso: str, lang: str) -> str:
    y, m = iso.split("-")
    return f"{MESES_PT[int(m) - 1]}/{y}" if lang == "pt" else f"{MESES_EN[int(m) - 1]} {y}"


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

    def _valor(m: re.Match) -> str:
        try:
            return campos[m[1]]
        except KeyError:
            raise ValueError(f"placeholder sem valor no template: {m[1]}") from None
    return re.sub(r"\{\{(\w+)\}\}", _valor, texto)  # uma passagem: valor com {{x}} dentro não é reexpandido


def curriculo_arquivos() -> dict[str, str]:
    cv = carregar_cv()
    return {f"mateus-fabro-{lang}.html": curriculo_html(dados(lang), cv, lang) for lang in LANGS}


def curriculo_desatualizado() -> list[str]:
    """Nomes dos arquivos de public/curriculo/ ausentes ou diferentes do gerado, sempre com prefixo `curriculo/`
    (ex.: `curriculo/mateus-fabro-pt.html`), para o `build.py --check` distinguir do site.
    Só o HTML entra na checagem; o PDF é regerado junto com ele, sem checagem de frescor."""
    return [f"curriculo/{n}" for n, c in curriculo_arquivos().items()
            if not (PUBLIC_CV / n).exists() or (PUBLIC_CV / n).read_text(encoding="utf-8") != c]


def saidas_privadas() -> list[Path]:
    return [ONEDRIVE / f"Curriculo_Mateus_Fabro_v5_{lang.upper()}.{ext}" for lang in LANGS for ext in ("html", "pdf")]


def pdf(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        nav = None
        for tentativa in ({"channel": "msedge"}, {}):  # Edge primeiro; sem ele, o Chromium do Playwright
            try:
                nav = pw.chromium.launch(**tentativa)
                break
            except Exception:  # noqa: BLE001
                continue
        if nav is None:
            raise SystemExit("navegador ausente: rode `py -3.12 -m playwright install chromium`")
        try:
            pg = nav.new_page()
            pg.goto(html_path.resolve().as_uri())
            pg.emulate_media(media="print")
            pg.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
        finally:
            nav.close()


def cmd_curriculo(args: list[str]) -> int:
    if "--check" in args:
        velhos = curriculo_desatualizado()
        print("curriculo em dia" if not velhos else f"desatualizado: {velhos}")
        return 1 if velhos else 0
    sem_pdf = "--sem-pdf" in args
    if "--privado" in args:  # só a cópia privada; falha antes de gerar qualquer coisa
        if not PRIVADO.exists():
            print(f"arquivo privado ausente: {PRIVADO}")
            return 1
        if not ONEDRIVE.parent.exists():
            print(f"pasta do OneDrive ausente ({ONEDRIVE.parent}): ajuste PORTFOLIO_ONEDRIVE")
            return 1
        tel = json.loads(PRIVADO.read_text(encoding="utf-8"))["telefone"]
        cv = carregar_cv()
        ONEDRIVE.mkdir(exist_ok=True)
        for lang in LANGS:
            alvo = ONEDRIVE / f"Curriculo_Mateus_Fabro_v5_{lang.upper()}.html"
            alvo.write_text(curriculo_html(dados(lang), cv, lang, telefone=tel), encoding="utf-8", newline="\n")
            if not sem_pdf:
                pdf(alvo, alvo.with_suffix(".pdf"))
            print(f"privado: {alvo}")
        return 0
    PUBLIC_CV.mkdir(parents=True, exist_ok=True)
    for nome, conteudo in curriculo_arquivos().items():
        alvo = PUBLIC_CV / nome
        alvo.write_text(conteudo, encoding="utf-8", newline="\n")
        if not sem_pdf:
            pdf(alvo, alvo.with_suffix(".pdf"))
        print(f"public/curriculo/{nome}{'' if sem_pdf else ' + .pdf'}")
    return 0


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
        if blocos and "bloco" in blocos[0]:
            # experiência principal: só o 1º bullet de cada bloco (limite de 2.000 caracteres do LinkedIn)
            itens = [b["itens"][0] for b in blocos] if x["id"] == "super-nova" else [i for b in blocos for i in b["itens"]]
        else:
            itens = blocos
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
        if x["id"] == "super-nova":
            L += [(f"Bullets completos no currículo em PDF: {d['site']['url']}/curriculo/mateus-fabro-pt.pdf" if pt else
                   f"Full bullets in the PDF résumé: {d['site']['url']}/curriculo/mateus-fabro-en.pdf"), ""]
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
    for lang in LANGS:
        alvo = DOCS_LI / f"kit-2026-11-{lang}.md"          # nome fixo: o git add do plano aponta para ele
        alvo.write_text(linkedin_md(dados(lang), cv, lang), encoding="utf-8", newline="\n")
        print(alvo.relative_to(RAIZ))
    return 0


def cmd_github(a): return 2  # Task 7


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("curriculo", "linkedin", "github"):
        print(__doc__)
        return 2
    return {"curriculo": cmd_curriculo, "linkedin": cmd_linkedin, "github": cmd_github}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
