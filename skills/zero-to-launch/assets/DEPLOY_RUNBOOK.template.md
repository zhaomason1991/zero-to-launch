# {{FILL:project_name}} — Deployment, Smoke Checks & Rollback Runbook (`DEPLOY_RUNBOOK`)

> OS Compatibility Rule: Use exact commands tested for the builder's OS. On Windows PowerShell 5.1, NEVER pass single-quoted JSON to `curl.exe -d '{"a":"b"}'` (use native `Invoke-WebRequest -UseBasicParsing` or Python) and always invoke `npm.cmd` / `npx.cmd`.

## 1. Staging Deployment & Rate-Limit Verification
```bash
{{FILL:staging_deploy_and_ratelimit_commands}}
```

## 2. Production Deployment (Requires Stage 5 Gate Exit Code 0 & User Approval)
```bash
{{FILL:production_deploy_commands}}
```

## 3. Non-Polluting Production Smoke Checks
*(Never spam public analytics/funnel tables in Production to test rate limits — rate-limit load tests belong in Staging.)*
```bash
{{FILL:production_smoke_commands}}
```

## 4. Non-Destructive Rollback & Emergency Kill-Switch
*(NEVER run `DROP TABLE` or destructive down-migrations against a live production database with real user data.)*
1. **Application Code Rollback**:
   ```bash
   {{FILL:app_rollback_command}}
   ```
2. **Emergency Feature / AI Kill-Switch**:
   ```bash
   {{FILL:emergency_killswitch_command}}
   ```
3. **Database Recovery (Forward-Fix or PITR Restore Only)**:
   ```bash
   {{FILL:db_pitr_or_forward_fix_command}}
   ```
