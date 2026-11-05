# Mateus Fabro — Engenheiro de Dados & Analytics

> Construo sistemas que leem fontes públicas e bancos de produção e transformam isso em aviso confiável. Quando erro, publico a retificação — e o erro vira uma regra escrita e, sempre que dá, um teste que a cobra.

Londrina, PR · mateusrfabro@hotmail.com · https://github.com/mateusrfabro · https://www.linkedin.com/in/mateus-fabro-7ba369173

Medido em 05/11/2026. Edição nº 125.

## Resumo

Trabalhei com dados em iGaming de outubro de 2025 a novembro de 2026, quando a operação encerrou: três casas, três países e três moedas. Liderei a frente de dados de duas delas — pipelines, a camada de consumo de uma migração de data lake, antifraude, atribuição de mídia e painéis.

Fora do expediente, construí produtos próprios e opero os que estão no ar: um radar de concursos e convocações de saúde (PR e SP), um sistema de cafeteria com cliente real em produção, um SaaS de clínicas, uma plataforma de compra cooperativa, um app de fotos com IA, cinco portais de conteúdo com dados oficiais e um SaaS de crédito sob NDA.

Trabalho em par com agentes de IA (Claude Code) e com um sistema de memória próprio: cada erro corrigido que vale para outro projeto vira uma lição com origem, motivo e forma de aplicar — e um script prova que o índice não esqueceu nenhuma.

## Números

- **125** lições registradas, cada uma com a origem de um caso real (fonte: memória global, global_index.json (84 universais + 17 de dados))
- **1.722** commits meus em 8 produtos próprios, em 2026 (fonte: git log dos repositórios dos produtos, só commits de minha autoria, sem os automáticos de bot)
- **6.357** funções de teste nos 4 produtos em Python (fonte: contagem de def test_ em tests/ dos produtos com suíte pytest)
- **3** operações de iGaming, em 3 países e 3 moedas (fonte: Super Nova Gaming, out/2025 – nov/2026)
- **3,07 bi** registros no data lake novo, que inventariei ao conduzir a migração da camada de consumo (fonte: inventário do catálogo Iceberg de 23/07/2026: 234 tabelas)

## Projetos

### Avisa Edital

Alerta no Telegram quando sai concurso, convocação ou nomeação para médicos no Paraná e em São Paulo.

- **Para quem:** Médicos que prestaram concurso ou PSS e não podem perder o prazo de uma convocação — em geral de 3 a 5 dias úteis.
- **Meu papel:** Construí sozinho: coletores, bot, site, pagamento e monitoramento. Meu sócio, da área médica, cuida da venda.
- **Status:** No ar desde agosto de 2026; operação diária desde outubro
- **Stack:** Python, GitHub Actions, Vercel (funções Python), Upstash Redis, Telegram Bot API, Kiwify (webhook HMAC), pypdf + Tesseract (OCR)
- **Endereço:** https://avisaedital.com.br
- **Fatos:**
  - 716 commits meus entre 12/08 e 05/11/2026, fora 85 automáticos do bot
  - 3.372 funções de teste
  - PR e SP: diários oficiais municipais e estaduais, bancas e fontes de convocação, coletados numa VM com systemd e complementados por GitHub Actions
  - assinatura pela Kiwify com teste grátis de 7 dias sem cartão, pelo próprio bot

Coletar não é publicar. Quando a cobertura cresce, o histórico entra no acervo como se fosse novidade; o alerta passa a notificar pela data do fato, marca os antigos em silêncio e só avisa o que saiu depois — senão o assinante receberia "13 convocações novas", das quais 10 eram de semanas antes.

### Pingado

Sistema de cafeteria: balcão em três toques, comanda, fiado, estoque e resultado do mês.

- **Para quem:** Cafeterias pequenas. A primeira cliente está em produção desde setembro de 2026.
- **Meu papel:** Desenvolvedor e dono do produto: reuniões com a cliente e cada versão entregue em até um dia após a reunião, da v0.2 em diante.
- **Status:** Em produção desde setembro de 2026, evoluindo com a cliente
- **Stack:** Flask, SQLAlchemy + Alembic, PostgreSQL (Neon), Redis, Docker, Render
- **Fatos:**
  - 484 commits meus entre 06/07 e 05/11/2026
  - 2.133 funções de teste
  - cliente real com duas lojas em produção

