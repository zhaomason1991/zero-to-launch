# {{FILL:project_name}} — Verbatim System Architecture & Contracts (`ARCHITECTURE`)

> Anti-Summarization Rule: Replace every placeholder below with verbatim executable DDL, exact JSON schemas, exact file trees, and exact commands.

## 1. Verified Technology Stack (Checked for Jurisdiction & Commercial Terms)
- **Frontend / Client**: {{FILL:frontend_stack}}
- **Backend / Runtime**: {{FILL:backend_stack}}
- **Database & Automated Backups**: {{FILL:database_and_backup_spec}}
- **AI / External APIs (Jurisdiction-Verified)**: {{FILL:external_apis_or_na}}
- **Transactional Email (Custom Domain SMTP/API)**: {{FILL:email_provider_or_na}}
- **Payment Provider (MoR / Store)**: {{FILL:payment_provider_or_na}}
- **Rate Limiting & Abuse Protection**: {{FILL:rate_limit_primitive}}
- **Testing & Lockfile Policy**: {{FILL:test_stack_and_lockfile}}
- **OS-Safe Local Commands**: {{FILL:os_safe_cli_prefix}}

## 2. Exact Directory Tree
```text
{{FILL:directory_tree}}
```

## 3. Verbatim Data Schema & Security Policies
*(Never place `.down.sql` inside auto-applied migration directories. For Postgres `SECURITY DEFINER` RPCs, always include `SET search_path = ''` and `REVOKE ALL ... FROM PUBLIC, anon, authenticated`.)*

```sql
{{FILL:verbatim_schema_ddl_or_state_model}}
```

## 4. 1:1 PRD-to-API & Webhook Contracts
- **Explicit Middleware Execution Order**: {{FILL:middleware_order}}
- **Streaming Body Size Cap Strategy**: {{FILL:streaming_body_cap}}
- **Trusted Client IP Header**: {{FILL:trusted_ip_header}}

| Route / Command | Auth & Rate Limit (Valid Cloud Period) | Request Schema / Headers | Exact Response Schema & HTTP Error Codes |
| :--- | :--- | :--- | :--- |
| {{FILL:route_1}} | {{FILL:auth_rl_1}} | {{FILL:req_1}} | {{FILL:res_1}} |

*(Verify every UI page/action in `PRD.md`—including account read, logout, checkout, webhook grant + symmetric refund/dispute revocation, and account deletion—has an explicit row above. One-time Magic Links must use `GET` page + `POST` consume.)*

## 5. Local Mock / Stub Strategy & Production Fail-Closed Guard
- **Local Development Mocks**: {{FILL:local_mock_strategy}}
- **Production Fail-Closed Startup Guard**: {{FILL:prod_fail_closed_guard}}

## 6. Strict Environment Variable Boundaries (Public vs. Server-Only)
| Variable Name | Scope | Public Frontend Prefix? | Purpose & Security Constraint |
| :--- | :--- | :---: | :--- |
| {{FILL:env_var_1}} | {{FILL:scope_1}} | {{FILL:public_yes_no}} | {{FILL:purpose_1}} |

## 7. Non-Git Packaging Exclusions & Monthly Cost Caps
- **Deploy Ignore Files**: {{FILL:deploy_ignore_files}}
- **Hard Cost Caps & Auto-Reload Safeguards**: {{FILL:cost_cap_controls}}
- **Staging Callback URL**: {{FILL:staging_url_spec}}
