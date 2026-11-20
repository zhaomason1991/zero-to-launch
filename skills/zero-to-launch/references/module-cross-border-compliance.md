# On-Demand Specialist Module: Cross-Border Compliance, Privacy & Monetization Audit

> **MANDATORY DISCLAIMER — NOT LEGAL, TAX, OR FINANCIAL ADVICE**
> This module provides operational risk checklists and live-verification prompts only. It does **not** constitute legal, tax, accounting, or regulatory advice. **Mandatory Escalation to a Licensed Lawyer or CPA** is required before: incorporating any offshore company, approaching foreign tax-nexus thresholds, operating in regulated sectors (healthcare, financial/investment advice, gambling, minors, crypto custody), or filing home-country global income / foreign-exchange tax declarations.

## Activation & Two-Tier Scoping
Triggered whenever `cross_border: true` (serving cross-border public **OR** cross-border monetization) across **Stages 2, 3, 4, and 5**:
- **Subset A (Free Cross-Border Products — `free-oss`, free tools)**: Modules **1, 2, 5, 6** (Developer Jurisdiction Eligibility, Global Privacy/GDPR, Upstream API/OSS Licenses, Consumer/OFAC).
- **Full Suite (Commercial Cross-Border Products — `subscription`, `one-time-purchase`, `app-store-iap`, `b2b-invoice`, `ads-affiliate`)**: Modules **1 through 6**.

> **LIVE-DATE VERIFICATION RULE**: Payment gateways, AUP lists, tax thresholds, and API region lists change abruptly. Always verify every item below **as of today's real date** via live search. If offline, emit a blocking `[HUMAN-VERIFY]` card with official URLs/queries—never pass compliance from stale model memory.

---

## Module 1 — Developer Jurisdiction & Upstream Vendor Eligibility *(Check in Stage 2 & Stage 4)*
Verify whether the **developer's country of residence, legal entity (individual vs company), and payment cards** are legally supported by EVERY planned upstream provider:
1. **LLM / AI API Providers**: Verify official Supported Countries & billing card acceptance (e.g., do not prescribe direct native OpenAI/Anthropic billing for developers residing in unsupported regions; route to legally supported commercial providers such as Cloudflare Workers AI or locally accessible commercial APIs). Never recommend ToS-violating proxy/fake-card workarounds.
2. **Cloud Hosting, DB & Email**: Verify commercial free/paid tier eligibility and payment card acceptance.
3. **Payment MoR / Storefront**: Verify current-date individual KYC support (passport vs national ID) and local payout channel legality.

---

## Module 2 — Global Privacy, Truthful AI Disclosure & GDPR Art. 17 Tiered Erasure *(Stages 2, 4, 5)*
1. **Privacy Policy Essentials (GDPR / UK GDPR / CCPA-CPRA)**:
   - Enumerate exact data collected, retention periods, third-party Sub-processors (host, DB, AI, email, MoR), cross-border transfer basis, and a monitored privacy contact email.
   - **Truthful AI Retention Disclosure**: Clearly distinguish **"API inputs not used for model training by default"** from **"vendor 7–30 day abuse-monitoring logs vs true Zero Data Retention (ZDR)"**. **NEVER claim "AI Zero Data Retention" under a standard API tier that retains abuse logs!** Only claim zero retention when contractually documented by the chosen provider & configuration (e.g., Cloudflare Workers AI stateless inference with AI Gateway logging disabled).
2. **Cookie Minimization**: Default to cookie-less privacy-friendly analytics (e.g., Plausible, Umami, or aggregated server-side counters) to avoid EU opt-in Cookie Banner friction. Any non-essential ad/tracking cookie requires explicit EU prior opt-in consent.
3. **GDPR Art. 17 Tiered Erasure (Wire into Stage 4 Schema)**:
   - Provide a working account/personal-data deletion path (`DELETE /api/account` or equivalent) that **immediately hard-deletes or anonymizes account PII, sessions, and user content**.
   - **NEVER blindly hard-delete statutory accounting & dispute evidence!** Under **GDPR Art. 17(3)(b)** (legal/tax obligation) and **Art. 17(3)(e)** (legal claims/chargeback defense), decouple (`user_id = NULL`, salted hash or order ref only) and retain minimal financial transaction records and digital withdrawal-waiver timestamps in a restricted ledger until statutory/dispute periods expire.
