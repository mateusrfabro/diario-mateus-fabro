# Pingado

Sistema de cafeteria: balcão em três toques, comanda, fiado, estoque e resultado do mês.

- **Para quem:** Cafeterias pequenas. A primeira cliente está em produção desde setembro de 2026.
- **Meu papel:** Desenvolvedor e dono do produto: reuniões com a cliente e cada versão entregue em até um dia após a reunião (v0.2 → v0.10).
- **Status:** Em produção desde setembro de 2026
- **Stack:** Flask, SQLAlchemy + Alembic, PostgreSQL (Neon), Redis, Docker, Render
- **Fatos:**
  - 234 commits entre 06/07 e 18/09/2026
  - 772 funções de teste
  - cliente real em produção
  - restauração de backup provada contra Postgres de verdade

O contrato prometia backup; auditar o contrato mostrou que ele não existia. O conserto só contou depois de provado num Postgres de teste igual ao de produção: apaguei 57 vendas, derrubei uma tabela, restaurei, e voltou tudo. Sete semanas depois, trocar de hospedagem invalidou o backup em silêncio — o único arquivo tinha 801 bytes.