Balcão não é escritório: login por PIN em vez de senha, venda em poucos toques e botões do tamanho de um dedo. O extrato impresso do fiado também é produto — foi imprimindo o papel de verdade que apareceu o "Seu tem R$ 29,00" (ver retificações).

### Nous Clinical

Gestão de clínicas: agenda, prontuário, exames, financeiro e retorno de pacientes.

- **Para quem:** Clínicas de saúde, com separação total de dados entre clínicas.
- **Meu papel:** Liderei o desenvolvimento de ponta a ponta.
- **Status:** Última versão em 06/10/2026
- **Stack:** Flask, PostgreSQL (Neon), Redis, gunicorn + nginx, Docker, 2FA/TOTP, NFS-e, Anthropic API (chatbot), backup cifrado (age → R2; restauração ainda não testada)
- **Fatos:**
  - 194 commits meus entre 05/06 e 06/10/2026, fora 7 automáticos do bot
  - 461 funções de teste
  - 111 rotas
  - auditoria interna de segurança (agentes, bandit e pip-audit) sem achado crítico ou alto (02/07/2026)

Anonimização pelo art. 18 da LGPD que preserva o histórico financeiro, e nota fiscal com descrição genérica — nunca o diagnóstico.

### Aggron

Compra cooperativa para hamburguerias: pedidos somados em rodadas e fornecedores disputando o lote.

- **Para quem:** Hamburguerias de Londrina que compram pouco sozinhas e bem juntas.
- **Meu papel:** Tech lead e desenvolvedor, com um sócio como dono do produto.
- **Status:** MVP completo; parado desde 28/05/2026
- **Stack:** Flask, PostgreSQL, Telegram Bot API, Docker, PDF de contrato
- **Fatos:**
  - 194 commits meus entre 14/04 e 28/05/2026, fora 7 automáticos do bot
  - 391 funções de teste
  - 109 rotas
  - origem da plataforma Flask que Nous e Pingado reaproveitam

Corrigi um vazamento entre clientes: a página da rodada mostrava a um restaurante os totais da rodada, e dali dava para deduzir por subtração o pedido de outro. As migrations viraram idempotentes depois de uma instalação limpa quebrar.

### DumpAI

A IA escolhe as 10 melhores de 30 fotos para um photo dump de Instagram.

- **Para quem:** Quem posta carrossel e perde meia hora escolhendo foto.
- **Meu papel:** No ar no dia seguinte ao primeiro commit; pagamento, limite de uso e auditoria de segurança em 12 dias.
- **Status:** No ar; vendas perto de zero
- **Stack:** Next.js 16, React 19, Tailwind v4, Claude (multimodal), Kiwify, Upstash (rate limit), Vercel
- **Endereço:** https://dumpai-omega.vercel.app
- **Fatos:**
  - 21 commits meus entre 10/06 e 28/09/2026
  - no ar desde 11/06/2026
  - compressão da imagem no navegador antes do envio

O produto foi ao ar em dois dias e as vendas não vieram. A lição foi de negócio, não de engenharia: o gargalo era distribuição.

### Secretária de WhatsApp

Recepcionista de WhatsApp com agenda real para profissionais autônomos.

- **Para quem:** Psicólogos, advogados e outros profissionais que atendem sozinhos.
- **Meu papel:** Arquitetura e implementação, com um squad de 5 agentes de IA.
- **Status:** Piloto parado na autorização do Google; não completou uma conversa de ponta a ponta com cliente
- **Stack:** n8n, Evolution API, PostgreSQL 16, Redis 7, LangChain, Google Calendar
- **Fatos:**
  - 8 commits meus entre 16/09 e 30/10/2026
  - projeto iniciado em 15/04/2026; primeira versão rodando local em 27/04
  - passagem para humano com trava na conversa
  - configuração por cliente em YAML (versão multi-cliente)

Campo de configuração do cliente entra no prompt com privilégio de sistema — então é superfície de injeção: enum, sanitização e negação explícita.

### SaaS de crédito (sob NDA)

Gestão de crédito multi-tenant para operadores pequenos: painel da equipe e portal do tomador como PWA.

- **Para quem:** Operadores de crédito de pequeno porte. Detalhes de negócio sob acordo de confidencialidade.
- **Meu papel:** Arquitetura e implementação de ponta a ponta, com um sócio como dono do produto.
- **Status:** Piloto no ar desde outubro de 2026
- **Stack:** Next.js 16 + TypeScript, PWA com branding por tenant, PostgreSQL (Supabase) com RLS por tenant, GitHub Actions, Docker (e2e em contêiner), Vercel
- **Fatos:**
  - 65 commits meus entre 13/10 e 28/10/2026
  - backup diário restaurado num banco descartável e conferido em CI: contagens, migrações e políticas de isolamento
  - auto-cadastro público com checagem antifraude e aprovação em um clique

