"""Gera public/og.png (1200×630), a imagem que aparece quando o link é colado no LinkedIn.

A imagem traz texto (edição e uma retificação), e texto numa imagem envelhece sem ninguém ver.
Por isso este script também grava public/og.json com o que foi desenhado, e
`tests/test_build.py` compara com o conteúdo atual: mudou a edição, o teste pede para rodar
este script de novo.

Uso: python scripts/gerar_og.py   (precisa de Playwright + Edge ou Chromium)
"""
from __future__ import annotations

import functools
import http.server
import json
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import build  # noqa: E402

PROTOCOLO_DA_CAPA = "RET-2026-0923"   # a retificação do próprio site


def descritor(d: dict) -> dict:
    """O que a imagem mostra — comparado pelo teste com o conteúdo atual."""
    r = next(x for x in d["retificacoes"] if x["protocolo"] == PROTOCOLO_DA_CAPA)
    # O "leia-se" da capa vem da PRÓPRIA retificação, não do número atual de commits: a
    # retificação de 23/09 falava de 820; o número vivo (que o recontar atualiza) é outro fato.
    leia_curto = r["leia_se"].split(".")[0] + "."
    return {"edicao": build.edicao(d), "nome": d["perfil"]["nome"], "cargo": d["perfil"]["cargo"],
            "protocolo": r["protocolo"], "onde_se_le": r["onde_se_le"],
            "leia_curto": leia_curto, "regra": r["regra"]}


def html_capa(desc: dict) -> str:
    e = build.e
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="/estilo.css">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body::before{{opacity:.7}}
.capa{{position:relative;z-index:1;box-sizing:border-box;width:1200px;height:630px;padding:56px 72px;
  display:grid;grid-template-columns:1.25fr 1fr;gap:48px;align-items:center}}
.capa .lin{{font-family:"JetBrains Mono";font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}}
.capa h1{{font-family:"Newsreader";font-weight:600;font-size:104px;line-height:.92;letter-spacing:-.02em;margin:18px 0 22px}}
.capa h1 em{{font-weight:400;color:var(--accent)}}
.capa .cargo{{font-size:30px;border-top:2px solid var(--ink);padding-top:14px}}
.capa .ret{{transform:rotate(1.2deg);padding:28px 26px 24px;font-size:24px}}
.capa .ret .onde,.capa .ret .leia{{grid-template-columns:8.2rem 1fr}}
.capa .carimbo{{font-size:15px;top:18px;right:20px}}
.capa .leia span{{font-size:26px}}
</style></head><body>
<div class="capa">
  <div>
    <div class="lin">Edição nº {e(desc['edicao'])} · uma por lição registrada</div>
    <h1>Diário de<br><em>{e(desc['nome'])}</em></h1>
    <div class="cargo">{e(desc['cargo'])} · dados e produtos, com as minhas retificações</div>
  </div>
  <article class="ret">
    <span class="carimbo">RETIFICAÇÃO</span>
    <div class="topo"><span class="protocolo">{e(desc['protocolo'])}</span></div>
    <p class="onde"><b>Onde se lê</b><span>{e(desc['onde_se_le'])}</span></p>
    <p class="leia"><b>Leia-se</b><span>{e(desc['leia_curto'])}</span></p>
    <p class="regra"><i>Regra que ficou:</i> {e(desc['regra'])}</p>
  </article>
</div></body></html>"""


def main() -> int:
    from playwright.sync_api import sync_playwright
    d = build.carregar()
    desc = descritor(d)
    saida = RAIZ / "public"
    (saida / "_capa.html").write_text(html_capa(desc), encoding="utf-8")
    manip = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(saida))
    manip.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manip)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            try:
                nav = p.chromium.launch(channel="msedge")
            except Exception:  # noqa: BLE001 — sem Edge, o Chromium do Playwright
                nav = p.chromium.launch()
            pg = nav.new_page(viewport={"width": 1200, "height": 630}, color_scheme="light")
            pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/_capa.html")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            pg.screenshot(path=str(saida / "og.png"))
            nav.close()
    finally:
        srv.shutdown()
        (saida / "_capa.html").unlink(missing_ok=True)
    (saida / "og.json").write_text(json.dumps(desc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("public/og.png gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
