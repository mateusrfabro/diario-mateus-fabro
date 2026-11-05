# Nous Clinical

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
