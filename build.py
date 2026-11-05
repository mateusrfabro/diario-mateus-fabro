"""Gera o site inteiro a partir de UM arquivo: conteudo/dados.json.

Por que um gerador e não HTML escrito à mão: o mesmo conteúdo sai em seis formas (página,
Markdown, llms.txt, llms-full.txt, JSON Resume e o servidor MCP). Escrito à mão, cada número
viveria em seis lugares e envelheceria em cada um no seu ritmo — "número fora do código
envelhece sozinho". Aqui ele nasce uma vez; `tests/test_build.py` confere que o que está em
public/ é exatamente o que este script produz hoje.

Uso:  python build.py          # regenera public/
      python build.py --check  # falha se public/ estiver desatualizado (usado no teste)
"""
from __future__ import annotations

import html
import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DADOS = RAIZ / "conteudo" / "dados.json"
DADOS_EN = RAIZ / "conteudo" / "dados.en.json"
SAIDA = RAIZ / "public"
CURRICULO = RAIZ / "conteudo" / "curriculo.json"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]

# Crawlers de IA liberados nominalmente (além do `*`). Nomes vigentes em set/2026:
# OpenAI, Anthropic, Perplexity, Google, Apple, Microsoft, DuckDuckGo, Mistral, Meta.
ROBOS_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
            "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot",
            "Bingbot", "Applebot", "Applebot-Extended", "DuckAssistBot", "MistralAI-User",
            "Meta-ExternalAgent", "Amazonbot", "CCBot"]


def carregar() -> dict:
    return json.loads(DADOS.read_text(encoding="utf-8"))


def carregar_en() -> dict:
    return json.loads(DADOS_EN.read_text(encoding="utf-8"))


def vista(d: dict, modo: str | None = None) -> dict:
    """Cópia profunda de `d` na versão que se publica. `site.modo` (ou o argumento `modo`) escolhe:
    "completo" = verdade inteira; "discreto" = cada campo `*_discreto`/`*_discreta` substitui o campo-base
    e o fim do emprego atual some (sem fim = emprego corrente). Os campos `*_discreto` nunca saem na vista."""
    import copy
    v = copy.deepcopy(d)
    modo = modo or v["site"].get("modo", "completo")
    v["site"]["modo"] = modo

    def aplicar(o):
        if isinstance(o, dict):
            for k in [k for k in o if k.endswith(("_discreto", "_discreta"))]:
                alt = o.pop(k)
                if modo == "discreto":
                    o[k[:-9]] = alt
            for x in o.values():
                aplicar(x)
        elif isinstance(o, list):
            for x in o:
                aplicar(x)
    aplicar(v)
    if modo == "discreto":
        v["experiencia"][0]["fim"] = None
    return v


def e(s: str) -> str:
    return html.escape(str(s), quote=True)


