# Aggron

Compra cooperativa para hamburguerias: pedidos somados em rodadas e fornecedores disputando o lote.

- **Para quem:** Hamburguerias de Londrina que compram pouco sozinhas e bem juntas.
- **Meu papel:** Tech lead e desenvolvedor, com um sócio como dono do produto.
- **Status:** MVP completo; parado desde 28/05/2026
- **Stack:** Flask, PostgreSQL, Telegram Bot API, Docker, PDF de contrato
- **Fatos:**
  - 194 commits entre 14/04 e 28/05/2026
  - 391 funções de teste
  - 109 rotas
  - origem da plataforma Flask que Nous e Pingado reaproveitam

Corrigi um vazamento entre clientes: a página da rodada mostrava a um restaurante os totais da rodada, e dali dava para deduzir por subtração o pedido de outro. As migrations viraram idempotentes depois de uma instalação limpa quebrar.
