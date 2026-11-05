"""Servidor MCP do diário — Streamable HTTP, sem estado, só leitura, sem login.

Lê o MESMO conteudo/dados.json que gera a página: o que um agente consulta aqui é, por
construção, o que uma pessoa lê no site.

Responde aos dois dialetos em uso em set/2026:
  • 2025-xx (`initialize` antes de tudo), que a maioria dos clientes ainda fala;
  • 2026-07-28 (sem handshake; `server/discover`; `resultType` em todo resultado).

Nenhuma ferramenta escreve nada. Uma ferramenta pública sem autenticação que escreve (mandar
mensagem, marcar conversa) é convite a spam — o contato é o e-mail, devolvido por
`verificar_disponibilidade`.
"""
from __future__ import annotations

import json
import unicodedata
from http.server import BaseHTTPRequestHandler
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "conteudo" / "dados.json"
VERSOES = ["2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26"]
INFO = {"name": "diario-mateus-fabro", "title": "Diário de Mateus Fabro", "version": "1.0.0"}
MAX_CORPO = 64 * 1024
MAX_ARG = 200

_SEM_ARGS = {"type": "object", "properties": {}, "additionalProperties": False}
_SO_LEITURA = {"readOnlyHint": True, "openWorldHint": False}

FERRAMENTAS = [
    {"name": "ler_perfil",
     "description": "Quem é Mateus Fabro: cargo, cidade, resumo, números medidos e contato.",
     "inputSchema": _SEM_ARGS, "annotations": _SO_LEITURA},
    {"name": "listar_projetos",
     "description": "Projetos (produtos próprios e o trabalho em iGaming, 2025–2026), com status real. "
                    "Filtro opcional tipo = 'produto' ou 'trabalho'.",
     "inputSchema": {"type": "object", "additionalProperties": False,
                     "properties": {"tipo": {"type": "string", "enum": ["produto", "trabalho"]}}},
     "annotations": _SO_LEITURA},
    {"name": "ver_projeto",
     "description": "Detalhe de um projeto pelo slug (ex.: avisa-edital, pingado, nous-clinical, aggron, dumpai).",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["slug"],
                     "properties": {"slug": {"type": "string", "maxLength": 60}}},
     "annotations": _SO_LEITURA},
    {"name": "listar_retificacoes",
     "description": "Erros que ele cometeu, com data e número: onde se lê / leia-se / regra que ficou.",
     "inputSchema": _SEM_ARGS, "annotations": _SO_LEITURA},
    {"name": "buscar_licoes",
     "description": "Lições de engenharia publicadas (as regras que nasceram de erros). "
                    "Busca opcional por termo no título ou no texto.",
     "inputSchema": {"type": "object", "additionalProperties": False,
                     "properties": {"termo": {"type": "string", "maxLength": MAX_ARG}}},
     "annotations": _SO_LEITURA},
    {"name": "verificar_disponibilidade",
     "description": "Se ele está aberto a projetos ou vagas e qual o canal de contato.",
     "inputSchema": _SEM_ARGS, "annotations": _SO_LEITURA},
]


def carregar() -> dict:
    return json.loads(DADOS.read_text(encoding="utf-8"))


def _norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s).lower())
                   if not unicodedata.combining(c))


class ErroDeArgumento(ValueError):
    pass


def executar(nome: str, args: dict, dados: dict | None = None):
    """Dado de volta da ferramenta, ou None se ela não existe."""
    d = dados or carregar()
    if not isinstance(args, dict):
        raise ErroDeArgumento("arguments precisa ser um objeto")
    if nome == "ler_perfil":
        p = d["perfil"]
        return {"perfil": {k: p[k] for k in ("nome", "cargo", "subtitulo", "cidade", "estado",
                                              "email", "github", "linkedin", "tese", "resumo",
                                              "formacao", "idiomas")},
                "numeros": d["numeros"], "medido_em": d["site"]["medido_em"],
                "site": d["site"]["url"]}
    if nome == "listar_projetos":
        tipo = args.get("tipo")
        if tipo not in (None, "produto", "trabalho"):
            raise ErroDeArgumento("tipo deve ser 'produto' ou 'trabalho'")
        return [{k: pr[k] for k in ("slug", "nome", "tipo", "linha", "status", "url")}
                for pr in d["projetos"] if tipo in (None, pr["tipo"])]
    if nome == "ver_projeto":
        slug = str(args.get("slug") or "")[:60]
        achado = next((pr for pr in d["projetos"] if pr["slug"] == slug), None)
        if achado is None:
            raise ErroDeArgumento(
                "slug desconhecido; opções: " + ", ".join(pr["slug"] for pr in d["projetos"]))
        return achado
    if nome == "listar_retificacoes":
        return sorted(d["retificacoes"], key=lambda r: r["data"])
    if nome == "buscar_licoes":
        termo = _norm(str(args.get("termo") or "")[:MAX_ARG]).strip()
        atos = d["atos"]
        if termo:
            atos = [a for a in atos if termo in _norm(a["titulo"] + " " + a["texto"])]
        return {"total_registradas": d["numeros"][0]["valor"], "publicadas": len(d["atos"]),
                "encontradas": atos}
    if nome == "verificar_disponibilidade":
        return d["disponibilidade"]
    return None


