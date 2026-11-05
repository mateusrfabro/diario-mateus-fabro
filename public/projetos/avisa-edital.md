# Avisa Edital

Alertas de convocação, nomeação e edital de concurso para médicos no Paraná e em São Paulo, no WhatsApp ou no Telegram, filtrados por especialidade e região.

- **Para quem:** Médicos que prestaram concurso ou PSS e não podem perder o prazo de uma convocação — em geral de 3 a 5 dias úteis.
- **Meu papel:** Sócio e desenvolvedor: construí sozinho coletores, bot, site, pagamento e monitoramento. O outro sócio, médico, cuida da venda.
- **Status:** No ar desde agosto de 2026; operação diária desde outubro
- **Stack:** Python, WhatsApp (Evolution API), Telegram Bot API, VM com systemd, GitHub Actions, Vercel (funções Python), Upstash Redis, Kiwify (webhook HMAC), pypdf + Tesseract (OCR)
- **Endereço:** https://avisaedital.com.br
- **Fatos:**
  - 717 commits meus entre 12/08 e 05/11/2026, fora 85 automáticos do bot
  - 3.372 funções de teste
  - Diários Oficiais de 213 municípios do PR e 110 de SP, secretarias de saúde, consórcios do SAMU e sites das bancas, lidos todo dia; OCR de atos escaneados
  - Ciclo de venda dentro do bot: teste grátis de 7 dias sem cartão, oferta ao fim do teste, lembrete a cadastro parado, indicação com código e planos pela Kiwify
  - Entrega todo dia por WhatsApp e Telegram, com fila humanizada, trava anti-banimento e sentinela que avisa o operador

Coletar não é publicar. Quando a cobertura cresce, o histórico entra no acervo como se fosse novidade; o alerta passa a notificar pela data do fato, marca os antigos em silêncio e só avisa o que saiu depois — senão o assinante receberia "13 convocações novas", das quais 10 eram de semanas antes.
