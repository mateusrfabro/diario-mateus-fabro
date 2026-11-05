# SaaS de crédito (sob NDA)

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