4. **Minors (COPPA / GDPR-K)**: Declare minimum user age in ToS and forbid knowingly collecting data from children without verifiable parental consent.

---

## Module 3 — MoR vs. Direct Gateway Tax Boundary, AUP & Payout Risk *(Stages 2, 3, 5)*
1. **Indirect Tax vs. Direct Tax Iron Boundary**:
   - A **Merchant of Record (MoR)** (e.g., Paddle, Creem, Freemius) collects and remits **consumption/indirect taxes** (EU/UK VAT, AU/CA GST, JP JCT, US State Sales Tax).
   - **An MoR NEVER pays the founder's corporate or personal income tax!** Founders remain responsible for home-country income tax reporting and maintaining settlement statements + service invoices as foreign-exchange compliance proof.
   - **Bare Direct Gateways (e.g., raw Stripe without MoR)**: Selling B2C digital services into the EU or UK triggers **`€0` / `£0` immediate VAT registration thresholds** from Sale #1 (tax calculators compute tax but do NOT file returns for you). Default to an MoR for solo global B2C unless a CPA manages multi-country tax filings.
2. **Mandatory Live AUP Check (Stage 2 & Stage 3)**: Search the target MoR/gateway's current Acceptable Use Policy for prohibited verticals (social automation bots, scrapers, unlicensed financial/trading advice, crypto trading tools, adult/gambling, empty pre-orders).
3. **KYC, Rolling Reserves & Cashflow**: Check current waitlist/onboarding times, passport vs ID rejection patterns, secondary pre-payout reviews, rolling reserves, and payout cycles (e.g., 14–70 days) before committing cashflow.

---

## Module 4 — Personal Bank AML & Offshore Entity Traps *(Stages 2 & 5)*
1. **Personal Overseas Bank Account AML Red Line**: Receiving recurring commercial SaaS payouts into a personal offshore savings account frequently violates personal account terms and triggers bank AML de-risking / forced account closure. Keep early validation payouts on compliant individual MoR payout paths until profit justifies a proper business entity + business bank account.
2. **Offshore Entity Cost & Filing Traps**:
   - **Foreign-Owned Single-Member US LLC**: Triggers mandatory annual **IRS Form 5472 + Pro Forma Form 1120**—even at **`$0` revenue**, late or missed filing carries a **`$25,000` statutory penalty**! Never open a US LLC casually on a micro-budget.
   - **HK / SG Limited Companies**: Factor mandatory annual statutory CPA audit, company secretary, and registration fees (`~$1,300–$3,200+/yr`)—do not incorporate before sustained net profit clearly covers fixed compliance overhead.
   - Always check home-country tax residency, CFC rules, and bank FX settlement documentation with a licensed CPA before scaling.

---

## Module 5 — Upstream Tech Terms, Data Rights & OSS Copyleft *(Stages 2, 4, 5)*
1. **Third-Party API & Public Data Commercial Rights**: "Publicly scrapeable or free API" ≠ "legally redistributable in commercial SaaS". Audit ToS of every external data source (e.g., market data, social feeds, government APIs).
2. **AI Output Disclaimers**: Disclose AI assistance transparently and state that generated outputs carry no exclusive copyright guarantee or outcome warranty.
3. **OSS Copyleft Audit**: Scan production dependency licenses before launch; block unauthorized **GPL / AGPL** libraries from being bundled into closed-source commercial software. Also verify all bundled fonts/icons/media carry commercial-safe licenses (e.g., SIL OFL, MIT, CC0) and avoid unauthorized third-party brand logos/trademarks.

---

## Module 6 — Consumer Protection & Sanctioned Regions *(Stages 4 & 5)*
1. **Subscription Auto-Renewal (California ARL / EU Consumer Rules)**: Disclose renewal price, cycle, and easy online cancellation clearly before checkout.
2. **One-Time Digital Content / Credits (EU 14-Day Withdrawal Right)**: Before immediate digital consumption, capture an explicit opt-in checkbox acknowledging waiver of the statutory 14-day withdrawal right upon starting consumption (persisted per order!) and ensure wording is **100% consistent** with your voluntary commercial refund policy.
3. **Sanctions & Export Controls (OFAC)**: Rely on MoR checkout country blocking and do not market or provide commercial services into restricted sanctioned jurisdictions.
