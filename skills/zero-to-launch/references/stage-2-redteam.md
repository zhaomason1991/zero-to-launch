# Stage 2: Multi-Domain Expert Red-Team Audit & V2 Reconstruction

## Stage Guardrails (Re-Anchored)
- **Anti-Sycophancy First**: Never rubber-stamp Stage 1's idea. Run an isolated blind subagent if supported, or write a harsh Pre-Mortem **before** scoring.
- **Developer Jurisdiction & Hosting Check**: Verify developer eligibility for chosen LLM APIs, cloud free-tier commercial terms, DB backup/sleep limits, and payment MoRs *now*, not in Stage 4.
- **Max 2 Redesign Rounds (`redteam_rounds <= 2`)**: Never loop forever or inflate scores without concrete cuts/evidence.

---

## 1. Entry Contract: Declare Candidate Enums & Vendor Eligibility

Before summoning experts or scoring, explicitly declare tentative values for the Primary Candidate:
- `product_type` (closed enum)
- `monetization` (closed enum)
- `cross_border` (`true` if serving cross-border public OR cross-border monetization; `false` for `internal-tool` or strictly local free/paid)

**Immediate Upstream Eligibility & Compliance Check**:
- If `cross_border: true`, load [module-cross-border-compliance.md](./module-cross-border-compliance.md) now (Subset A for free cross-border tools; Full Suite for commercial cross-border products).
- Verify as of today's date:
  1. **Developer jurisdiction & card eligibility** for planned LLM APIs (e.g., region-blocked providers), cloud hosts, email providers, and MoRs.
  2. **Commercial terms & fixed monthly infra floor** (e.g., hobby tiers prohibiting commercial SaaS, free DBs with 7-day auto-pause and zero backups, built-in auth SMTP capped at 2 emails/hr). Factor fixed monthly infra costs directly into Dimension 5 unit economics and the Stage 0 cash cap!

---

## 2. Multi-Domain Expert Red-Team & Pre-Mortem Protocol

Dynamically summon **5–7 domain-specific practitioner personas** matching the candidate (e.g., Domain Data/API Engineer, Core Media/Frontend/Platform Specialist, Competitor & Niche Strategist, Minimalist Security & Architecture Lead, Solo Growth Funnel Analyst, Payment/Tax/Legal Compliance Specialist).

**Mandatory Execution Order**:
1. **Blind Subagent or Pre-Mortem**: If subagents are supported, spawn a blind reviewer given ONLY `00-profile.md` + neutral candidate spec (no Stage 1 persuasion). In single-thread runtimes, write a **Pre-Mortem** first: **3 concrete reasons this product hits `$0` / fails within 90 days** + **1 free-incumbent crush scenario**, each backed by live-date checks.
2. **Excavate Unmentioned Practitioner Traps**: Explicitly answer: *"What critical failure modes, API limits, hidden costs, legal landmines, or radically simpler architectures would top practitioners immediately catch that our current V1 completely missed?"*
3. **Cross-Check Every Claim**: Live-verify API CORS/rate/licensing limits, browser/OS constraints, competitor pricing, and AUP prohibitions.

---

## 3. Anchored 6-Dimension Weighted Scorecard (Exact 100% Sum)

Select the weight map matching the candidate's `monetization`:

| # | Commercial Products (`subscription` / `one-time-purchase` / `app-store-iap` / `b2b-invoice` / `ads-affiliate`) | Wt | `free-oss` Remap | `internal-tool` Remap |
| :-: | :--- | :-: | :--- | :--- |
| 1 | **Demand Reality & Pain Urgency** | **25%** | Developer Pain Reality & Urgency (25%) | Internal Pain Urgency & Hours-Saved ROI (30%) |
| 2 | **Cold-Start Acquisition Within Constraints** | **20%** | Community Reach & First-50 Install Path (20%) | Org Adoption Friction & Rollout Feasibility (20%) |
| 3 | **Delivery & Solo Ops Within `effective_hours` & `post_launch_hours`** | **15%** | Delivery Simplicity Within `effective_hours` (15%) | Delivery Simplicity & Maintainability (20%) |
| 4 | **Differentiation & Free-Incumbent Defense** | **15%** | Differentiation & Non-Trivial Value (15%) | Advantage Over Current Workaround / Buy (10%) |
| 5 | **Unit Economics & Monetization Viability** *(net of gateway fees + marginal AI/cloud cost + fixed monthly infra; `one-time-purchase` = AOV × conv × refund; `subscription` = LTV/Churn)* | **15%** | Adoption Compounding & Low Maintenance Burden (15%) | Long-Term Maintenance & Workflow Durability (10%) |
| 6 | **Legal, Compliance, Jurisdiction & Platform Safety** | **10%** | OSS Licensing, Supply-Chain & Registry Compliance (10%) | Enterprise Data Security, ACL & IT Compliance (10%) |

