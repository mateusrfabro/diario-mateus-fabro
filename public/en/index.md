# Mateus Fabro — Data & Analytics Engineer

> I build systems that read public sources and production databases and turn them into alerts people can trust. When I get something wrong, I publish the correction — and the mistake becomes a written rule and, whenever possible, a test that enforces it.

Londrina, PR · mateusrfabro@hotmail.com · https://github.com/mateusrfabro · https://www.linkedin.com/in/mateusrfabro

Measured on 2026-11-05. Edition no. 125.

## Summary

I have worked with data in iGaming since October 2025 — three operations, three countries and three currencies. I am the data lead for two of them — pipelines, the consumer layer of a data lake migration, anti-fraud, media attribution and dashboards.

Outside work, I built my own products and run the ones that are live: an alert service for physicians' public-sector job calls (PR and SP), a café management system with a real customer in production, a clinic SaaS, a group-buying platform, an AI photo app, five content portals fed by official data and a credit SaaS under NDA.

I work paired with AI agents (Claude Code) and with a memory system of my own: every fixed mistake that applies to another project becomes a lesson with an origin, a reason and a way to apply it — and a script proves the index forgot none.

## Numbers

- **125** recorded lessons, each with the origin of a real case (source: global memory, global_index.json (107 general + 18 data))
- **1,734** of my commits in 2026, across 8 own products (source: git log of the product repositories, my commits only, excluding automated bot commits)
- **6,357** test functions in the 4 Python products (source: count of def test_ under tests/ in the products with a pytest suite)
- **3** iGaming operations, in 3 countries and 3 currencies (source: Super Nova Gaming, since Oct 2025)
- **3.07 bn** records in the new data lake, which I inventoried while leading the consumer-layer migration (source: Iceberg catalog inventory of 07/23/2026: 234 tables)

## Projects

### Avisa Edital

Telegram alert when a public exam, job call or appointment for physicians is published in Paraná or São Paulo.

- **For whom:** Physicians who sat a public exam or selection process and cannot miss a job-call deadline — usually 3 to 5 business days.
- **My role:** Partner and developer: I built the collectors, bot, site, payments and monitoring alone. The other partner, a physician, handles sales.
- **Status:** Live since August 2026; daily operation since October
- **Stack:** Python, GitHub Actions, Vercel (Python functions), Upstash Redis, Telegram Bot API, Kiwify (HMAC webhook), pypdf + Tesseract (OCR)
- **Address:** https://avisaedital.com.br
- **Facts:**
  - 717 of my commits between 08/12 and 11/05/2026, plus 85 automated bot commits
  - 3,372 test functions
  - PR and SP: municipal and state official gazettes, exam boards and job-call sources, collected on a VM with systemd and complemented by GitHub Actions
  - Kiwify subscription with a 7-day free trial, no card, from the bot itself

Collecting is not publishing. When coverage grows, history enters the archive looking like news; the alert now notifies by the date of the event, silently marks the old ones and only announces what came out afterwards — otherwise a subscriber would get "13 new call-ups", 10 of them weeks old.

### Pingado

Café management: counter sales in three taps, tabs, store credit, stock and the month's results.

- **For whom:** Small cafés. The first customer has been in production since September 2026.
- **My role:** Developer and product owner: meetings with the customer and each version delivered within a day of the meeting, from v0.2 on.
- **Status:** In production since September 2026, evolving with the customer
- **Stack:** Flask, SQLAlchemy + Alembic, PostgreSQL (Neon), Redis, Docker, Render
- **Facts:**
  - 486 of my commits between 07/06 and 11/05/2026
  - 2,133 test functions
  - real customer with two stores in production

A counter is not an office: PIN login instead of a password, a sale in a few taps and buttons sized for a finger. The printed store-credit statement is product too — printing the real paper is what surfaced "Seu tem R$ 29,00" (see corrections).

### Nous Clinical

Clinic management: scheduling, medical records, exams, finance and patient follow-ups.

- **For whom:** Health clinics, with full data separation between clinics.
- **My role:** I led development end to end.
- **Status:** Last product version on 10/06/2026; repository maintenance only since
- **Stack:** Flask, PostgreSQL (Neon), Redis, gunicorn + nginx, Docker, 2FA/TOTP, NFS-e (service invoices), Anthropic API (chatbot), encrypted backup (age → R2)
- **Facts:**
  - 197 of my commits between 06/05 and 11/05/2026, plus 7 automated bot commits
  - 461 test functions
  - 111 routes
  - internal security audit (agents, bandit and pip-audit) with no critical or high finding (07/02/2026)
  - backup restore not yet tested

