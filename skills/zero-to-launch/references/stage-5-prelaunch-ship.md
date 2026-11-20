# Stage 5: DevSecOps Pre-Launch Gate & Production Ship

## Stage Guardrails (Re-Anchored)
- **Non-Waivable Hard Blockers**: Never waive leaked secrets, tracked or unignored `.env*`/`.dev.vars*`, unresolved `tbd` enums, missing `LAUNCH_BLOCKERS` delimiters, unverified payment webhooks, or `anon`-executable Postgres `SECURITY DEFINER` RPCs.
- **Non-Polluting Production Smoke Tests**: Never blast public analytics/funnel endpoints in Production to test rate limits—run load/rate-limit tests on Staging or an isolated test route.
- **Explicit Approval Before Live Deploy**: Present the completed sign-off summary and exact deploy command to the user before pushing to Production.

---

## 1. Execution Modes: Full vs. Standalone

- **Full Mode** (standard Stage 0–4 flow): Run `<python> -B "<SKILL_DIR>/scripts/check_launch_gate.py" --mode full --target "<PROJECT_DIR>" --json` (or execute the inline gate inside `RUN_THIS_PLAN.md` if `<SKILL_DIR>` is unavailable).
- **Standalone Mode** (direct jump onto an existing codebase):
  - **Strictly read-only by default** — do **not** create `.zero-to-launch/` in the user's existing repo.
  - Inspect repo manifests (`package.json`, `wrangler.*`, `manifest.json`, `pyproject.toml`, `LICENSE`, payment SDKs) + confirm `product_type`, `monetization`, and `cross_border` in 1 sentence.
  - Run `check_launch_gate.py --mode standalone --target "<PROJECT_DIR>" --json`, perform the DevSecOps baseline below, and print the sign-off report directly in chat (save to disk only if the user explicitly asks).

---

## 2. Production DevSecOps Baseline (All Products)

1. **Automated Gate Script (`check_launch_gate.py`)**: Must exit `0` (all 5 checks green: SSOT enums, spec/blockers, 5-class secret & prod-`MOCK_*` scan including `.zero-to-launch/archive/`, Git tracking/unignored `.env*`/`.dev.vars*` + `.zero-to-launch/` strict allowlist, and non-Git PaaS/Docker/build-output leak checks).
2. **Ecosystem-Tiered SCA & License Audit**:
   - Node: run built-in `npm audit --omit=dev --audit-level=high` (or `pnpm audit`); verify lockfile committed and zero unaddressed High/Critical CVEs (including known framework floors like Next.js `>=15.2.3`).
   - Python: run `pip-audit` if already installed; **never** silently `pip install` globally—fall back to pinned lockfile review + live CVE lookup on core web/auth/crypto libraries (and recommend GitHub Dependabot). Zero-dependency projects mark `N/A`.
   - Closed-source commercial projects: verify production dependency tree contains **zero unauthorized GPL/AGPL** packages.
3. **Server Security, RPC & Abuse Defense**:
   - Verify server-side AuthZ, IDOR protection, DB RLS/tenant isolation, server-authoritative pricing, and **`REVOKE ALL ... FROM PUBLIC, anon, authenticated` + `SET search_path = ''`** on any Postgres/Supabase `SECURITY DEFINER` RPC.
   - Verify streaming Body Size Cap + trusted-IP/per-user Rate Limiting (not hammering primary DB) + LLM prompt-injection isolation + monthly Cost Caps (confirm Auto-reload disabled / spend pause enabled).
4. **Production Hardening, Custom SMTP & Live-vs-Test Key Check**:
   - Force HTTPS + security headers (`HSTS`, `nosniff`, `DENY`), disable `DEBUG`/stack traces, lock CORS to `APP_URL`, set `HttpOnly + Secure + SameSite` cookies.
   - Confirm Production secrets hold **Live keys** (never `test_`/sandbox) and zero `MOCK_*` flags.
   - If email auth/Magic Link is used: verify **real external mailbox delivery** (non-org email via Custom Domain SPF/DKIM/DMARC, not landing in spam) and verify `GET` does not consume one-time tokens.