### Anchored Scoring Rubric & Two-Tier Evidence Caps (No Deadlock)
- **`<= 4.0` (Hard Veto)**: Structural fatal flaw (ToS ban, region-blocked core vendor, impossible inside `effective_hours`, free substitute kills WTP, negative net margin, or zero realistic reach).
- **`4.5 – 5.5` (Weak / Unproven)**: High friction or weak differentiation; requires surgical redesign.
- **`6.0 – 7.5` (Solid / Ready to Validate)**: Viable architecture and evidence; primary user behavior still to be tested in Stage 3.
- **`8.0 – 10.0` (Proven Strong)**: Verified hard advantage or direct empirical traction.
- **Tier 1 Cap (`<= 5.0` — Desk/Secondary Facts)**: Missing desk-verifiable facts (competitor pricing, public pain citations, baseline channel viability, vendor jurisdiction/commercial terms) hard-caps that dimension at `<= 5.0`, blocking pass. Offline runtimes unlock via `[HUMAN-VERIFY]` user lookup or explicit user override.
- **Tier 2 Cap (`<= 7.5` — Primary Behavioral Assumptions)**: Assumptions inherently requiring Stage 3 live user tests (exact conversion rate, real buyer commitment) cap at `<= 7.5` (never triggering `<= 5.0` deadlock) and automatically populate Stage 3's mandatory hypothesis card.

### Pass Thresholds (All 3 Must Hold)
1. **Weighted Total `>= 6.5 / 10`**;
2. **Zero Hard Vetoes** (every single dimension `> 4.0`);
3. **Demand / Adoption Composite Floor**: Dimensions 1 and 2 must **each be `>= 5.5`** AND **average `>= 6.0`** (prevents easy-to-code engineering toys from hiding dead demand).

---

## 4. V1 → V2 Surgical Reconstruction & Kill Loop

If V1 fails any threshold:
1. Perform **Ruthless Subtraction** (cut unnecessary DB/Auth/scrapers/heavy features/expensive fixed-cost hosts) + **High-Leverage Addition** (deterministic wedge, simpler billing, zero-login demo, compliant vendor swap).
2. **Anti-Inflation Delta Contract**: Every point gained from V1→V2 must map 1-to-1 to a concrete cut, verified replacement, or new external evidence. Zero points for vague "better marketing/UX".
3. **Core Value Integrity Check**: Verify the stripped V2 still delivers unmistakable paid value over free ChatGPT/incumbents.
4. Increment `redteam_rounds` (`0` = V1 initial, `1` = V2 redesign, `2` = V3 final redesign). Mark superseded V1 sections explicitly obsolete so Stage 4 agents never implement stale specs.
5. **Hard Cap (`redteam_rounds == 2` still fails)**: Archive `01..02` into `.zero-to-launch/archive/attempt-NN-<slug>/`, append a 2-line root-cause epitaph to `Killed Hypotheses Graveyard` in `STATE.md`, increment `attempt_number + 1`, reset `redteam_rounds: 0`, and route:
   - If `< 2` consecutive tracks dead → return to Stage 1 (promote `Bench Candidate #1` or re-run Track B).
   - If `>= 2` consecutive tracks dead → bounce back to **Stage 0 Re-Entry: Constraint Relaxation Mode**.

---

## 5. Fast-Track Lite Red-Team Protocol (Direct Jump to Stage 4)

Used ONLY when the user explicitly skips Stages 0–3 to jump straight into building:
1. Run `PROJECT_DIR` gate + `init_workspace.py --stage init`.
2. Lock `product_type`, `monetization`, `cross_border`, and developer jurisdiction.
3. If `cross_border: true`, immediately run the applicable subset of [module-cross-border-compliance.md](./module-cross-border-compliance.md) + upstream vendor eligibility check.
4. Deliver a crisp **2-minute Lite Red-Team** listing the **Top 3 fatal engineering, commercial, or compliance risks**.
5. Obtain explicit user confirmation, record `fast_track_override: true` (and `fast_track_unvalidated: true` if no external demand evidence exists) in `STATE.md`, and advance to [stage-4-spec-and-build.md](./stage-4-spec-and-build.md).

---

## Stage Exit Gate
- [ ] `.zero-to-launch/02-redteam-report.md` written with Pre-Mortem, expert blind spots, exact weighted scorecard, and frozen V2 architecture/budget/kill criteria.
- [ ] `STATE.md` updated: `product_type`, `monetization`, and `cross_border` **ALL locked non-`tbd`**, `current_stage: 3`.
- [ ] Proceed to [stage-3-validation.md](./stage-3-validation.md).