Anonymization under article 18 of Brazil's data protection law (LGPD) that keeps the financial history, and invoices with a generic description — never the diagnosis.

### Aggron

Group buying for burger restaurants: orders pooled into rounds and suppliers bidding for the lot.

- **For whom:** Burger restaurants in Londrina that buy little alone and well together.
- **My role:** Tech lead and developer, with a partner as product owner.
- **Status:** Complete MVP; paused since 05/28/2026 (repository maintenance only since)
- **Stack:** Flask, PostgreSQL, Telegram Bot API, Docker, contract PDF
- **Facts:**
  - 196 of my commits between 04/14 and 11/05/2026, plus 7 automated bot commits
  - 391 test functions
  - 109 routes
  - origin of the Flask platform that Nous and Pingado reuse

I fixed a cross-customer leak: the round page showed a restaurant the round's totals, and from there another restaurant's order could be deduced by subtraction. Migrations became idempotent after a clean install broke.

### DumpAI

AI picks the best 10 of 30 photos for an Instagram photo dump.

- **For whom:** People who post carousels and lose half an hour choosing photos.
- **My role:** Live the day after the first commit; payments, rate limiting and a security audit within 12 days.
- **Status:** Live; sales close to zero
- **Stack:** Next.js 16, React 19, Tailwind v4, Claude (multimodal), Kiwify, Upstash (rate limit), Vercel
- **Address:** https://dumpai-omega.vercel.app
- **Facts:**
  - 23 of my commits between 06/10 and 11/05/2026
  - live since 06/11/2026
  - images compressed in the browser before upload

The product went live in two days and sales did not come. The lesson was about business, not engineering: the bottleneck was distribution.

### WhatsApp Receptionist

A WhatsApp receptionist with a real calendar for self-employed professionals.

- **For whom:** Psychologists, lawyers and other professionals who work alone.
- **My role:** Architecture and implementation, with a squad of 5 AI agents.
- **Status:** Pilot paused (Google authorization)
- **Stack:** n8n, Evolution API, PostgreSQL 16, Redis 7, LangChain, Google Calendar
- **Facts:**
  - 9 of my commits between 09/16 and 11/05/2026
  - project started on 04/15/2026; first version running locally on 04/27
  - hand-off to a human with a lock on the conversation
  - per-customer configuration in YAML (multi-customer version)
  - never completed an end-to-end conversation with a customer

A customer's configuration field enters the prompt with system privilege — so it is an injection surface: enums, sanitization and explicit negation.

### Credit SaaS (under NDA)

Multi-tenant credit management: a staff panel and a customer portal as a PWA.

- **For whom:** Small credit operations. Business details under a non-disclosure agreement.
- **My role:** End-to-end architecture and implementation, with a partner as product owner.
- **Status:** Pilot live since October 2026
- **Stack:** Next.js 16 + TypeScript, PWA with per-tenant branding, PostgreSQL (Supabase) with per-tenant RLS, GitHub Actions, Docker (e2e in a container), Vercel
- **Facts:**
  - 66 of my commits between 10/13 and 11/05/2026
  - daily backup restored into a throwaway database and checked in CI: row counts, migrations and isolation policies
  - public signup flow with validations and one-click approval

When the OS application control blocked the native password-hashing binary, development moved into a container — and the e2e suite with it.

### Content portals fed by official data

Five static portals on finance and labor rights, with indicators that refresh themselves from official sources.

- **For whom:** Brazilian readers (credit, fixed income, labor rights, dollar finance) and a U.S. audience (personal finance).
- **My role:** Built all five: indicator collection, build, AI-assisted editorial review with human approval, and publication on their own domains.
- **Status:** Live since October 2026; monetization under evaluation
- **Stack:** Astro 7, TypeScript, GitHub Actions, Official APIs, Vercel
- **Address:** https://guiadocredito.com.br
- **Facts:**
  - 40 of my commits between 10/20 and 11/03/2026
  - 33 to 45 guides per portal, each with a primary source
  - indicators recomputed by workflow, never typed in
  - sources: Central Bank/SGS, FRED, IBGE, Treasury, ANP

The first version of one of them carried the photo and credentials of an author who did not exist, generated by AI. They came out before publication: text signed by a person, or unsigned.

### Super Nova Gaming / MultiBet (PGX Group)

Pipelines, data lake migration, anti-fraud, media attribution and dashboards for three operations in three countries.

