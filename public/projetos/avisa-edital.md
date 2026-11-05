# Avisa Edital

Alerta no Telegram quando sai concurso, convocação ou nomeação para médicos no Paraná e em São Paulo.

- **Para quem:** Médicos que prestaram concurso ou PSS e não podem perder o prazo de uma convocação — em geral de 3 a 5 dias úteis.
- **Meu papel:** Sócio e desenvolvedor: construí sozinho coletores, bot, site, pagamento e monitoramento. O outro sócio, médico, cuida da venda.
- **Status:** No ar desde agosto de 2026; operação diária desde outubro
- **Stack:** Python, GitHub Actions, Vercel (funções Python), Upstash Redis, Telegram Bot API, Kiwify (webhook HMAC), pypdf + Tesseract (OCR)
- **Endereço:** https://avisaedital.com.br
- **Fatos:**
  - 717 commits meus entre 12/08 e 05/11/2026, fora 85 automáticos do bot
  - 3.372 funções de teste
  - PR e SP: diários oficiais municipais e estaduais, bancas e fontes de convocação, coletados numa VM com systemd e complementados por GitHub Actions
  - assinatura pela Kiwify com teste grátis de 7 dias sem cartão, pelo próprio bot

Coletar não é publicar. Quando a cobertura cresce, o histórico entra no acervo como se fosse novidade; o alerta passa a notificar pela data do fato, marca os antigos em silêncio e só avisa o que saiu depois — senão o assinante receberia "13 convocações novas", das quais 10 eram de semanas antes.