5. **Staging, Observability, Backups & Non-Destructive Rollback**:
   - Run full Staging smoke + rate-limit test + rollback dry-run first.
   - Verify basic error alerts/health check, real automated DB backups (confirm no 7-day sleep/zero-backup trap), and non-destructive Production rollback path (app version rollback + maintenance kill-switch + PITR/forward-fix; never `DROP TABLE`).
   - If `cross_border: true`, execute final verification pass against [module-cross-border-compliance.md](./module-cross-border-compliance.md).

---

## 3. Closed-Enum Conditional Launch Checklists

Apply all rows matching the project's `monetization` and `product_type`:

| Archetype | Mandatory Conditional Checks |
| :--- | :--- |
| **`subscription`** | Webhook HMAC byte-length + `timingSafeEqual` verification, symmetric `refund`/`dispute` revocation, transparent auto-renewal disclosure (California ARL), 10-sec self-serve cancel flow, clear Statement Descriptor, `/terms` + `/privacy` + `/refund`, Sandbox checkout + refund test |
| **`one-time-purchase`** | Webhook HMAC verification + symmetric `refund`/`dispute` revocation (tolerant of `user_id IS NULL` after GDPR erasure), visible balance/usage log, EU 14-day digital withdrawal waiver timestamp aligned with commercial refund policy, clear Statement Descriptor, `/terms` + `/privacy` + `/refund` *(do NOT force subscription cancel/Dunning flows!)* |
| **`b2b-invoice`** | Written invoicing/contract/reconciliation workflow (webhook check required only if using an online payment gateway) |
| **`app-store-iap` / `mobile-app`** | Store privacy nutrition labels, in-app AI third-party data disclosure modal, store guideline compliance & account deletion flow |
| **`browser-extension`** | Manifest V3 minimal `host_permissions`, zero remote code execution, strict CSP, single-purpose description & store privacy policy |
| **`bot-agent`** | Platform webhook signature verification, rate/concurrency limits, target platform automation ToS compliance |
| **`ads-affiliate`** | Clear affiliate/advertising disclosure, EU opt-in cookie consent if using ad/tracking cookies |
| **`free-oss` / `cli-tool`** | Valid `LICENSE`, clean cross-platform install & `--help` smoke test, crisp README with quickstart |
| **`internal-tool`** | Org SSO / network ACL verification + written sign-off from IT/business owner |

> **Anti-Self-Dealing Payment Test Warning**: For live payment gateways, **never repeatedly charge and refund your own personal credit card on your own production merchant account** (triggers Self-Dealing / AML account freeze). Validate end-to-end in official Sandbox plus the provider's permitted 100% test coupon or single compliant acceptance flow.

---

## 4. Blocker Escalation & Retry Cap

Track repair retries per blocker in `STATE.md` (`blocker_retries: { rule_id: count }`).
- **Non-Waivable Hard Blockers**: Leaked secrets/credentials, tracked or unignored `.env*`/`.dev.vars*`, `tbd` enums, missing `LAUNCH_BLOCKERS` delimiters, unverified payment webhook, open `SECURITY DEFINER` RPC. **Zero waivers allowed.**
- **Waivable Blockers**: If the same non-hard blocker fails `3` repair rounds, stop looping, present full diagnostics, and require explicit human sign-off with a remediation deadline recorded in `.zero-to-launch/05-launch-signoff.md` (or in chat for Standalone mode).

---

## Stage Exit Gate
- [ ] All Hard Blockers green; Staging smoke & rollback verified; user explicitly approved Production deploy.
- [ ] Production deployed via `DEPLOY_RUNBOOK.md` and non-polluting smoke checks passed.
- [ ] `.zero-to-launch/05-launch-signoff.md` written (Full mode) and `STATE.md` updated to `current_stage: 6`; proceed to [stage-6-growth-ops.md](./stage-6-growth-ops.md).