Quando o controle de aplicativos do sistema bloqueou o binário nativo de hash de senha, o ambiente de desenvolvimento foi para um contêiner — e o e2e junto.

### Portais de conteúdo com dados oficiais

Cinco portais estáticos de finanças e direitos, com indicadores que se atualizam sozinhos a partir de fontes oficiais.

- **Para quem:** Leitores brasileiros (crédito, renda fixa, direitos trabalhistas, finanças em dólar) e um público dos EUA (finanças pessoais).
- **Meu papel:** Construí os cinco: coleta dos indicadores, build, revisão editorial assistida por IA com aprovação humana e publicação em domínio próprio.
- **Status:** No ar desde outubro de 2026; monetização em avaliação
- **Stack:** Astro 7, TypeScript, GitHub Actions, APIs oficiais (Banco Central/SGS, FRED, IBGE, Tesouro, ANP), Vercel
- **Endereço:** https://guiadocredito.com.br
- **Fatos:**
  - 40 commits meus entre 20/10 e 03/11/2026
  - 33 a 45 guias por portal, cada um com fonte primária
  - indicadores recalculados por workflow, não digitados

A primeira versão de um deles trazia foto e credenciais de um autor que não existia, geradas por IA. Saíram antes da publicação: texto assinado por pessoa, ou não assinado.

### Super Nova Gaming / MultiBet (Grupo PGX)

Pipelines, migração de data lake, antifraude, atribuição de mídia e painéis para três operações em três países.

- **Para quem:** Squad de dados de 4 pessoas atendendo três operações de iGaming; liderei a frente de dados de duas delas.
- **Meu papel:** Analista de dados de out/2025 a nov/2026, com trabalho de engenharia de ponta a ponta.
- **Status:** Encerrado em nov/2026 (fim da operação)
- **Stack:** Python, SQL (PostgreSQL e motores distribuídos), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Fatos:**
  - 1408 commits meus entre 12/03 e 04/11/2026
  - migração de data lake (3,07 bi de registros, 234 tabelas): camada de conexão com fonte única e rollback por uma variável, preservando a interface dos pipelines consumidores
  - custo de mídia (Meta, Google Ads, TikTok) num tracker de atribuição multi-tenant, substituindo um fornecedor pago
  - serviço diário de risco e score de crédito de jogador
  - linter multi-tenant que falha fechado: lista de exceções de 43 para 3
  - consulta crítica de 240 s para 21 s, com equivalência provada por conjunto

A maior parte das retificações deste diário nasceu aqui. Os números são reais; os nomes de cliente ficam de fora.

## Retificações

Erros que cometi, no formato de retificação de diário oficial. Cada um virou uma regra.

### RET-2026-0716 — 16/07/2026 — Pingado, extrato impresso do fiado

- **Onde se lê:** 347 testes verdes.
- **Leia-se:** O papel dizia "Seu tem R$ 29,00 de crédito": o código cortava o nome no primeiro espaço, e na cafeteria metade da clientela é "Seu" alguma coisa ou "Dona" alguma coisa. Só imprimir o artefato real pegou.
- **Regra que ficou:** Gerar o artefato que o usuário recebe

### RET-2026-0727 — 27/07/2026 — Conciliação financeira

- **Onde se lê:** 0 créditos duplicados.
- **Leia-se:** Uma constraint UNIQUE tornava o zero obrigatório: o controle só repetia o schema. O caso que de fato podia acontecer não estava sendo medido — e tinha candidatos.
- **Regra que ficou:** Controle com resultado forçado não é controle

### RET-2026-0728 — 28/07/2026 — Verificador de um alerta automático

- **Onde se lê:** 24 checagens verdes: correção validada.
- **Leia-se:** O verificador deixou passar 3 de 7 reversões do bug. Desde então, teste importante é provado por mutação: reverto o conserto numa cópia e exijo que a suíte fique vermelha.
- **Regra que ficou:** Teste de mutação: prove que o teste sabe falhar

### RET-2026-0819 — 19/08/2026 — Uma troca com o time de infraestrutura

