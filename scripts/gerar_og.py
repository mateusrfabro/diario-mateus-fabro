"""Gera public/og.png e public/og-en.png (1200×630), a imagem que aparece quando o link é colado no LinkedIn.

A imagem traz texto (nome, cargo, a frase da abertura e o endereço), e texto numa imagem envelhece
sem ninguém ver. Por isso este script também grava public/og.json com o que foi desenhado, e
`tests/test_build.py` compara com o conteúdo atual: mudou a frase, o teste pede para rodar
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


def descritor(d: dict) -> dict:
    """O que a imagem mostra — comparado pelo teste com o conteúdo atual."""
    return {"nome": d["perfil"]["nome"], "cargo": d["perfil"]["cargo"],
            "frase": d["perfil"]["frase_hero"], "site": d["site"]["url"].split("//")[1]}


def html_capa(desc: dict) -> str:
    e = build.e
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="/estilo.css">
<style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#FFFFFF}}
.capa{{box-sizing:border-box;width:1200px;height:630px;padding:72px 88px 64px;display:flex;flex-direction:column;
  border-top:12px solid var(--accent)}}
.capa .signo{{width:22px;height:22px;border-radius:5px;background:var(--accent);margin:0}}
.capa h1{{font-size:96px;line-height:1;letter-spacing:-.04em;font-weight:750;margin:36px 0 0}}
.capa .cargo{{font-size:38px;margin-top:18px;font-weight:600}}
.capa .frase{{font-size:28px;line-height:1.45;max-width:880px;margin-top:28px}}
.capa .site{{margin-top:auto;font-family:var(--mono);font-size:22px;color:var(--accent);display:flex;align-items:center;gap:16px}}
.capa .site::before{{content:"";width:56px;height:4px;border-radius:2px;background:var(--accent)}}
</style></head><body>
<div class="capa">
  <p class="signo"></p>
  <h1>{e(desc['nome'])}</h1>
  <p class="cargo">{e(desc['cargo'])}</p>
  <p class="frase">{e(desc['frase'])}</p>
  <p class="site">{e(desc['site'])}</p>
</div></body></html>"""


# (língua, carregador, imagem, descritor gravado): a página /en/ aponta para a capa em inglês.
CAPAS = (("pt", "carregar", "og.png", "og.json"), ("en", "carregar_en", "og-en.png", "og-en.json"))


def main() -> int:
    from playwright.sync_api import sync_playwright
    saida = RAIZ / "public"
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
            for _lang, carregador, png, js in CAPAS:
                desc = descritor(getattr(build, carregador)())
                (saida / "_capa.html").write_text(html_capa(desc), encoding="utf-8")
                pg = nav.new_page(viewport={"width": 1200, "height": 630}, color_scheme="light")
                pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/_capa.html")
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(400)
                pg.screenshot(path=str(saida / png))
                pg.close()
                (saida / js).write_text(json.dumps(desc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"public/{png} gerado")
            nav.close()
    finally:
        srv.shutdown()
        (saida / "_capa.html").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
