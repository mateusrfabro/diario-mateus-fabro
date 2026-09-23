# Diário de Mateus Fabro

Portfólio pessoal em formato de diário oficial, escrito para dois leitores: pessoas e agentes de IA.

- **Editais**: os projetos, com o status real de cada um, inclusive os que pararam.
- **Retificações**: erros que cometi, com data e número. Cada um vem no formato "onde se lê / leia-se".
- **Atos**: as regras que nasceram desses erros.
- **Para máquinas**: o mesmo conteúdo em Markdown, `llms.txt`, JSON Resume e um servidor MCP.

## Uma fonte, seis formas

Todo o conteúdo mora em `conteudo/dados.json`. O `build.py` lê esse arquivo e gera `public/`:

| Arquivo | Para quem |
|---|---|
| `index.html` | pessoas (com JSON-LD para buscadores) |
| `index.md` | agentes; também é o que aparece no botão "Ler como máquina" |
| `llms.txt`, `llms-full.txt` | agentes que seguem llmstxt.org |
| `resume.json` | JSON Resume |
| `projetos/*.md` | um arquivo por projeto |
| `robots.txt`, `sitemap.xml` | crawlers (os de IA liberados pelo nome) |

O servidor MCP (`api/mcp.py`, função Python na Vercel) lê o **mesmo** `dados.json`. O que um agente consulta nele é o que uma pessoa lê na página.

```bash
python build.py            # regenera public/
python -m pytest -q        # confere tudo, inclusive que public/ está em dia
```

## Guardas

`tests/` cobre três coisas:

1. **Nomes que não podem sair.** Nenhum nome de empregador, cliente ou pessoa pode aparecer no que é publicado. A lista desses nomes **não fica neste repositório**: uma lista de clientes versionada seria ela mesma o vazamento. Ela fica em `../portfolio-denylist.txt`, e o teste falha se não a encontrar. Para rodar sem ela é preciso declarar `PORTFOLIO_SEM_DENYLIST=1`.
2. **Números derivados.** Os totais de commits e de testes são a soma dos fatos de cada projeto. Se um projeto muda e o total não acompanha, o teste acusa.
3. **Protocolo MCP.** Testado nos dois dialetos (com `initialize` e o de 2026-07-28, sem handshake) e por HTTP de verdade: 202 para notificação, 405 para GET, 413 para corpo grande.

## MCP

Endpoint `POST /mcp`, só leitura e sem login. Ferramentas:

- `ler_perfil`
- `listar_projetos`
- `ver_projeto`
- `listar_retificacoes`
- `buscar_licoes`
- `verificar_disponibilidade`

Para conectar no Claude: Configurações → Conectores → adicionar conector personalizado → URL do `/mcp`.

Nenhuma ferramenta escreve nada. Uma ferramenta pública sem autenticação que manda mensagem seria convite a spam. O contato é o e-mail.
