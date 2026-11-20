# Contributing to `zero-to-launch`

Contributions that improve practical 0-to-1 launch rigor, domain red-team blind spots, cross-platform agent reliability, or security checks are welcome!

## Design Rules Before Opening a PR

1. **Keep `SKILL.md` Lean**: `skills/zero-to-launch/SKILL.md` must stay concise (`<= 250` lines) to preserve progressive disclosure. Place detailed stage procedures in `skills/zero-to-launch/references/`.
2. **Preserve Self-Containment**: Files inside `skills/zero-to-launch/` must NEVER reference files outside `skills/zero-to-launch/` via `../../` so standalone skill installs never break.
3. **Zero Third-Party Script Dependencies**: All Python scripts must run on **Python 3.9+ standard library only** (`from __future__ import annotations`, explicit `encoding="utf-8"`, zero `pip` packages).
4. **Never Hardcode Perishable Policy Facts**: Regional payment/tax/platform rules change constantly—contribute live-date verification checklists rather than static lists.
5. **No Personal Data or Local Paths**: Use cross-platform placeholders (`~/` or `%USERPROFILE%\`) in documentation. Never include real personal emails, local user paths, or live API keys.

## Local Verification (Required Before Submitting)

Run the full zero-side-effect repository validator and test suite from the repo root:

```bash
python -B scripts/validate_repo.py --release
```

On Windows:

```powershell
py -3 -B scripts/validate_repo.py --release
```

All checks (YAML frontmatter compliance, version parity across `SKILL.md`/`plugin.json`/`CHANGELOG.md`, relative Markdown links, generic privacy/secret guards, in-memory AST syntax checks, and end-to-end unit tests for `init_workspace.py` and `check_launch_gate.py`) must pass with exit code `0`.

## Pull Request Process

1. Fork `https://github.com/zhaomason1991/zero-to-launch` and create a feature branch.
2. Keep changes focused and update `CHANGELOG.md` under an `Unreleased` heading if behavior changes.
3. Fill out the PR template checklist and verify the 4-matrix CI workflow (`ubuntu-latest` / `windows-latest` × Python `3.9` / `3.12`) passes cleanly.
