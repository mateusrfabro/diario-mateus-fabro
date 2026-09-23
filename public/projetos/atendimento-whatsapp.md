# Secretária de WhatsApp

Recepcionista de WhatsApp com agenda real para profissionais autônomos.

- **Para quem:** Psicólogos, advogados e outros profissionais que atendem sozinhos.
- **Meu papel:** Arquitetura e implementação, com um squad de 5 agentes de IA.
- **Status:** Piloto parado na autorização do Google; não completou uma conversa de ponta a ponta com cliente
- **Stack:** n8n, Evolution API, PostgreSQL 16, Redis 7, LangChain, Google Calendar
- **Fatos:**
  - projeto iniciado em 15/04/2026; primeira versão rodando local em 27/04
  - passagem para humano com trava na conversa
  - configuração por cliente em YAML (versão multi-cliente)

Campo de configuração do cliente entra no prompt com privilégio de sistema — então é superfície de injeção: enum, sanitização e negação explícita.
