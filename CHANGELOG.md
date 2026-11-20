# Changelog

All notable changes to `zero-to-launch` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-20

### Added
- **Cross-Platform Open Agent Skill (`skills/zero-to-launch/SKILL.md`)**: Fully compliant with the `agentskills.io` specification and Antigravity `plugin.json` manifest; supports Antigravity, Claude Code, Cursor, Codex CLI, and Gemini CLI with automatic user-language mirroring and untranslated machine-readable YAML frontmatter.
- **7-Stage Closed-Loop Product Launch Methodology (`references/`)**:
  - `stage-0-intake.md`: Conditional 4–7 atomic-question decision tree covering North Star, team/tech baseline, 70% effective pre-launch hours, post-launch ops ceiling, existing reach assets, audience geography, developer jurisdiction, and Re-Entry Constraint Relaxation mode.
  - `stage-1-opportunity.md`: Dual-entry opportunity discovery (Track A anti-hype diagnosis + Track B 4-step Anti-Slop money-trail discovery), balanced `Fail vs. Viable Wedge` acquisition matrix, offline anti-fabrication rule, and Primary + Bench convergence.
  - `stage-2-redteam.md`: Blind subagent / Pre-Mortem anti-sycophancy red-teaming, 3 full 100%-sum 6-dimension scorecards (`commercial`, `free-oss`, `internal-tool`), two-tier evidence caps (`<=5.0` desk facts / `<=7.5` primary assumptions), demand-side composite floor, max 2 redesign rounds, and Fast-Track Lite Red-Team protocol.
  - `stage-3-validation.md`: 4-archetype Behavioral Evidence Matrix (zero points for verbal praise), elastic effort/cash budgets, Build-Cheaper-Than-Fake isolated prototype rules, and bounded 3-way Go / Pivot / Kill diagnostics.
  - `stage-4-spec-and-build.md`: Runtime Preflight, 6 Managed-Service Production Traps audit, verbatim Anti-Summarization 6-file Agent-Ready Spec Pack (`RUN_THIS_PLAN.md`, `PRD.md`, `ARCHITECTURE.md`, `TASKS.md`, `HUMAN_HANDOFF.md`, `DEPLOY_RUNBOOK.md`) with 1:1 PRD-to-API closure, DAG verification, single-anchor `[HUMAN]` pointers, 3-Strike circuit breaker, and Safe Build Loop.
  - `stage-5-prelaunch-ship.md`: Full & read-only Standalone pre-launch DevSecOps gates covering SCA, Postgres `SECURITY DEFINER` RPC lockdown, streaming Body Cap, trusted-IP rate limits, Custom SMTP verification, non-polluting smoke tests, non-destructive rollbacks, and closed-enum checklists.
  - `stage-6-growth-ops.md`: Day 0 Conversion Surface Audit, First 10 Users manual playbook + 3 staged launch waves, arithmetically reconciled two-layer unit economics, Feature Freeze low-traffic rule, quantitative `Scale / Iterate / Sunset` gates, and 6-step Graceful Sunset SOP.
  - `module-cross-border-compliance.md`: On-demand live-date checklist covering developer jurisdiction eligibility, truthful AI retention disclosures, GDPR Art. 17 tiered erasure, MoR indirect vs. direct tax boundaries, Form 5472 / AML traps, and OSS copyleft audits.
- **Zero-Dependency Python 3.9+ Helper Scripts (`scripts/`)**:
  - `init_workspace.py`: Atomic workspace initializer (`--stage init|spec|all`) with strict exact-vs-subtree cross-platform path guards and Secure-by-Default `.zero-to-launch/.gitignore` (`*`).
  - `check_launch_gate.py`: Fail-Closed pre-launch gate (`--mode full|standalone`, `--json`) scanning SSOT enums, `LAUNCH_BLOCKERS` delimiters, 5 secret classes across `.env*`/`.dev.vars*`/source/`archive/`, Git allowlist tracking, and Docker/PaaS/build-output packaging isolation without printing plaintext secrets.
- **Automated Quality & Security CI**: Self-contained `scripts/validate_repo.py` and 4-matrix GitHub Actions workflow (`ubuntu-latest` / `windows-latest` × Python `3.9` / `3.12`) with 40-char SHA-pinned official actions.