- **For whom:** Four-person data squad serving three iGaming operations; I was the data lead for two of them.
- **My role:** Data analyst since Oct 2025, with end-to-end engineering work.
- **Status:** Current job
- **Stack:** Python, SQL (PostgreSQL and distributed engines), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Facts:**
  - 1,408 of my commits between 03/12 and 11/04/2026
  - data lake migration (3.07 bn records, 234 tables): a single-source connection layer with one-variable rollback, keeping the interface of the consumer pipelines
  - media cost (Meta, Google Ads, TikTok) in a multi-tenant attribution tracker, replacing a paid vendor
  - daily risk service and a player credit score
  - fail-closed multi-tenant linter: exception list cut from 43 to 3
  - critical query from 240 s to 21 s, with equivalence proven by set comparison

Most of this gazette's corrections were born here. The numbers are real; client names are left out.

## Corrections

Mistakes I made, in the format of a gazette erratum. Each one became a rule.

### RET-2026-0716 — 2026-07-16 — Pingado, printed store-credit statement

- **For:** 347 green tests.
- **Read:** The paper said "Seu tem R$ 29,00 de crédito" (roughly "Mr has … in credit"): the code cut the name at the first space, and at a Brazilian café half the regulars are "Seu" or "Dona" somebody. Only printing the real artifact caught it.
- **Rule that stayed:** Render the artifact the user receives

### RET-2026-0727 — 2026-07-27 — Financial reconciliation

- **For:** 0 duplicate credits.
- **Read:** A UNIQUE constraint made the zero mandatory: the control just repeated the schema. The case that could actually happen was not being measured — and it had candidates.
- **Rule that stayed:** A control with a forced result is not a control

### RET-2026-0728 — 2026-07-28 — Checker for an automated alert

- **For:** 24 green checks: fix validated.
- **Read:** The checker let 3 of 7 reversions of the bug slip through. Since then, every important test is proven by mutation: I revert the fix in a copy and require the suite to go red.
- **Rule that stayed:** Mutation testing: prove the test can fail

### RET-2026-0819 — 2026-08-19 — One exchange with the infrastructure team

- **For:** Six statements, each backed by a query.
- **Read:** Six wrong statements. No query was wrong: in every one, the sentence claimed more than the predicate measured. The person on the other side was right on the detail every single time.
- **Rule that stayed:** The conclusion cannot be wider than the test

### RET-2026-0821 — 2026-08-21 — Avisa Edital, Telegram bot

- **For:** SEO redirect: just domain canonicalization.
- **Read:** The bot's webhook started getting 308 and the bot went silent for 3h30. The API route left the redirect, a test reads the configuration and a sentinel watches for silence.
- **Rule that stayed:** A canonicalization redirect swallows webhooks

### RET-2026-0824 — 2026-08-24 — Avisa Edital, the bot's reply

- **For:** We don't watch your city yet.
- **Read:** We watched 192; production saw 11. The canonical list lived in a git-ignored folder that only existed on my machine.
- **Rule that stayed:** Reference data lives with the code, not in the ignored folder

### RET-2026-0824-B — 2026-08-24 — Avisa Edital, 90-day backfill

- **For:** Backfill in 7-day slices, one per night in the cloud, until complete.
- **Read:** Slices were computed from today, so their edges moved one day per day: 0 of 13 slices in common between two consecutive days. The step timed out without ever saving progress — about 30% of the monthly CI allowance spent on work that could never finish.
- **Rule that stayed:** Progress only persists if its key is stable over time

### RET-2026-0921 — 2026-09-21 — Avisa Edital, per-platform alarm

- **For:** If a gazette platform goes down entirely, the dashboard names it.
- **Read:** The adapter swallowed the failure and returned an empty list: the five cities looked alive, and the alarm would never fire in the one case it was built for. The dashboard also filtered out the platform name. Found in a review of what I myself had shipped four days earlier.
- **Rule that stayed:** An exception path only exists if it is exercised on purpose

### RET-2026-0923 — 2026-09-23 — This site, the day before going live

- **For:** 847 commits across the four products.
- **Read:** 820 of my commits across five products. The four added up to 827 — the 847 included a fifth — and 27 came from the publishing bot. The test that sums the projects caught the first mistake; the fact-check caught the second.
- **Rule that stayed:** A number outside the code ages on its own

## Standing orders (lessons)

20 of the 125 recorded lessons, published here.

