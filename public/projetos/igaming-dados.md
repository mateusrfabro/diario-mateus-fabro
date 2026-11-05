# Super Nova Gaming / MultiBet (Grupo PGX)

Pipelines, migração de data lake, antifraude, atribuição de mídia e painéis para três operações em três países.

- **Para quem:** Squad de dados de 4 pessoas atendendo três operações de iGaming; liderei a frente de dados de duas delas.
- **Meu papel:** Analista de dados de out/2025 a nov/2026, com trabalho de engenharia de ponta a ponta.
- **Status:** Encerrado em nov/2026 (fim da operação)
- **Stack:** Python, SQL (PostgreSQL e motores distribuídos), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Fatos:**
  - 963 commits meus entre 24/04 e 23/10/2026
  - migração de data lake (3,07 bi de registros, 234 tabelas): camada de conexão com fonte única e rollback por uma variável, preservando a interface dos ~71 pipelines consumidores
  - custo de mídia (Meta, Google Ads, TikTok) num tracker de atribuição multi-tenant, substituindo um fornecedor pago
  - serviço diário de risco e score de crédito de jogador
  - linter multi-tenant que falha fechado: lista de exceções de 43 para 3
  - consulta crítica de 240 s para 21 s, com equivalência provada por conjunto

A maior parte das retificações deste diário nasceu aqui. Os números são reais; os nomes de cliente ficam de fora.