def data_extenso(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def data_curta(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def edicao(d: dict) -> str:
    """Número de lições registradas (o 1º de `numeros`, recontado pelo recontar.py)."""
    return d["numeros"][0]["valor"]


def ordenadas(retificacoes: list[dict]) -> list[dict]:
    return sorted(retificacoes, key=lambda r: r["data"])


# ============================================================================ textos fixos
# Tudo que a página diz e não vem do conteúdo. Um dicionário por idioma: a versão em inglês
# é a mesma página, não uma cópia que envelhece à parte.
T = {
    "pt": {
        "prefixo": "", "locale": "pt_BR", "outro": "en", "outro_rotulo": "English",
        "outro_href": "/en/", "menu": "Seções", "inicio": "Início",
        "nav": ["Experiência", "Projetos", "Stack", "Lições", "Contato"],
        "h_numeros": "Em números", "h_pilares": "O que eu entrego", "h_exp": "Experiência",
        "h_form": "Formação", "h_proj": "Projetos", "h_stack": "Stack", "h_met": "Como trabalho",
        "h_contato": "Contato", "h_licoes": "Lições", "sub_licoes": "Erros que viraram regra",
        "medido": "Números medidos em {d}, contados nos repositórios — não de cabeça.",
        "como_medido": "Como cada número foi contado",
        "l_exp": "Dados em produção para três operações de iGaming, e antes disso crédito, cobrança e indicadores.",
        "l_proj": "Produtos próprios, do coletor ao cliente, com o status real de cada um — inclusive os que pararam.",
        "l_stack": "O que uso no dia a dia, agrupado pelo tipo de trabalho.",
        "l_met": "Em par com agentes de IA, e com um sistema que impede o mesmo erro de acontecer duas vezes.",
        "link_licoes": "{n} lições de casos reais →",
        "idiomas": "Idiomas", "atual": "atual", "tecnologias": "Tecnologias",
        "remoto": "remoto", "faq": "Perguntas frequentes",
        "maquinas": "Para máquinas",
        "rodape": "Gerado de um arquivo só (conteudo/dados.json): página, Markdown, llms.txt, JSON Resume e MCP.",
        "medido_em": "Medido em {d}",
        "l_licoes": ("Erros que eu cometi em casos reais, com a data em que cada um foi achado e corrigido, "
                     "e as regras que ficaram. Nomes de cliente ficam de fora."),
        "h_ret": "Erros corrigidos", "h_atos": "Regras que ficaram",
        "l_atos": "{a} das {n} lições registradas. Cada uma nasceu de um caso real e tem origem, motivo e forma de aplicar.",
        "onde": "Onde se lê", "leia": "Leia-se", "regra": "Regra que ficou:",
        "voltar": "← Voltar ao início",
        # Markdown
        "md_medido": "Medido em {d}.", "md_resumo": "Resumo", "md_numeros": "Números",
        "md_fonte": "fonte", "md_proj": "Projetos", "md_ret": "Lições de casos reais: erros corrigidos",
        "md_ret_l": "Erros que cometi, no formato onde se lê / leia-se. Cada um virou uma regra.",
        "md_atos": "Regras que ficaram", "md_atos_l": "{a} das {n} lições registradas, publicadas aqui.",
        "md_met": "Como trabalho", "md_disp": "Disponibilidade", "md_contato": "Contato",
        "md_faq": "Perguntas frequentes", "md_agentes": "Para agentes",
        "md_mcp": "Servidor MCP (Streamable HTTP, sem autenticação, só leitura)",
        "md_resume": "Currículo em JSON Resume", "md_este": "Este texto",
        "p_para_quem": "Para quem", "p_papel": "Meu papel", "p_status": "Status", "p_stack": "Stack",
        "p_endereco": "Endereço", "p_fatos": "Fatos",
        "cv": "Currículo (PDF)", "email_btn": "Falar por e-mail", "ver_proj": "Ver projetos", "md_cv": "Currículo em PDF",
        "cv_arquivo": "mateus-fabro-pt.pdf", "assunto": "Vaga%20-%20via%20site",
    },
    "en": {
        "prefixo": "/en", "locale": "en_US", "outro": "pt", "outro_rotulo": "Português",
        "outro_href": "/", "menu": "Sections", "inicio": "Home",
        "nav": ["Experience", "Projects", "Stack", "Lessons", "Contact"],
        "h_numeros": "In numbers", "h_pilares": "What I deliver", "h_exp": "Experience",
        "h_form": "Education", "h_proj": "Projects", "h_stack": "Stack", "h_met": "How I work",
        "h_contato": "Contact", "h_licoes": "Lessons", "sub_licoes": "Mistakes that became rules",
        "medido": "Numbers measured on {d}, counted in the repositories — not from memory.",
        "como_medido": "How each number was counted",
        "l_exp": "Production data for three iGaming operations, and before that credit, collections and KPIs.",
        "l_proj": "My own products, from the scraper to the customer, with the real status of each — including the ones that stopped.",
        "l_stack": "What I use day to day, grouped by kind of work.",
        "l_met": "Paired with AI agents, and with a system that keeps the same mistake from happening twice.",
        "link_licoes": "{n} lessons from real cases →",
        "idiomas": "Languages", "atual": "present", "tecnologias": "Technologies",
        "remoto": "remote", "faq": "Frequently asked questions",
        "maquinas": "For machines",
        "rodape": "Generated from a single file (conteudo/dados.en.json): page, Markdown, JSON Resume.",
        "medido_em": "Measured on {d}",
        "l_licoes": ("Mistakes I made in real cases, with the date each one was found and fixed, "
                     "and the rules that stayed. Client names are left out."),
        "h_ret": "Corrected mistakes", "h_atos": "Rules that stayed",
        "l_atos": "{a} of the {n} recorded lessons. Each came from a real case and has an origin, a reason and a way to apply it.",
        "onde": "For", "leia": "Read", "regra": "Rule that stayed:",
        "voltar": "← Back to home",
        "md_medido": "Measured on {d}.", "md_resumo": "Summary", "md_numeros": "Numbers",
        "md_fonte": "source", "md_proj": "Projects", "md_ret": "Lessons from real cases: corrected mistakes",
        "md_ret_l": "Mistakes I made, in the format “for … read …”. Each one became a rule.",
        "md_atos": "Rules that stayed", "md_atos_l": "{a} of the {n} recorded lessons, published here.",
        "md_met": "How I work", "md_disp": "Availability", "md_contato": "Contact",
        "md_faq": "Frequently asked questions", "md_agentes": "For agents",
        "md_mcp": "MCP server (Streamable HTTP, no auth, read-only; tools and content in Portuguese)",
        "md_resume": "JSON Resume", "md_este": "This text",
        "p_para_quem": "For whom", "p_papel": "My role", "p_status": "Status", "p_stack": "Stack",
        "p_endereco": "Address", "p_fatos": "Facts",
        "cv": "Résumé (PDF)", "email_btn": "Email me", "ver_proj": "See projects", "md_cv": "Résumé as PDF",
        "cv_arquivo": "mateus-fabro-en.pdf", "assunto": "Role%20-%20via%20site",
    },
}

MESES_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
            "October", "November", "December"]


def data_extenso_t(iso: str, t: dict) -> str:
    if t is T["en"]:
        dd = date.fromisoformat(iso)
        return f"{MESES_EN[dd.month - 1]} {dd.day}, {dd.year}"
    return data_extenso(iso)


def data_curta_t(iso: str, t: dict) -> str:
    return iso if t is T["en"] else data_curta(iso)


# ============================================================================ Markdown
def markdown(d: dict, t: dict = T["pt"]) -> str:
    p, s = d["perfil"], d["site"]
    base = s["url"] + t["prefixo"]
    L = [f"# {p['nome']} — {p['cargo']}", "",
         f"> {p['tese']}", "",
         f"{p['cidade']}, {p['estado']} · {p['email']} · {p['github']} · {p['linkedin']}", "",
         t["md_medido"].format(d=data_curta_t(s["medido_em"], t), n=edicao(d)), ""]
    L += [f"## {t['md_resumo']}", ""] + [f"{par}\n" for par in p["resumo"]]
    L += [f"## {t['md_numeros']}", ""]
    L += [f"- **{n['valor']}** {n['rotulo']} ({t['md_fonte']}: {n['fonte']})" for n in d["numeros"]]
    L += ["", f"## {t['md_proj']}", ""]
    for pr in d["projetos"]:
        L += [projeto_md(pr, nivel=3, t=t), ""]
    L += [f"## {t['md_ret']}", "", t["md_ret_l"], ""]
    for r in ordenadas(d["retificacoes"]):
        L += [f"### {r['protocolo']} — {data_curta_t(r['data'], t)} — {r['contexto']}", "",
              f"- **{t['onde']}:** {r['onde_se_le']}",
              f"- **{t['leia']}:** {r['leia_se']}",
              f"- **{t['regra'].rstrip(':')}:** {r['regra']}", ""]
    L += [f"## {t['md_atos']}", "", t["md_atos_l"].format(a=len(d["atos"]), n=edicao(d)), ""]
    L += [f"{i}. **{a['titulo']}** — {a['texto']}" for i, a in enumerate(d["atos"], 1)]
    L += ["", f"## {t['md_met']}", ""]
    L += [f"- **{m['titulo']}.** {m['texto']}" for m in d["metodo"]]
    L += ["", f"## {t['md_disp']}", "", d["disponibilidade"]["texto"], "",
          f"{t['md_contato']}: {d['disponibilidade']['canal']}", ""]
    L += [f"## {t['md_faq']}", ""]
    for f in d["faq"]:
        L += [f"**{f['pergunta']}**", "", f["resposta"], ""]
    L += [f"## {t['md_agentes']}", "",
          f"- {t['md_mcp']}: {s['url']}/mcp",
          f"- {t['md_resume']}: {s['url']}/resume.json",
          f"- {t['md_cv']}: {s['url']}/curriculo/{t['cv_arquivo']}",
          f"- {t['md_este']}: {base}/index.md", ""]
    return "\n".join(L)


def projeto_md(pr: dict, nivel: int = 1, t: dict = T["pt"]) -> str:
    h = "#" * nivel
    L = [f"{h} {pr['nome']}", "", pr["linha"], "",
         f"- **{t['p_para_quem']}:** {pr['para_quem']}",
         f"- **{t['p_papel']}:** {pr['papel']}",
         f"- **{t['p_status']}:** {pr['status']}",
         f"- **{t['p_stack']}:** {', '.join(pr['stack'])}"]
    if pr.get("url"):
        L.append(f"- **{t['p_endereco']}:** {pr['url']}")
    L += [f"- **{t['p_fatos']}:**"] + [f"  - {f}" for f in pr["fatos"]]
    L += ["", pr["historia"]]
    return "\n".join(L)


def llms_txt(d: dict) -> str:
    p, s = d["perfil"], d["site"]
    L = [f"# {p['nome']}", "", f"> {s['descricao']}", "",
         p["tese"], "",
         "## Principal",
         f"- [Página completa em Markdown]({s['url']}/index.md): perfil, projetos, retificações, lições e contato",
         f"- [Full page in English]({s['url']}/en/index.md): the same content, translated",
         f"- [Lições de casos reais]({s['url']}/licoes/): erros corrigidos (onde se lê / leia-se) e as regras que ficaram",
         f"- [Currículo em JSON Resume]({s['url']}/resume.json): formato estruturado",
         f"- [Currículo em PDF]({s['url']}/curriculo/{T['pt']['cv_arquivo']}): para imprimir (English: {s['url']}/curriculo/{T['en']['cv_arquivo']})",
         f"- [Servidor MCP]({s['url']}/mcp): ferramentas ler_perfil, listar_projetos, ver_projeto, listar_retificacoes, buscar_licoes, verificar_disponibilidade",
         "", "## Projetos"]
    L += [f"- [{pr['nome']}]({s['url']}/projetos/{pr['slug']}.md): {pr['linha']}" for pr in d["projetos"]]
    L += ["", "## Optional",
          f"- [Texto completo]({s['url']}/llms-full.txt): tudo acima num arquivo só", ""]
    return "\n".join(L)


def resume_json(d: dict) -> dict:
    p, s = d["perfil"], d["site"]
    trabalho = next(pr for pr in d["projetos"] if pr["tipo"] == "trabalho")
    work = []
    for x in d["experiencia"]:
        item = {"name": x["empresa"], "position": x["cargo"], "startDate": x["inicio"],
                "summary": x["resumo"] + (f" ({x['nota']})" if x.get("nota") else "")}
        if x.get("fim"):                       # sem endDate = emprego atual (JSON Resume)
            item["endDate"] = x["fim"]
        if x["id"] == "super-nova":
            item["highlights"] = trabalho["fatos"]
        work.append(item)
    return {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {
            "name": p["nome"], "label": p["cargo"], "email": p["email"], "url": s["url"],
            "summary": " ".join(p["resumo"]),
            "location": {"city": p["cidade"], "region": p["estado"], "countryCode": "BR"},
            "profiles": [{"network": "GitHub", "username": "mateusrfabro", "url": p["github"]},
                         {"network": "LinkedIn", "url": p["linkedin"]}],
        },
        "work": work,
        "projects": [{"name": pr["nome"], "description": pr["linha"], "highlights": pr["fatos"],
                      "keywords": pr["stack"], **({"url": pr["url"]} if pr.get("url") else {})}
                     for pr in d["projetos"] if pr["tipo"] == "produto"],
        "education": [{"institution": f["instituicao"], "area": f["curso"],
                       "studyType": f"Graduação ({f['status']})", "startDate": f["inicio"], "endDate": f["fim"]}
                      for f in p["formacao"]],
        "languages": [{"language": i.split(" (")[0], "fluency": i.split("(")[1].rstrip(")")}
                      for i in p["idiomas"]],
        "meta": {"lastModified": s["medido_em"], "version": f"edicao-{edicao(d)}"},
    }


def json_ld(d: dict) -> dict:
    p, s = d["perfil"], d["site"]
    pagina_url = s["url"] + ("/en/" if s["idioma"] == "en" else "/")
    pessoa = {"@type": "Person", "@id": f"{s['url']}/#pessoa", "name": p["nome"],
              "jobTitle": p["cargo"], "email": f"mailto:{p['email']}",
              "url": s["url"], "sameAs": [p["github"], p["linkedin"]],
              "address": {"@type": "PostalAddress", "addressLocality": p["cidade"],
                          "addressRegion": p["estado"], "addressCountry": "BR"},
              "knowsAbout": ["Engenharia de dados", "Analytics engineering", "Python", "SQL",
                             "PostgreSQL", "AWS", "TypeScript", "Antifraude", "Agentes de IA", "Next.js", "Flask"],
              "description": p["tese"]}
    return {"@context": "https://schema.org", "@graph": [
        pessoa,
        {"@type": "WebSite", "@id": f"{s['url']}/#site", "url": s["url"], "name": s["titulo"],
         "inLanguage": s["idioma"], "author": {"@id": f"{s['url']}/#pessoa"}},
        {"@type": "ProfilePage", "@id": f"{pagina_url}#pagina", "url": pagina_url, "name": s["titulo"],
         "dateModified": s["medido_em"], "mainEntity": {"@id": f"{s['url']}/#pessoa"},
         "isPartOf": {"@id": f"{s['url']}/#site"}},
        {"@type": "ItemList", "name": "Projetos", "itemListElement": [
            {"@type": "ListItem", "position": i,
             "item": {"@type": "CreativeWork", "name": pr["nome"], "description": pr["linha"],
                      **({"url": pr["url"]} if pr.get("url") else {})}}
            for i, pr in enumerate(d["projetos"], 1)]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["pergunta"],
             "acceptedAnswer": {"@type": "Answer", "text": f["resposta"]}} for f in d["faq"]]},
    ]}


