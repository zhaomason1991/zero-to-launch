# Security Policy

## Supported Versions

| Version | Supported |
| :--- | :---: |
| `1.0.x` | Yes |

## Reporting a Vulnerability

Please **do not** disclose security vulnerabilities (such as `check_launch_gate.py` bypasses, path-guard bugs in `init_workspace.py`, or prompt-injection weaknesses in `SKILL.md`) via public GitHub Issues.

Instead, report vulnerabilities privately through GitHub's **Private Vulnerability Reporting** feature on this repository:

- Navigate to `https://github.com/zhaomason1991/zero-to-launch/security/advisories/new`
- Provide a clear description, reproduction steps, and potential impact.

We aim to acknowledge private reports within **72 hours** and coordinate a fix before public disclosure.

## Security Scope & Boundaries

- `zero-to-launch` helper scripts (`init_workspace.py`, `check_launch_gate.py`) use **Python 3.9+ standard library only**, make **zero outbound network requests**, and never modify IDE or system-wide configurations.
- Because AI coding agents can read untrusted web pages and execute shell commands, `SKILL.md` enforces direct & second-order prompt-injection defenses, dependency metadata verification, and explicit human approval before destructive, paid, or public actions. Users remain responsible for reviewing commands before approving execution in their local environment.
- Compliance checklists in `references/module-cross-border-compliance.md` are operational risk guides only and do **not** constitute legal, tax, or accounting advice.
