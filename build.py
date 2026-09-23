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


def e(s: str) -> str:
    return html.escape(str(s), quote=True)


def data_extenso(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def data_curta(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}/{d.year}"


def edicao(d: dict) -> str:
    """O número da edição é o número de lições registradas — o diário cresce quando eu erro."""
    return d["numeros"][0]["valor"]


def ordenadas(retificacoes: list[dict]) -> list[dict]:
    return sorted(retificacoes, key=lambda r: r["data"])


# ============================================================================ textos fixos
# Tudo que a página diz e não vem do conteúdo. Um dicionário por idioma: a versão em inglês
# é a mesma página, não uma cópia que envelhece à parte.
T = {
    "pt": {
        "prefixo": "", "locale": "pt_BR", "outro": "en", "outro_rotulo": "English",
        "outro_href": "/en/", "maquina": "Ler como máquina", "edicao": "Edição nº {n} · uma por lição registrada",
        "titulo_de": "Diário de", "menu": "Seções",
        "nav": ["Projetos", "Retificações", "Lições", "Método", "Contato", "Para máquinas"],
        "frase": "Em uma frase", "apresentacao": "Apresentação",
        "medido": "Números medidos em {d}, contados nos repositórios — não de cabeça.",
        "s1": "Seção I", "h_proj": "Editais — o que eu construí",
        "l_proj": "Produtos próprios, do coletor ao cliente, com o status real de cada um — inclusive os que pararam.",
        "s2": "Seção II", "h_ret": "Retificações",
        "l_ret": ("Erros que eu cometi, no formato do diário oficial: onde se lê, leia-se. A data é a da "
                  "retificação — quando o erro foi achado e corrigido. Nomes de empresa e de cliente ficam de fora."),
        "s3": "Seção III", "h_atos": "Atos — as regras que ficaram",
        "l_atos": "{a} das {n} lições registradas. Cada uma nasceu de um caso real e tem origem, motivo e forma de aplicar.",
        "s4": "Seção IV", "h_met": "Expediente — como eu trabalho",
        "l_met": "Em par com agentes de IA, e com um sistema que impede o mesmo erro de acontecer duas vezes.",
        "convocacao": "Convocação", "maq_eyebrow": "Para máquinas", "h_maq": "O mesmo diário, para agentes",
        "l_maq": "Sem raspar HTML: o conteúdo desta página sai do mesmo arquivo em formatos que um agente lê direto.",
        "mcp_nota": "servidor MCP, só leitura, sem login",
        "dica": "No Claude: Configurações → Conectores → adicionar conector personalizado → cole o endereço do",
        "rodape": "Gerado de um arquivo só (conteudo/dados.json) — página, Markdown, llms.txt, JSON Resume e MCP.",
        "medido_em": "Medido em {d}", "para_quem": "para quem", "papel": "meu papel", "tecnologias": "Tecnologias",
        "carimbo": "RETIFICAÇÃO", "onde": "Onde se lê", "leia": "Leia-se", "regra": "Regra que ficou:",
        # Markdown
        "md_medido": "Medido em {d}. Edição nº {n}.", "md_resumo": "Resumo", "md_numeros": "Números",
        "md_fonte": "fonte", "md_proj": "Projetos", "md_ret": "Retificações",
        "md_ret_l": "Erros que cometi, no formato de retificação de diário oficial. Cada um virou uma regra.",
        "md_atos": "Atos (lições)", "md_atos_l": "{a} das {n} lições registradas, publicadas aqui.",
        "md_met": "Como trabalho", "md_disp": "Disponibilidade", "md_contato": "Contato",
        "md_faq": "Perguntas frequentes", "md_agentes": "Para agentes",
        "md_mcp": "Servidor MCP (Streamable HTTP, sem autenticação, só leitura)",
        "md_resume": "Currículo em JSON Resume", "md_este": "Este texto",
        "p_para_quem": "Para quem", "p_papel": "Meu papel", "p_status": "Status", "p_stack": "Stack",
        "p_endereco": "Endereço", "p_fatos": "Fatos",
    },
    "en": {
        "prefixo": "/en", "locale": "en_US", "outro": "pt", "outro_rotulo": "Português",
        "outro_href": "/", "maquina": "Read as a machine", "edicao": "Edition no. {n} · one per recorded lesson",
        "titulo_de": "The Gazette of", "menu": "Sections",
        "nav": ["Projects", "Corrections", "Lessons", "Method", "Contact", "For machines"],
        "frase": "In one sentence", "apresentacao": "Introduction",
        "medido": "Numbers measured on {d}, counted in the repositories — not from memory.",
        "s1": "Section I", "h_proj": "Notices — what I built",
        "l_proj": "My own products, from the scraper to the customer, with the real status of each — including the ones that stopped.",
        "s2": "Section II", "h_ret": "Corrections",
        "l_ret": ("Mistakes I made, in the format of a gazette erratum: for … read …. The date is the date of the "
                  "correction — when the mistake was found and fixed. Company and client names are left out."),
        "s3": "Section III", "h_atos": "Standing orders — the rules that stayed",
        "l_atos": "{a} of the {n} recorded lessons. Each came from a real case and has an origin, a reason and a way to apply it.",
        "s4": "Section IV", "h_met": "Masthead — how I work",
        "l_met": "Paired with AI agents, and with a system that keeps the same mistake from happening twice.",
        "convocacao": "Summons", "maq_eyebrow": "For machines", "h_maq": "The same gazette, for agents",
        "l_maq": "No HTML scraping: this page's content comes from the same file in formats an agent reads directly.",
        "mcp_nota": "MCP server, read-only, no login",
        "dica": "In Claude: Settings → Connectors → add custom connector → paste the address of",
        "rodape": "Generated from a single file (conteudo/dados.en.json) — page, Markdown, JSON Resume.",
        "medido_em": "Measured on {d}", "para_quem": "for whom", "papel": "my role", "tecnologias": "Technologies",
        "carimbo": "CORRECTION", "onde": "For", "leia": "Read", "regra": "Rule that stayed:",
        "md_medido": "Measured on {d}. Edition no. {n}.", "md_resumo": "Summary", "md_numeros": "Numbers",
        "md_fonte": "source", "md_proj": "Projects", "md_ret": "Corrections",
        "md_ret_l": "Mistakes I made, in the format of a gazette erratum. Each one became a rule.",
        "md_atos": "Standing orders (lessons)", "md_atos_l": "{a} of the {n} recorded lessons, published here.",
        "md_met": "How I work", "md_disp": "Availability", "md_contato": "Contact",
        "md_faq": "Frequently asked questions", "md_agentes": "For agents",
        "md_mcp": "MCP server (Streamable HTTP, no auth, read-only; tools and content in Portuguese)",
        "md_resume": "JSON Resume", "md_este": "This text",
        "p_para_quem": "For whom", "p_papel": "My role", "p_status": "Status", "p_stack": "Stack",
        "p_endereco": "Address", "p_fatos": "Facts",
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
         f"- [Currículo em JSON Resume]({s['url']}/resume.json): formato estruturado",
         f"- [Servidor MCP]({s['url']}/mcp): ferramentas ler_perfil, listar_projetos, ver_projeto, listar_retificacoes, buscar_licoes, verificar_disponibilidade",
         "", "## Projetos"]
    L += [f"- [{pr['nome']}]({s['url']}/projetos/{pr['slug']}.md): {pr['linha']}" for pr in d["projetos"]]
    L += ["", "## Optional",
          f"- [Texto completo]({s['url']}/llms-full.txt): tudo acima num arquivo só", ""]
    return "\n".join(L)


def resume_json(d: dict) -> dict:
    p, s = d["perfil"], d["site"]
    trabalho = next(pr for pr in d["projetos"] if pr["tipo"] == "trabalho")
    return {
        "$schema": "https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json",
        "basics": {
            "name": p["nome"], "label": p["cargo"], "email": p["email"], "url": s["url"],
            "summary": " ".join(p["resumo"]),
            "location": {"city": p["cidade"], "region": p["estado"], "countryCode": "BR"},
            "profiles": [{"network": "GitHub", "username": "mateusrfabro", "url": p["github"]},
                         {"network": "LinkedIn", "url": p["linkedin"]}],
        },
        "work": [{"name": "Grupo de iGaming (nome omitido)", "position": "Analista de Dados",
                  "startDate": "2025-10", "summary": trabalho["linha"],
                  "highlights": trabalho["fatos"]}],
        "projects": [{"name": pr["nome"], "description": pr["linha"], "highlights": pr["fatos"],
                      "keywords": pr["stack"], **({"url": pr["url"]} if pr.get("url") else {})}
                     for pr in d["projetos"] if pr["tipo"] == "produto"],
        "education": [{"institution": "Universidade Anhembi Morumbi",
                       "area": "Administração de Empresas", "studyType": "Graduação (em curso)"}],
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
                             "PostgreSQL", "AWS", "TypeScript", "Antifraude", "Agentes de IA"],
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
CSS = r"""
@font-face{font-family:"Newsreader";font-style:normal;font-weight:400 600;font-display:swap;
  src:url(/fontes/newsreader-normal.woff2) format("woff2")}
@font-face{font-family:"Newsreader";font-style:italic;font-weight:400;font-display:swap;
  src:url(/fontes/newsreader-italic.woff2) format("woff2")}
@font-face{font-family:"JetBrains Mono";font-style:normal;font-weight:400 700;font-display:swap;
  src:url(/fontes/jetbrains-mono-normal.woff2) format("woff2")}
:root{
  --paper:#F6F8F9; --paper-2:#EDF1F2; --ink:#14232B; --muted:#56676F; --rule:#C6D1D5;
  --accent:#0E5A63; --accent-soft:#D6E7E9; --stamp:#9E3A2E; --stamp-soft:#F3E3E0;
  --shadow:0 1px 0 rgba(20,35,43,.06), 0 12px 30px -18px rgba(20,35,43,.35);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0F171C; --paper-2:#16222A; --ink:#E4EAED; --muted:#93A4AB; --rule:#2A3942;
    --accent:#5CBAC6; --accent-soft:#17343A; --stamp:#E3806F; --stamp-soft:#35211E;
    --shadow:0 1px 0 rgba(0,0,0,.4), 0 14px 30px -18px rgba(0,0,0,.8);
  }
}
:root[data-theme="dark"]{
  --paper:#0F171C; --paper-2:#16222A; --ink:#E4EAED; --muted:#93A4AB; --rule:#2A3942;
  --accent:#5CBAC6; --accent-soft:#17343A; --stamp:#E3806F; --stamp-soft:#35211E;
  --shadow:0 1px 0 rgba(0,0,0,.4), 0 14px 30px -18px rgba(0,0,0,.8);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Newsreader",Georgia,"Times New Roman",serif;font-size:1.125rem;line-height:1.6;
  font-optical-sizing:auto;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.5;z-index:0;
  background-image:radial-gradient(color-mix(in srgb,var(--ink) 7%,transparent) .6px,transparent .7px);
  background-size:3px 3px}
.mono,.eyebrow,.protocolo,nav a,.botao,.fato-lista,.stack li,.rodape{
  font-family:"JetBrains Mono","Cascadia Code",Consolas,monospace}
a{color:var(--accent);text-underline-offset:.18em;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}
.folha{position:relative;z-index:1;max-width:1080px;margin:0 auto;padding:0 16px 64px}
@media (min-width:720px){.folha{padding:0 40px 96px}}

/* ---------- cabeçalho */
.cabeca{padding:28px 0 0;border-bottom:3px double var(--ink)}
.linha-topo{display:flex;flex-wrap:wrap;gap:8px 16px;justify-content:space-between;align-items:center;
  font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.titulo{font-weight:600;font-size:clamp(2.6rem,9vw,5.6rem);line-height:.95;letter-spacing:-.02em;
  margin:18px 0 6px;text-wrap:balance}
.titulo em{font-style:italic;font-weight:400;color:var(--accent)}
.sob-titulo{display:flex;flex-wrap:wrap;gap:6px 18px;justify-content:space-between;
  border-top:1px solid var(--ink);padding:8px 0 10px;font-size:.78rem;letter-spacing:.08em;
  text-transform:uppercase}
.sob-titulo strong{font-weight:600}
nav{display:flex;gap:0 18px;flex-wrap:wrap;padding:4px 0;border-bottom:1px solid var(--rule);font-size:.8rem}
nav a{text-decoration:none;color:var(--ink)}
nav a:hover{color:var(--accent)}
.botao{appearance:none;border:1px solid var(--ink);background:transparent;color:var(--ink);
  font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;padding:7px 12px;cursor:pointer;
  border-radius:2px;transition:background .2s,color .2s}
.botao:hover,.botao[aria-pressed="true"]{background:var(--ink);color:var(--paper)}

/* ---------- abertura */
.abertura{display:grid;gap:28px;padding:44px 0 36px;border-bottom:1px solid var(--rule)}
@media (min-width:900px){.abertura{grid-template-columns:1.35fr 1fr;gap:56px}}
.eyebrow{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin:0 0 12px}
.tese{font-size:clamp(1.55rem,3.6vw,2.35rem);line-height:1.22;font-weight:400;margin:0;text-wrap:balance}
.tese::first-letter{float:left;font-size:3.4em;line-height:.82;padding:.06em .08em 0 0;font-weight:600;color:var(--accent)}
.resumo p{margin:0 0 14px;max-width:62ch;color:var(--ink)}
.resumo p:first-child{margin-top:4px}
.numeros{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;
  border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);margin:0 0 8px}
.numero{padding:18px 16px 16px;border-right:1px solid var(--rule)}
.numero:first-child{padding-left:0}
.numero:last-child{border-right:0}
@media (max-width:719px){
  .numeros{grid-template-columns:1fr 1fr}
  .numero{padding:16px 12px;border-right:0;border-bottom:1px solid var(--rule)}
  .numero:nth-child(odd){padding-left:0;border-right:1px solid var(--rule)}
  .numero:last-child{grid-column:1/-1;border-right:0;border-bottom:0}
  .numero b{font-size:2rem}
}
.numero b{display:block;font-size:2.4rem;line-height:1;font-weight:500;font-variant-numeric:tabular-nums lining-nums;letter-spacing:-.02em}
.numero span{display:block;font-size:.9rem;line-height:1.35;color:var(--muted);margin-top:6px}
.medido{font-size:.72rem;color:var(--muted);letter-spacing:.06em;margin:8px 0 0}

/* ---------- seções */
.secao{padding:56px 0 8px}
.secao>header{display:grid;gap:4px;margin-bottom:26px}
.secao h2{font-size:clamp(1.9rem,4.6vw,2.8rem);line-height:1.05;margin:0;font-weight:600;letter-spacing:-.015em;text-wrap:balance}
.secao .lead{color:var(--muted);max-width:62ch;margin:6px 0 0}

/* projetos */
.projetos{display:grid;gap:0;border-top:1px solid var(--ink)}
.projeto{display:grid;gap:10px 40px;padding:26px 0;border-bottom:1px solid var(--rule)}
@media (min-width:860px){.projeto{grid-template-columns:260px 1fr}}
.projeto h3{font-size:1.65rem;line-height:1.1;margin:0 0 6px;font-weight:600}
.projeto .status{font-family:"JetBrains Mono","Cascadia Code",monospace;font-size:.72rem;letter-spacing:.06em;
  color:var(--muted);text-transform:uppercase}
.projeto .status.vivo{color:var(--accent)}
.projeto .status.vivo::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--accent);margin-right:7px;vertical-align:1px;box-shadow:0 0 0 3px var(--accent-soft)}
.projeto .linha{font-size:1.25rem;line-height:1.35;margin:0 0 10px}
.projeto dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;margin:0 0 12px;font-size:1rem}
.projeto dt{color:var(--muted);font-style:italic}
.projeto dd{margin:0}
.fato-lista{list-style:none;padding:0;margin:0 0 12px;font-size:.8rem;line-height:1.5;display:grid;gap:4px}
.fato-lista li::before{content:"§ ";color:var(--accent)}
.stack{list-style:none;padding:0;margin:0 0 12px;display:flex;flex-wrap:wrap;gap:6px}
.stack li{font-size:.75rem;border:1px solid var(--rule);padding:3px 7px;border-radius:2px;color:var(--muted)}
.historia{margin:0;padding-left:14px;border-left:2px solid var(--accent);font-style:italic;max-width:64ch}
.contato-topo{margin:0;padding:2px 0 6px;display:flex;flex-wrap:wrap;gap:0 18px;
  font-family:"JetBrains Mono","Cascadia Code",Consolas,monospace;font-size:.78rem}
.contato-topo a,nav a,.redes a,.maquinas li a,.convocacao .email a{display:inline-flex;align-items:center;min-height:44px}
.contato-topo a:first-child{font-weight:600}
.botao{min-height:44px}
.faq summary{padding:10px 0;min-height:44px}
.redes{font-size:.8rem}
.dica{margin-top:14px}
.maquinas p.eyebrow{color:var(--accent)}
.ret h3.contexto{font-weight:400;font-size:.95rem;line-height:1.4;font-style:italic;color:var(--muted);margin:0 0 12px}
.projeto.trabalho{background:var(--paper-2);padding:26px 18px;margin-top:18px;border:1px solid var(--rule)}

/* retificações: a peça principal */
.retificacoes{display:grid;gap:22px}
@media (min-width:860px){.retificacoes{grid-template-columns:1fr 1fr}}
.ret{position:relative;background:var(--paper);border:1px solid var(--ink);padding:22px 20px 18px;
  box-shadow:var(--shadow);transform:rotate(var(--giro,0deg));transition:transform .3s ease}
.ret:nth-child(3n+1){--giro:-.35deg}.ret:nth-child(3n+2){--giro:.3deg}
.ret:hover{transform:rotate(0) translateY(-2px)}
.ret .topo{display:flex;justify-content:space-between;gap:12px;align-items:baseline;
  border-bottom:1px solid var(--rule);padding-bottom:8px;margin-bottom:12px}
.protocolo{font-size:.75rem;letter-spacing:.1em;color:var(--muted)}
.ret .contexto{font-size:.95rem;font-style:italic;color:var(--muted);margin:0 0 12px}
.ret .topo{padding-right:128px}
@media (max-width:420px){
  .ret{padding-top:48px}
  .ret .topo{padding-right:0}
  .onde,.leia{grid-template-columns:1fr;gap:2px}
}
.carimbo{position:absolute;top:12px;right:14px;font-family:"JetBrains Mono","Cascadia Code",monospace;
  font-size:.7rem;letter-spacing:.2em;font-weight:700;color:var(--stamp);border:2px solid var(--stamp);
  padding:3px 7px 2px;transform:rotate(6deg);border-radius:3px;
  mask-image:radial-gradient(circle at 30% 40%,#000 60%,rgba(0,0,0,.8) 100%)}
.onde,.leia{margin:0 0 10px;display:grid;grid-template-columns:5.6rem 1fr;gap:10px;align-items:baseline}
.onde b,.leia b{font-family:"JetBrains Mono","Cascadia Code",monospace;font-size:.75rem;letter-spacing:.12em;
  text-transform:uppercase;font-weight:600}
.onde span{text-decoration:line-through;text-decoration-color:var(--stamp);text-decoration-thickness:1.5px;color:var(--muted)}
.leia b{color:var(--accent)}
.regra{margin:12px 0 0;padding-top:10px;border-top:1px dashed var(--rule);font-size:.95rem}
.regra i{color:var(--muted)}

/* atos */
.atos{columns:1;column-gap:48px;padding:0;margin:0;list-style:none;counter-reset:ato}
@media (min-width:860px){.atos{columns:2}}
.atos li{break-inside:avoid;padding:14px 0 16px;border-top:1px solid var(--rule);counter-increment:ato}
.atos li::before{content:"Ato " counter(ato,decimal-leading-zero);display:block;
  font-family:"JetBrains Mono","Cascadia Code",monospace;font-size:.66rem;letter-spacing:.14em;color:var(--accent);
  text-transform:uppercase;margin-bottom:4px}
.atos strong{display:block;font-size:1.18rem;line-height:1.25;font-weight:600;margin-bottom:4px}
.atos span{color:var(--muted);font-size:1rem}

/* método */
.metodo{display:grid;gap:0;border-top:1px solid var(--ink)}
@media (min-width:860px){.metodo{grid-template-columns:repeat(5,1fr)}}
.metodo div{padding:16px 16px 18px 0;border-bottom:1px solid var(--rule)}
@media (min-width:860px){.metodo div{border-bottom:0;border-right:1px solid var(--rule);padding-left:16px}.metodo div:first-child{padding-left:0}.metodo div:last-child{border-right:0}}
.metodo h3{font-size:1.1rem;margin:0 0 6px;font-weight:600}
.metodo p{margin:0;font-size:.98rem;color:var(--muted)}

/* convocação e máquinas */
.duas{display:grid;gap:24px}
@media (min-width:860px){.duas{grid-template-columns:1fr 1fr}}
.convocacao{border:2px solid var(--accent);padding:26px 22px;position:relative}
.convocacao h2{color:var(--accent)}
.convocacao .email{font-size:clamp(1.2rem,3vw,1.6rem);word-break:break-word}
.maquinas{border:1px solid var(--rule);padding:26px 22px;background:var(--paper-2)}
.maquinas ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.maquinas code{font-family:"JetBrains Mono","Cascadia Code",monospace;font-size:.8rem;
  background:var(--paper);border:1px solid var(--rule);padding:2px 6px;border-radius:2px;word-break:break-all}
.maquinas p{margin:0 0 14px;color:var(--muted)}
.faq{margin-top:10px}
.faq details{border-top:1px solid var(--rule);padding:12px 0}
.faq summary{cursor:pointer;font-weight:600}
.faq p{margin:8px 0 0;color:var(--muted)}
.rodape{margin-top:64px;padding-top:14px;border-top:3px double var(--ink);font-size:.72rem;
  letter-spacing:.04em;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between}

/* versão para máquinas */
#maquina{display:none;white-space:pre-wrap;word-break:break-word;margin:28px 0 0;padding:22px 18px;
  font-family:"JetBrains Mono","Cascadia Code",monospace;font-size:.82rem;line-height:1.65;
  background:var(--paper-2);border:1px solid var(--rule);color:var(--ink)}
body.modo-maquina #humano{display:none}
body.modo-maquina #maquina{display:block}

/* entrada da página: a edição "sai da prensa" uma vez */
@keyframes prensa{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.cabeca,.abertura>*{animation:prensa .7s cubic-bezier(.2,.7,.2,1) both}
.abertura>*:nth-child(2){animation-delay:.12s}
"""

JS = r"""
(function(){
  var botao=document.getElementById('alternar');
  var menu=document.querySelector('nav');
  function aplicar(maquina){
    document.body.classList.toggle('modo-maquina',maquina);
    botao.setAttribute('aria-pressed',String(maquina));
    menu.hidden=maquina;
    if(maquina)document.getElementById('maquina').focus();
  }
  botao.addEventListener('click',function(){aplicar(!document.body.classList.contains('modo-maquina'))});
  if(location.hash==='#maquina')aplicar(true);

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
    return s.startswith(("no ar", "em produção", "live", "in production"))


def html_projeto(pr: dict, t: dict = T["pt"]) -> str:
    classe = "projeto trabalho" if pr["tipo"] == "trabalho" else "projeto"
    link = (f' · <a href="{e(pr["url"])}" rel="noopener">{e(pr["url"].split("//")[1])}</a>'
            if pr.get("url") else "")
    stack = "".join(f"<li>{e(s)}</li>" for s in pr["stack"])
    fatos = "".join(f"<li>{e(f)}</li>" for f in pr["fatos"])
    return f"""
<article class="{classe}" id="{e(pr['slug'])}">
  <div>
    <h3>{e(pr['nome'])}</h3>
    <div class="status{' vivo' if status_vivo(pr) else ''}">{e(pr['status'])}</div>
  </div>
  <div>
    <p class="linha">{e(pr['linha'])}</p>
    <dl><dt>{t['para_quem']}</dt><dd>{e(pr['para_quem'])}</dd><dt>{t['papel']}</dt><dd>{e(pr['papel'])}{link}</dd></dl>
    <ul class="fato-lista">{fatos}</ul>
    <ul class="stack" aria-label="{t['tecnologias']}">{stack}</ul>
    <p class="historia">{e(pr['historia'])}</p>
  </div>
</article>"""


def html_retificacao(r: dict, t: dict = T["pt"]) -> str:
    return f"""
<article class="ret" id="{e(r['protocolo'].lower())}">
  <span class="carimbo" aria-hidden="true">{t['carimbo']}</span>
  <div class="topo"><span class="protocolo">{e(r['protocolo'])} · <time datetime="{e(r['data'])}">{data_curta_t(r['data'], t)}</time></span></div>
  <h3 class="contexto">{e(r['contexto'])}</h3>
  <p class="onde"><b>{t['onde']}</b><span>{e(r['onde_se_le'])}</span></p>
  <p class="leia"><b>{t['leia']}</b><span>{e(r['leia_se'])}</span></p>
  <p class="regra"><i>{t['regra']}</i> {e(r['regra'])}</p>
</article>"""


def pagina(d: dict, md: str, t: dict = T["pt"]) -> str:
    p, s = d["perfil"], d["site"]
    base = s["url"] + t["prefixo"]
    ld = json.dumps(json_ld(d), ensure_ascii=False)
    dados_js = json.dumps({k: d[k] for k in ("perfil", "numeros", "projetos", "retificacoes",
                                                "disponibilidade")}, ensure_ascii=False)
    ld, dados_js = json_em_script(ld), json_em_script(dados_js)
    numeros = "".join(f'<div class="numero"><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>'
                      for n in d["numeros"])
    produtos = "".join(html_projeto(pr, t) for pr in d["projetos"] if pr["tipo"] == "produto")
    trabalho = "".join(html_projeto(pr, t) for pr in d["projetos"] if pr["tipo"] == "trabalho")
    rets = "".join(html_retificacao(r, t) for r in ordenadas(d["retificacoes"]))
    atos = "".join(f"<li><strong>{e(a['titulo'])}</strong><span>{e(a['texto'])}</span></li>"
                   for a in d["atos"])
    metodo = "".join(f"<div><h3>{e(m['titulo'])}</h3><p>{e(m['texto'])}</p></div>" for m in d["metodo"])
    faq = "".join(f"<details><summary>{e(f['pergunta'])}</summary><p>{e(f['resposta'])}</p></details>"
                  for f in d["faq"])
    resumo = "".join(f"<p>{e(par)}</p>" for par in p["resumo"])
    titulo_pag = f"{p['nome']} — {p['cargo']}"
    nav = t["nav"]
    ancoras = ["projetos", "retificacoes", "atos", "metodo", "convocacao", "maquinas"]
    menu = "".join(f'<a href="#{a}">{e(r)}</a>' for a, r in zip(ancoras, nav))
    return f"""<!doctype html>
<html lang="{e(s['idioma'])}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo_pag)}</title>
<meta name="description" content="{e(s['descricao'])}">
<link rel="canonical" href="{e(base)}/">
<link rel="alternate" hreflang="pt-BR" href="{e(s['url'])}/">
<link rel="alternate" hreflang="en" href="{e(s['url'])}/en/">
<link rel="alternate" hreflang="x-default" href="{e(s['url'])}/">
<link rel="alternate" type="text/markdown" href="{t['prefixo']}/index.md" title="Markdown">
<link rel="alternate" type="application/json" href="/resume.json" title="JSON Resume">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(titulo_pag)}">
<meta property="og:description" content="{e(s['descricao'])}">
<meta property="og:url" content="{e(base)}/">
<meta property="og:locale" content="{t['locale']}">
<meta property="profile:first_name" content="Mateus">
<meta property="profile:last_name" content="Fabro">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo_pag)}">
<meta name="twitter:description" content="{e(s['descricao'])}">
<meta name="theme-color" content="#0E5A63">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:image" content="{e(s['url'])}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(s['titulo'])} — {e(t['edicao'].format(n=edicao(d)).split(' · ')[0])}">
<meta name="twitter:image" content="{e(s['url'])}/og.png">
<link rel="preload" href="/fontes/newsreader-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/estilo.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<div class="folha">
<header class="cabeca">
  <div class="linha-topo">
    <span>{e(p['cidade'])}, {e(data_extenso_t(s['medido_em'], t))} · <a href="{t['outro_href']}" hreflang="{t['outro']}" lang="{t['outro']}">{t['outro_rotulo']}</a></span>
    <button class="botao" id="alternar" type="button" aria-pressed="false" aria-controls="maquina">{t['maquina']}</button>
  </div>
  <h1 class="titulo">{t['titulo_de']} <em>{e(p['nome'])}</em></h1>
  <div class="sob-titulo">
    <span><strong>{e(p['cargo'])}</strong> · {e(p['subtitulo'])}</span>
    <span>{e(t['edicao'].format(n=edicao(d)))}</span>
  </div>
  <p class="contato-topo"><a href="mailto:{e(p['email'])}">{e(p['email'])}</a><a href="{e(p['github'])}" rel="me noopener">GitHub</a><a href="{e(p['linkedin'])}" rel="me noopener">LinkedIn</a><a href="#convocacao">{e(d['disponibilidade']['status'].capitalize())}</a></p>
