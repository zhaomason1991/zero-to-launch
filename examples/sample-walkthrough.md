# Anonymized End-to-End Walkthrough (`zero-to-launch`)

> **Note**: This walkthrough is a **100% fictional, illustrative scenario** demonstrating how `zero-to-launch` rescues a hyped, high-risk idea and turns it into an executable, compliant, live product specification.

---

## Scenario Setup (Stage 0 Intake)
- **Builder (Fictional)**: Alex, a solo part-time frontend engineer (`10h/week × 10 weeks = 100h` → **`70h effective_hours`** after the 70% realism discount; **`4h/week` post-launch maintenance cap**; **`$400` hard cash cap**; zero social followers; refuses on-camera video and cold calling).
- **Initial Hyped Idea (Track A)**: *"A `$19/mo` Chrome extension that scrapes social profiles and auto-sends AI cold DMs."*

---

## Stage 1 — Anti-Hype Diagnosis & Surgical Pivot
`zero-to-launch` immediately checks live-date realities instead of cheerleading:
- **Fatal Traps Found**:
  1. Target social platform ToS explicitly bans automated scraping & auto-DM (instant user account bans → refund/chargeback cascade).
  2. Chrome Web Store scrutinizes broad `host_permissions` reading logged-in PII.
  3. Scraped bios can inject hostile instructions into unsupervised auto-DMs (Indirect Prompt Injection).
  4. Major MoRs prohibit "automated social media marketing / scraping bots" under Acceptable Use Policies.
  5. Frequent DOM changes violate Alex's `4h/week` part-time maintenance ceiling.
- **3-State Verdict**: `Pivot / Narrow Wedge` — cut scraping and auto-DM entirely; keep the validated pain point (B2B consultants hate paying `$30–$50/mo` subscriptions just to fix robotic AI-sounding outreach drafts).
- **Primary Candidate Selected**: **`BriefLint`** — a zero-scraping, manual-paste B2B outreach linter (free client-side 8-rule instant score + `$29` one-time pack of 200 AI rewrites).

---

## Stage 2 — Multi-Domain Expert Red-Team (V1 `4.83` → V2 `7.38`)
- **V1 Pre-Mortem & Hard Vetoes**:
  - Monthly subscription mismatched episodic outreach buyers (high churn + ARL compliance overhead).
  - Hobby cloud tier prohibited commercial use, and default free DB auto-paused after 7 days with zero backups (`$45/mo` Pro upgrades would blow the `$400` budget).
  - V1 weighted score: **`4.83 / 10` (`FAIL`)** — two hard vetoes `<= 4.0`.
- **V2 Surgical Redesign**:
  - **Cuts**: Removed URL scraping, CRM sync, and monthly subscription billing.
  - **Additions**: Switched to a **commercially-permitted `$0–$5/mo` edge stack** (Cloudflare Workers + Static Assets + D1 with automatic Time Travel backups + Workers AI stateless inference + Resend custom-domain transactional email + compliant individual MoR), `$29` one-time credit pack (~94% net margin), and deterministic client-side linting as a zero-login acquisition wedge.
  - **V2 Weighted Score**: **`7.38 / 10` (`PASS`)** — Demand `7.0` / Acquisition `6.5` (both `>= 5.5`, avg `6.75 >= 6.0`), zero vetoes.
  - Locked `STATE.md` frontmatter enums:
    ```yaml
    product_type: web-saas
    monetization: one-time-purchase
    cross_border: true
    redteam_rounds: 1
    ```

---

## Stage 3 — Phase 0 Behavioral Validation (`Go`)
- **Elastic Budget**: `10h` active effort + `7` calendar days; `$12` cash spent on domain (within `$40` cap).
- **Behavioral Proof (Zero Points for Verbal Praise)**:
  - Concierge manually rewrote 5 real drafts in niche communities (zero-link value first) → 4 adopted immediately.
  - Isolated static prototype (`../brieflint-proto`, zero prod secrets) received 194 targeted visits → 71 real draft checks (36.6% activation) → 14 real work emails clicking `$29 One-Time Early Access` (7.2%).
  - Completed 15-minute MoR AUP self-check in Sandbox.
- **Verdict**: `Go` → choose Clean Rewrite and queue deletion of `../brieflint-proto`.

---

## Stage 4 — Verbatim 6-File Spec Pack & Closed-Loop Build
Running `init_workspace.py --target <PROJECT_DIR> --stage spec` creates `.zero-to-launch/spec/`, frozen with verbatim schemas and DAG-verified tasks:
1. **`RUN_THIS_PLAN.md`**: Standalone manual with 5 Iron Laws (OS-safe commands, anti-reward-hacking `Evidence:` logs, 3-Strike circuit breaker, `<= 2` batched `[STOP-FOR-HUMAN]` stops, self-contained inline Stage 5 gate).
2. **`PRD.md`**: Exact 4 flows, `Explicit Non-Goals`, truthful AI retention disclosure, and GDPR Art. 17 tiered erasure (hard-deletes PII while decoupling statutory accounting records).
3. **`ARCHITECTURE.md`**: Verbatim 7-table D1 SQLite DDL (zero `.down.sql` in `migrations/`), 1:1 PRD-to-API JSON contracts, `GET` page + `POST` verify Magic Link (immune to B2B email scanners), streaming 16KB Body Cap before auth, Cloudflare `period: 60` rate limits, conditional `INSERT ... SELECT ... WHERE credits >= 1`, and symmetric webhook grant + `refund`/`dispute` revocation.
4. **`TASKS.md`**: Atomic `[AI]` tasks inside `<!-- LAUNCH_BLOCKERS_START -->` ... `<!-- LAUNCH_BLOCKERS_END -->` + 2 single-anchor `[HUMAN]` Batch pointers.
5. **`HUMAN_HANDOFF.md`**: Granular non-automatable steps (personal-device hygiene, domain DNS SPF/DKIM/DMARC, Sandbox & Live secrets via CLI — zero plaintext secrets).
6. **`DEPLOY_RUNBOOK.md`**: Staging deploy & load test, non-polluting Production smoke tests, and non-destructive `rollback` / `time-travel restore` commands.

---

## Stage 5 & Stage 6 — Launch Gate & Weekly Growth Loop
- **Stage 5**: `check_launch_gate.py --mode full --json` verifies zero unresolved `{{FILL:...}}`, zero unchecked blockers, zero leaked keys across code & `.zero-to-launch/archive/`, clean Git tracking allowlist, and `.assetsignore`/`.gitignore` packaging exclusion (`exit 0`). External real-mailbox test, Staging rollback dry-run, and live deploy complete.
- **Stage 6**: Passes Day 0 5-Second Above-the-Fold Conversion Audit → Wave 1 72h seed beta to 14 early-access leads → Wave 2 vertical community teardowns → Weekly reconciled unit-economics review (`$86.00` gross from 3 early-bird + 1 full-price order, net `~$80.82` after MoR fees & prorated domain, `2.8h <= 4h` ops) with 1 OMTM and a 6-step Graceful Sunset fallback.
