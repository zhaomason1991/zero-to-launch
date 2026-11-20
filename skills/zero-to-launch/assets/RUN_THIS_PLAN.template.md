# {{FILL:project_name}} — Autonomous Agent Execution Manual (`RUN_THIS_PLAN`)

> Standalone entry point for ANY AI coding agent (Antigravity, Claude Code, Cursor, Codex, Gemini CLI) — works even if `zero-to-launch` is NOT installed.

## 1. Mandatory Reading Order
1. `RUN_THIS_PLAN.md` (this file: iron laws, cross-machine fallback, inline launch gate)
2. `PRD.md` (exact MVP flows, `Explicit Non-Goals`, privacy/compliance & minimal telemetry)
3. `ARCHITECTURE.md` (verbatim DDL/schemas, 1:1 API/Webhook contracts, middleware order, Local Mock, env-var boundaries, Cost Caps)
4. `TASKS.md` (**Single Source of Truth** for build progress — DAG-verified)
5. `HUMAN_HANDOFF.md` (**Cross-machine `git clone` fallback**: because `HUMAN_HANDOFF.md` is intentionally excluded from Git, if it does not exist after cloning, use `ARCHITECTURE.md`'s env-var table and the `[HUMAN]` Batch pointers in `TASKS.md` to confirm local secrets with the user instead of halting.)
6. `DEPLOY_RUNBOOK.md` (Staging/Production deploy, non-polluting smoke checks, non-destructive rollback)

## 2. Five Iron Laws of Autonomous Execution
1. **OS-Safe Commands & Anti-Slopsquatting**: Follow the OS runtime baseline in `ARCHITECTURE.md` (e.g., on Windows use `npm.cmd` / `npx.cmd` — never weaken Windows PowerShell ExecutionPolicy). Before adding any new dependency, verify package metadata (`npm view <pkg> repository license` or official PyPI) and reject unauthorized GPL/AGPL in closed-source commercial projects. Never run `curl | sh` or `irm | iex`.
2. **Anti-Reward-Hacking Test Evidence**: Never delete, skip, or weaken failing tests, and never hardcode fake passes. Before marking any task `[x]` in `TASKS.md`, execute its verification command and record the exact command, exit code, and output summary under `Evidence:`.
3. **3-Strike Circuit Breaker**: If the same build, test, auth, or webhook failure persists after **3 repair attempts**, STOP immediately. Log all 3 attempts and raw stderr in `TASKS.md`, mark the task `BLOCKED`, and hand off to the human.
4. **`[STOP-FOR-HUMAN]` Topological Batching (`<= 2` Stops)**: Finish all locally mockable `[AI]` milestones before pausing at the batched `[HUMAN]` checkpoints in `TASKS.md`. Never interrupt the user one key at a time.
5. **Cross-Session Resume & Safe Checkpoints**: On every fresh session, read `TASKS.md` (and `git log -n 5` if Git exists) to resume from the first unchecked `[ ]` task. After each passing Milestone, create a local Git checkpoint commit—or if Git is absent, copy ONLY whitelisted source/config folders (NEVER `.zero-to-launch/`, `node_modules/`, `.venv/`, build outputs, or `.env*`/`.dev.vars*`) into `.zero-to-launch/backups/mN/` (rotate max 2 backups; delete before launch). Always terminate locally spawned server process trees cleanly after tests.

## 3. Optional Team Git Allowlist (`.zero-to-launch/.gitignore`)
By default `.zero-to-launch/.gitignore` contains `*` (everything private, safest default). Only if a team deliberately wants to share the 5 secret-free spec files in Git, replace `.zero-to-launch/.gitignore` with this exact 8-line allowlist (never allow `HUMAN_HANDOFF.md`, `STATE.md`, `00..06`, `archive/`, `backups/`, or `ops/`):

```gitignore
*
!.gitignore
!spec/
!spec/RUN_THIS_PLAN.md
!spec/PRD.md
!spec/ARCHITECTURE.md
!spec/TASKS.md
!spec/DEPLOY_RUNBOOK.md
```

## 4. Self-Contained Inline Stage 5 Pre-Launch Gate (No `<SKILL_DIR>` Needed)
Before running Production deploy in `DEPLOY_RUNBOOK.md`, verify EVERY applicable item below (`[HARD]` items may NEVER be waived):

- [ ] **[HARD] Spec & Blocker Completion**: Zero unresolved `{{FILL:...}}` tokens outside code blocks in `spec/`; zero unchecked `[ ]` items between `<!-- LAUNCH_BLOCKERS_START -->` and `<!-- LAUNCH_BLOCKERS_END -->` in `TASKS.md` (and local `HUMAN_HANDOFF.md`).
- [ ] **[HARD] Secret & Env Isolation**: Zero plaintext API keys, PEM private keys, DB passwords, or hardcoded secrets in source/docs/archive; zero server secrets under frontend public prefixes (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`, `PUBLIC_`, `NUXT_PUBLIC_`, `EXPO_PUBLIC_`); `.env*` and `.dev.vars*` are NOT tracked and NOT unignored (`git -c core.quotepath=false ls-files -z` & `git -c core.quotepath=false status --porcelain -z -uall`).
- [ ] **[HARD] Deploy Packaging Isolation**: Zero non-allowlisted `.zero-to-launch/` files in Git; Docker/PaaS ignore config excludes `.zero-to-launch/` and `.env*`/`.dev.vars*`; build output dir (`dist/`/`build/`/`out/`/`.next/static/`) contains no `.zero-to-launch`; `.zero-to-launch/backups/` deleted.
- [ ] **[HARD] Production Safety & Payments**: Zero `MOCK_*` flags or `test_` payment keys in Production; server-side AuthZ/RLS/RPC `REVOKE EXECUTE` verified; streaming Body Cap + trusted-IP Rate Limit + monthly Cost Caps active; webhook signature byte-length + `timingSafeEqual` + symmetric grant & `refund`/`dispute` revocation tested.
- [ ] **SCA & Licenses**: `{{FILL:sca_command}}` shows 0 unaddressed High/Critical CVEs; no unauthorized GPL/AGPL in closed-source commercial deps.
- [ ] **Archetype Compliance & Rollback**: {{FILL:archetype_specific_launch_checks}} (Staging smoke, custom SMTP external mailbox check if email auth is used, and non-destructive rollback verified before live deploy).
