#!/usr/bin/env python3
"""Pre-launch security, spec completeness, Git tracking, and PaaS packaging gate.

Standard library only (Python 3.9+). Fail-Closed on critical blockers and scan limits.
Never prints plaintext secrets in reports or JSON output.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 1024 * 1024  # 1 MB
MAX_LINE_SCAN_CHARS = 4096

ALLOWED_PRODUCT_TYPES = frozenset(
    {
        "web-saas",
        "mobile-app",
        "browser-extension",
        "cli-tool",
        "desktop-app",
        "bot-agent",
        "api-service",
        "digital-asset",
    }
)
ALLOWED_MONETIZATIONS = frozenset(
    {
        "subscription",
        "one-time-purchase",
        "app-store-iap",
        "b2b-invoice",
        "ads-affiliate",
        "free-oss",
        "internal-tool",
    }
)
ALLOWED_CROSS_BORDER = frozenset({"true", "false"})

REQUIRED_SPEC_FILES = (
    "RUN_THIS_PLAN.md",
    "PRD.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "HUMAN_HANDOFF.md",
    "DEPLOY_RUNBOOK.md",
)

ZTL_GIT_ALLOWLIST = frozenset(
    {
        ".zero-to-launch/.gitignore",
        ".zero-to-launch/spec/RUN_THIS_PLAN.md",
        ".zero-to-launch/spec/PRD.md",
        ".zero-to-launch/spec/ARCHITECTURE.md",
        ".zero-to-launch/spec/TASKS.md",
        ".zero-to-launch/spec/DEPLOY_RUNBOOK.md",
    }
)

SKIP_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        ".next",
        "dist",
        "build",
        "out",
        ".turbo",
        ".cache",
        ".nuxt",
        ".svelte-kit",
        ".venv",
        "venv",
        "__pycache__",
        "target",
        "coverage",
        "vendor",
        "Pods",
        ".gradle",
        ".wrangler",
    }
)

BINARY_EXTS = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".bmp",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".rar",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".wasm",
        ".mp4",
        ".mov",
        ".webm",
        ".mp3",
        ".wav",
        ".woff",
        ".woff2",
        ".ttf",
        ".otf",
        ".eot",
        ".sqlite",
        ".db",
        ".pyc",
        ".pyo",
        ".class",
        ".jar",
        ".bin",
        ".safetensors",
    }
)

ENV_FILE_RE = re.compile(r"^(?:\.env|\.dev\.vars)(?:\..+)?$", re.IGNORECASE)
ENV_TEMPLATE_SUFFIX_RE = re.compile(r"\.(?:example|sample|template|dist)$", re.IGNORECASE)
PLACEHOLDER_VALUE_RE = re.compile(
    r"(?:your_|replace_me|changeme|example|dummy|placeholder|test_only|xxxx|0000|<[^>]+>|\{\{[^}]+\}\})",
    re.IGNORECASE,
)

# Constructed via concatenation to prevent false triggers with secret scanners / Push Protection
VENDOR_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("STRIPE_LIVE_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk_" + "live_" + r"[A-Za-z0-9]{16,}")),
    ("OPENAI_PROJECT_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk-" + "proj-" + r"[A-Za-z0-9_-]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk-" + "ant-" + r"[A-Za-z0-9_-]{20,}")),
    ("CREEM_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "creem_" + r"(?:live|test)_[A-Za-z0-9_-]{16,}")),
    ("WEBHOOK_SECRET", re.compile(r"(?<![A-Za-z0-9_])" + "wh" + "sec_" + r"[A-Za-z0-9_-]{16,}")),
    ("RESEND_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "re" + "_" + r"[A-Za-z0-9]{20,}(?![A-Za-z0-9_])")),
    ("SUPABASE_PAT", re.compile(r"(?<![A-Za-z0-9_])" + "sbp" + "_" + r"[0-9a-f]{40}(?![0-9a-f])")),
    ("GITHUB_PAT", re.compile(r"(?<![A-Za-z0-9_])(?:" + "gh" + "p_|" + "gh" + "o_|" + "github_" + "pat_)" + r"[A-Za-z0-9_]{20,}")),
    ("AWS_ACCESS_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "AK" + "IA" + r"[0-9A-Z]{16}(?![A-Za-z0-9])")),
    ("GOOGLE_API_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "AI" + "za" + r"[0-9A-Za-z_-]{35}(?![A-Za-z0-9_-])")),
)

PEM_PRIVATE_KEY_RE = re.compile(
    r"-----" + "BEGIN " + r"(?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?" + "PRIVATE KEY" + r"-----"
)
DB_URI_PASSWORD_RE = re.compile(
    r"(?:postgres(?:ql)?|mongodb(?:\+srv)?|mysql|rediss?)://[^/\s:@]+:([^@\s/]{6,})@[^/\s]+",
    re.IGNORECASE,
)
HARDCODED_SECRET_ASSIGN_RE = re.compile(
    r"""(?<![A-Za-z0-9_])(?:JWT_SECRET|WEBHOOK_SECRET|SUPABASE_SERVICE_ROLE_KEY|PRIVATE_KEY|SIGNING_SECRET|SESSION_SECRET)\s*[:=]\s*["']([A-Za-z0-9_\-./+=]{16,})["']"""
)
FRONTEND_PUBLIC_SECRET_RE = re.compile(
    r"""(?<![A-Za-z0-9_])((?:NEXT_PUBLIC_|VITE_|REACT_APP_|PUBLIC_|NUXT_PUBLIC_|EXPO_PUBLIC_)[A-Z0-9_]*(?:SECRET|PRIVATE|SERVICE_ROLE|API_KEY|TOKEN|PASSWORD))\s*[:=]\s*["']?([^\s"'#]{8,})["']?"""
)
PROD_MOCK_FLAG_RE = re.compile(
    r"""(?<![A-Za-z0-9_])(MOCK_AI|MOCK_PAYMENT|MOCK_EMAIL)\s*[:=]\s*["']?true["']?""",
    re.IGNORECASE,
)
SENSITIVE_GIT_FILE_RE = re.compile(
    r"(?:^|/)(?:id_rsa(?:\..*)?|.*service-account.*\.json|.*credentials.*\.json|[^/]+\.(?:pem|key|p12|pfx))$",
    re.IGNORECASE,
)
PROD_CONFIG_FILE_RE = re.compile(
    r"^(?:\.env\.production(?:\..*)?|\.env\.prod(?:\..*)?|vercel\.json|wrangler\.(?:toml|json|jsonc)|fly\.toml|Dockerfile(?:\..*)?|railway\.(?:json|toml)|netlify\.toml|next\.config\.[A-Za-z0-9]+)$",
    re.IGNORECASE,
)
FILL_TOKEN_RE = re.compile(r"\{\{FILL:[^}\n]+\}\}")
UNCHECKED_TASK_RE = re.compile(r"^\s*[-*]\s*\[\s\]\s+")


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def mask_secret(value: str) -> str:
    clean = value.strip()
    if len(clean) < 12:
        return "***"
    return clean[:4] + "***"