- **Onde se lê:** Seis afirmações, cada uma com a consulta que a sustentava.
- **Leia-se:** Seis afirmações erradas. Nenhuma query estava errada: em todas, a frase cobria mais do que o predicado media. Quem estava do outro lado tinha razão no detalhe todas as vezes.
- **Regra que ficou:** A conclusão não pode ser mais larga que o teste

### RET-2026-0821 — 21/08/2026 — Avisa Edital, bot do Telegram

- **Onde se lê:** Redirect de SEO: só canonicalização de domínio.
- **Leia-se:** O webhook do bot passou a receber 308 e o bot ficou mudo por 3h30. A rota da API saiu do redirect, um teste lê a configuração e uma sentinela vigia o silêncio.
- **Regra que ficou:** Redirect de canonicalização engole webhook

### RET-2026-0824 — 24/08/2026 — Avisa Edital, resposta do bot

- **Onde se lê:** Ainda não vigiamos sua cidade.
- **Leia-se:** Vigiávamos 192; a produção enxergava 11. A lista canônica morava numa pasta ignorada pelo git, que só existia na minha máquina.
- **Regra que ficou:** Dado de referência mora com o código, não na pasta ignorada

### RET-2026-0824-B — 24/08/2026 — Avisa Edital, busca retroativa de 90 dias

- **Onde se lê:** Retroativo em fatias de 7 dias, uma por noite na nuvem, até completar.
- **Leia-se:** As fatias eram calculadas a partir de hoje, então as bordas andavam um dia por dia: 0 de 13 fatias em comum entre dois dias seguidos. O passo estourava o tempo sem nunca gravar progresso — cerca de 30% da franquia mensal de CI em trabalho que não podia terminar.
- **Regra que ficou:** Progresso só persiste se a chave dele for estável no tempo

### RET-2026-0921 — 21/09/2026 — Avisa Edital, alarme por plataforma

- **Onde se lê:** Se uma plataforma de diário cair inteira, o painel avisa pelo nome.
- **Leia-se:** O adaptador engolia a falha e devolvia lista vazia: as cinco cidades pareciam vivas, e o alarme nunca dispararia no único caso para o qual foi feito. O painel ainda filtrava o nome da plataforma. Achado numa revisão do que eu mesmo tinha entregado quatro dias antes.
- **Regra que ficou:** Caminho de exceção só existe se for exercitado de propósito

### RET-2026-0923 — 23/09/2026 — Este site, na véspera de ir ao ar

- **Onde se lê:** 847 commits nos quatro produtos.
- **Leia-se:** 820 commits meus em cinco produtos. A soma dos quatro dava 827 — os 847 incluíam um quinto — e 27 eram do robô de publicação. O teste que soma os projetos pegou o primeiro erro; a checagem de fatos, o segundo.
- **Regra que ficou:** Número fora do código envelhece sozinho

## Atos (lições)

20 das 125 lições registradas, publicadas aqui.

