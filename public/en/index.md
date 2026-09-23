# Mateus Fabro — Analytics Engineer

> I build systems that read public sources and production databases and turn them into alerts people can trust. When I get something wrong, I publish the correction — and the mistake becomes a written rule and, whenever possible, a test that enforces it.

Londrina, PR · mateusrfabro@hotmail.com · https://github.com/mateusrfabro · https://www.linkedin.com/in/mateus-fabro-7ba369173

Measured on 2026-09-23. Edition no. 102.

## Summary

I have worked with data in iGaming since October 2025 — today across three operations, three countries and three currencies: pipelines, the consumer layer of a data lake migration, anti-fraud, media attribution and dashboards.

Outside work, I built my own products and run the ones that are live: an alert service for public-health job calls in Paraná, a café management system with a real customer in production, a clinic SaaS, a group-buying platform and an AI photo app.

I work paired with AI agents (Claude Code) and with a memory system of my own: every fixed mistake that applies to another project becomes a lesson with an origin, a reason and a way to apply it — and a script proves the index forgot none.

## Numbers

- **102** recorded lessons, each with the origin of a real case (source: global memory, global_index.json (84 general + 17 data))
- **820** of my commits across five products, in 2026 (source: git log of avisa-edital, pingado, nous-clinical, aggron and dumpai, excluding 27 automated bot commits)
- **2,675** test functions in the four Python products (source: count of def test_ in avisa-edital, pingado, nous-clinical and aggron)
- **3** iGaming operations, in 3 countries and 3 currencies (source: current job, since Oct 2025)
- **3.07 bn** records in the new data lake, which I inventoried while leading the consumer-layer migration (source: 234 tables, ~71 consumer pipelines)

## Projects

### Avisa Edital

A Telegram alert when a public-health job opening or call-up is published in Paraná.

- **For whom:** Doctors in Paraná who passed a public exam and cannot miss the deadline of a call-up — usually 3 to 5 business days.
- **My role:** I built it alone: scrapers, bot, site, payments and monitoring. My partner, from the medical field, handles sales.
- **Status:** Live since August 2026
- **Stack:** Python, GitHub Actions, Vercel (Python functions), Upstash Redis, Telegram Bot API, Kiwify (HMAC webhook), pypdf + Tesseract (OCR)
- **Address:** https://avisaedital.com.br
- **Facts:**
  - 182 of my commits between 08/12 and 09/21/2026, plus 27 automated bot commits
  - 1,055 test functions
  - 192 Paraná municipalities watched in official gazettes
  - 5 exam boards and 8 call-up sources (municipal gazettes, Querido Diário, the State Health Department and the regional ambulance consortium)

Collecting is not publishing. When coverage grows, history enters the archive looking like news; the alert now notifies by the date of the event, silently marks the old ones and only announces what came out afterwards — otherwise a subscriber would get "13 new call-ups", 10 of them weeks old.

### Pingado

Café management: a counter screen in a few taps, tabs, store credit, stock and the month's results.

- **For whom:** Small cafés. The first customer has been in production since September 2026.
- **My role:** Developer and product owner: meetings with the customer and every version delivered within a day of the meeting (v0.2 → v0.10).
- **Status:** In production since September 2026
- **Stack:** Flask, SQLAlchemy + Alembic, PostgreSQL (Neon), Redis, Docker, Render
- **Facts:**
  - 234 commits between 07/06 and 09/18/2026
  - 772 test functions
  - real customer in production

A counter is not an office: PIN login instead of a password, a sale in a few taps and buttons sized for a finger. The printed store-credit statement is product too — printing the real paper is what surfaced "Seu tem R$ 29,00" (see corrections).

### Nous Clinical

Clinic management: scheduling, medical records, exams, finance and patient follow-ups.

- **For whom:** Health clinics, with full data separation between clinics.
- **My role:** I led development end to end.
- **Status:** Last version on 08/26/2026
- **Stack:** Flask, PostgreSQL (Neon), Redis, gunicorn + nginx, Docker, 2FA/TOTP, NFS-e (service invoices), Anthropic API (chatbot), encrypted backup (age → R2; restore not yet tested)
- **Facts:**
  - 190 commits between 06/05 and 08/26/2026
  - 457 test functions
  - 111 routes
  - internal security audit (agents, bandit and pip-audit) with no critical or high finding (07/02/2026)

