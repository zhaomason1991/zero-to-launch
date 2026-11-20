# Stage 4: Runtime Preflight, Agent-Ready 6-File Spec Pack & Safe Build Loop

## Stage Guardrails (Re-Anchored)
- **Anti-Summarization Rule**: Never write vague prose summaries into `.zero-to-launch/spec/`. Produce verbatim executable DDL/schemas, exact JSON contracts, exact env-var tables, and OS-safe commands so a stranger agent can build without guessing.
- **Zero-Trust Security & Anti-Slopsquatting**: Verify every new dependency (`npm view` / PyPI) before installing; never put server secrets under frontend public prefixes; never skip or weaken failing tests.
- **3-Strike Circuit Breaker**: If the same build/test/auth/webhook error fails 3 consecutive repair attempts, stop immediately, log attempts + stderr, mark `BLOCKED`, and escalate to the user.

---

## Part 0 — Local Runtime Preflight & Managed-Service Production Traps

Before freezing `ARCHITECTURE.md`:
1. **Read-Only Local Runtime Preflight**:
   - Probe installed runtimes and **actual executable package managers**: on Windows check `npm.cmd`/`pnpm.cmd`/`npx.cmd` (never weaken Windows PowerShell ExecutionPolicy!), `py -3`/`python`, `git`, and target deploy CLI (`wrangler`, `vercel`, `flyctl`, etc.).
   - Never specify Docker or heavy local infra for a builder who doesn't have Docker installed.
2. **Managed-Service Production Traps Audit (6 Mandatory Checks)**:
   1. **Commercial Free-Tier Terms & Fixed Monthly Cost**: Check whether the hosting free tier legally permits commercial SaaS (e.g., Vercel Hobby prohibits commercial use; Cloudflare Workers/Pages Free explicitly allows commercial use). Never let hidden fixed monthly bills blow the user's Stage 0 cash cap.
   2. **Database Sleep & Backup Reality**: Reject free DBs that auto-pause after 7 days inactivity with zero backups (e.g., Supabase Free) unless budgeted for Pro; prefer zero-pause DBs with automatic PITR backups (e.g., Cloudflare D1 Time Travel).
   3. **Custom SMTP for Auth/Transactional Email**: Never ship on sandbox/built-in auth SMTP (e.g., Supabase built-in SMTP is capped at 2 emails/hr and org-members only!). Any email login/Magic Link MUST configure a real custom-domain sender (Resend/Postmark + SPF/DKIM/DMARC).
   4. **Developer Jurisdiction + Auto-Reload / Spend Traps**: Confirm the developer's country & payment card are supported by the chosen LLM API & host. In `HUMAN_HANDOFF.md`, explicitly instruct disabling default Auto-Reload where applicable and enabling hard monthly Cost Caps / deployment pause triggers.
   5. **Migration & Non-Destructive Rollback Safety**: **Never** place `.down.sql` inside auto-applied migration folders (e.g., `supabase/migrations/` executes ALL `*.sql`!). **Never** prescribe `DROP TABLE` as a production rollback; production uses forward-fix migrations or PITR backup restore.
   6. **Staging Callback Stability**: Ensure Staging uses a stable callback URL without random preview-auth walls that break OAuth/Magic Link/Webhook verification.

---

## Part A — Initialize & Freeze the 6-File Agent-Ready Spec Pack

1. **Initialize Spec Skeletons Explicitly**:
   ```bash
   <python> -B "<SKILL_DIR>/scripts/init_workspace.py" --target "<PROJECT_DIR>" --stage spec
   ```
