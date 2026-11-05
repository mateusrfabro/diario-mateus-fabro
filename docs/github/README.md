# Mateus Fabro — Engenheiro de Dados & Analytics

**Construo o pipeline e o produto em volta dele — Python · SQL · TypeScript · agentes de IA**

🟢 **Em busca de vaga** — Em busca de vaga de engenharia de dados, analytics engineering ou desenvolvimento de produto — PJ ou CLT, remoto. Converso também sobre projeto fechado. O jeito mais rápido é o e-mail.

- Site (projetos, números medidos e retificações): https://mateusfabro.vercel.app
- Currículo: [PT](https://mateusfabro.vercel.app/curriculo/mateus-fabro-pt.pdf) · [EN](https://mateusfabro.vercel.app/curriculo/mateus-fabro-en.pdf)
- LinkedIn: https://www.linkedin.com/in/mateus-fabro-7ba369173
- E-mail: mateusrfabro@hotmail.com

## O que eu faço

- Engenheiro de dados e analytics: projeto, construo e opero sistemas de dados de ponta a ponta — pipelines, antifraude, atribuição de mídia, APIs e painéis — e também o produto em volta do dado, em Python e TypeScript.
- De out/2025 a nov/2026, num squad de dados de 4 pessoas, atendi três operações de iGaming em três países e três moedas e liderei a frente de dados de duas delas, até o encerramento da operação.
- Fora do expediente, construí e opero produtos próprios com cliente real em produção, cobertos por testes e com status honesto — inclusive os que pararam.
- Uso agentes de IA (Claude Code) como multiplicador, com memória em camadas e gates de qualidade próprios; cada erro corrigido vira regra escrita e, quando dá, um teste.

## Projetos

| Projeto | O que é | Status | Código |
|---|---|---|---|
| **Avisa Edital** | Alerta no Telegram quando sai concurso, convocação ou nomeação para médicos no Paraná e em São Paulo. | No ar desde agosto de 2026; operação diária desde outubro | `avisa-edital` (privado) |
| **Pingado** | Sistema de cafeteria: balcão em três toques, comanda, fiado, estoque e resultado do mês. | Em produção desde setembro de 2026, evoluindo com a cliente | `cafesaas` (privado) |
| **Nous Clinical** | Gestão de clínicas: agenda, prontuário, exames, financeiro e retorno de pacientes. | Última versão em 06/10/2026 | [nous-clinical](https://github.com/mateusrfabro/nous-clinical) |
| **Aggron** | Compra cooperativa para hamburguerias: pedidos somados em rodadas e fornecedores disputando o lote. | MVP completo; parado desde 28/05/2026 | [poolcompras](https://github.com/mateusrfabro/poolcompras) |
| **DumpAI** | A IA escolhe as 10 melhores de 30 fotos para um photo dump de Instagram. | No ar; vendas perto de zero | [dumpai](https://github.com/mateusrfabro/dumpai) |
| **Secretária de WhatsApp** | Recepcionista de WhatsApp com agenda real para profissionais autônomos. | Piloto parado na autorização do Google; não completou uma conversa de ponta a ponta com cliente | `secretaria-ia` (privado) |
| **SaaS de crédito (sob NDA)** | Gestão de crédito multi-tenant para operadores pequenos: painel da equipe e portal do tomador como PWA. | Piloto no ar desde outubro de 2026 | `credito-saas` (privado) |
| **Portais de conteúdo com dados oficiais** | Cinco portais estáticos de finanças e direitos, com indicadores que se atualizam sozinhos a partir de fontes oficiais. | No ar desde outubro de 2026; monetização em avaliação | `guiadocredito` (privado) |
| **diario-mateus-fabro** | Portfólio em formato de diário oficial, para pessoas e agentes de IA: site, JSON Resume, llms.txt e servidor MCP de um JSON só | — | [diario-mateus-fabro](https://github.com/mateusrfabro/diario-mateus-fabro) |
| **lab-ia** | Laboratório local de IA: Ollama + PyTorch numa RTX 4060 — agente com ferramentas, QLoRA, ML tabular | — | [lab-ia](https://github.com/mateusrfabro/lab-ia) |

Trabalho anterior: Super Nova Gaming / MultiBet (Grupo PGX), out/2025 – nov/2026 — repositórios privados (dados da empresa).

## Engenharia de agentes

- Squad de 25 agentes Claude Code com papel definido (10 do squad de dados iGaming + 15 gerais: segurança, testes, UX, revisão de conteúdo, growth) e 28 skills próprias (22 globais + 6 do projeto), com gate obrigatório extração → boas práticas → auditoria → entrega e hooks que bloqueiam git destrutivo e commit sem teste.
- Memória em três camadas (projeto → global → export): 125 lições registradas, cada uma com origem, motivo e forma de aplicar, e um script que prova que o índice não esqueceu nenhuma.
- API da Anthropic em produção em dois produtos (IA multimodal no DumpAI; chatbot clínico no Nous Clinical), agente LangChain/n8n na secretária de WhatsApp e laboratório local (Ollama + PyTorch numa RTX 4060) para saber o que roda sem API.

## Como eu trabalho

- **Memória em camadas.** Cada projeto tem um índice de memória com o que é armadilha viva. O que vale para outro projeto sobe para uma memória global: lição com origem, motivo e forma de aplicar.
- **Um gate fecha a promoção.** Promover uma lição é escrevê-la no disco, no índice legível e no índice de máquina. Esse passo falhou duas vezes sem sintoma; hoje um script confere os três e tem um modo que prova que ele sabe ficar vermelho.
- **Mutação como hábito.** 66 dos 716 commits meus no Avisa Edital registram teste de mutação: o defeito é reintroduzido e o teste tem de reprovar antes de o conserto valer.
- **Agentes com papel, não com autonomia.** 15 agentes especializados (qualidade, segurança, testes, UX, revisão de conteúdo, growth) trabalham em paralelo. O que os revisores acham é reproduzido antes de virar mudança.
- **Onde paramos.** Todo projeto tem um arquivo de retomada que a próxima sessão lê primeiro: estado, decisões de quem é dono do negócio e pendências, com data.

_README gerado de `conteudo/dados.json` em 2026-11-05 pelo repositório [diario-mateus-fabro](https://github.com/mateusrfabro/diario-mateus-fabro)._