Anonymization under article 18 of Brazil's data protection law (LGPD) that keeps the financial history, and invoices with a generic description — never the diagnosis.

### Aggron

Group buying for burger restaurants: orders pooled into rounds and suppliers bidding for the lot.

- **For whom:** Burger restaurants in Londrina that buy little alone and well together.
- **My role:** Tech lead and developer, with a partner as product owner.
- **Status:** Complete MVP; paused since 05/28/2026
- **Stack:** Flask, PostgreSQL, Telegram Bot API, Docker, contract PDF
- **Facts:**
  - 194 commits between 04/14 and 05/28/2026
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
  - 20 commits between 06/10 and 06/22/2026
  - live since 06/11/2026
  - images compressed in the browser before upload

The product went live in two days and sales did not come. The lesson was about business, not engineering: the bottleneck was distribution.

### WhatsApp Receptionist

A WhatsApp receptionist with a real calendar for self-employed professionals.

- **For whom:** Psychologists, lawyers and other professionals who work alone.
- **My role:** Architecture and implementation, with a squad of 5 AI agents.
- **Status:** Pilot paused at Google authorization; never completed an end-to-end conversation with a customer
- **Stack:** n8n, Evolution API, PostgreSQL 16, Redis 7, LangChain, Google Calendar
- **Facts:**
  - project started on 04/15/2026; first version running locally on 04/27
  - hand-off to a human with a lock on the conversation
  - per-customer configuration in YAML (multi-customer version)

A customer's configuration field enters the prompt with system privilege — so it is an injection surface: enums, sanitization and explicit negation.

### Data in iGaming

Pipelines, data lake migration, anti-fraud, media attribution and dashboards for three operations in three countries.

- **For whom:** A 4-person data squad at an iGaming group; I lead the data front for two operations.
- **My role:** Data analyst since Oct 2025, doing end-to-end engineering work.
- **Status:** Current job (company and client names omitted)
- **Stack:** Python, SQL (PostgreSQL and distributed engines), AWS, NestJS + Next.js, systemd, Slack / Telegram / WhatsApp
- **Facts:**
  - data lake migration (3.07 bn records, 234 tables): a single-source connection layer with one-variable rollback, keeping the interface of ~71 consumer pipelines
  - media cost (Meta, Google Ads, TikTok) in a multi-tenant attribution tracker, replacing a paid vendor
  - daily risk service and a player credit score
  - fail-closed multi-tenant linter: exception list cut from 43 to 3
  - critical query from 240 s to 21 s, with equivalence proven by set comparison

Several of this gazette's corrections were born here. The lessons are public; the company's numbers are not.

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

20 of the 102 recorded lessons, published here.

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
- **Mutation as a habit.** 53 of my 182 commits on Avisa Edital record mutation testing: the defect is reintroduced and the test must fail before the fix counts.
- **Agents with a role, not autonomy.** 15 specialized agents (quality, security, testing, UX, content review, growth) work in parallel. What the reviewers find is reproduced before it becomes a change.
- **Where we left off.** Every project has a resume file the next session reads first: state, the business owner's decisions and open items, with dates.

## Availability

Happy to talk about data and product projects, and about data engineering and analytics engineering roles. Email is the fastest way.

Contact: mateusrfabro@hotmail.com

## Frequently asked questions

**Who is Mateus Fabro?**

An analytics engineer in Londrina, Brazil. He works with data for three iGaming operations and builds his own products: Avisa Edital, Pingado, Nous Clinical, Aggron and DumpAI.

**What does he work with?**

Python, SQL and TypeScript: pipelines, data lake migration, anti-fraud, media attribution, Telegram bots and SaaS in Flask and Next.js, with AI agents (Claude Code) as a multiplier.

**What are the corrections on this site?**

Mistakes he made, with dates and numbers, in the format of a gazette erratum: for … read …. Each became a checkable lesson.

**Is he available?**

Open to talking about projects and roles. Contact by email: mateusrfabro@hotmail.com.

## For agents

- MCP server (Streamable HTTP, no auth, read-only; tools and content in Portuguese): https://mateusfabro.vercel.app/mcp
- JSON Resume: https://mateusfabro.vercel.app/resume.json
- This text: https://mateusfabro.vercel.app/en/index.md