</header>
<nav aria-label="{t['menu']}">
  {menu}
</nav>

<main id="humano">
<section class="abertura" aria-label="{t['apresentacao']}">
  <div>
    <p class="eyebrow">{t['frase']}</p>
    <p class="tese">{e(p['tese'])}</p>
  </div>
  <div class="resumo">{resumo}</div>
</section>
<div class="numeros">{numeros}</div>
<p class="medido mono">{e(t['medido'].format(d=data_curta_t(s['medido_em'], t)))}</p>

<section class="secao" id="projetos">
  <header><p class="eyebrow">{t['s1']}</p><h2>{t['h_proj']}</h2>
  <p class="lead">{t['l_proj']}</p></header>
  <div class="projetos">{produtos}</div>
  {trabalho}
</section>

<section class="secao" id="retificacoes">
  <header><p class="eyebrow">{t['s2']}</p><h2>{t['h_ret']}</h2>
  <p class="lead">{t['l_ret']}</p></header>
  <div class="retificacoes">{rets}</div>
</section>

<section class="secao" id="atos">
  <header><p class="eyebrow">{t['s3']}</p><h2>{t['h_atos']}</h2>
  <p class="lead">{e(t['l_atos'].format(a=len(d['atos']), n=edicao(d)))}</p></header>
  <ol class="atos">{atos}</ol>