# ============================================================================ HTML
# Pele: clara, corporativa, uma cor de destaque (o teal #0E5A63), fonte do sistema (a CSP só aceita
# estilo e fonte de 'self'; fonte do sistema não pesa nada e não pisca). O motivo visual é um só:
# o quadradinho teal — na marca, nos marcadores das provas e no traço sobre cada título.
CSS = r"""
:root{
  --bg:#FFFFFF; --bg-2:#F3F6F7; --card:#FFFFFF; --ink:#0F1D22; --ink-2:#33464D; --muted:#5A6B72;
  --line:#E1E8EB; --line-2:#C8D3D7; --accent:#0E5A63; --accent-ink:#FFFFFF; --accent-hover:#0A464D;
  --accent-soft:#E6F0F1; --sombra:0 14px 34px -22px rgba(15,29,34,.45);
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif;
  --mono:ui-monospace,"SFMono-Regular","Cascadia Mono","Segoe UI Mono",Menlo,Consolas,monospace;
  --r:12px; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0C1316; --bg-2:#111B1F; --card:#101A1E; --ink:#E6EDEF; --ink-2:#C1CDD1; --muted:#8D9EA4;
    --line:#1E2B30; --line-2:#2B3B41; --accent:#5DB6C1; --accent-ink:#05262A; --accent-hover:#82CAD3;
    --accent-soft:#11292C; --sombra:0 14px 34px -22px rgba(0,0,0,.9); color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --bg:#0C1316; --bg-2:#111B1F; --card:#101A1E; --ink:#E6EDEF; --ink-2:#C1CDD1; --muted:#8D9EA4;
  --line:#1E2B30; --line-2:#2B3B41; --accent:#5DB6C1; --accent-ink:#05262A; --accent-hover:#82CAD3;
  --accent-soft:#11292C; --sombra:0 14px 34px -22px rgba(0,0,0,.9); color-scheme:dark;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:76px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:1rem;line-height:1.6;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;overflow-wrap:break-word}
h1,h2,h3{color:var(--ink);text-wrap:balance}
p{margin:0}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:.2em}
a:hover{color:var(--accent-hover)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:6px}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
@media (min-width:720px){.wrap{padding:0 32px}}
.mono{font-family:var(--mono)}
.pular{position:absolute;left:-9999px}
.pular:focus{left:16px;top:12px;z-index:20;background:var(--card);padding:10px 14px;border-radius:8px}

/* ---------- barra do topo */
.topo{position:sticky;top:0;z-index:10;border-top:3px solid var(--accent);border-bottom:1px solid var(--line);
  background:color-mix(in srgb,var(--bg) 90%,transparent);-webkit-backdrop-filter:saturate(1.4) blur(10px);
  backdrop-filter:saturate(1.4) blur(10px)}
.topo-in{display:flex;align-items:center;gap:12px;min-height:60px}
.marca{display:inline-flex;align-items:center;gap:10px;min-height:44px;font-weight:700;letter-spacing:-.01em;
  color:var(--ink);text-decoration:none;margin-right:auto}
.marca::before{content:"";width:10px;height:10px;border-radius:2px;background:var(--accent)}
.marca:hover{color:var(--ink)}
.topo nav{display:none;gap:2px}
.topo nav a{display:inline-flex;align-items:center;min-height:44px;padding:0 12px;border-radius:8px;
  color:var(--ink-2);text-decoration:none;font-size:.9375rem}
.topo nav a:hover{color:var(--accent);background:var(--accent-soft)}
@media (min-width:880px){.topo nav{display:flex}}
.idioma{display:inline-flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line-2);
  border-radius:999px;color:var(--ink-2);text-decoration:none;font-size:.875rem;font-weight:500}
.idioma:hover{border-color:var(--accent);color:var(--accent)}

/* ---------- abertura */
.hero{padding:44px 0 56px}
@media (min-width:1024px){.hero{padding:88px 0 88px}}
.hero-grid{display:grid;gap:40px}
@media (min-width:1024px){.hero-grid{grid-template-columns:minmax(0,1.25fr) minmax(0,.85fr);gap:64px;align-items:start}}
.disp{display:inline-flex;align-items:center;gap:9px;padding:6px 14px 6px 12px;margin-bottom:22px;border-radius:999px;
  background:var(--accent-soft);color:var(--accent);font-size:.875rem;font-weight:600}
.hero h1{font-size:clamp(2.5rem,8.4vw,4.25rem);line-height:1.02;letter-spacing:-.035em;font-weight:750;margin:0}
.cargo{margin-top:12px;font-size:clamp(1.125rem,2.6vw,1.5rem);line-height:1.3;font-weight:600;letter-spacing:-.01em;color:var(--accent)}
.frase{margin-top:20px;max-width:38em;font-size:clamp(1.0625rem,2vw,1.25rem);line-height:1.55;color:var(--ink-2)}
.ctas{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:32px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 22px;
  border:1px solid transparent;border-radius:10px;font-size:1rem;font-weight:600;text-decoration:none;
  transition:background .15s,border-color .15s,color .15s}
.btn-pri{background:var(--accent);color:var(--accent-ink)}
.btn-pri:hover{background:var(--accent-hover);color:var(--accent-ink)}
.btn-sec{background:var(--card);border-color:var(--line-2);color:var(--ink)}
.btn-sec:hover{border-color:var(--accent);color:var(--accent)}
.btn-ter{display:inline-flex;align-items:center;min-height:48px;padding:0 8px;font-weight:600;text-decoration:none}
@media (max-width:479px){.ctas .btn{flex:1 1 100%}}
.meta{list-style:none;display:flex;flex-wrap:wrap;margin:24px 0 0;padding:0;color:var(--muted);font-size:.9375rem}
.meta li{display:inline-flex;align-items:center;min-height:44px}
.meta li+li::before{content:"";width:4px;height:4px;border-radius:50%;background:var(--line-2);margin:0 12px}
.meta a{display:inline-flex;align-items:center;min-height:44px;color:var(--ink-2)}
.meta a:hover{color:var(--accent)}

/* ---------- números */
.prova{border:1px solid var(--line);border-radius:var(--r);background:var(--card);padding:22px 20px 16px;box-shadow:var(--sombra)}
.prova h2{margin:0;font-size:.8125rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.numeros{display:grid;grid-template-columns:1fr 1fr;margin-top:12px}
.numero{padding:16px 16px 16px 0;border-top:1px solid var(--line)}
.numero:nth-child(even){padding:16px 0 16px 16px;border-left:1px solid var(--line)}
.numero:last-child:nth-child(odd){grid-column:1/-1;padding-right:0}
.numero b{display:block;font-size:clamp(1.75rem,4.4vw,2.25rem);line-height:1.05;font-weight:750;letter-spacing:-.03em;
  font-variant-numeric:tabular-nums;color:var(--ink)}
.numero span{display:block;margin-top:6px;font-size:.8125rem;line-height:1.45;color:var(--muted)}
.medido{margin-top:6px;padding-top:12px;border-top:1px solid var(--line);font-size:.8125rem;color:var(--muted)}
.fontes summary{display:flex;align-items:center;min-height:44px;cursor:pointer;font-size:.8125rem;font-weight:600;color:var(--accent)}
.fontes ul{margin:0 0 6px;padding-left:18px;font-size:.8125rem;line-height:1.5;color:var(--muted);display:grid;gap:6px}

/* ---------- seções */
.secao{padding:64px 0;border-top:1px solid var(--line)}
@media (min-width:1024px){.secao{padding:88px 0}}
.secao-cab{max-width:46rem;margin-bottom:32px}
.secao-cab h2{margin:0;font-size:clamp(1.5rem,3.4vw,2rem);line-height:1.15;letter-spacing:-.02em;font-weight:750}
.secao-cab h2::before{content:"";display:block;width:28px;height:3px;border-radius:2px;background:var(--accent);margin-bottom:16px}
.lead{margin-top:10px;font-size:1.0625rem;color:var(--muted)}
.marcas{list-style:none;margin:0;padding:0;display:grid;gap:9px}
.marcas li{position:relative;padding-left:18px}
.marcas li::before{content:"";position:absolute;left:0;top:.6em;width:7px;height:7px;border-radius:2px;background:var(--accent)}
.chips{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 0;padding:0}
.chips li{padding:5px 11px;border:1px solid var(--line-2);border-radius:999px;background:var(--card);
  font-size:.8125rem;line-height:1.3;color:var(--ink-2)}

/* pilares */
.pilares{display:grid;gap:16px}
@media (min-width:880px){.pilares{grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}
.pilar{display:flex;flex-direction:column;padding:24px;border:1px solid var(--line);border-radius:var(--r);background:var(--card)}
.pilar h3{margin:0 0 10px;font-size:1.1875rem;font-weight:750;letter-spacing:-.01em}
.pilar>p{margin-bottom:20px;color:var(--ink-2)}
.pilar .marcas{padding-top:16px;border-top:1px solid var(--line);font-size:.875rem;color:var(--muted)}

/* experiência e formação */
.linhas{list-style:none;margin:0;padding:0}
.linha-item{display:grid;gap:4px 32px;padding:28px 0;border-top:1px solid var(--line)}
.linha-item:first-child{border-top:0;padding-top:0}
@media (min-width:880px){.linha-item{grid-template-columns:11rem minmax(0,1fr)}}
.quando{padding-top:3px;font-family:var(--mono);font-size:.8125rem;color:var(--muted)}
.linha-item h3{margin:0;font-size:1.1875rem;font-weight:750;letter-spacing:-.01em}
.funcao{margin-top:2px;font-weight:600;color:var(--accent)}
.linha-item .resumo{margin-top:10px;max-width:46rem;color:var(--ink-2)}
.linha-item .marcas{margin-top:16px;max-width:46rem;font-size:.9375rem;color:var(--ink-2)}
.idiomas{margin-top:8px;color:var(--ink-2)}

/* projetos */
.cards{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr))}
.card{display:flex;flex-direction:column;padding:22px;border:1px solid var(--line);border-radius:var(--r);background:var(--card);
  transition:border-color .2s,box-shadow .2s,transform .2s}
.card:hover{border-color:var(--line-2);box-shadow:var(--sombra);transform:translateY(-2px)}
@media (min-width:1024px){.card.destaque{grid-column:span 2}}
.card.destaque{border-color:color-mix(in srgb,var(--accent) 45%,var(--line))}
.status{display:flex;align-items:flex-start;gap:9px;margin-bottom:12px;font-size:.8125rem;line-height:1.4;color:var(--muted)}
.dot{flex:none;width:8px;height:8px;border-radius:50%;border:1.5px solid var(--muted)}
.status .dot{margin-top:.4em}
.dot.vivo{background:var(--accent);border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 22%,transparent)}
.disp .dot.vivo{box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 25%,transparent)}
.card h3{margin:0 0 6px;font-size:1.1875rem;font-weight:750;letter-spacing:-.01em}
.card .linha{color:var(--ink-2)}
.card .marcas{margin-top:14px;font-size:.875rem;color:var(--muted)}
.card .ir{margin-top:auto;padding-top:14px}
.card .ir a{display:inline-flex;align-items:center;min-height:44px;font-weight:600;text-decoration:none}
.card .ir a:hover{text-decoration:underline}

/* stack */
.stack{margin:0}
.stack>div{display:grid;gap:10px 32px;padding:20px 0;border-top:1px solid var(--line)}
.stack>div:first-child{border-top:0;padding-top:0}
@media (min-width:880px){.stack>div{grid-template-columns:11rem minmax(0,1fr)}}
.stack dt{padding-top:4px;font-weight:700;font-size:.9375rem}
.stack dd{margin:0}
.stack .chips{margin:0}

/* como trabalho */
.metodo{display:grid;gap:0 40px}
@media (min-width:880px){.metodo{grid-template-columns:repeat(2,minmax(0,1fr))}}
.metodo div{padding:20px 0;border-top:1px solid var(--line)}
.metodo h3{margin:0 0 6px;font-size:1.0625rem;font-weight:700}
.metodo p{color:var(--ink-2)}
.para-licoes{margin-top:28px}

/* contato */
.contato{background:var(--bg-2)}
.contato-grid{display:grid;gap:40px}
@media (min-width:1024px){.contato-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:64px}}
.contato .texto{max-width:36rem;color:var(--ink-2)}
.email-grande{display:inline-flex;align-items:center;min-height:48px;margin-top:18px;font-size:clamp(1.2rem,4.6vw,1.75rem);
  font-weight:750;letter-spacing:-.02em;word-break:break-word}
.contato .ctas{margin-top:20px}
.faq h3{margin:0 0 8px;font-size:.8125rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.faq details{border-top:1px solid var(--line-2)}
.faq details:last-child{border-bottom:1px solid var(--line-2)}
.faq summary{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:52px;padding:8px 0;
  cursor:pointer;list-style:none;font-weight:600}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";flex:none;font-size:1.25rem;font-weight:400;color:var(--accent)}
.faq details[open] summary::after{content:"−"}
.faq details p{padding-bottom:16px;color:var(--ink-2)}

/* rodapé */
.rodape{padding:28px 0 44px;border-top:1px solid var(--line);font-size:.875rem;color:var(--muted)}
.rodape-in{display:grid;gap:10px}
@media (min-width:880px){.rodape-in{grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:24px}}
.maq{display:flex;flex-wrap:wrap;align-items:center;gap:0 4px}
.maq b{font-weight:600;color:var(--ink-2);margin-right:6px}
.maq a{display:inline-flex;align-items:center;min-height:44px;padding:0 6px;font-family:var(--mono);font-size:.8125rem}

/* página de lições */
.pag-cab{padding:36px 0 48px}
@media (min-width:1024px){.pag-cab{padding:64px 0 64px}}
.voltar{display:inline-flex;align-items:center;min-height:44px;margin-bottom:12px;font-weight:600;text-decoration:none}
.pag-cab h1{margin:0;font-size:clamp(2.25rem,7vw,3.5rem);line-height:1.05;letter-spacing:-.035em;font-weight:750}
.pag-cab .frase{max-width:42em}
.rets{display:grid;gap:16px}
@media (min-width:960px){.rets{grid-template-columns:repeat(2,minmax(0,1fr))}}
.ret{display:flex;flex-direction:column;padding:22px;border:1px solid var(--line);border-radius:var(--r);background:var(--card)}
.proto{font-family:var(--mono);font-size:.75rem;color:var(--muted)}
.ret h3{margin:6px 0 14px;font-size:1.0625rem;font-weight:700;line-height:1.4}
.ret dl{display:grid;gap:12px;margin:0}
.ret dt{font-size:.75rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.ret dd{margin:2px 0 0;color:var(--ink-2)}
.ret .onde dd{color:var(--muted);text-decoration:line-through;text-decoration-color:color-mix(in srgb,var(--muted) 60%,transparent)}
.ret .leia dt{color:var(--accent)}
.regra{margin-top:auto;padding-top:16px}
.regra p{padding:12px 14px;border-radius:8px;background:var(--accent-soft);font-size:.9375rem}
.regra b{color:var(--accent);font-weight:700}
.atos{list-style:none;display:grid;gap:0 40px;margin:0;padding:0}
@media (min-width:880px){.atos{grid-template-columns:repeat(2,minmax(0,1fr))}}
.atos li{padding:18px 0;border-top:1px solid var(--line)}
.atos strong{display:block;margin-bottom:4px}
.atos span{color:var(--ink-2);font-size:.9375rem}

/* 404 */
.erro{min-height:72vh;display:grid;align-content:center;gap:14px;padding:48px 0}
.erro h1{margin:0;font-size:clamp(2rem,6vw,3rem);letter-spacing:-.03em}
.erro p{color:var(--ink-2)}

/* entrada: uma vez, curta, e só para quem não pediu menos movimento */
@media (prefers-reduced-motion: no-preference){
  @keyframes sobe{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
  .hero-texto>*,.prova{animation:sobe .4s cubic-bezier(.2,.7,.2,1) both}
  .hero-texto>*:nth-child(2){animation-delay:.03s}.hero-texto>*:nth-child(3){animation-delay:.06s}
  .hero-texto>*:nth-child(4){animation-delay:.09s}.hero-texto>*:nth-child(5){animation-delay:.12s}
  .hero-texto>*:nth-child(6),.prova{animation-delay:.15s}
}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}*{transition:none!important}}
@media print{.topo{position:static}.btn,.idioma{border:1px solid #999}}
"""

