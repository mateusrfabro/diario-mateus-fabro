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
ONEDRIVE = Path(os.environ.get("PORTFOLIO_ONEDRIVE", Path.home() / "OneDrive" / "Curriculo"))
LANGS = ("pt", "en")
MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
e = build.e


def carregar_cv() -> dict:
    return json.loads(CV.read_text(encoding="utf-8"))


def dados(lang: str, modo: str | None = None) -> dict:
    """Vista publicável (site.modo); `modo="completo"` força a verdade inteira (só a cópia privada usa)."""
    return build.vista(build.carregar() if lang == "pt" else build.carregar_en(), modo)


def discreto(d: dict) -> bool:
    return d["site"].get("modo") == "discreto"


def mes_ano(iso: str, lang: str) -> str:
    y, m = iso.split("-")
    return f"{MESES_PT[int(m) - 1]}/{y}" if lang == "pt" else f"{MESES_EN[int(m) - 1]} {y}"


def periodo(x: dict, lang: str) -> str:
    fim = mes_ano(x["fim"], lang) if x.get("fim") else ("atual" if lang == "pt" else "present")
    return f"{mes_ano(x['inicio'], lang)} – {fim}"


def periodo_ats(x: dict, lang: str) -> str:
    """Datas MM/AAAA no currículo: é o formato que os ATS (Gupy, Workday, Greenhouse) leem sem ambiguidade."""
    def mm(iso: str) -> str:
        y, m = iso.split("-")
        return f"{m}/{y}"
    fim = mm(x["fim"]) if x.get("fim") else ("atual" if lang == "pt" else "present")
    return f"{mm(x['inicio'])} – {fim}"


def _bullets(itens: list[dict]) -> str:
    return "<ul>" + "".join(f"<li>{e(i['texto'])}</li>" for i in itens if not i.get("so_site")) + "</ul>"