1. **Verify before concluding** — Never say "done" without running the check and reading its output. Green applies only to the exact tree tested: editing afterwards voids the run.
2. **Mutation testing: prove the test can fail** — A green test is worth something only if it could be red. Revert the fix in a copy and require the suite to fail.
3. **A control with a forced result is not a control** — Before publishing "0 occurrences", ask whether the number could have been anything other than zero.
4. **The conclusion cannot be wider than the test** — Right query, right number, false sentence. Put the predicate next to the sentence before publishing.
5. **Missing data is not a statement** — An empty list caused by missing coverage becomes "there is nothing" and reassures the person who should act. Separate "there is none" from "I don't know".
6. **A queue is not a delivery, and a delivery is not a view** — Counting the queue table measures what was enqueued, not what happened. As a denominator, it yields a low, plausible number.
7. **Watch the effect, not only the cause** — A cause monitor only catches the failure someone already imagined. An effect monitor is a single one and indifferent to the cause.
8. **A backup only exists if it restores** — A backup never restored is not a backup; a volume or a replica isn't either. Prove the cycle by destroying real data and bringing it back.
9. **Silent fallback on a critical value** — Exchange rate, configuration, version and limits never sit behind a try/except with a default. Failing loudly beats publishing a wrong number.
10. **A number outside the code ages on its own** — Every published number comes out of the code in the same run. Patching a paragraph creates two quantities with the same name.
11. **"New to us" is not "just happened"** — Widening coverage makes history arrive as news. Notify by the date of the event and mark the old ones.
12. **Render the artifact the user receives** — A green suite does not prove the screen or the paper. Render the receipt, PDF or email the person actually gets.
13. **Reference data lives with the code** — A canonical list in a git-ignored folder only exists on the developer's machine; CI and production degrade silently.
14. **Never analyze on the database that serves the customer** — A read query can also take production down. The default is a replica or an analytical database, with an identified session and a timeout.
15. **Don't clear a suspect with a non-discriminating signal** — To claim "not fraud" or "not a regression", run the detector that would find it. A signal the culprit would also show clears no one.
16. **The PII guard is the leak vector** — The list that proves "no personal data in the delivery" is itself personal data. Derive the target at runtime; don't version it.
17. **Environment identity from configuration, not from data** — "Is this production?" is answered by reading the deploy configuration, not by the presence of a row that may have been deleted.
18. **Escapes don't survive the shell** — \b and \n written through a heredoc reach the file as control characters. The terminal hides it; the regex never matches.
19. **A subagent judges against a snapshot** — An agent without live access gets the reasoning right and the fact wrong. In infrastructure that changes weekly, the snapshot ages in days.
20. **Don't rely on AI alone** — Guess before asking for the number. AI speeds things up; the judgment is still mine.

## How I work

- **Layered memory.** Every project has a memory index of its live pitfalls. What applies to another project moves up to a global memory: a lesson with an origin, a reason and a way to apply it.
- **A gate closes the promotion.** Promoting a lesson means writing it to disk, to the human index and to the machine index. That step failed twice without a symptom; today a script checks all three and has a mode that proves it can go red.
- **Mutation as a habit.** 66 of my 717 commits on Avisa Edital record mutation testing: the defect is reintroduced and the test must fail before the fix counts.
- **Agents with a role, not autonomy.** 15 specialized agents (quality, security, testing, UX, content review, growth) work in parallel. What the reviewers find is reproduced before it becomes a change.
- **Where we left off.** Every project has a resume file the next session reads first: state, the business owner's decisions and open items, with dates.

## Availability

I talk about data and product projects, and about roles in data engineering, analytics engineering and product development — contract or full-time, remote. Email is the fastest way.

Contact: mateusrfabro@hotmail.com

## Frequently asked questions

**Who is Mateus Fabro?**

A data and analytics engineer in Londrina, Brazil. He works with data for three iGaming operations and builds his own products: Avisa Edital, Pingado, Nous Clinical, Aggron, DumpAI, WhatsApp Receptionist, five content portals and a credit SaaS under NDA.

**What does he work with?**

Python, SQL and TypeScript: pipelines, data lake migration, anti-fraud, media attribution, Telegram bots and SaaS in Flask and Next.js, with AI agents (Claude Code) as a multiplier.

**What are the corrections on this site?**

Mistakes he made, with dates and numbers, in the format of a gazette erratum: for … read …. Each became a checkable lesson.

**Is he available?**

Open to talking about projects and roles. Contact by email: mateusrfabro@hotmail.com.

## For agents

- MCP server (Streamable HTTP, no auth, read-only; tools and content in Portuguese): https://mateusfabro.vercel.app/mcp
- JSON Resume: https://mateusfabro.vercel.app/resume.json
- Résumé as PDF: https://mateusfabro.vercel.app/curriculo/mateus-fabro-en.pdf
- This text: https://mateusfabro.vercel.app/en/index.md