1. **Verificar antes de concluir** — Nunca dizer "pronto" sem rodar a verificação e ler a saída. O verde vale só para a árvore exata testada: editar depois invalida a rodada.
2. **Teste de mutação: prove que o teste sabe falhar** — Teste verde só vale se pudesse estar vermelho. Reverter o conserto numa cópia e exigir que a suíte reprove.
3. **Controle com resultado forçado não é controle** — Antes de publicar "0 ocorrências", perguntar se o número poderia ser diferente de zero.
4. **A conclusão não pode ser mais larga que o teste** — Query certa, número certo, frase falsa. Colar o predicado ao lado da frase antes de publicar.
5. **Ausência de dado não é afirmação** — Lista vazia por falta de cobertura vira "não há nada" e tranquiliza quem deveria agir. Separar "não há" de "não sei".
6. **Fila não é entrega, e entrega não é visualização** — Contar a tabela de fila mede o que foi enfileirado, não o que aconteceu. Como denominador, produz um número baixo e plausível.
7. **Vigiar o efeito, não só a causa** — Monitor de causa só pega a falha já imaginada. Um monitor de efeito é um só e indiferente à causa.
8. **Backup só existe se restaurar** — Backup nunca restaurado não é backup; volume e réplica também não. Provar o ciclo destruindo dado de verdade e trazendo de volta.
9. **Fallback silencioso em valor crítico** — Câmbio, configuração, versão e limite nunca atrás de try/except com valor padrão. Falhar alto é melhor que publicar número errado.
10. **Número fora do código envelhece sozinho** — Todo número publicado sai do código na mesma rodada. Remendo de parágrafo produz duas grandezas com o mesmo nome.
11. **"Novo para nós" não é "aconteceu agora"** — Ampliar cobertura faz o histórico entrar como novidade. Notificar pela data do evento e marcar os antigos.
12. **Gerar o artefato do usuário** — Suíte verde não prova a tela nem o papel. Renderizar o cupom, o PDF ou o e-mail que a pessoa recebe.
13. **Dado de referência mora com o código** — Lista canônica numa pasta ignorada pelo git só existe na máquina de quem desenvolve; CI e produção degradam calados.
14. **Análise nunca no banco que atende o cliente** — Consulta de leitura também derruba produção. O padrão é réplica ou banco analítico, com sessão identificada e tempo limite.
15. **Não inocentar com sinal que não discrimina** — Para afirmar "não é fraude" ou "não é regressão", rodar o detector que acharia a coisa. Sinal que o culpado também exibiria não absolve.
16. **O guard de PII é o vetor de vazamento** — A lista que prova "sem dado pessoal na entrega" é ela própria dado pessoal. Derivar o alvo em tempo de execução, não versionar.
17. **Identidade de ambiente por configuração, não por dado** — "Isto é produção?" se responde lendo a configuração do deploy, não pela presença de uma linha que pode ter sido apagada.
18. **Escape não atravessa o shell** — \b e \n escritos por heredoc chegam ao arquivo como caractere de controle. O terminal esconde, a regex nunca casa.
19. **Subagente julga contra uma fotografia** — Agente sem acesso ao vivo acerta o raciocínio e erra o fato. Em infraestrutura que muda toda semana, a fotografia envelhece em dias.
20. **Não depender só da IA** — Palpitar antes de pedir o número. A IA acelera; o julgamento continua sendo meu.

## Como trabalho

- **Memória em camadas.** Cada projeto tem um índice de memória com o que é armadilha viva. O que vale para outro projeto sobe para uma memória global: lição com origem, motivo e forma de aplicar.
- **Um gate fecha a promoção.** Promover uma lição é escrevê-la no disco, no índice legível e no índice de máquina. Esse passo falhou duas vezes sem sintoma; hoje um script confere os três e tem um modo que prova que ele sabe ficar vermelho.
- **Mutação como hábito.** 66 dos 716 commits meus no Avisa Edital registram teste de mutação: o defeito é reintroduzido e o teste tem de reprovar antes de o conserto valer.
- **Agentes com papel, não com autonomia.** 15 agentes especializados (qualidade, segurança, testes, UX, revisão de conteúdo, growth) trabalham em paralelo. O que os revisores acham é reproduzido antes de virar mudança.
- **Onde paramos.** Todo projeto tem um arquivo de retomada que a próxima sessão lê primeiro: estado, decisões de quem é dono do negócio e pendências, com data.

## Disponibilidade

Em busca de vaga de engenharia de dados, analytics engineering ou desenvolvimento de produto — PJ ou CLT, remoto. Converso também sobre projeto fechado. O jeito mais rápido é o e-mail.

Contato: mateusrfabro@hotmail.com

## Perguntas frequentes

**Quem é Mateus Fabro?**

Engenheiro de dados e analytics em Londrina (PR). Trabalhou com dados de três operações de iGaming até novembro de 2026 e constrói produtos próprios: Avisa Edital, Pingado, Nous Clinical, Aggron, DumpAI e cinco portais de conteúdo.

**Com o que ele trabalha?**

Python, SQL e TypeScript: pipelines, migração de data lake, antifraude, atribuição de mídia, bots do Telegram e SaaS em Flask e Next.js, com agentes de IA (Claude Code) como multiplicador.

**O que são as retificações deste site?**

Erros que ele cometeu, com data e número, no formato de retificação de diário oficial: onde se lê, leia-se. Cada um virou uma lição verificável.

**Ele está disponível?**

Sim: em busca de vaga, PJ ou CLT, remoto. Contato por e-mail: mateusrfabro@hotmail.com.

## Para agentes

- Servidor MCP (Streamable HTTP, sem autenticação, só leitura): https://mateusfabro.vercel.app/mcp
- Currículo em JSON Resume: https://mateusfabro.vercel.app/resume.json
- Currículo em PDF: https://mateusfabro.vercel.app/curriculo/mateus-fabro-pt.pdf
- Este texto: https://mateusfabro.vercel.app/index.md
