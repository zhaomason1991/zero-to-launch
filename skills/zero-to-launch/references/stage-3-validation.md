# Stage 3: Phase 0 Behavioral Demand Validation & Kill Gate

## Stage Guardrails (Re-Anchored)
- **Zero Value for Verbal Praise**: Polite compliments ("cool idea, I'd totally buy this!") score **`0`**. Only behavioral cost commitments count.
- **No Illegal / ToS-Violating Fake Checkouts**: Never publish empty "Coming Soon" checkout pages on MoRs that prohibit pre-orders without a working product.
- **Bounded Retries & Pivots**: `validation_retries <= 2`, `validation_pivots <= 1`. Never loop indefinitely.

---

## 1. Elastic Validation Budget Formula

Separate **Active Effort** from **Calendar Wait Window** (waiting for replies/approvals takes calendar days, not active hours):
- **Active Effort Budget**: `min(max(4h, effective_hours * 0.10 to 0.15), 25h)`
- **Calendar Wait Window**: Typically `3–7 days`
- **Cash Budget**: `$0` default, up to `min(cash_budget * 0.10, $150)`

---

## 2. 4-Archetype Behavioral Evidence Matrix

Never force a one-size-fits-all "20 cold interviews" on zero-audience builders. Pick the track matching the candidate:

| Archetype | Valid Behavioral Proof Methods | Valid Commitment Signals (Pass Evidence) |
| :--- | :--- | :--- |
| **Zero-Audience C-Side / Tools / Extensions** | ① 20–30 public pain-archaeology evidence citations (structured summaries, no raw scraped text); ② **Concierge / Wizard-of-Oz** manually serving 3–5 real strangers; ③ High-craft sample output / interactive demo + Waitlist page | Real usage/adoption of manual output, repeat ask for tool launch, real work email + pain detail submitted after interacting with demo |
| **High-Ticket B2B (`b2b-invoice` or `>$50/mo` / `>$300`)** | 5–8 decision-maker **The Mom Test** past-behavior interviews ("How did you solve this last month? What did it cost?") | Sharing sanitized real data/files, booking a pilot onboarding slot, or written LOI/budget confirmation |
| **Free Open Source / CLI (`free-oss`)** | Post an RFC, minimal spec, or short Demo GIF on relevant high-vote open issues / developer forums | Concrete technical feedback, real developers testing a snippet/demo, or explicit interest in adopting once shipped |
| **Internal Tool (`internal-tool`)** | Shadow 2–3 real internal operators + run manual prototype on sanitized historical data | Written sign-off from business/IT owner on data permissions, workflow fit, and adoption commitment |

### Zero-Audience Community Anti-Ban Discipline
When validating in Reddit, IndieHackers, Discord, or niche forums with a low-karma/new account:
- **Never** drop cold promotional links from a brand-new account (triggers AutoModerator removal or domain shadowban).
- Lead with pure-text, standalone value (manual teardowns, concrete solutions); share a prototype/waitlist link only when explicitly asked or in permitted showcase threads/profile bio.

---

## 3. Escape Hatch: "Build-Cheaper-Than-Fake" Isolated Prototype

If the core validation slice can be built in **`<= 6–8 hours`** with **zero production payment/compliance risk** (e.g., a static browser tool or local CLI), you may validate with a disposable prototype instead of fake mockups—strictly under 2 safety rules:
1. **Strict Isolation**: Place the prototype in an isolated folder or throwaway branch (`../<slug>-proto` or `proto` branch). **Never put real production secrets, payment keys, or customer PII in it.**
2. **No Dirty Prototype Straight to Prod**: On Stage 3 `Go`, you MUST choose one of two paths in Stage 4:
   - **Option A (Recommended) — Clean Rewrite**: Build cleanly from `ARCHITECTURE.md` and auto-add a `HUMAN_HANDOFF.md` / `TASKS.md` blocker to **delete the isolated prototype folder/branch** before launch; OR
   - **Option B — Mandatory Hardening Audit**: Convert every missing security/auth/rate-limit/test/error-handling control into explicit `[AI]` blockers in `TASKS.md`.

### Commercial Payment & AUP Self-Check (15 Minutes)
For paid products (`subscription`, `one-time-purchase`, `app-store-iap`, `b2b-invoice`): register and inspect the target MoR/store dashboard **now**—verify developer jurisdiction acceptance, payout method availability, waitlist status, and confirm the product category is **not** banned under current AUP terms.

---

## 4. Pre-Registered Hypothesis Card & 3-Way Diagnostics

**Before** starting outreach or publishing a demo, lock exact numbers in `.zero-to-launch/03-validation-log.md` (prevents moving the goalposts afterward):
- Minimum Valid Sample Size (e.g., `>= 150` qualified demo visitors, or `>= 5` completed B2B interviews);
- Exact `Go` threshold (activation + commitment signal + payment AUP green);
- Exact `Pivot` condition;
- Exact `Kill` floor.

### Deterministic 3-Way Diagnosis
1. **Insufficient Sample (`validation_retries < 2`)**: Distribution test failed, NOT proven dead demand. Switch channel or hook angle, increment `validation_retries + 1`, and retry. If still below min sample after `2` retries → treat as unreachable distribution and trigger **Channel Pivot → Stage 2** (or `Kill` if pivot budget spent).
2. **Demand Proven, Monetization/Channel Blocked (`validation_pivots < 1`)**: Increment `validation_pivots + 1` and return to **Stage 2** for a targeted pricing/channel redesign (max 1 pivot).
3. **Valid Sample Met, Zero Behavioral Commitment (or Pivot Budget Exhausted)**: Trigger **`Kill`** → archive `01..03` into `.zero-to-launch/archive/attempt-NN-<slug>/`, record root cause in `STATE.md` `Killed Hypotheses Graveyard`, increment `attempt_number + 1`, reset stage counters (`redteam_rounds: 0`, `validation_retries: 0`, `validation_pivots: 0`), and return to **Stage 1** (or Stage 0 Relaxation if `>= 2` consecutive dead tracks).
4. **`Go` Met**: Update `STATE.md` (`current_stage: 4`) and advance to [stage-4-spec-and-build.md](./stage-4-spec-and-build.md).

---

## Stage Exit Gate
- [ ] `.zero-to-launch/03-validation-log.md` records pre-registered thresholds, real behavioral evidence (zero verbal-only pass), and payment/AUP check (if paid).
- [ ] If a disposable prototype was used, Rewrite vs Hardening decision is recorded.
- [ ] `STATE.md` updated cleanly (`current_stage: 4` on `Go`, or archived cleanly on `Kill`).
- [ ] Proceed to [stage-4-spec-and-build.md](./stage-4-spec-and-build.md).