def curriculo_html(d: dict, cv: dict, lang: str, telefone: str | None = None) -> str:
    p, s, r = d["perfil"], d["site"], cv["rotulos"][lang]
    local = f"{e(p['cidade'])}, {e(p['estado'])}" if lang == "pt" else f"{e(p['cidade'])}, {e(p['pais'])}"
    contato = [f"{local} · {r['remoto']}", f'<a href="mailto:{e(p["email"])}">{e(p["email"])}</a>']
    if telefone:
        contato.append(e(telefone))
    contato += [f'<a href="{e(p["github"])}">github.com/mateusrfabro</a>', f'<a href="{e(p["linkedin"])}">{e(p["linkedin"].split("//")[1].removeprefix("www."))}</a>',
                f'<a href="{e(s["url"])}">{e(s["url"].split("//")[1])}</a>']
    destaques = cv.get("destaques", {}).get(lang) or d["numeros"]   # currículo: impacto; site: números recontados
    numeros = "".join(f'<div class="numero"><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in destaques)
    exp = []
    for x in d["experiencia"]:
        blocos = cv["experiencia"][x["id"]][lang]
        corpo = ("".join(f"<h4>{e(b['bloco'])}</h4>{_bullets(b['itens'])}" for b in blocos)
                 if blocos and "bloco" in blocos[0] else _bullets(blocos))
        resumo_exp = f"<p>{e(x['resumo'])}</p>" if blocos and "bloco" in blocos[0] else ""  # flat: o bullet ja diz o mesmo
        nota = f" · {e(x['nota'])}" if x.get("nota") else ""
        # ATS: cargo primeiro, depois empresa · local · datas numa linha só
        exp.append(f'<div class="exp"><div class="topo"><h3>{e(x["cargo"])}</h3>'
                   f'<span class="quando">{e(periodo_ats(x, lang))}</span></div>'
                   f'<p class="cargo-exp">{e(x["empresa"])} · {e(x["local"])}{nota}</p>{resumo_exp}{corpo}</div>')
    produtos = []
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        link = f' · <a href="{e(pr["url"])}">{e(pr["url"].split("//")[1])}</a>' if pr.get("url") else ""
        produtos.append(f'<p class="produto"><b>{e(pr["nome"])}</b> — {e(pr["linha"])} '
                        f'<span class="status">· {e(pr["status"])}</span>{link}</p>')
    # sem tabela: ATS junta células ("Segurança e práticasArgon2"); "Categoria: itens" sai limpo
    stack = "".join(f'<p class="comp"><b>{e(c["categoria"])}:</b> {e(c["itens"])}</p>' for c in cv["stack"][lang])
    formacao = "".join(f"<p><b>{e(f['curso'])}</b> — {e(f['instituicao'])} · {e(f['inicio'])}–{e(f['fim'])} ({e(f['status'])})</p>"
                       for f in p["formacao"])
    campos = {
        "lang_html": "pt-BR" if lang == "pt" else "en", "nome": e(p["nome"]),
        "cargo": e(cv.get("titulo_ats", {}).get(lang, p["cargo"])),
        "subtitulo": e(p["subtitulo"]), "contato": " · ".join(contato),
        "resumo": "".join(f"<p>{e(par)}</p>" for par in
                          (cv["resumo_discreto"] if discreto(d) else cv["resumo"])[lang]), "numeros": numeros,
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


def curriculo_docx(d: dict, cv: dict, lang: str, destino: Path, telefone: str | None = None) -> None:
    """Mesmo conteúdo do currículo em .docx de uma coluna, só com estilos nativos do Word (Título, Lista).
    A Gupy recomenda .doc/.docx para o preenchimento automático dos campos; sem tabela, caixa de texto,
    cabeçalho/rodapé ou imagem, que são o que os parsers leem mal."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    p, s, r = d["perfil"], d["site"], cv["rotulos"][lang]
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(10)
    for sec in doc.sections:
        sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Pt(42)

    def h(texto: str, nivel: int) -> None:
        par = doc.add_heading(texto, level=nivel)
        for run in par.runs:
            run.font.color.rgb = RGBColor(0x0E, 0x5A, 0x63)

    def par(texto: str, negrito: str = "") -> None:
        x = doc.add_paragraph()
        if negrito:
            x.add_run(negrito).bold = True
        x.add_run(texto)
        x.paragraph_format.space_after = Pt(3)

    def item(texto: str) -> None:
        x = doc.add_paragraph(texto, style="List Bullet")
        x.paragraph_format.space_after = Pt(1)

    titulo = doc.add_paragraph()
    rn = titulo.add_run(p["nome"])
    rn.bold, rn.font.size = True, Pt(20)
    sub = doc.add_paragraph()
    rc = sub.add_run(cv.get("titulo_ats", {}).get(lang, p["cargo"]))
    rc.bold, rc.font.size = True, Pt(12)
    par(p["subtitulo"])
    local = f"{p['cidade']}, {p['estado']}" if lang == "pt" else f"{p['cidade']}, {p['pais']}"
    contato = [f"{local} · {r['remoto']}", p["email"]] + ([telefone] if telefone else [])
    contato += ["github.com/mateusrfabro", p["linkedin"].split("//")[1].removeprefix("www."), s["url"].split("//")[1]]
    par(" · ".join(contato))

    h(r["resumo"], 1)
    for t in (cv["resumo_discreto"] if discreto(d) else cv["resumo"])[lang]:
        par(t)
    h(r["numeros"], 1)
    for n in cv.get("destaques", {}).get(lang) or d["numeros"]:
        item(f"{n['valor']} {n['rotulo']}")
    h(r["experiencia"], 1)
    for x in d["experiencia"]:
        blocos = cv["experiencia"][x["id"]][lang]
        h(x["cargo"], 2)
        nota = f" · {x['nota']}" if x.get("nota") else ""
        par(f"{x['empresa']} · {x['local']} · {periodo_ats(x, lang)}{nota}")
        if blocos and "bloco" in blocos[0]:
            par(x["resumo"])
            for b in blocos:
                par("", negrito=b["bloco"])
                for i in b["itens"]:
                    if not i.get("so_site"):
                        item(i["texto"])
        else:
            for i in blocos:
                item(i["texto"])
    h(r["produtos"], 1)
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        link = f" · {pr['url'].split('//')[1]}" if pr.get("url") else ""
        par(f" — {pr['linha']} · {pr['status']}{link}", negrito=pr["nome"])
    h(r["stack"], 1)
    for c in cv["stack"][lang]:
        par(f" {c['itens']}", negrito=f"{c['categoria']}:")
    h(r["formacao"], 1)
    for f in p["formacao"]:
        par(f" — {f['instituicao']} · {f['inicio']}–{f['fim']} ({f['status']})", negrito=f["curso"])
    h(r["idiomas"], 1)
    par(" · ".join(p["idiomas"]))
    doc.core_properties.author = p["nome"]
    doc.core_properties.title = f"{p['nome']} — {cv.get('titulo_ats', {}).get(lang, p['cargo'])}"
    doc.save(str(destino))


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
    return [ONEDRIVE / f"Curriculo_Mateus_Fabro_v5_{lang.upper()}.{ext}" for lang in LANGS for ext in ("html", "pdf", "docx")]


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
            alvo.write_text(curriculo_html(dados(lang, "completo"), cv, lang, telefone=tel), encoding="utf-8", newline="\n")
            curriculo_docx(dados(lang, "completo"), cv, lang, alvo.with_suffix(".docx"), telefone=tel)
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
    "Data Pipelines", "ETL", "AWS", "Amazon Athena", "Apache Iceberg", "Prefect", "MongoDB", "Redis",
    "Supabase", "NestJS", "Next.js", "React", "Flask", "FastAPI", "Astro", "Docker", "Linux", "Git",
    "GitHub Actions", "CI/CD", "pytest", "Jest", "Prisma", "Playwright", "Antifraude", "Detecção de Fraude",
    "Credit Scoring", "Atribuição de Marketing", "Meta Ads API", "Google Ads API", "CRM", "Power BI",
    "pandas", "Machine Learning", "LLM", "Claude Code", "Anthropic API", "LangChain", "n8n", "Automação", "LGPD", "Engenharia de Agentes", "Prompt Engineering", "MCP"]


COMPETENCIAS_EN = {"Engenharia de Dados": "Data Engineering", "Antifraude": "Anti-fraud", "Detecção de Fraude": "Fraud Detection",
                   "Atribuição de Marketing": "Marketing Attribution", "Automação": "Automation",
                   "Engenharia de Agentes": "Agent Engineering"}


def competencias(lang: str) -> list[str]:
    return COMPETENCIAS if lang == "pt" else [COMPETENCIAS_EN.get(c, c) for c in COMPETENCIAS]


def _check(nome: str, texto: str) -> str:
    chave = nome.split(":")[0]
    if len(texto) > LIMITES[chave]:
        raise ValueError(f"{nome}: {len(texto)} caracteres, limite {LIMITES[chave]}")
    return texto


MESES_EXT = {"pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
                    "outubro", "novembro", "dezembro"],
             "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                    "October", "November", "December"]}


def mes_extenso(iso: str, lang: str) -> str:
    y, m = iso.split("-")
    return f"{MESES_EXT[lang][int(m) - 1]} de {y}" if lang == "pt" else f"{MESES_EXT[lang][int(m) - 1]} {y}"


def _bullets_agentes(cv: dict, lang: str) -> list[str]:
    """Bullets do bloco de IA do currículo (fonte única: curriculo.json)."""
    pref = "IA" if lang == "pt" else "Applied"
    bloco = next(b for b in cv["experiencia"]["super-nova"][lang] if b["bloco"].startswith(pref))
    return [i.get("texto_sobre", i["texto"]) for i in bloco["itens"]]   # About do LinkedIn: versão longa, já publicada


def _sobre_e_post(d: dict, cv: dict, lang: str) -> tuple[str, str]:
    """Sobre e post: estrutura fixa (prosa) + todo número/fato vem dos dados, nada digitado."""
    pt = lang == "pt"
    p, x0, n, site = d["perfil"], d["experiencia"][0], d["numeros"], d["site"]["url"]
    proj = {pr["slug"]: pr for pr in d["projetos"]}
    produtos = [pr for pr in d["projetos"] if pr["tipo"] == "produto"]
    no_ar = sum(1 for pr in produtos if build.status_vivo(pr))      # derivado do status, não digitado
    fatos = [f[0].upper() + f[1:] for f in proj["igaming-dados"]["fatos"]
             if not re.match(r"\d[\d.,]* (commits|of my commits)", f)]
    k_py = re.search(r"\d+", n[2]["rotulo"]).group()                   # nº de produtos em Python, do rótulo medido
    fora = (f"Fora do expediente, {len(produtos)} produtos próprios construídos de ponta a ponta, {no_ar} no ar. "
            f"Em 2026: {n[1]['valor']} commits meus nesses produtos e {n[2]['valor']} funções de teste nos {k_py} escritos em Python." if pt else
            f"Outside work, {len(produtos)} products of my own built end to end, {no_ar} of them live. "
            f"In 2026: {n[1]['valor']} commits of mine across them and {n[2]['valor']} test functions in the {k_py} written in Python.")
    # O Sobre (limite 2.600) deixa de fora o serviço de risco, o único fato sem número; ele segue no currículo e no post.
    fatos_sobre = [f for f in fatos if not f.lower().startswith(("serviço diário", "daily risk"))]
    ini = mes_extenso(x0["inicio"], lang)
    fim = mes_extenso(x0["fim"], lang) if x0.get("fim") else None
    st = proj["dumpai"]["status"]
    st = st[0].lower() + st[1:]
    sobre = "\n\n".join([
        f"{p['cargo']}. {p['subtitulo']}",
        "Na prática: ingestão, modelagem, antifraude, atribuição, API e painel saem da mesma mão." if pt else
        "In practice: ingestion, modeling, anti-fraud, attribution, API and dashboard come from the same hands.",
        (f"O que provei em produção — {x0['empresa']}, {periodo(x0, lang)}:" if pt else
         f"What I proved in production — {x0['empresa']}, {periodo(x0, lang)}:") + "\n" + x0["resumo"]
        + "\n" + "\n".join(f"• {f}" for f in fatos_sobre),
        fora + (f" Um deles tem {proj['pingado']['fatos'][2]}; outro está {st} — e o site diz isso." if pt else
                f" One of them has a {proj['pingado']['fatos'][2]}; another is {st} — and the site says so."),
        ("Engenharia de agentes (trabalho em par com Claude Code; cada erro corrigido vira lição):" if pt else
         "Agent engineering (I work paired with Claude Code; every fixed mistake becomes a lesson):") + "\n" + "\n".join(f"• {t}" for t in _bullets_agentes(cv, lang)),
        d["disponibilidade"]["texto"],            # o fim da operação já está no resumo do bloco acima
        ("Site, números medidos e lições de casos reais: " if pt else "Site, measured numbers and lessons from real cases: ") + site + "\n"
        + ("Currículo: " if pt else "Résumé: ") + f"{site}/curriculo/mateus-fabro-{lang}.pdf\n"
        + ("Contato: " if pt else "Contact: ") + p["email"]])

    def post_com(k: int) -> str:
        return "\n\n".join([
            (f"A empresa em que trabalhei de {ini} a {fim} foi encerrada. Saio com o que construí lá e começo a busca: "
             f"vaga de engenharia de dados, analytics engineering ou desenvolvimento de produto — PJ ou CLT, remoto." if pt else
             f"The company I worked at from {ini} to {fim} shut down. I leave with what I built there and start "
             f"the search: a data engineering, analytics engineering or product development role — contract or full-time, remote."),
            ("O que levo:\n" if pt else "What I bring:\n") + "\n".join(f"• {f}" for f in fatos[:k]) + f"\n• {fora}",
            ("Se você souber de uma vaga, ou de um time que precise de alguém que constrói o pipeline e o produto em volta "
             "dele, uma indicação ajuda muito. Converso também sobre projeto de escopo fechado." if pt else
             "If you know of an opening, or a team that needs someone who builds the pipeline and the product around it, "
             "a referral helps a lot. Also open to fixed-scope projects."),
            (f"Site e currículo: {site}\nE-mail: {p['email']}" if pt else f"Site and résumé: {site}\nE-mail: {p['email']}"),
            "#EngenhariaDeDados #AnalyticsEngineering #OpenToWork" if pt else "#DataEngineering #AnalyticsEngineering #OpenToWork"])

    if discreto(d):                                        # o post anuncia a saída: não existe em modo discreto
        return sobre, ("Post de disponibilidade: não publicar em modo discreto." if pt else
                       "Availability post: do not publish in discreet mode.")
    post = post_com(3)
    if len(post) > LIMITES["post"]:
        post = post_com(2)                                 # estourou: vão só 2 fatos
    return sobre, post


def linkedin_secoes(d: dict, cv: dict, lang: str) -> dict[str, str]:
    p, x0 = d["perfil"], d["experiencia"][0]
    pt = lang == "pt"
    fecho = {("pt", True): "aberto a projetos e vagas", ("en", True): "open to projects and roles",
             ("pt", False): "em busca de vaga (PJ/CLT, remoto)",
             ("en", False): "open to work (contract or full-time, remote)"}[(lang, discreto(d))]
    # Busca de recrutador (LinkedIn) prioriza o cargo exato: os títulos da vaga abrem a headline.
    cargos = cv.get("titulo_ats", {}).get(lang, p["cargo"])
    titulo = (f"{cargos} | Python · SQL · TypeScript · AWS · agentes de IA | pipelines, antifraude e atribuição · "
              f"produtos próprios | {fecho}" if pt else
              f"{cargos} | Python · SQL · TypeScript · AWS · AI agents | pipelines, anti-fraud and attribution · "
              f"own products in production | {fecho}")
    sobre, post = _sobre_e_post(d, cv, lang)
    secoes = {"titulo": titulo, "sobre": sobre}
    for x in d["experiencia"]:
        blocos = cv["experiencia"][x["id"]][lang]
        if blocos and "bloco" in blocos[0]:
            # experiência principal: só o 1º bullet de cada bloco (limite de 2.000 caracteres do LinkedIn)
            # super-nova: 1º bullet de cada bloco, menos o de IA (já está no Sobre)
            pref_ia = "IA" if pt else "Applied"
            itens = ([b["itens"][0] for b in blocos if not b["bloco"].startswith(pref_ia)] if x["id"] == "super-nova"
                     else [i for b in blocos for i in b["itens"]])
        else:
            itens = blocos
        lista = "\n".join(f"• {i['texto']}" for i in itens)
        corpo = x["resumo"] + "\n\n" + lista if x["id"] == "super-nova" else lista   # flat: o resumo duplicaria os bullets
        secoes[f"experiencia:{x['id']}"] = corpo
    fora_do_kit = {"atendimento-whatsapp", "credito-nda"}          # piloto parado; sob NDA — ficam 6 (limite do LinkedIn)
    for pr in d["projetos"]:
        if pr["tipo"] == "produto" and pr["slug"] not in fora_do_kit:
            secoes[f"projeto:{pr['slug']}"] = f"{pr['linha']}\n{pr['status']}.\n" + "\n".join(f"• {f}" for f in pr["fatos"][:3])
    secoes["post"] = post
    return {k: _check(k, v) for k, v in secoes.items()}


def linkedin_md(d: dict, cv: dict, lang: str) -> str:
    s = linkedin_secoes(d, cv, lang)
    p = d["perfil"]
    pt = lang == "pt"
    L = [f"# Kit LinkedIn — {p['nome']} — {date.today().isoformat()} ({lang})", "",
         (("Cada seção abaixo cabe no limite do LinkedIn. Colar na ordem. "
           "Open to work: ativar SÓ com visibilidade 'Somente recrutadores' (nunca o selo público); "
           "desligar 'Compartilhar atualizações do perfil com a rede' antes de editar."
           if discreto(d) else
           "Cada seção abaixo cabe no limite do LinkedIn. Colar na ordem. Depois de colar, ligar o "
           "\"Open to work\" (Cargos: Engenheiro de Dados, Analytics Engineer, Desenvolvedor Python; remoto; PJ e CLT).")
          if pt else
          ("Each section fits LinkedIn's limit. Paste in order. Open to work: turn on ONLY with 'Recruiters only' "
           "visibility (never the public badge); turn off 'Share profile updates with your network' before editing."
           if discreto(d) else "Each section fits LinkedIn's limit. Paste in order.")), "",
         "## 1. Título (Intro → Headline)", "", "```", s["titulo"], "```", "",
         "## 2. Sobre (About)", "", "```", s["sobre"], "```", ""]
    L += ["## 3. Experiência (uma entrada por bloco; cargo, empresa, datas, local, descrição)", ""]
    for x in d["experiencia"]:
        nota = f" · {x['nota']}" if x.get("nota") else ""
        motivo = ("- Motivo de saída (se perguntarem): encerramento da operação."
                  if x["id"] == "super-nova" and pt and not discreto(d) else None)   # discreto: omitido
        L += [f"### {x['cargo']} — {x['empresa']}", f"- Datas: {periodo(x, lang)} · {x['local']}{nota}"]
        L += [motivo] if motivo else []
        L += ["", "```", s[f"experiencia:{x['id']}"], "```", ""]
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
            L += [f"### {pr['nome']}", f"- Link: {pr.get('url') or d['site']['url'] + ('/#' if pt else '/en/#') + pr['slug']}",
                  "", "```", v, "```", ""]
    L += ["## 6. Competências (Skills) — marcar estas 50", "", ", ".join(competencias(lang)), "",
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


# ============================================================================ GitHub
REPOS_GH = RAIZ / "scripts" / "github_repos.json"
DOCS_GH = RAIZ / "docs" / "github"


def github_readme(d: dict, cv: dict) -> str:
    p, s = d["perfil"], d["site"]
    repos = json.loads(REPOS_GH.read_text(encoding="utf-8"))
    L = [f"# {p['nome']} — {p['cargo']}", "", f"**{p['subtitulo']}**", "",
         f"🟢 **{d['disponibilidade']['status'].capitalize()}** — {d['disponibilidade']['texto']}", "",
         f"- Site (projetos, números medidos e lições de casos reais): {s['url']}",
         f"- Currículo: [PT]({s['url']}/curriculo/mateus-fabro-pt.pdf) · [EN]({s['url']}/curriculo/mateus-fabro-en.pdf)",
         f"- LinkedIn: {p['linkedin']}", f"- E-mail: {p['email']}", "",
         "## O que eu faço", ""] + [f"- {par}" for par in (cv["resumo_discreto"] if discreto(d) else cv["resumo"])["pt"]] + ["",
         "## Projetos", "", "| Projeto | O que é | Status | Código |", "|---|---|---|---|"]
    por_nome = {r["nome"]: r for r in repos}
    pares = {"avisa-edital": "avisa-edital", "pingado": "cafesaas", "nous-clinical": "nous-clinical",
             "aggron": "poolcompras", "dumpai": "dumpai", "atendimento-whatsapp": "secretaria-ia",
             "credito-nda": "credito-saas", "portais-conteudo": "guiadocredito"}
    portais = ["guiadocredito", "radardoinvestidor", "central-do-trabalhador", "usmoneybrasil", "mydollarpilot"]
    ausentes = [n for n in portais if n not in por_nome]
    if ausentes:
        raise SystemExit(f"github_repos.json sem os repositórios dos portais: {ausentes}")
    for pr in d["projetos"]:
        if pr["tipo"] != "produto":
            continue
        r = por_nome[pares[pr["slug"]]]
        codigo = f"[{r['nome']}](https://github.com/mateusrfabro/{r['nome']})" if r["abre"] else f"`{r['nome']}` (privado)"
        if pr["slug"] == "portais-conteudo":
            codigo = ", ".join(f"`{n}`" for n in portais) + " (privados)"
        L.append(f"| **{pr['nome']}** | {pr['linha']} | {pr['status']} | {codigo} |")
    extra = [r for r in repos if r["mostrar"] and r["nome"] not in pares.values()]
    for r in extra:
        codigo = f"[{r['nome']}](https://github.com/mateusrfabro/{r['nome']})" if r["abre"] else f"`{r['nome']}` (privado)"
        L.append(f"| **{r['nome']}** | {r['descricao']} | — | {codigo} |")
    x0 = d["experiencia"][0]
    trabalho = (f"Trabalho atual: {x0['empresa']}, desde {mes_ano(x0['inicio'], 'pt')}" if discreto(d)
                else f"Trabalho anterior: {x0['empresa']}, {periodo(x0, 'pt')}")
    L += ["", f"{trabalho} — repositórios privados (dados da empresa).", "",
          "## Engenharia de agentes", ""] + [f"- {t}" for t in _bullets_agentes(cv, "pt")] + ["",
          "## Como trabalho", ""] + [f"- **{m['titulo']}.** {m['texto']}" for m in d["metodo"]] + ["",
          f"_README gerado de `conteudo/dados.json` em {s['medido_em']} pelo repositório "
          f"[diario-mateus-fabro](https://github.com/mateusrfabro/diario-mateus-fabro)._", ""]
    return "\n".join(L)


def cmd_github(args: list[str]) -> int:
    DOCS_GH.mkdir(parents=True, exist_ok=True)
    alvo = DOCS_GH / "README.md"
    alvo.write_text(github_readme(dados('pt'), carregar_cv()), encoding="utf-8", newline="\n")
    print(alvo.relative_to(RAIZ))
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("curriculo", "linkedin", "github"):
        print(__doc__)
        return 2
    return {"curriculo": cmd_curriculo, "linkedin": cmd_linkedin, "github": cmd_github}[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
