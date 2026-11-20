# Stage 0: User Profile & Hard Constraints Intake

## Stage Guardrails (Re-Anchored)
- **Atomic 1-at-a-Time Questions**: Ask exactly ONE focused decision per turn. Never dump a multi-question survey.
- **No Premature Writes**: Complete intake and confirm a valid `PROJECT_DIR` before invoking `init_workspace.py --stage init`.
- **Language Mirroring + Enum Immunity**: Speak and write prose in the user's language; keep `STATE.md` YAML frontmatter strictly English enums.

---

## 1. Conditional Branching Decision Tree (4–7 Atomic Steps)

Walk top-down, skipping irrelevant branches automatically. Offer 3–4 crisp options (with a recommended default where appropriate) plus open custom input.

### Q1 — North Star & Commercial Master Switch
Identify the primary goal and preset monetization where obvious:
1. **Direct Revenue** (side-income cashflow or commercial SaaS) → `monetization: tbd`
2. **Open-Source / Portfolio / Developer Credibility** → `monetization: free-oss`
3. **Free Traffic Magnet / Ad or Affiliate Tool** → `monetization: ads-affiliate` (or `tbd`)
4. **Internal Team / Personal Productivity Tool** → `monetization: internal-tool`, `cross_border: false` (skips Q6 & Q7)

### Q2 — Team Topology, Technical Baseline & Employment Hygiene
Use compact preset cards (e.g., *Solo part-time + AI-assisted no-code*, *Solo part-time + frontend/full-stack dev*, *Solo full-time builder*, *2–3 person complementary team*) and capture two critical realities:
- Hands-on coding & ops baseline (no-code / can edit & debug / production full-stack).
- If employed part-time: **employer IP/non-compete boundary**, **daytime incident SLA limit** (cannot take calls or fix live outages during work hours), and strict **device/network/account/off-hours hygiene**.

### Q3 — Hard Cash Cap, Effective Pre-Launch Hours & Post-Launch Ops Ceiling
Use preset cards + exact numbers:
- Hard cash budget ceiling (e.g., `$0`, `$100–$500`, `$500–$2,000`, `>$2,000`).
- Pre-launch time window: `total_project_hours = weekly_hours * weeks`. Automatically compute realistic **`effective_hours = round(total_project_hours * 0.70)`** (30% buffer for debugging, approvals, and life interruptions) and anchor all Stage 1–3 sizing to `effective_hours`.
- **Sustainable post-launch maintenance cap** (`post_launch_hours_per_week`): prevents shipping high-maintenance scrapers or support-heavy products that collapse after Week 2.

### Q4 — Unfair Advantages & Zero-Cost Distribution Assets
Dig past self-described weaknesses ("I don't know marketing") to uncover real leverage:
- Domain/workflow intuition, UI/visual taste, product/MRD structuring, niche technical skills.
- **Existing zero-cost reach assets**: niche communities, email list, social audience, client network, or existing traffic.

### Q5 — Acquisition & Interaction Psychological Red Lines
Clarify what the user **refuses** to do (so Stage 1/3/6 never prescribe unexecutable channels):
- On-camera short video, cold calling / live Zoom sales demos, heavy daily social posting, real-time customer support, etc.

### Q6 — Audience Geography & Developer Jurisdiction *(Skip only for `internal-tool`)*
Collect two facts cleanly:
1. **Target Audience Geography**: Local-only (`cross_border: false`), global / cross-border public (`cross_border: true`), or undecided (`cross_border: tbd`, locked by Stage 2 exit).
2. **Developer Jurisdiction, Entity & Payment Cards**: Country/region of residence, individual vs registered company, available bank/payment cards — required in Stage 2/4 to verify upstream LLM API, cloud host, email provider, and payment gateway eligibility!

### Q7 — Payback Urgency & Compliance/Payout Red Lines *(Ask ONLY if Q1 = Direct Revenue)*
- Cashflow urgency (fast validation within 4–12 weeks vs long-term compounding).
- Legal, tax, and payout boundaries (strict white-hat compliance, local payout vs offshore retention, prohibited verticals).

---

## 2. Project Directory Gate & Workspace Bootstrap

Before writing any file:
1. Verify `PROJECT_DIR` is NOT a filesystem root, home directory (`~`), OS system directory, AI config directory (`~/.gemini`, `~/.claude`, `~/.cursor`, `~/.codex`), `SKILL_DIR`, or an unrelated Git repository lacking `.zero-to-launch/`.
2. If invalid or empty workspace for a brand-new idea, ask the user to confirm a dedicated project directory (e.g., `./my-product/`).
3. Run workspace initialization (using the verified Python 3.9+ binary):
   ```bash
   <python> -B "<SKILL_DIR>/scripts/init_workspace.py" --target "<PROJECT_DIR>" --stage init
   ```
   *(If Python is unavailable, manually create `.zero-to-launch/`, `.zero-to-launch/ops/`, `.zero-to-launch/.gitignore` containing `*`, and copy `assets/STATE.template.md`.)*
4. Write `.zero-to-launch/00-profile.md` (clean structured summary of Q1–Q7) and populate `.zero-to-launch/STATE.md` (`current_stage: 1`, `attempt_number: 1`, resolved enums or `tbd`, plus concise Constraints Ledger).

---

## 3. Re-Entry: Constraint Relaxation Mode

Triggered automatically when **2 consecutive tracks die in Stage 2** (`Killed Hypotheses Graveyard` has `>= 2` failed tracks).
- **Do NOT re-ask Q1–Q7.**
- Display `00-profile.md` constraints side-by-side with the shared failure bottleneck across the dead tracks (e.g., *"zero budget + zero audience + <30h + refusal of any active outreach + revenue target $3,000/mo in 60 days"*).
- Ask **one focused question** asking the user which **1 constraint** to relax (timeline, revenue target, acquisition red line, budget, or product scope), update `00-profile.md` & `STATE.md`, and return to Stage 1.

---

## Stage Exit Gate
- [ ] `00-profile.md` written with `effective_hours` (`70%` discount), `post_launch_hours_per_week`, distribution assets, psychological red lines, and (if non-internal) audience geography + developer jurisdiction.
- [ ] `.zero-to-launch/.gitignore` (`*`) exists and protects private profile files.
- [ ] `STATE.md` updated with valid English YAML frontmatter (`current_stage: 1`) and `<= 120` lines.
- [ ] Proceed to [stage-1-opportunity.md](./stage-1-opportunity.md).
