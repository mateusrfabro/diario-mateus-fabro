# Avisa Edital

Alerta no Telegram quando sai edital ou convocação de saúde no Paraná.

- **Para quem:** Médicos do Paraná que prestaram concurso ou PSS e não podem perder o prazo de uma convocação — em geral de 3 a 5 dias úteis.
- **Meu papel:** Construí sozinho: coletores, bot, site, pagamento e monitoramento. Meu sócio, da área médica, cuida da venda.
- **Status:** No ar desde agosto de 2026
- **Stack:** Python, GitHub Actions, Vercel (funções Python), Upstash Redis, Telegram Bot API, Kiwify (webhook HMAC), pypdf + Tesseract (OCR)
- **Endereço:** https://avisaedital.com.br
- **Fatos:**
  - 182 commits meus entre 12/08 e 21/09/2026, fora 27 automáticos do bot
  - 1.055 funções de teste
  - 192 municípios do PR vigiados em diários oficiais
  - 5 bancas e 8 fontes de convocação (diários municipais, Querido Diário, Secretaria de Saúde e consórcio do SAMU)

Coletar não é publicar. Quando a cobertura cresce, o histórico entra no acervo como se fosse novidade; o alerta passa a notificar pela data do fato, marca os antigos em silêncio e só avisa o que saiu depois — senão o assinante receberia "13 convocações novas", das quais 10 eram de semanas antes.