</section>

<section class="secao" id="metodo">
  <header><p class="eyebrow">{t['s4']}</p><h2>{t['h_met']}</h2>
  <p class="lead">{t['l_met']}</p></header>
  <div class="metodo">{metodo}</div>
</section>

<section class="secao duas">
  <div class="convocacao" id="convocacao">
    <p class="eyebrow">{t['convocacao']}</p>
    <h2>{e(d['disponibilidade']['status'].capitalize())}</h2>
    <p>{e(d['disponibilidade']['texto'])}</p>
    <p class="email"><a href="mailto:{e(p['email'])}">{e(p['email'])}</a></p>
    <p class="redes mono"><a href="{e(p['github'])}" rel="me noopener">GitHub</a> · <a href="{e(p['linkedin'])}" rel="me noopener">LinkedIn</a> · {e(p['cidade'])}, {e(p['estado'])}</p>
    <div class="faq">{faq}</div>
  </div>
  <div class="maquinas" id="maquinas">
    <p class="eyebrow">{t['maq_eyebrow']}</p>
    <h2>{t['h_maq']}</h2>
    <p>{t['l_maq']}</p>
    <ul>
      <li><code>{e(s['url'])}/mcp</code><br>{t['mcp_nota']}</li>
      <li><a href="/llms.txt"><code>/llms.txt</code></a> · <a href="/llms-full.txt"><code>/llms-full.txt</code></a></li>
      <li><a href="{t['prefixo']}/index.md"><code>{t['prefixo']}/index.md</code></a> · <a href="/resume.json"><code>/resume.json</code></a></li>
    </ul>
    <p class="dica">{t['dica']} <code>/mcp</code>.</p>
  </div>
