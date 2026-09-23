# Dados em iGaming

Pipelines, migração de data lake, antifraude, atribuição de mídia e painéis para três operações em três países.

- **Para quem:** Squad de dados de 4 pessoas de um grupo de iGaming; lidero a frente de dados de duas operações.
- **Meu papel:** Analista de dados desde out/2025, com trabalho de engenharia de ponta a ponta.
- **Status:** Trabalho atual (nomes de empresa e cliente omitidos)
- **Stack:** Python, SQL (PostgreSQL e motores distribuídos), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Fatos:**
  - migração de data lake (3,07 bi de registros, 234 tabelas): camada de conexão com fonte única e rollback por uma variável, preservando a interface dos ~71 pipelines consumidores
  - custo de mídia (Meta, Google Ads, TikTok) num tracker de atribuição multi-tenant, substituindo um fornecedor pago
  - serviço diário de risco e score de crédito de jogador
  - linter multi-tenant que falha fechado: lista de exceções de 43 para 3
  - consulta crítica de 240 s para 21 s, com equivalência provada por conjunto

A maior parte das retificações deste diário nasceu aqui. Os números são reais; os nomes ficam de fora.