2. **Fill ALL 6 Files Verbatim (Zero Remaining `{{FILL:...}}`)**:
   - **`RUN_THIS_PLAN.md`**: Standalone execution contract enabling **any** external coding agent (even without `zero-to-launch` installed!) to build, test, audit, and deploy:
     - Mandatory reading order (including cross-machine `git clone` fallback if `HUMAN_HANDOFF.md` is absent);
     - 5 Iron Laws (OS-safe commands + Anti-Slopsquatting, Anti-Reward-Hacking Test Rule + mandatory `Evidence:` log per `[x]`, 3-Strike circuit breaker, `[STOP-FOR-HUMAN]` batching `<= 2` stops, cross-session resume + checkpoints);
     - Optional 8-line reverse-allowlist `.zero-to-launch/.gitignore` recipe if a team intentionally shares the 5 secret-free `spec/` files via Git;
     - **Self-contained inline Stage 5 launch gate checklist** (no dependency on `<SKILL_DIR>`).
   - **`PRD.md`**: Exact MVP user flows, **Explicit Non-Goals (Do Not Build)**, privacy/GDPR Art. 17 tiered erasure & legal pages (if applicable), and minimal cookie-less telemetry events (`activation` + `conversion` + marginal cost logs).
   - **`ARCHITECTURE.md`**:
     - Exact stack (with CVE patch floors, e.g., Next.js `>=15.2.3` for CVE-2025-29927), directory tree, and mandatory lockfile commitment;
     - **Verbatim Data Schema DDL** + **1:1 PRD↔API Closure** (every UI page/action including account read & logout has an exact route, request/response JSON schema, idempotency key, error codes, and explicit middleware order — e.g., streaming `bodySizeCap` registered BEFORE `requireAuth`);
     - **Cloud Primitive & DB Transaction Bounds**: Verify platform limits before freezing (e.g., Cloudflare `ratelimits` `period` allows ONLY `10` or `60`s; SQLite/D1 `batch()` does NOT roll back on 0-row `UPDATE`, so use conditional `INSERT ... SELECT ... WHERE` to prevent orphan rows);
     - **Auth, RPC, Webhook & LLM Security Rules**:
       - One-time Magic Links/verification links **MUST NOT consume tokens on bare `GET`** (defeats Outlook Safe Links / Proofpoint email scanners); use a lightweight `GET` confirmation page submitting `POST`;
       - Any Postgres/Supabase `SECURITY DEFINER` RPC **MUST** include `SET search_path = ''` AND `REVOKE ALL ON FUNCTION ... FROM PUBLIC, anon, authenticated; GRANT EXECUTE ... TO service_role;`;
       - Payment webhooks **MUST** compare byte lengths before `timingSafeEqual` (preventing 500 `RangeError`), enforce idempotent event IDs, AND handle **both** grant (`checkout.completed`) and symmetric revocation (`refund.created` / `dispute.created`, safely skipping `UPDATE users` when `user_id IS NULL` after GDPR erasure!);
       - LLM endpoints **MUST** isolate untrusted user input (XML delimiters + structured output), use streaming byte-count Body Cap (defeating `Transfer-Encoding: chunked`), enforce platform-trusted IP rate limits (never blind `X-Forwarded-For`, never hammering primary business DB with anonymous events), and couple Rate Limits with monthly Cost Caps;
     - Local Mock/Stub strategy + Production Fail-Closed guard rejecting `MOCK_*=true` or test payment keys in prod;
     - Strict public vs server-only env-var table + non-Git deploy exclusions (`.dockerignore`/`.assetsignore`/`.vercelignore`/`.gitignore`).
   - **`TASKS.md`**: Wrap all launch-blocking tasks between `<!-- LAUNCH_BLOCKERS_START -->` and `<!-- LAUNCH_BLOCKERS_END -->` (never delete delimiters!). Verify **DAG topological order** (no Milestone task may depend on cloud accounts provisioned in a *later* `[STOP-FOR-HUMAN]` Batch!). Use the **Single-Anchor `[HUMAN]` Pointer Pattern**: place only 1 summary `[HUMAN]` pointer per Batch in `TASKS.md` pointing to `HUMAN_HANDOFF.md Batch N`. Include exact files, verification command, DoD, and `Evidence:` slot for every task.
   - **`HUMAN_HANDOFF.md`**: Top `CAUTION` banning plaintext keys/secrets/IDs. Wrap all granular human checklist items inside `<!-- LAUNCH_BLOCKERS_START --> ... <!-- LAUNCH_BLOCKERS_END -->` in `<= 2` Batches (include part-time employer device/network/off-hours hygiene, Cost Cap + Auto-reload disable, and Stage 3 isolated prototype deletion if Rewrite was chosen).
   - **`DEPLOY_RUNBOOK.md`**: Staging deploy & load/rate-limit tests, Production deploy, non-polluting smoke tests using **OS-compatible commands** (**on Windows PowerShell 5.1 NEVER write `curl.exe -d '{"a":"b"}'` because PS 5.1 strips inner double quotes**—use native `Invoke-WebRequest -UseBasicParsing` or Python!), and non-destructive rollback commands.
3. Ask the user to review & freeze the 6-file spec pack before starting code edits.

---

## Part B — Safe Closed-Loop Build Execution

1. **Vertical Slice First**: Get one runnable end-to-end happy path passing tests before polishing secondary UI.
2. **Milestone Checkpoints**: After each Milestone passes its tests:
   - If Git is initialized: make a local checkpoint commit (`checkpoint: mN ...`).
   - If Git is not yet initialized: copy **only whitelisted source/config directories** (NEVER `.zero-to-launch/`, `node_modules/`, `.venv/`, build artifacts, or `.env*`/`.dev.vars*`) into `.zero-to-launch/backups/mN/`, rotating to keep **at most 2 backups**, and delete `backups/` before Stage 5 ship.
3. **Clean Server Lifecycle**: Prefer test runners with managed lifecycles (Vitest, Pytest, Playwright `webServer`). If starting a dev server manually, terminate its full process tree cleanly after checks (Windows: `taskkill /PID <pid> /T /F`; POSIX: kill process group).
4. **Evidence-Backed Progress**: Never mark `[x]` in `TASKS.md` without recording real command output & exit code `0`.

---

## Stage Exit Gate
- [ ] All 6 spec files in `.zero-to-launch/spec/` contain zero `{{FILL:...}}` tokens, pass DAG & PRD↔API closure checks, and all tasks inside `TASKS.md` `LAUNCH_BLOCKERS` have `[x]` + verified `Evidence:`.
- [ ] All `.zero-to-launch/backups/` snapshots cleaned up (if any).
- [ ] `STATE.md` updated to `current_stage: 5`; proceed to [stage-5-prelaunch-ship.md](./stage-5-prelaunch-ship.md).
