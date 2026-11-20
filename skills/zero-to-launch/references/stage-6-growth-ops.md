# Stage 6: Conversion Audit, Staged Cold Start & Weekly Growth Ops

## Stage Guardrails (Re-Anchored)
- **Audit Conversion Surface Before Driving Traffic**: Never waste launch traffic on an unclear landing page or broken store listing.
- **Arithmetic Reconciliation**: Weekly ops reports must mathematically reconcile `Gross Revenue = sum(tier_qty * tier_price)` and deduct gateway fees, marginal AI/cloud costs, AND prorated fixed monthly infra.
- **Feature Freeze on Low Traffic**: Below the minimum traffic sample, freeze new features—only fix P0 crash/auth/payment/conversion blockers and focus 100% on distribution.

---

## 0. Direct-Entry Quick Intake *(Only if jumping straight into Stage 6)*
Collect live URL/package name, `product_type`, `monetization`, `cross_border`, current baseline metrics, and **Explicit Non-Goals**; initialize minimal `STATE.md` + `06-ops-playbook.md` so weekly reviews never reference missing Stage 1–4 docs.

---

## 1. Day 0 Conversion Surface Audit & Telemetry Check

*(For `internal-tool`, skip public conversion pages & chargeback SOPs; audit internal quickstart docs, onboarding friction, and adoption baseline instead.)*

### Conversion Surface Gate (By `product_type`)
- **`web-saas` / `digital-asset`**: 5-Second Above-the-Fold H1 (concrete outcome + target user), zero-login visible Proof (interactive demo, GIF, or before/after sample), single primary CTA, transparent 1–2 tier pricing anchor + refund guarantee, verified OG/Twitter Card + Favicon + mobile viewport.
- **`browser-extension`**: Store hero screenshots, 30s silent demo video, plain-English justification for every permission.
- **`mobile-app`**: First 3 store screenshots showing outcome + paywall clarity + subtitle keywords.
- **`free-oss` / `cli-tool`**: Top-of-README 10-second Demo GIF + 1-line copyable install command + clear problem/solution comparison.

### Minimal Telemetry & Cost Observability Check
Verify live capture of: UTM source links + `1 activation event` + `1 conversion event` + server-side marginal AI/cloud cost logs (cookie-less by default).

---

## 2. Dual-Track Staged Cold Start (Never Blow Every Channel on Day 1)

### Track A — Unscalable First 10 Users Playbook
1. Activate Stage 3 waitlist & interview leads with concise plain-text founder outreach (no heavy HTML newsletters that land in Promotions).
2. Offer white-glove concierge onboarding (15-min async review or manual setup) to the first 5–10 users to capture real friction and authentic testimonials.
3. Follow **Zero-Audience Anti-Ban Rules**: lead with pure-text, standalone help in niche threads; drop product links only when asked or permitted.

### Track B — 3 Staged Launch Waves
- **Wave 1 (Days 1–3 — 72h Seed Beta)**: Release exclusively to seed/waitlist users; watch auth delivery, webhook idempotency, credit deduction, and P0 crashes.
- **Wave 2 (Weeks 1–2 — Vertical Communities)**: High-value teardown posts, Show HN, IndieHackers, niche forums matching Stage 0 psychological red lines.
- **Wave 3 (Weeks 3–4+ — Directories & Compounding Assets)**: Product Hunt (silent GIF/screenshots if no-camera), vertical directories, and compounding transactional tool/comparison SEO pages.

---

## 3. Two-Layer Metrics & Archetype Growth Matrix

### Layer 1: Archetype North-Star Funnel
- **`subscription`**: Qualified Visits → Activation → Trial/Paid Conv → D7/D30 Retention & Monthly Churn.
- **`one-time-purchase`**: Qualified Visits → Activation → Checkout Paid → Top-Up Repeat / Referral Share *(do NOT force monthly SaaS Churn!)*.
- **`browser-extension`**: Store Impressions → Installs → First Core Action → WAU & Uninstall Rate (+ 1-question uninstall survey).
- **`mobile-app`**: Installs → Onboarding Complete → Paywall View → Trial Start → Trial-to-Paid.
- **`free-oss` / `cli-tool`**: Real Package Downloads/Installs → First Successful Run → Repeat Usage / Issues / PRs *(ignore vanity Stars)*.
- **`internal-tool`**: Active Team Adoption % → Weekly Hours Saved ROI → Support Ticket Load.