def _erro(mid, codigo: int, msg: str) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": codigo, "message": msg}}


def _id_valido(mid) -> bool:
    """JSON-RPC aceita string, número ou null. Aqui: string curta ou inteiro seguro — um id
    `1e999` virava `Infinity` na resposta (JSON inválido), e um id-objeto de 60 KB era ecoado."""
    if mid is None or (isinstance(mid, str) and len(mid) <= 128):
        return True
    return isinstance(mid, int) and not isinstance(mid, bool) and abs(mid) <= 2 ** 53


def tratar(msg) -> dict | None:
    """Uma mensagem JSON-RPC → resposta (ou None para notificação)."""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
        mid = msg.get("id") if isinstance(msg, dict) else None
        return _erro(mid if _id_valido(mid) else None, -32600, "requisição inválida")
    if "id" not in msg:
        return None                                   # notificação: 202 sem corpo
    metodo, params, mid = msg["method"], msg.get("params", {}), msg["id"]
    if not _id_valido(mid):
        return _erro(None, -32600, "id precisa ser string curta ou inteiro")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _erro(mid, -32602, "params precisa ser um objeto")

    if metodo == "initialize":
        pedida = params.get("protocolVersion")
        r = {"protocolVersion": pedida if pedida in VERSOES else VERSOES[1],
             "capabilities": {"tools": {"listChanged": False}}, "serverInfo": INFO,
             "instructions": "Diário de Mateus Fabro. Comece por ler_perfil; as retificações "
                             "(listar_retificacoes) mostram como ele trabalha."}
    elif metodo == "server/discover":
        r = {"supportedVersions": VERSOES, "capabilities": {"tools": {}}, "serverInfo": INFO}
    elif metodo == "ping":
        r = {}
    elif metodo == "tools/list":
        r = {"tools": FERRAMENTAS, "ttlMs": 3_600_000, "cacheScope": "public"}
    elif metodo == "tools/call":
        try:
            args = params.get("arguments", {})
            dado = executar(params.get("name"), {} if args is None else args)
        except ErroDeArgumento as exc:
            r = {"content": [{"type": "text", "text": str(exc)}], "isError": True}
        else:
            if dado is None:
                return _erro(mid, -32602, f"ferramenta desconhecida: {params.get('name')!r}")
            texto = json.dumps(dado, ensure_ascii=False)
            r = {"content": [{"type": "text", "text": texto}], "isError": False}
            if isinstance(dado, dict):
                r["structuredContent"] = dado
    else:
        return _erro(mid, -32601, f"método não suportado: {metodo}")
    r.setdefault("resultType", "complete")
    return {"jsonrpc": "2.0", "id": mid, "result": r}


class handler(BaseHTTPRequestHandler):
    server_version = "mcp"
    sys_version = ""

    def _enviar(self, codigo: int, corpo=None):
        self.send_response(codigo)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
                         "Content-Type, Accept, Mcp-Protocol-Version, Mcp-Method, Mcp-Name, Mcp-Session-Id")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        if corpo is None:
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        bruto = json.dumps(corpo, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(bruto)))
        self.end_headers()
        self.wfile.write(bruto)

    def do_OPTIONS(self):
        self._enviar(204)

    def do_GET(self):
        # Sem stream SSE: o servidor não inicia mensagens. 405 é a resposta prevista pela spec.
        self._enviar(405, {"erro": "use POST com JSON-RPC; veja /llms.txt"})

    do_HEAD = do_PUT = do_DELETE = do_PATCH = do_GET

    def do_POST(self):
        if self.headers.get("Transfer-Encoding") or self.headers.get("Content-Length") is None:
            self.close_connection = True
            return self._enviar(411, _erro(None, -32600, "Content-Length obrigatório"))
        try:
            n = int(self.headers.get("Content-Length"))
        except ValueError:
            n = -1
        if n < 0 or n > MAX_CORPO:
            # não lê o corpo (é o que se quer evitar) e fecha a conexão: o que sobrou no
            # socket não pode ser interpretado como a próxima requisição
            self.close_connection = True
            return self._enviar(413, _erro(None, -32600, "corpo grande demais"))
        try:
            msg = json.loads(self.rfile.read(n) or b"null")
        except (ValueError, UnicodeDecodeError, RecursionError):
            # RecursionError: ~30 KB de "[" aninhado cabem no limite e derrubavam o handler
            return self._enviar(400, _erro(None, -32700, "JSON inválido"))
        if isinstance(msg, list):
            # lotes saíram da spec em 2025-06-18
            return self._enviar(400, _erro(None, -32600, "lotes não são suportados"))
        try:
            resposta = tratar(msg)
        except Exception:  # noqa: BLE001 — nada de traceback para fora; o log da Vercel guarda
            import traceback
            traceback.print_exc()
            return self._enviar(500, _erro(None, -32603, "erro interno"))
        if resposta is None:
            return self._enviar(202)
        self._enviar(200, resposta)
