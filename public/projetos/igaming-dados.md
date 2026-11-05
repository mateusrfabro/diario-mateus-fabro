# Super Nova Gaming / MultiBet (Grupo PGX)

Pipelines, migração de data lake, antifraude, atribuição de mídia e painéis para três operações em três países.

- **Para quem:** Squad de dados de 4 pessoas atendendo três operações de iGaming.
- **Meu papel:** Analista de dados desde out/2025, com trabalho de engenharia de ponta a ponta.
- **Status:** Trabalho atual
- **Stack:** Python, SQL (PostgreSQL e motores distribuídos), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Fatos:**
  - 1.408 commits meus entre 12/03 e 04/11/2026
  - migração de data lake (3,07 bi de registros, 234 tabelas): camada de conexão com fonte única e rollback por uma variável, preservando a interface dos pipelines consumidores
  - custo de mídia (Meta, Google Ads, TikTok) num tracker de atribuição multi-tenant, substituindo um fornecedor pago
  - serviço diário de risco e score de crédito de jogador
  - linter multi-tenant que falha fechado: lista de exceções de 43 para 3
  - consulta crítica de 240 s para 21 s, com equivalência provada por conjunto

A maior parte das lições publicadas neste site nasceu aqui. Os números são reais; os nomes de cliente ficam de fora.