def is_env_file(filename: str) -> bool:
    return bool(ENV_FILE_RE.match(filename)) and not bool(ENV_TEMPLATE_SUFFIX_RE.search(filename))


def is_env_template(filename: str) -> bool:
    return bool(ENV_FILE_RE.match(filename)) and bool(ENV_TEMPLATE_SUFFIX_RE.search(filename))


def strip_markdown_code(text: str) -> str:
    out_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Strip inline backtick code spans
        out_lines.append(re.sub(r"`[^`\n]+`", "", line))
    return "\n".join(out_lines)


def parse_simple_yaml_frontmatter(text: str) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, ["Missing opening '---' YAML frontmatter delimiter."]

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return {}, ["Missing closing '---' YAML frontmatter delimiter."]

    data: dict[str, Any] = {}
    fm_lines = lines[1:end_idx]
    idx = 0
    while idx < len(fm_lines):
        raw = fm_lines[idx]
        idx += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            errors.append(f"Tab indentation is forbidden in YAML frontmatter (line {idx + 1}).")
            continue
        if raw.startswith(" "):
            errors.append(f"Unexpected indented line in YAML frontmatter (line {idx + 1}).")
            continue
        if ":" not in raw:
            errors.append(f"Invalid YAML key-value line (line {idx + 1}): {raw}")
            continue
        key, val = raw.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val in (">-", ">", "|", "|-"):
            block_lines: list[str] = []
            while idx < len(fm_lines) and (fm_lines[idx].startswith("  ") or not fm_lines[idx].strip()):
                block_lines.append(fm_lines[idx].strip())
                idx += 1
            sep = "\n" if val.startswith("|") else " "
            data[key] = sep.join(part for part in block_lines if part).strip()
        elif val == "{}":
            data[key] = {}
        elif val == "":
            nested: dict[str, Any] = {}
            while idx < len(fm_lines) and (fm_lines[idx].startswith("  ") or not fm_lines[idx].strip()):
                nline = fm_lines[idx]
                idx += 1
                if not nline.strip() or nline.lstrip().startswith("#"):
                    continue
                if "\t" in nline:
                    errors.append(f"Tab indentation in nested YAML block (line {idx + 1}).")
                    continue
                if ":" in nline:
                    nk, nv = nline.strip().split(":", 1)
                    nested[nk.strip()] = nv.strip().strip('"').strip("'")
            data[key] = nested
        else:
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            data[key] = val
    return data, errors