</section>
</main>

<pre id="maquina" tabindex="-1">{e(md)}</pre>

<footer class="rodape">
  <span>{t['rodape']}</span>
  <span>{e(t['medido_em'].format(d=data_curta_t(s['medido_em'], t)))}</span>
</footer>
</div>
<script type="application/json" id="dados">{dados_js}</script>
<script src="/app.js" defer></script>
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
    urls = [f"{s['url']}/", f"{s['url']}/en/", f"{s['url']}/index.md", f"{s['url']}/en/index.md",
            f"{s['url']}/llms.txt",
            f"{s['url']}/llms-full.txt", f"{s['url']}/resume.json"]
    urls += [f"{s['url']}/projetos/{pr['slug']}.md" for pr in d["projetos"]]
    corpo = "".join(f"<url><loc>{e(u)}</loc><lastmod>{s['medido_em']}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{corpo}</urlset>\n')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="3" fill="#0E5A63"/>
<rect x="6" y="7" width="20" height="2" fill="#F6F8F9"/><rect x="6" y="11" width="20" height="1" fill="#F6F8F9"/>
<text x="16" y="27" font-family="Georgia,serif" font-size="15" font-style="italic" text-anchor="middle" fill="#F6F8F9">F</text>
</svg>
"""


def pagina_404(d: dict) -> str:
    return f"""<!doctype html>
<html lang="{e(d['site']['idioma'])}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página não encontrada — {e(d['site']['titulo'])}</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/estilo.css"></head>
<body><div class="folha"><header class="cabeca"><h1 class="titulo">Diário de <em>{e(d['perfil']['nome'])}</em></h1></header>
<section class="secao"><article class="ret"><span class="carimbo" aria-hidden="true">RETIFICAÇÃO</span>
<div class="topo"><span class="protocolo">ERRO 404</span></div>
<p class="onde"><b>Onde se lê</b><span>esta página existe.</span></p>
<p class="leia"><b>Leia-se</b><span>ela não existe — ou mudou de endereço. <a href="/">Voltar à edição de hoje</a>.</span></p>
</article></section></div></body></html>
"""


def gerar(d: dict, d_en: dict | None = None) -> dict[str, str]:
    d_en = d_en if d_en is not None else carregar_en()
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
    }
    for pr in d["projetos"]:
        arquivos[f"projetos/{pr['slug']}.md"] = projeto_md(pr) + "\n"
    return arquivos


def main() -> int:
    arquivos = gerar(carregar())
    if "--check" in sys.argv:
        velhos = [n for n, c in arquivos.items()
                  if not (SAIDA / n).exists() or (SAIDA / n).read_text(encoding="utf-8") != c]
        if velhos:
            print("public/ desatualizado — rode `python build.py`:", ", ".join(velhos))
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
