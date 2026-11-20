# {{FILL:project_name}} — Atomic Engineering Tasks (`TASKS` — Build SSOT)

> Execute top-to-bottom. **NEVER delete or rename the `LAUNCH_BLOCKERS` delimiters below.**
> DAG Rule: No Milestone may depend on cloud services provisioned in a later `[STOP-FOR-HUMAN]` Batch.
> Single-Anchor Rule: Put granular human setup steps in `HUMAN_HANDOFF.md`; put only 1 summary `[HUMAN]` pointer per Batch here.

<!-- LAUNCH_BLOCKERS_START -->

## Milestone 0: Project Scaffold, Packaging Exclusions & Core Vertical Slice (Local-Only)
- [ ] **T0.1 `[AI]` {{FILL:task_0_1_title}}**
  - Files: {{FILL:task_0_1_files}}
  - Verify: `{{FILL:task_0_1_command}}`
  - DoD: {{FILL:task_0_1_dod}}
  - Evidence: *(Record actual command, exit code, and output summary before checking `[x]`)*

## Milestone 1: Local End-to-End Core Logic, Security Controls & Automated Tests (Local Mocks)
- [ ] **T1.1 `[AI]` {{FILL:task_1_1_title}}**
  - Files: {{FILL:task_1_1_files}}
  - Verify: `{{FILL:task_1_1_command}}`
  - DoD: {{FILL:task_1_1_dod}}
  - Evidence: *(Record actual command, exit code, and output summary)*

## [STOP-FOR-HUMAN] Batch 1: External Accounts, Custom Domain & Staging Sandbox Setup
- [ ] **T2.0 `[HUMAN]` Complete all items in `HUMAN_HANDOFF.md` Batch 1 (Single-Anchor Pointer)**
  - DoD: {{FILL:batch_1_dod}}
  - Evidence: *(Human confirmation recorded)*

## Milestone 2: Staging Deployment, Real Integration Tests, SCA & Rollback Dry-Run
- [ ] **T2.1 `[AI]` {{FILL:task_2_1_title}}**
  - Verify: `{{FILL:task_2_1_command}}`
  - DoD: {{FILL:task_2_1_dod}}
  - Evidence: *(Record actual command, exit code, and output summary)*

## [STOP-FOR-HUMAN] Batch 2: External Mailbox Check, Production Live Secrets & Ship Approval
- [ ] **T3.0 `[HUMAN]` Complete all items in `HUMAN_HANDOFF.md` Batch 2 (Single-Anchor Pointer)**
  - DoD: {{FILL:batch_2_dod}}
  - Evidence: *(Human confirmation recorded)*

## Milestone 3: Production Deploy & Non-Polluting Smoke Verification
- [ ] **T3.1 `[AI]` Execute Production deployment & smoke checks per `DEPLOY_RUNBOOK.md`**
  - Verify: `{{FILL:task_3_1_command}}`
  - DoD: {{FILL:task_3_1_dod}}
  - Evidence: *(Record actual command, exit code, and output summary)*

<!-- LAUNCH_BLOCKERS_END -->

## Post-MVP Backlog (Non-Blocking — Do NOT Build Before Launch)
- [ ] {{FILL:post_mvp_item_1}}