JS = r"""
(function(){
  // WebMCP: expõe ao agente do navegador as mesmas ferramentas do servidor /mcp.
  // Sem suporte no navegador, nada acontece. Tudo só leitura.
  var mc=document.modelContext||navigator.modelContext;
  if(!mc||!mc.registerTool)return;
  var dados=JSON.parse(document.getElementById('dados').textContent);
  function resp(obj){return {content:[{type:'text',text:JSON.stringify(obj)}]}}
  var ferramentas=[
    {name:'ler_perfil',description:'Perfil, resumo e contato de Mateus Fabro',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp({perfil:dados.perfil,numeros:dados.numeros})}},
    {name:'listar_projetos',description:'Projetos de Mateus Fabro (produtos próprios e trabalho)',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.projetos)}},
    {name:'listar_retificacoes',description:'Erros que ele cometeu, com data, número e a regra que ficou',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.retificacoes)}},
    {name:'verificar_disponibilidade',description:'Se está aberto a projetos ou vagas, e como falar com ele',
     inputSchema:{type:'object',properties:{}},execute:async function(){return resp(dados.disponibilidade)}}
  ];
  ferramentas.forEach(function(f){try{mc.registerTool(f)}catch(err){}});
})();
"""


def json_em_script(texto: str) -> str:
    """JSON dentro de <script>: `<`, `>` e `&` viram escapes unicode. Assim nenhum campo
    fecha a tag (`</script>`) nem abre comentário (`<!--`), e o JSON continua idêntico."""
    return texto.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def urls_seguras(d: dict) -> None:
    """Todo href que vem do conteúdo é https — `e()` escapa aspas, não impede `javascript:`."""
    urls = [d["perfil"]["github"], d["perfil"]["linkedin"], d["site"]["url"]]
    urls += [pr["url"] for pr in d["projetos"] if pr.get("url")]
    ruins = [u for u in urls if not u.startswith("https://")]
    if ruins:
        raise ValueError(f"URL sem https no conteúdo: {ruins}")


