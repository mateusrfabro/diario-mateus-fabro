# Nous Clinical

Gestão de clínicas: agenda, prontuário, exames, financeiro e retorno de pacientes.

- **Para quem:** Clínicas de saúde, com separação total de dados entre clínicas.
- **Meu papel:** Desenvolvi de ponta a ponta.
- **Status:** Última versão do produto em 06/10/2026; depois só manutenção do repositório
- **Stack:** Flask, PostgreSQL (Neon), Redis, gunicorn + nginx, Docker, 2FA/TOTP, NFS-e, Anthropic API (chatbot), backup cifrado (age → R2)
- **Fatos:**
  - 197 commits meus entre 05/06 e 05/11/2026, fora 7 automáticos do bot
  - 461 funções de teste
  - 111 rotas
  - auditoria interna de segurança (agentes, bandit e pip-audit) sem achado crítico ou alto (02/07/2026)
  - restauração do backup ainda não testada

Anonimização pelo art. 18 da LGPD que preserva o histórico financeiro, e nota fiscal com descrição genérica — nunca o diagnóstico.