class GateReporter:
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []

    def add(
        self,
        severity: str,
        rule_id: str,
        message: str,
        file: str | None = None,
        line: int | None = None,
        waivable: bool = False,
    ) -> None:
        entry: dict[str, Any] = {
            "severity": severity,  # FAIL | WARN | INFO
            "rule_id": rule_id,
            "waivable": waivable,
            "message": message,
        }
        if file is not None:
            entry["file"] = file
        if line is not None:
            entry["line"] = line
        self.findings.append(entry)

    @property
    def fail_count(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f["severity"] == "WARN")


def check_state_frontmatter(target: Path, rep: GateReporter) -> dict[str, Any]:
    state_path = target / ".zero-to-launch" / "STATE.md"
    if not state_path.is_file():
        rep.add(
            "FAIL",
            "MISSING_STATE_FILE",
            "Missing required .zero-to-launch/STATE.md in full mode.",
            file=".zero-to-launch/STATE.md",
            waivable=False,
        )
        return {}

    text = state_path.read_text(encoding="utf-8", errors="replace")
    fm, parse_errors = parse_simple_yaml_frontmatter(text)
    for err in parse_errors:
        rep.add("FAIL", "INVALID_STATE_YAML", err, file=".zero-to-launch/STATE.md", waivable=False)

    required_keys = (
        "schema_version",
        "current_stage",
        "attempt_number",
        "product_type",
        "monetization",
        "cross_border",
        "redteam_rounds",
        "validation_retries",
        "validation_pivots",
        "fast_track_override",
        "fast_track_unvalidated",
        "blocker_retries",
    )
    for k in required_keys:
        if k not in fm:
            rep.add(
                "FAIL",
                "MISSING_STATE_KEY",
                f"STATE.md frontmatter missing required SSOT key '{k}'.",
                file=".zero-to-launch/STATE.md",
                waivable=False,
            )

    pt = str(fm.get("product_type", "")).strip()
    if pt not in ALLOWED_PRODUCT_TYPES:
        rep.add(
            "FAIL",
            "INVALID_PRODUCT_TYPE",
            f"STATE.md product_type='{pt}' must be locked to a valid non-tbd enum: {sorted(ALLOWED_PRODUCT_TYPES)}",
            file=".zero-to-launch/STATE.md",
            waivable=False,
        )

    mon = str(fm.get("monetization", "")).strip()
    if mon not in ALLOWED_MONETIZATIONS:
        rep.add(
            "FAIL",
            "INVALID_MONETIZATION",
            f"STATE.md monetization='{mon}' must be locked to a valid non-tbd enum: {sorted(ALLOWED_MONETIZATIONS)}",
            file=".zero-to-launch/STATE.md",
            waivable=False,
        )

    cb = str(fm.get("cross_border", "")).strip().lower()
    if cb not in ALLOWED_CROSS_BORDER:
        rep.add(
            "FAIL",
            "INVALID_CROSS_BORDER",
            f"STATE.md cross_border='{cb}' must be locked to 'true' or 'false' (not 'tbd').",
            file=".zero-to-launch/STATE.md",
            waivable=False,
        )
    return fm