def status_vivo(pr: dict) -> bool:
    s = pr["status"].lower()
    return any(x in s for x in ("no ar", "em produção", "live", "in production"))


def lingua(t: dict) -> str:
    return "en" if t is T["en"] else "pt"


def carregar_cv() -> dict:
    return json.loads(CURRICULO.read_text(encoding="utf-8"))


MESES_CURTOS = {"pt": ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"],
                "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}


def mes_ano(iso: str, t: dict) -> str:
    y, m = iso.split("-")
    mes = MESES_CURTOS[lingua(t)][int(m) - 1]
    return f"{mes}/{y}" if t is T["pt"] else f"{mes} {y}"


def periodo(x: dict, t: dict) -> str:
    """Sem `fim` = emprego atual (é o que a vista discreta produz)."""
    return f"{mes_ano(x['inicio'], t)} – {mes_ano(x['fim'], t) if x.get('fim') else t['atual']}"


def inicial(s: str) -> str:
    return s[:1].upper() + s[1:]


def provas_pilares(d: dict, cv: dict, t: dict) -> list[list[str]]:
    """Duas provas por pilar, LIDAS dos dados (nunca digitadas aqui): mudou o fato, muda o pilar.
    Ordem = a de `pilares`: Dados, Produto, Agentes de IA."""
    pr = {p["slug"]: p for p in d["projetos"]}
    ig = pr["igaming-dados"]["fatos"]
    bloco_ia = next(b for b in cv["experiencia"]["super-nova"][lingua(t)] if b["bloco"].startswith(("IA", "Applied")))
    ia = bloco_ia["itens"][2]["texto"]
    ia = ia[: ia.index(")") + 1]
    return [[inicial(ig[4]), inicial(ig[5])],
            [f"{pr['pingado']['nome']}: {pr['pingado']['fatos'][2]}",
             f"{pr['avisa-edital']['nome']}: {pr['avisa-edital']['status'][:1].lower()}{pr['avisa-edital']['status'][1:]}"],
            [d["metodo"][3]["texto"], ia]]


def marcas(itens: list[str]) -> str:
    return '<ul class="marcas">' + "".join(f"<li>{e(i)}</li>" for i in itens) + "</ul>"


def chips(itens: list[str], rotulo: str) -> str:
    return f'<ul class="chips" aria-label="{e(rotulo)}">' + "".join(f"<li>{e(i)}</li>" for i in itens) + "</ul>"


def ponto(vivo: bool) -> str:
    return f'<span class="dot{" vivo" if vivo else ""}" aria-hidden="true"></span>'


def html_projeto(pr: dict, t: dict = T["pt"], destaque: bool = False) -> str:
    fatos = pr["fatos"][:3] if destaque else pr["fatos"][:1]
    link = (f'<p class="ir"><a href="{e(pr["url"])}" rel="noopener">{e(pr["url"].split("//")[1])} ↗</a></p>'
            if pr.get("url") else "")
    return f"""
<article class="card{' destaque' if destaque else ''}" id="{e(pr['slug'])}">
  <p class="status">{ponto(status_vivo(pr))}{e(pr['status'])}</p>
  <h3>{e(pr['nome'])}</h3>
  <p class="linha">{e(pr['linha'])}</p>
  {marcas(fatos)}
  {chips(pr['stack'], t['tecnologias'])}
  {link}
</article>"""


def html_retificacao(r: dict, t: dict = T["pt"]) -> str:
    return f"""
<article class="ret" id="{e(r['protocolo'].lower())}">
  <p class="proto">{e(r['protocolo'])} · <time datetime="{e(r['data'])}">{data_curta_t(r['data'], t)}</time></p>
  <h3>{e(r['contexto'])}</h3>
  <dl>
    <div class="onde"><dt>{t['onde']}</dt><dd>{e(r['onde_se_le'])}</dd></div>
    <div class="leia"><dt>{t['leia']}</dt><dd>{e(r['leia_se'])}</dd></div>
  </dl>
  <div class="regra"><p><b>{t['regra']}</b> {e(r['regra'])}</p></div>
</article>"""


def cabeca(d: dict, t: dict, caminho: str, titulo: str, descricao: str, extra: str = "") -> str:
    """<head> comum. `caminho` é o da página sem o prefixo de idioma: "/" ou "/licoes/"."""
    s = d["site"]
    url = s["url"] + t["prefixo"] + caminho
    return f"""<!doctype html>
<html lang="{e(s['idioma'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(url)}">
<link rel="alternate" hreflang="pt-BR" href="{e(s['url'])}{caminho}">
<link rel="alternate" hreflang="en" href="{e(s['url'])}/en{caminho}">
<link rel="alternate" hreflang="x-default" href="{e(s['url'])}{caminho}">
<link rel="alternate" type="text/markdown" href="{t['prefixo']}/index.md" title="Markdown">
<link rel="alternate" type="application/json" href="/resume.json" title="JSON Resume">
<meta property="og:type" content="{'profile' if caminho == '/' else 'website'}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:locale" content="{t['locale']}">
<meta property="profile:first_name" content="Mateus">
<meta property="profile:last_name" content="Fabro">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}">
<meta name="twitter:description" content="{e(descricao)}">
<meta name="theme-color" content="#0E5A63">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:image" content="{e(s['url'])}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(d['perfil']['nome'])} — {e(d['perfil']['cargo'])}">
<meta name="twitter:image" content="{e(s['url'])}/og.png">
<link rel="stylesheet" href="/estilo.css">{extra}
</head>
<body>
<a class="pular" href="#conteudo">{'Skip to content' if t is T['en'] else 'Pular para o conteúdo'}</a>"""


def barra(d: dict, t: dict, caminho: str) -> str:
    """Barra do topo. Na home as âncoras são locais; nas outras páginas apontam para a home."""
    home = f"{t['prefixo']}/"
    pre = "" if caminho == "/" else home
    alvos = [f"{pre}#experiencia", f"{pre}#projetos", f"{pre}#stack", f"{t['prefixo']}/licoes/", f"{pre}#contato"]
    menu = "".join(f'<a href="{a}">{e(r)}</a>' for a, r in zip(alvos, t["nav"]))
    outro = t["outro_href"] + ("" if caminho == "/" else caminho.lstrip("/"))
    return f"""
<header class="topo"><div class="wrap topo-in">
  <a class="marca" href="{home}">{e(d['perfil']['nome'])}</a>
  <nav aria-label="{t['menu']}">{menu}</nav>
  <a class="idioma" href="{outro}" hreflang="{t['outro']}" lang="{t['outro']}">{t['outro_rotulo']}</a>
</div></header>"""


def rodape(d: dict, t: dict) -> str:
    s = d["site"]
    return f"""
<footer class="rodape"><div class="wrap rodape-in">
  <p class="maq"><b>{t['maquinas']}:</b><a href="{t['prefixo']}/index.md">{t['prefixo']}/index.md</a><a href="/resume.json">/resume.json</a><a href="/llms.txt">/llms.txt</a><a href="/mcp">/mcp</a></p>
  <p>{e(t['medido_em'].format(d=data_curta_t(s['medido_em'], t)))}</p>
  <p>{t['rodape']}</p>
</div></footer>"""


def pagina(d: dict, md: str = "", t: dict = T["pt"]) -> str:
    """Home: abertura → números → pilares → experiência e formação → projetos → stack → como trabalho
    → contato. `md` fica na assinatura por compatibilidade: o Markdown mora em /index.md, linkado no rodapé."""
    p, s = d["perfil"], d["site"]
    cv = carregar_cv()
    lang = lingua(t)
    ld = json_em_script(json.dumps(json_ld(d), ensure_ascii=False))
    dados_js = json_em_script(json.dumps({k: d[k] for k in ("perfil", "numeros", "projetos", "retificacoes",
                                                            "disponibilidade")}, ensure_ascii=False))
    mailto = f"mailto:{e(p['email'])}?subject={t['assunto']}"
    cv_href = f"/curriculo/{t['cv_arquivo']}"
    disp = d["disponibilidade"]

    numeros = "".join(f'<div class="numero"><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>'
                      for n in d["numeros"])
    fontes = "".join(f"<li><b>{e(n['valor'])}</b>: {e(n['fonte'])}</li>" for n in d["numeros"])

    pilares = "".join(f'<article class="pilar"><h3>{e(pl["titulo"])}</h3><p>{e(pl["texto"])}</p>{marcas(pv)}</article>'
                      for pl, pv in zip(d["pilares"], provas_pilares(d, cv, t)))

    trabalho = next(pr for pr in d["projetos"] if pr["tipo"] == "trabalho")
    exps = []
    for x in d["experiencia"]:
        nota = f" · {e(x['nota'])}" if x.get("nota") else ""
        extra = (marcas([inicial(f) for f in trabalho["fatos"]]) + chips(trabalho["stack"], t["tecnologias"])
                 if x["id"] == "super-nova" else "")
        exps.append(f"""<li class="linha-item">
  <p class="quando">{e(periodo(x, t))}<br>{e(x['local'])}{nota}</p>
  <div><h3>{e(x['empresa'])}</h3><p class="funcao">{e(x['cargo'])}</p><p class="resumo">{e(x['resumo'])}</p>{extra}</div>
</li>""")
    formacao = "".join(f"""<li class="linha-item">
  <p class="quando">{e(f['inicio'])} – {e(f['fim'])}</p>
  <div><h3>{e(f['curso'])}</h3><p class="funcao">{e(f['instituicao'])}</p><p class="resumo">{e(inicial(f['status']))}</p></div>
</li>""" for f in p["formacao"])
    formacao += f"""<li class="linha-item"><p class="quando">{t['idiomas']}</p><div><p class="idiomas">{e(' · '.join(p['idiomas']))}</p></div></li>"""

    produtos = sorted((pr for pr in d["projetos"] if pr["tipo"] == "produto"),
                      key=lambda pr: pr["slug"] != "avisa-edital")          # o carro-chefe primeiro
    cards = "".join(html_projeto(pr, t, destaque=(pr["slug"] == "avisa-edital")) for pr in produtos)

    stack = "".join(f'<div><dt>{e(c["categoria"])}</dt><dd>{chips(c["itens"].split(" · "), c["categoria"])}</dd></div>'
                    for c in cv["stack"][lang])
    metodo = "".join(f"<div><h3>{e(m['titulo'])}</h3><p>{e(m['texto'])}</p></div>" for m in d["metodo"])
    faq = "".join(f"<details><summary>{e(f['pergunta'])}</summary><p>{e(f['resposta'])}</p></details>"
                  for f in d["faq"])
    ctas = (f'<a class="btn btn-pri" href="{cv_href}">{t["cv"]}</a>'
            f'<a class="btn btn-sec" href="{mailto}">{t["email_btn"]}</a>')

    return cabeca(d, t, "/", s["titulo"], s["descricao"],
                  extra=f'\n<script type="application/ld+json">{ld}</script>') + barra(d, t, "/") + f"""
<main id="conteudo">
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-texto">
    <p class="disp">{ponto(True)}{e(inicial(disp['status']))}</p>
    <h1>{e(p['nome'])}</h1>
    <p class="cargo">{e(p['cargo'])}</p>
    <p class="frase">{e(p['frase_hero'])}</p>
    <div class="ctas">{ctas}<a class="btn-ter" href="#projetos">{t['ver_proj']} ↓</a></div>
    <ul class="meta"><li>{e(p['cidade'])}, {e(p['estado'])}</li><li>{t['remoto']}</li><li><a href="{e(p['github'])}" rel="me noopener">GitHub</a></li><li><a href="{e(p['linkedin'])}" rel="me noopener">LinkedIn</a></li></ul>
  </div>
  <aside class="prova" id="numeros" aria-labelledby="h-numeros">
    <h2 id="h-numeros">{t['h_numeros']}</h2>
    <div class="numeros">{numeros}</div>
    <p class="medido">{e(t['medido'].format(d=data_curta_t(s['medido_em'], t)))}</p>
    <details class="fontes"><summary>{t['como_medido']}</summary><ul>{fontes}</ul></details>
  </aside>
</div></section>

<section class="secao" id="entrega"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_pilares']}</h2></header>
  <div class="pilares">{pilares}</div>
</div></section>

<section class="secao" id="experiencia"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_exp']}</h2><p class="lead">{t['l_exp']}</p></header>
  <ol class="linhas">{''.join(exps)}</ol>
</div></section>

<section class="secao" id="formacao"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_form']}</h2></header>
  <ul class="linhas">{formacao}</ul>
</div></section>

<section class="secao" id="projetos"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_proj']}</h2><p class="lead">{t['l_proj']}</p></header>
  <div class="cards">{cards}</div>
</div></section>

<section class="secao" id="stack"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_stack']}</h2><p class="lead">{t['l_stack']}</p></header>
  <dl class="stack">{stack}</dl>
</div></section>

<section class="secao" id="metodo"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_met']}</h2><p class="lead">{t['l_met']}</p></header>
  <div class="metodo">{metodo}</div>
  <p class="para-licoes"><a class="btn btn-sec" href="{t['prefixo']}/licoes/">{e(t['link_licoes'].format(n=len(d['atos'])))}</a></p>
</div></section>

<section class="secao contato" id="contato"><div class="wrap contato-grid">
  <div>
    <header class="secao-cab"><h2>{t['h_contato']}</h2></header>
    <p class="disp">{ponto(True)}{e(inicial(disp['status']))}</p>
    <p class="texto">{e(disp['texto'])}</p>
    <p><a class="email-grande" href="{mailto}">{e(p['email'])}</a></p>
    <div class="ctas">{ctas}</div>
    <ul class="meta"><li>{e(p['cidade'])}, {e(p['estado'])}</li><li><a href="{e(p['github'])}" rel="me noopener">GitHub</a></li><li><a href="{e(p['linkedin'])}" rel="me noopener">LinkedIn</a></li></ul>
  </div>
  <div class="faq"><h3>{t['faq']}</h3>{faq}</div>
</div></section>
</main>
""" + rodape(d, t) + f"""
<script type="application/json" id="dados">{dados_js}</script>
<script src="/app.js" defer></script>
</body>
</html>
"""


def pagina_licoes(d: dict, t: dict = T["pt"]) -> str:
    """/licoes/: as retificações (onde se lê / leia-se / regra) e os atos, fora da home."""
    p = d["perfil"]
    rets = "".join(html_retificacao(r, t) for r in ordenadas(d["retificacoes"]))
    atos = "".join(f"<li><strong>{e(a['titulo'])}</strong><span>{e(a['texto'])}</span></li>" for a in d["atos"])
    titulo = f"{t['h_licoes']} — {p['nome']}"
    return cabeca(d, t, "/licoes/", titulo, t["l_licoes"]) + barra(d, t, "/licoes/") + f"""
<main id="conteudo">
<section class="pag-cab"><div class="wrap">
  <a class="voltar" href="{t['prefixo']}/">{t['voltar']}</a>
  <h1>{t['h_licoes']}</h1>
  <p class="cargo">{t['sub_licoes']}</p>
  <p class="frase">{t['l_licoes']}</p>
</div></section>

<section class="secao" id="erros"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_ret']}</h2></header>
  <div class="rets">{rets}</div>
</div></section>

<section class="secao" id="regras"><div class="wrap">
  <header class="secao-cab"><h2>{t['h_atos']}</h2><p class="lead">{e(t['l_atos'].format(a=len(d['atos']), n=edicao(d)))}</p></header>
  <ol class="atos">{atos}</ol>
</div></section>
</main>
""" + rodape(d, t) + """
</body>
</html>
"""


def robots(d: dict) -> str:
    L = ["# Agentes de IA são bem-vindos: o conteúdo existe para ser lido e citado.", ""]
    for bot in ROBOS_IA:
        L += [f"User-agent: {bot}", "Allow: /", ""]
    L += ["User-agent: *", "Allow: /", "", f"Sitemap: {d['site']['url']}/sitemap.xml", ""]
    return "\n".join(L)


def sitemap(d: dict) -> str:
    s = d["site"]
    urls = [f"{s['url']}/", f"{s['url']}/en/", f"{s['url']}/licoes/", f"{s['url']}/en/licoes/",
            f"{s['url']}/index.md", f"{s['url']}/en/index.md", f"{s['url']}/llms.txt",
            f"{s['url']}/llms-full.txt", f"{s['url']}/resume.json"]
    urls += [f"{s['url']}/projetos/{pr['slug']}.md" for pr in d["projetos"]]
    corpo = "".join(f"<url><loc>{e(u)}</loc><lastmod>{s['medido_em']}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{corpo}</urlset>\n')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="7" fill="#0E5A63"/>
<text x="16" y="21.5" font-family="system-ui,-apple-system,Segoe UI,Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="-.5" text-anchor="middle" fill="#FFFFFF">MF</text>
</svg>
"""


def pagina_404(d: dict) -> str:
    return f"""<!doctype html>
<html lang="{e(d['site']['idioma'])}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página não encontrada — {e(d['perfil']['nome'])}</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/estilo.css"></head>
<body>
<header class="topo"><div class="wrap topo-in"><a class="marca" href="/">{e(d['perfil']['nome'])}</a></div></header>
<main class="wrap erro">
  <p class="proto">404</p>
  <h1>Página não encontrada</h1>
  <p>Este endereço não existe ou mudou de lugar. <span lang="en">This page does not exist or has moved.</span></p>
  <p><a class="btn btn-pri" href="/">Voltar ao início</a></p>
</main>
</body></html>
"""


def gerar(d: dict, d_en: dict | None = None) -> dict[str, str]:
    d_en = d_en if d_en is not None else carregar_en()
    d, d_en = vista(d), vista(d_en)           # o que se publica: site.modo decide discreto/completo
    urls_seguras(d)
    urls_seguras(d_en)
    md = markdown(d)
    md_en = markdown(d_en, T["en"])
    arquivos = {
        "index.html": pagina(d, md),
        "index.md": md,
        "llms.txt": llms_txt(d),
        "llms-full.txt": md + "\n\n" + "\n\n".join(projeto_md(pr) for pr in d["projetos"]) + "\n",
        "resume.json": json.dumps(resume_json(d), ensure_ascii=False, indent=2) + "\n",
        "robots.txt": robots(d),
        "estilo.css": CSS.lstrip(),
        "favicon.svg": FAVICON,
        "404.html": pagina_404(d),
        "app.js": JS.lstrip(),
        "sitemap.xml": sitemap(d),
        "en/index.html": pagina(d_en, md_en, T["en"]),
        "en/index.md": md_en,
        "licoes/index.html": pagina_licoes(d),
        "en/licoes/index.html": pagina_licoes(d_en, T["en"]),
    }
    for pr in d["projetos"]:
        arquivos[f"projetos/{pr['slug']}.md"] = projeto_md(pr) + "\n"
    return arquivos


def main() -> int:
    arquivos = gerar(carregar())
    if "--check" in sys.argv:
        velhos = [n for n, c in arquivos.items()
                  if not (SAIDA / n).exists() or (SAIDA / n).read_text(encoding="utf-8") != c]
        sys.path.insert(0, str(RAIZ / "scripts"))
        import gerar_pecas
        velhos += gerar_pecas.curriculo_desatualizado()
        do_cv = any(v.startswith("curriculo/") for v in velhos)
        do_site = any(not v.startswith("curriculo/") for v in velhos)
        comandos = (["python build.py"] if do_site else []) + (["python scripts/gerar_pecas.py curriculo"] if do_cv else [])
        dica = "` e `".join(comandos)
        if velhos:
            print(f"public/ desatualizado — rode `{dica}`:", ", ".join(velhos))
            return 1
        print("public/ confere com conteudo/dados.json")
        return 0
    for nome, conteudo in arquivos.items():
        alvo = SAIDA / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8", newline="\n")
    print(f"{len(arquivos)} arquivos gerados em public/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
