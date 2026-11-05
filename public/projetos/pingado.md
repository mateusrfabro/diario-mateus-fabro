# Pingado

Sistema de cafeteria: balcão em três toques, comanda, fiado, estoque e resultado do mês.

- **Para quem:** Cafeterias pequenas. A primeira cliente está em produção desde setembro de 2026, com duas lojas.
- **Meu papel:** Desenvolvedor e dono do produto: reuniões com a cliente e cada versão entregue em até um dia após a reunião, da v0.2 em diante.
- **Status:** Em produção desde setembro de 2026; cliente com mensalidade contratada
- **Stack:** Flask, SQLAlchemy + Alembic, PostgreSQL (Neon), Redis, Docker, Render
- **Fatos:**
  - 486 commits meus entre 06/07 e 05/11/2026
  - 2.133 funções de teste
  - cliente real com duas lojas em produção
  - NFC-e implementada (Focus NFe); emissão aguarda o credenciamento fiscal da cliente

Balcão não é escritório: login por PIN em vez de senha, venda em poucos toques e botões do tamanho de um dedo. O extrato impresso do fiado também é produto — foi imprimindo o papel de verdade que apareceu o "Seu tem R$ 29,00" (ver retificações).
