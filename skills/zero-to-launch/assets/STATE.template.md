---
schema_version: "1.0"
current_stage: 0
attempt_number: 1
product_type: tbd
monetization: tbd
cross_border: tbd
redteam_rounds: 0
validation_retries: 0
validation_pivots: 0
fast_track_override: false
fast_track_unvalidated: false
blocker_retries: {}
---

# Zero-to-Launch Project State (Keep <= 120 Lines)

<!--
MACHINE-READABLE IMMUNITY RULES (DO NOT TRANSLATE YAML KEYS OR ENUMS ABOVE):
- product_type: tbd | web-saas | mobile-app | browser-extension | cli-tool | desktop-app | bot-agent | api-service | digital-asset
- monetization: tbd | subscription | one-time-purchase | app-store-iap | b2b-invoice | ads-affiliate | free-oss | internal-tool
- cross_border: tbd | true | false
- Counters: redteam_rounds (0=V1 initial, 1=V2, 2=V3 max); attempt_number increments ONLY on Stage 2/3 Kill archive (not Stage 1 Pivot).
-->

## 1. Hard Constraints & Frozen Decisions Ledger (<= 12 Bullets)
- **Project Name**: {{FILL:project_name}}
- **North Star Goal**: {{FILL:north_star_goal}}
- **Team & Tech Baseline**: {{FILL:team_and_tech_baseline}}
- **Effective Hours & Ops Cap**: `effective_hours = {{FILL:effective_hours}}h` | `post_launch_hours_per_week = {{FILL:post_launch_hours}}h`
- **Hard Cash Cap**: {{FILL:cash_cap}}
- **Developer Jurisdiction & Eligible Vendors**: {{FILL:jurisdiction_and_vendors}}
- **Psychological / Compliance Red Lines**: {{FILL:red_lines}}
- **Frozen V2 Summary & Non-Goals**: {{FILL:frozen_v2_or_pending}}

## 2. Killed Hypotheses Graveyard & Bench Candidates
- **Killed Hypotheses Graveyard**: {{FILL:none_or_archived_failures}}
- **Bench Candidates**: {{FILL:none_or_bench_list}}

## 3. Current Stage Pointer & Micro-State
- **Last Updated**: {{FILL:YYYY-MM-DD}}
- **Completed Artifacts**: {{FILL:completed_artifacts}}
- **Immediate Next Action**: {{FILL:next_action}}
- **Open `[HUMAN]` Blockers**: {{FILL:none_or_open_human_blockers}}

## 4. Stage Read Matrix (Load Only What Current Stage Needs)
| Stage | Artifact Written | Upstream Files to Read |
| :--- | :--- | :--- |
| 0 — Intake | `00-profile.md` | None |
| 1 — Discovery | `01-opportunity-audit.md` | `00-profile.md` |
| 2 — Red-Team | `02-redteam-report.md` | `00-profile.md`, `01-opportunity-audit.md` |
| 3 — Validation | `03-validation-log.md` | `00-profile.md`, `02-redteam-report.md` |
| 4 — Spec & Build | `spec/*` (6 files) | `00-profile.md`, `02-redteam-report.md`, `03-validation-log.md` (`spec/TASKS.md` is build SSOT) |
| 5 — Launch Gate | `05-launch-signoff.md` | `spec/*` |
| 6 — Growth Ops | `06-ops-playbook.md`, `ops/week-NN.md` | `00-profile.md`, `spec/PRD.md`, `05-launch-signoff.md` |