### Layer 2: Unit Economics Sentinels (Reconciled Weekly)
- `Gross Revenue = sum(tier_orders * tier_price)` (explicitly itemize early-bird discounts).
- `Net Profit = Gross Revenue - Gateway/MoR Fees - Marginal AI/Cloud Cost - Prorated Fixed Monthly Infra`.
- Hard Alerts: Refund Rate `>= 5%` | Chargeback Rate `>= 0.5%` | Weekly Ops Hours `> post_launch_hours_per_week`.

---

## 4. 4-Stage Funnel Bottleneck Tree, Feedback Triage & Weekly Log

### Diagnostic Bottleneck Matrix
1. **Low Traffic** (`< 200 qualified visits / 2 weeks` for mass/prosumer tools; **`< 15–20 decision-maker outreaches` or `< 5 Demos` for high-ticket `b2b-invoice`**) → **Feature Freeze**: ban new feature work; fix only P0 crash/auth/payment/conversion blockers and focus 100% on distribution & hooks.
2. **Low Activation (`< 10–15%`)** → Fix hero promise mismatch, login wall friction, or Time-to-Value (`> 2 min`).
3. **Low Paid Conversion (`< 1–2%`)** → Fix over-generous free tier, weak before/after proof, paywall timing, or price anchor.
4. **High First-Month Churn (`> 10–15%` for `subscription`)** → Evaluate switching from subscription to one-time/credit packs, or fix core delivery quality.

### Feedback Triage Priority & Weekly Rhythm
Rank feedback strictly: `Paying User Stuck > Checkout Drop-off > Power Free User >> Random Passerby Feature Wish`. Reject wishes violating `PRD.md` `Explicit Non-Goals`. Lock **1 OMTM (One Metric That Matters)** and **max 1–2 changes/week**, logged in a concise fixed table at `.zero-to-launch/ops/week-NN.md`.

---

## 5. Anti-Chargeback SOP & Quantitative Tri-State Decision

### Solo Anti-Chargeback & Lifecycle SOP (Decoupled by Monetization)
- **`subscription`**: Verify gateway **Statement Descriptor** matches product name; 10-sec self-serve cancel + 1-question exit reason; 3 plain-text emails (Day 0 welcome, 48h activated-unpaid check-in, failed-payment Dunning); weekly quota/abuse check.
- **`one-time-purchase`**: Verify **Statement Descriptor**; visible refund email & 14-day/EU terms on receipt and `/account`; 2 plain-text emails (receipt + refund link, 48h light feedback check-in — **no cancel/Dunning flows**); weekly usage/dispute check.

### Quantitative Weekly Tri-State Gate
- **`Scale`**: `>= 2` consecutive weeks of positive net margin (after fixed infra), target conversion met, and `>= 1` repeatable acquisition channel working inside `post_launch_hours_per_week`.
- **`Iterate`**: Inside Stage 0 validation time-box with a clear single funnel bottleneck.
- **`Sunset`**: Time-box exhausted (`>= 4` weeks active distribution, minimum valid sample reached, `>= 2` positioning/pricing iterations) with no real paid/retention/adoption signal, **or** unfixable negative marginal unit economics / uncontrollable chargebacks.

### 6-Step Graceful Sunset Checklist (Zero Delayed Chargebacks)
*(For `internal-tool`: send internal sunset & migration notice, export team data, tear down infra.)*
1. Disable new paid checkouts (keep existing user login/read access alive during notice window).
2. Email all active & paid users **14–30 days** in advance with exact shutdown date.
3. **Stop renewals & proactively refund**: for `subscription`, cancel all renewals and refund unused periods; for `one-time-purchase`, proactively refund recent buyers (e.g., last 30 days) or unused credit balances per fair policy to eliminate delayed chargebacks.
4. Provide self-serve data export (CSV/JSON); retain decoupled restricted accounting records strictly for statutory tax/dispute windows.
5. On shutdown date, revoke API keys and tear down all cloud/cron resources to stop zombie billing.
6. Archive reusable assets (domain, clean code modules, learnings) and return to Stage 1 with `00-profile.md` preserved.

---

## Stage Exit Gate (Continuous Ops Loop)
- [ ] `.zero-to-launch/06-ops-playbook.md` created and Day 0 Conversion Surface + Telemetry verified.
- [ ] Weekly review logged in `.zero-to-launch/ops/week-NN.md` with reconciled unit economics, 1 OMTM, and explicit `Scale / Iterate / Sunset` verdict.