def check_spec_and_blockers(target: Path, rep: GateReporter) -> None:
    ztl_dir = target / ".zero-to-launch"
    spec_dir = ztl_dir / "spec"

    files_to_check_fill: list[Path] = []
    state_path = ztl_dir / "STATE.md"
    if state_path.is_file():
        files_to_check_fill.append(state_path)

    for fname in REQUIRED_SPEC_FILES:
        fpath = spec_dir / fname
        if not fpath.is_file():
            rep.add(
                "FAIL",
                "MISSING_SPEC_FILE",
                f"Missing required spec file: .zero-to-launch/spec/{fname}",
                file=f".zero-to-launch/spec/{fname}",
                waivable=False,
            )
        else:
            files_to_check_fill.append(fpath)

    # Check unresolved {{FILL:...}} strictly in STATE.md + 6 spec files (strip code blocks/spans first)
    for fpath in files_to_check_fill:
        rel = fpath.relative_to(target).as_posix()
        text = fpath.read_text(encoding="utf-8", errors="replace")
        cleaned = strip_markdown_code(text)
        matches = FILL_TOKEN_RE.findall(cleaned)
        if matches:
            rep.add(
                "FAIL",
                "UNRESOLVED_PLACEHOLDER",
                f"Found {len(matches)} unresolved placeholder(s) (first: {matches[0]}).",
                file=rel,
                waivable=False,
            )

    # Check language-agnostic LAUNCH_BLOCKERS delimiters (Fail-Closed if missing/unpaired/inverted!)
    for blocker_file in ("TASKS.md", "HUMAN_HANDOFF.md"):
        bpath = spec_dir / blocker_file
        if not bpath.is_file():
            continue
        rel = bpath.relative_to(target).as_posix()
        raw = bpath.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        start_tag = "<!-- LAUNCH_BLOCKERS_START -->"
        end_tag = "<!-- LAUNCH_BLOCKERS_END -->"
        start_count = raw.count(start_tag)
        end_count = raw.count(end_tag)
        start_pos = raw.find(start_tag)
        end_pos = raw.find(end_tag)

        if start_count != 1 or end_count != 1 or start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
            rep.add(
                "FAIL",
                "MISSING_BLOCKER_DELIMITERS",
                f"Missing, duplicated, or inverted {start_tag}/{end_tag} delimiters.",
                file=rel,
                waivable=False,
            )
            continue

        segment = raw[start_pos + len(start_tag) : end_pos]
        in_fence = False
        unchecked_lines: list[int] = []
        prefix_line_offset = raw[: start_pos + len(start_tag)].count("\n")
        for idx, line in enumerate(segment.split("\n"), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if UNCHECKED_TASK_RE.match(line):
                unchecked_lines.append(prefix_line_offset + idx)
        if unchecked_lines:
            rep.add(
                "FAIL",
                "UNCHECKED_LAUNCH_BLOCKER",
                f"Found {len(unchecked_lines)} unchecked blocker item(s) inside LAUNCH_BLOCKERS (first at line {unchecked_lines[0]}).",
                file=rel,
                line=unchecked_lines[0],
                waivable=False,
            )


def _run_git(target: Path, args: list[str]) -> tuple[int, bytes, str]:
    try:
        proc = subprocess.run(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=str(target),
            shell=False,
            timeout=10,
            capture_output=True,
        )
        return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", errors="replace")
    except FileNotFoundError:
        return -1, b"", "git executable not found"
    except subprocess.TimeoutExpired:
        return -2, b"", "git command timed out"
    except OSError as exc:
        return -3, b"", str(exc)


def check_git_safety(target: Path, rep: GateReporter) -> tuple[bool, set[str]]:
    if not (target / ".git").exists():
        rep.add(
            "WARN",
            "GIT_NOT_INITIALIZED",
            "Project directory is not a Git repository; ensure non-Git deploy exclusions cover .zero-to-launch/ and local secret files.",
            waivable=True,
        )
        return False, set()

    rc, out, err = _run_git(target, ["ls-files", "-z"])
    if rc != 0:
        rep.add(
            "WARN",
            "GIT_NOT_INITIALIZED",
            f"Unable to run git ls-files ({err.strip()}); falling back to disk/PaaS checks.",
            waivable=True,
        )
        return False, set()

    tracked: set[str] = set()
    for raw_entry in out.split(b"\x00"):
        if not raw_entry:
            continue
        norm_rel = raw_entry.decode("utf-8", errors="replace").replace("\\", "/")
        tracked.add(norm_rel)

    for rel in sorted(tracked):
        fname = rel.rsplit("/", 1)[-1]
        if is_env_file(fname):
            rep.add(
                "FAIL",
                "TRACKED_ENV_SECRET_FILE",
                f"Local secret env file is tracked/staged in Git: {rel}",
                file=rel,
                waivable=False,
            )
        if SENSITIVE_GIT_FILE_RE.search(rel):
            rep.add(
                "FAIL",
                "TRACKED_SENSITIVE_KEY_FILE",
                f"Sensitive key/credential file is tracked/staged in Git: {rel}",
                file=rel,
                waivable=False,
            )
        if rel.startswith(".zero-to-launch/") and rel not in ZTL_GIT_ALLOWLIST:
            rep.add(
                "FAIL",
                "TRACKED_ZTL_PRIVATE_FILE",
                f"Non-allowlisted .zero-to-launch file tracked in Git: {rel}",
                file=rel,
                waivable=False,
            )

    # Check untracked, unignored ?? .env* / ?? .dev.vars* (Blocker FAIL!)
    rc_st, out_st, _ = _run_git(target, ["status", "--porcelain", "-z", "-uall"])
    if rc_st == 0:
        entries = out_st.split(b"\x00")
        idx = 0
        while idx < len(entries):
            raw_item = entries[idx]
            idx += 1
            if not raw_item or len(raw_item) < 4:
                continue
            item = raw_item.decode("utf-8", errors="replace")
            status_code = item[:2]
            rel_path = item[3:].replace("\\", "/")
            if status_code[0] in ("R", "C"):
                idx += 1  # skip rename original path
            if status_code == "??":
                fname = rel_path.rsplit("/", 1)[-1]
                if is_env_file(fname):
                    rep.add(
                        "FAIL",
                        "UNIGNORED_ENV_FILE",
                        f"Untracked local secret file is NOT ignored by .gitignore: {rel_path}. Add it to .gitignore immediately.",
                        file=rel_path,
                        waivable=False,
                    )

    return True, tracked


def scan_line_for_secrets(
    rel: str,
    line_no: int,
    line: str,
    is_local_env: bool,
    is_prod_cfg: bool,
    rep: GateReporter,
) -> None:
    sample = line[:MAX_LINE_SCAN_CHARS]

    # Frontend public env var leaking secret-named values (always check, EVEN in local .env/.dev.vars!)
    m_pub = FRONTEND_PUBLIC_SECRET_RE.search(sample)
    if m_pub:
        var_name, val = m_pub.group(1), m_pub.group(2)
        if not PLACEHOLDER_VALUE_RE.search(val):
            rep.add(
                "FAIL",
                "FRONTEND_PUBLIC_SECRET",
                f"Frontend public env var '{var_name}' holds a secret-like value ({mask_secret(val)}).",
                file=rel,
                line=line_no,
                waivable=False,
            )

    if is_prod_cfg:
        m_mock = PROD_MOCK_FLAG_RE.search(sample)
        if m_mock:
            rep.add(
                "FAIL",
                "PROD_MOCK_FLAG_ENABLED",
                f"Production config enables '{m_mock.group(1)}=true'.",
                file=rel,
                line=line_no,
                waivable=False,
            )

    # Untracked local .env / .dev.vars legitimately hold server secrets — skip server-secret scan
    if is_local_env:
        return

    for rule_id, pat in VENDOR_SECRET_PATTERNS:
        m = pat.search(sample)
        if m:
            found = m.group(0)
            if not PLACEHOLDER_VALUE_RE.search(found):
                rep.add(
                    "FAIL",
                    f"LEAKED_{rule_id}",
                    f"Detected probable secret token ({mask_secret(found)}).",
                    file=rel,
                    line=line_no,
                    waivable=False,
                )

    if PEM_PRIVATE_KEY_RE.search(sample):
        rep.add(
            "FAIL",
            "LEAKED_PEM_PRIVATE_KEY",
            "Detected PEM private key header in file (***).",
            file=rel,
            line=line_no,
            waivable=False,
        )

    m_db = DB_URI_PASSWORD_RE.search(sample)
    if m_db:
        pw = m_db.group(1)
        if not PLACEHOLDER_VALUE_RE.search(pw):
            rep.add(
                "FAIL",
                "LEAKED_DB_URI_PASSWORD",
                f"Detected database/cache URI with embedded password ({mask_secret(pw)}).",
                file=rel,
                line=line_no,
                waivable=False,
            )

    m_assign = HARDCODED_SECRET_ASSIGN_RE.search(sample)
    if m_assign:
        val = m_assign.group(1)
        if not PLACEHOLDER_VALUE_RE.search(val):
            rep.add(
                "FAIL",
                "HARDCODED_SERVER_SECRET",
                f"Detected hardcoded server secret assignment ({mask_secret(val)}).",
                file=rel,
                line=line_no,
                waivable=False,
            )


def check_secrets_on_disk(
    target: Path,
    tracked: set[str],
    git_ready: bool,
    max_files: int,
    rep: GateReporter,
) -> int:
    scanned = 0
    backups_dir = target / ".zero-to-launch" / "backups"
    if backups_dir.is_dir():
        rep.add(
            "WARN",
            "UNDELETED_LOCAL_BACKUPS",
            "Found .zero-to-launch/backups/ snapshots. Clean up temporary backups before shipping.",
            file=".zero-to-launch/backups",
            waivable=True,
        )

    for root, dirs, files in os.walk(str(target), topdown=True, followlinks=False):
        root_path = Path(root)
        rel_root = root_path.relative_to(target).as_posix()

        # Prune skipped dirs and .zero-to-launch/backups (NEVER skip .zero-to-launch/archive!)
        kept_dirs: list[str] = []
        for d in dirs:
            if d in SKIP_DIRS:
                continue
            if rel_root == ".zero-to-launch" and d == "backups":
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for fname in files:
            fpath = root_path / fname
            if fpath.suffix.lower() in BINARY_EXTS:
                continue
            scanned += 1
            if scanned > max_files:
                rep.add(
                    "FAIL",
                    "INCOMPLETE_SCAN",
                    f"File scan exceeded limit of {max_files} files (Fail-Closed). Pass --max-files to raise cap after verifying ignore dirs.",
                    waivable=False,
                )
                return scanned

            try:
                if fpath.is_symlink():
                    continue
                size = fpath.stat().st_size
            except OSError as exc:
                rep.add("WARN", "UNREADABLE_FILE", f"Cannot stat file: {exc}", file=fpath.relative_to(target).as_posix(), waivable=True)
                continue

            if size > MAX_FILE_BYTES:
                continue

            rel = fpath.relative_to(target).as_posix()
            local_env = is_env_file(fname) and (rel not in tracked)
            if is_env_file(fname) and not git_ready:
                rep.add(
                    "WARN",
                    "LOCAL_ENV_WITHOUT_GIT",
                    f"Local secret file '{rel}' found in non-Git directory; confirm deploy ignore excludes it.",
                    file=rel,
                    waivable=True,
                )

            prod_cfg = bool(PROD_CONFIG_FILE_RE.match(fname))
            try:
                with fpath.open("r", encoding="utf-8", errors="replace") as handle:
                    for line_no, line in enumerate(handle, start=1):
                        scan_line_for_secrets(rel, line_no, line, local_env, prod_cfg, rep)
            except OSError as exc:
                rep.add("WARN", "UNREADABLE_FILE", f"Cannot read file: {exc}", file=rel, waivable=True)

    return scanned


def _ignore_file_covers(path: Path, tokens: tuple[str, ...]) -> tuple[bool, list[str]]:
    if not path.is_file():
        return False, list(tokens)
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [tok for tok in tokens if tok not in text]
    return len(missing) == 0, missing


def check_packaging_isolation(target: Path, rep: GateReporter) -> None:
    # 1. Docker / Fly.io (Docker never reads .gitignore -> .dockerignore mandatory)
    if (target / "Dockerfile").is_file() or (target / "fly.toml").is_file():
        dockerignore = target / ".dockerignore"
        ok, missing = _ignore_file_covers(dockerignore, (".zero-to-launch", ".env"))
        if not ok:
            rep.add(
                "FAIL",
                "MISSING_DOCKERIGNORE_EXCLUSION",
                f"Dockerfile/fly.toml detected: .dockerignore must exist and exclude {missing}.",
                file=".dockerignore",
                waivable=False,
            )

    # 2. PaaS deployments (check dedicated ignore if present; else verify root .gitignore to avoid overriding .gitignore!)
    root_gitignore = target / ".gitignore"
    paas_rules: list[tuple[bool, tuple[str, ...], tuple[str, ...], str]] = [
        (
            any(
                (target / p).exists()
                for p in ("vercel.json", ".vercel", "next.config.js", "next.config.mjs", "next.config.ts")
            ),
            (".vercelignore",),
            (".zero-to-launch", ".env"),
            "Vercel/Next.js",
        ),
        (
            any((target / p).is_file() for p in ("wrangler.toml", "wrangler.json", "wrangler.jsonc")),
            (".assetsignore", ".cfignore"),
            (".zero-to-launch", ".dev.vars"),
            "Cloudflare Wrangler",
        ),
        (
            (target / "netlify.toml").is_file() or (target / "railway.json").is_file() or (target / "railway.toml").is_file(),
            (".netlifyignore",),
            (".zero-to-launch", ".env"),
            "Netlify/Railway",
        ),
    ]

    for detected, dedicated_names, req_tokens, label in paas_rules:
        if not detected:
            continue
        existing_dedicated = [target / n for n in dedicated_names if (target / n).is_file()]
        if existing_dedicated:
            for dpath in existing_dedicated:
                ok, missing = _ignore_file_covers(dpath, req_tokens)
                if not ok:
                    rep.add(
                        "FAIL",
                        "PAAS_IGNORE_MISSING_EXCLUSION",
                        f"{label} ignore file '{dpath.name}' exists but does not exclude {missing}.",
                        file=dpath.name,
                        waivable=False,
                    )
        else:
            ok_root, missing_root = _ignore_file_covers(root_gitignore, req_tokens)
            if not ok_root:
                rep.add(
                    "FAIL",
                    "PAAS_ROOT_IGNORE_MISSING",
                    f"{label} detected without dedicated ignore file and root .gitignore does not exclude {missing_root}.",
                    file=".gitignore",
                    waivable=False,
                )

    # 3. Publishable npm package (package.json without "private": true)
    pkg_path = target / "package.json"
    if pkg_path.is_file():
        try:
            pkg_data = json.loads(pkg_path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            pkg_data = {}
        if isinstance(pkg_data, dict) and pkg_data.get("private") is not True:
            has_files_allowlist = isinstance(pkg_data.get("files"), list) and len(pkg_data["files"]) > 0
            ok_npm, _ = _ignore_file_covers(target / ".npmignore", (".zero-to-launch",))
            if not has_files_allowlist and not ok_npm:
                rep.add(
                    "FAIL",
                    "NPM_PUBLISH_LEAK_RISK",
                    "package.json is not marked \"private\": true and lacks both 'files' allowlist and .npmignore excluding .zero-to-launch.",
                    file="package.json",
                    waivable=False,
                )

    # 4. Independent shallow probe of build outputs (unaffected by Check 3 dir skips!)
    for out_rel in ("dist", "build", "out", ".next/static"):
        candidate = target / out_rel / ".zero-to-launch"
        if candidate.exists():
            rep.add(
                "FAIL",
                "BUILD_OUTPUT_ZTL_LEAK",
                f"Build output directory contains leaked .zero-to-launch: {out_rel}/.zero-to-launch",
                file=f"{out_rel}/.zero-to-launch",
                waivable=False,
            )


def run_gate(target: Path, mode: str, max_files: int) -> dict[str, Any]:
    rep = GateReporter()
    state_meta: dict[str, Any] = {}
    if mode == "full":
        state_meta = check_state_frontmatter(target, rep)
        check_spec_and_blockers(target, rep)

    git_ready, tracked = check_git_safety(target, rep)
    scanned_files = check_secrets_on_disk(target, tracked, git_ready, max_files, rep)
    check_packaging_isolation(target, rep)

    return {
        "status": "PASS" if rep.fail_count == 0 else "FAIL",
        "mode": mode,
        "target": str(target),
        "scanned_files": scanned_files,
        "fail_count": rep.fail_count,
        "warn_count": rep.warn_count,
        "archetype": {
            "product_type": state_meta.get("product_type", "unknown"),
            "monetization": state_meta.get("monetization", "unknown"),
            "cross_border": state_meta.get("cross_border", "unknown"),
        },
        "findings": rep.findings,
    }


def format_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Zero-to-Launch Pre-Launch Gate: {result['status']}",
        f"- Mode: `{result['mode']}` | Scanned Files: `{result['scanned_files']}` | Failures: `{result['fail_count']}` | Warnings: `{result['warn_count']}`",
    ]
    if not result["findings"]:
        lines.append("- All automated gate checks passed cleanly.")
        return "\n".join(lines)
    lines.append("")
    lines.append("## Findings")
    for f in result["findings"]:
        loc = f.get("file", "-")
        if f.get("line") is not None:
            loc = f"{loc}:{f['line']}"
        tag = "Waivable" if f["waivable"] else "Non-Waivable"
        lines.append(f"- **[{f['severity']} | {tag}] `{f['rule_id']}`** (`{loc}`): {f['message']}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the zero-to-launch automated pre-launch security, spec, Git, and packaging gate."
    )
    parser.add_argument("--target", default=".", help="Target project directory (default: cwd).")
    parser.add_argument(
        "--mode",
        choices=("full", "standalone"),
        default="full",
        help="full (requires .zero-to-launch/STATE.md + 6 spec files) or standalone (existing repo audit).",
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON.")
    parser.add_argument(
        "--max-files",
        type=int,
        default=5000,
        help="Fail-Closed file scan limit (default: 5000).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = parse_args(argv)
    target = Path(args.target).expanduser().resolve(strict=False)
    if not target.is_dir():
        msg = f"Target directory does not exist: {target}"
        if args.json:
            print(json.dumps({"status": "FAIL", "error": msg}, ensure_ascii=False))
        else:
            print(f"[ERROR] {msg}", file=sys.stderr)
        return 1

    result = run_gate(target, args.mode, args.max_files)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_markdown(result))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
