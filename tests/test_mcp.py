"""Servidor MCP: os dois dialetos do protocolo, as ferramentas e o comportamento HTTP real."""
from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from api import mcp  # noqa: E402

D = mcp.carregar()


def rpc(metodo, params=None, mid=1):
    msg = {"jsonrpc": "2.0", "id": mid, "method": metodo}
    if params is not None:
        msg["params"] = params
    return mcp.tratar(msg)


def chamar(nome, args=None):
    r = rpc("tools/call", {"name": nome, "arguments": args or {}})["result"]
    return r, (json.loads(r["content"][0]["text"]) if not r["isError"] else r["content"][0]["text"])


# ------------------------------------------------------------------ protocolo
def test_initialize_devolve_a_versao_pedida_quando_suportada():
    r = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "t", "version": "0"}})["result"]
    assert r["protocolVersion"] == "2025-06-18"
    assert r["capabilities"]["tools"] == {"listChanged": False}
    assert r["serverInfo"]["name"] == "diario-mateus-fabro"


def test_initialize_com_versao_desconhecida_cai_numa_suportada():
    assert rpc("initialize", {"protocolVersion": "1999-01-01"})["result"]["protocolVersion"] in mcp.VERSOES


def test_dialeto_2026_sem_handshake():
    r = rpc("server/discover", {})["result"]
    assert "2026-07-28" in r["supportedVersions"] and r["resultType"] == "complete"
    lista = rpc("tools/list", {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28"}})["result"]
    assert lista["ttlMs"] > 0 and lista["cacheScope"] == "public"


def test_notificacao_nao_tem_resposta():
    assert mcp.tratar({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_metodo_desconhecido_e_requisicao_invalida():
    assert rpc("resources/list")["error"]["code"] == -32601
    assert mcp.tratar({"id": 1, "method": "ping"})["error"]["code"] == -32600
    assert mcp.tratar("oi")["error"]["code"] == -32600
    assert rpc("tools/call", ["nao", "e", "objeto"])["error"]["code"] == -32602


# ------------------------------------------------------------------ ferramentas
def test_toda_ferramenta_listada_executa_e_e_so_leitura():
    nomes = [f["name"] for f in rpc("tools/list")["result"]["tools"]]
    assert nomes == ["ler_perfil", "listar_projetos", "ver_projeto", "listar_retificacoes",
                     "buscar_licoes", "verificar_disponibilidade"]
    for f in mcp.FERRAMENTAS:
        assert f["annotations"]["readOnlyHint"] is True
        args = {"slug": "avisa-edital"} if f["name"] == "ver_projeto" else {}
        r, _ = chamar(f["name"], args)
        assert r["isError"] is False, f["name"]


def test_webmcp_da_pagina_usa_os_mesmos_nomes_do_servidor():
    """As ferramentas do navegador são um subconjunto das do servidor, com o mesmo nome."""
    import re
    js = (RAIZ / "public" / "app.js").read_text(encoding="utf-8")
    nomes_js = set(re.findall(r"name:'([a-z_]+)'", js))
    assert nomes_js and nomes_js <= {f["name"] for f in mcp.FERRAMENTAS}


def test_perfil_traz_contato_e_numeros_medidos():
    _, dado = chamar("ler_perfil")
    assert dado["perfil"]["email"] == D["perfil"]["email"]
    assert dado["medido_em"] == D["site"]["medido_em"]
    assert [n["valor"] for n in dado["numeros"]] == [n["valor"] for n in D["numeros"]]


def test_listar_projetos_filtra_por_tipo_e_rejeita_tipo_invalido():
    _, trab = chamar("listar_projetos", {"tipo": "trabalho"})
    assert [p["tipo"] for p in trab] == ["trabalho"]
    r, msg = chamar("listar_projetos", {"tipo": "cassino"})
    assert r["isError"] is True and "produto" in msg


def test_ver_projeto_desconhecido_lista_as_opcoes():
    r, msg = chamar("ver_projeto", {"slug": "nao-existe"})
    assert r["isError"] is True and "avisa-edital" in msg


def test_buscar_licoes_ignora_acento_e_caixa():
    _, dado = chamar("buscar_licoes", {"termo": "MUTACAO"})
    assert [a["titulo"] for a in dado["encontradas"]] == ["Teste de mutação: prove que o teste sabe falhar"]
    assert dado["total_registradas"] == "101"
    _, tudo = chamar("buscar_licoes")
    assert len(tudo["encontradas"]) == len(D["atos"])


def test_retificacoes_saem_em_ordem_de_data():
    _, rets = chamar("listar_retificacoes")
    assert [r["data"] for r in rets] == sorted(r["data"] for r in D["retificacoes"])


def test_ferramenta_desconhecida_e_erro_de_protocolo():
    assert rpc("tools/call", {"name": "marcar_reuniao", "arguments": {}})["error"]["code"] == -32602


# ------------------------------------------------------------------ HTTP de verdade
@pytest.fixture(scope="module")
def servidor():
    srv = HTTPServer(("127.0.0.1", 0), mcp.handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _post(url, corpo: bytes, extra=None):
    req = urllib.request.Request(url, data=corpo, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json, text/event-stream", **(extra or {})})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def test_http_chamada_completa(servidor):
    st, corpo, h = _post(servidor, json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                                                "params": {"name": "verificar_disponibilidade"}}).encode())
    assert st == 200 and h["Content-Type"].startswith("application/json")
    assert h["Access-Control-Allow-Origin"] == "*"
    r = json.loads(corpo)
    assert r["id"] == 7 and json.loads(r["result"]["content"][0]["text"])["canal"] == D["perfil"]["email"]


def test_http_notificacao_202_sem_corpo(servidor):
    st, corpo, _ = _post(servidor, b'{"jsonrpc":"2.0","method":"notifications/initialized"}')
    assert st == 202 and corpo == b""


def test_http_json_quebrado_e_lote(servidor):
    assert _post(servidor, b"{nao e json")[0] == 400
    assert _post(servidor, b'[{"jsonrpc":"2.0","id":1,"method":"ping"}]')[0] == 400


def test_http_corpo_grande_e_recusado_sem_ser_lido(servidor):
    """O limite é decidido pelo Content-Length, antes de ler. Mandar 64 KB de verdade deixava
    o teste instável no Windows (1 em 6): o servidor responde e fecha enquanto o cliente ainda
    escreve, e o cliente toma "connection reset" em vez do 413."""
    import http.client
    host, porta = servidor.split("//")[1].split(":")
    c = http.client.HTTPConnection(host, int(porta), timeout=5)
    c.putrequest("POST", "/")
    c.putheader("Content-Type", "application/json")
    c.putheader("Content-Length", str(mcp.MAX_CORPO + 1))
    c.endheaders()
    r = c.getresponse()
    assert r.status == 413 and json.loads(r.read())["error"]["code"] == -32600
    c.close()


def test_http_get_e_405(servidor):
    try:
        urllib.request.urlopen(servidor, timeout=5)
        assert False, "GET deveria falhar"
    except urllib.error.HTTPError as exc:
        assert exc.code == 405


# ------------------------------------------------------------------ bordas (revisão de segurança, 23/09)
def test_id_invalido_nao_e_ecoado():
    assert mcp.tratar({"jsonrpc": "2.0", "id": float("inf"), "method": "ping"})["error"]["code"] == -32600
    assert mcp.tratar({"jsonrpc": "2.0", "id": {"x": 1}, "method": "ping"})["id"] is None
    assert mcp.tratar({"jsonrpc": "2.0", "id": True, "method": "ping"})["id"] is None
    assert mcp.tratar({"jsonrpc": "2.0", "id": "abc", "method": "ping"})["result"] == {"resultType": "complete"}


def test_http_json_aninhado_fundo_e_400_nao_500(servidor):
    st, corpo, _ = _post(servidor, b"[" * 30000)
    assert st == 400 and json.loads(corpo)["error"]["code"] == -32700


def test_http_id_infinito_nao_gera_json_invalido(servidor):
    st, corpo, _ = _post(servidor, b'{"jsonrpc":"2.0","id":1e999,"method":"ping"}')
    json.loads(corpo)          # tem de ser JSON válido
    assert b"Infinity" not in corpo


def test_http_sem_content_length_e_411_e_outros_metodos_405(servidor):
    import http.client
    host, porta = servidor.split("//")[1].split(":")
    c = http.client.HTTPConnection(host, int(porta), timeout=5)
    # sem enviar o corpo: o servidor recusa pelo cabeçalho e fecha; mandar o terminador do
    # chunked depois disso dava "connection reset" intermitente no Windows (mesmo caso do 413)
    c.putrequest("POST", "/"); c.putheader("Transfer-Encoding", "chunked"); c.endheaders()
    assert c.getresponse().status == 411
    c.close()
    for metodo in ("PUT", "DELETE"):
        c = http.client.HTTPConnection(host, int(porta), timeout=5)
        c.request(metodo, "/")
        r = c.getresponse()
        assert r.status == 405 and r.getheader("Content-Type").startswith("application/json")
        assert "Python" not in (r.getheader("Server") or "")
        c.close()
