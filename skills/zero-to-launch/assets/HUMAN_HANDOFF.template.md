# {{FILL:project_name}} — Human Handoff Checklist (`HUMAN_HANDOFF`)

> [!CAUTION]
> **NEVER paste plaintext API keys, webhook secrets, database passwords, personal IDs, or bank numbers into this file, source code, Git commits, or chat!**
> Enter secrets ONLY in your local ignored `.env.local` / `.dev.vars` file or your hosting provider's encrypted Secrets UI. Check `[x]` here only to record completion.

<!-- LAUNCH_BLOCKERS_START -->

## Batch 1: Staging Accounts, Hygiene & Sandbox Setup (Complete Once Before Staging Milestone)
- [ ] **H1.1 Employment Hygiene & Local Git Init**: {{FILL:hygiene_and_git_step}}
- [ ] **H1.2 Stage 3 Prototype Cleanup (if applicable)**: {{FILL:proto_cleanup_or_na}}
- [ ] **H1.3 Hosting, DB & Custom Domain Email Setup**: {{FILL:hosting_db_email_step}}
- [ ] **H1.4 Payment Sandbox & Monthly Hard Cost Caps (Disable Auto-Reload)**: {{FILL:payment_and_costcap_step}}

## Batch 2: External Mailbox Proof, Live Credentials & Launch Sign-Off (Complete Once Before Production)
- [ ] **H2.1 External Real Mailbox Delivery Test (Staging)**: {{FILL:external_email_test_or_na}}
- [ ] **H2.2 Production Live Secrets & Spend Alerts (Zero `test_` / `MOCK_*`)**: {{FILL:prod_live_secrets_step}}
- [ ] **H2.3 Legal Pages, Statement Descriptor & Anti-Self-Dealing Approval**: {{FILL:legal_and_launch_approval_step}}

<!-- LAUNCH_BLOCKERS_END -->
