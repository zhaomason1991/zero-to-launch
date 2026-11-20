#!/usr/bin/env python3
"""Zero-dependency repository validator and isolated test suite for zero-to-launch.

Requires Python 3.9+ standard library only. Never writes .pyc bytecode to disk.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "zero-to-launch"
SKILL_MD = SKILL_DIR / "SKILL.md"
PLUGIN_JSON = REPO_ROOT / "plugin.json"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"
WORKFLOW_YML = REPO_ROOT / ".github" / "workflows" / "validate-skill.yml"
INIT_SCRIPT = SKILL_DIR / "scripts" / "init_workspace.py"
GATE_SCRIPT = SKILL_DIR / "scripts" / "check_launch_gate.py"

PLUGIN_JSON_WHITELIST = frozenset(
    {
        "name",
        "displayName",
        "version",
        "description",
        "logo",
        "suggestedPrompts",
        "author",
        "homepage",
        "repository",
        "disabled",
    }
)

REQUIRED_REPO_FILES = (
    "plugin.json",
    "README.md",
    "README_CN.md",
    "LICENSE",
    "SECURITY.md",
    ".gitattributes",
    ".gitignore",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    ".github/workflows/validate-skill.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    "examples/sample-walkthrough.md",
    "docs/images/logo.svg",
    "docs/images/logo.png",
    "docs/images/hero-banner.png",
    "docs/images/card-1-redteam.png",
    "docs/images/card-2-specpack.png",
    "docs/images/card-3-launchgate.png",
    "docs/images/real-output.png",
    "scripts/validate_repo.py",
    "skills/zero-to-launch/SKILL.md",
    "skills/zero-to-launch/references/stage-0-intake.md",
    "skills/zero-to-launch/references/stage-1-opportunity.md",
    "skills/zero-to-launch/references/stage-2-redteam.md",
    "skills/zero-to-launch/references/stage-3-validation.md",
    "skills/zero-to-launch/references/stage-4-spec-and-build.md",
    "skills/zero-to-launch/references/stage-5-prelaunch-ship.md",
    "skills/zero-to-launch/references/stage-6-growth-ops.md",
    "skills/zero-to-launch/references/module-cross-border-compliance.md",
    "skills/zero-to-launch/assets/STATE.template.md",
    "skills/zero-to-launch/assets/RUN_THIS_PLAN.template.md",
    "skills/zero-to-launch/assets/PRD.template.md",
    "skills/zero-to-launch/assets/ARCHITECTURE.template.md",
    "skills/zero-to-launch/assets/TASKS.template.md",
    "skills/zero-to-launch/assets/HUMAN_HANDOFF.template.md",
    "skills/zero-to-launch/assets/DEPLOY_RUNBOOK.template.md",
    "skills/zero-to-launch/scripts/init_workspace.py",
    "skills/zero-to-launch/scripts/check_launch_gate.py",
)

ALLOWED_EMAIL_DOMAINS = frozenset(
    {
        "example.com",
        "example.org",
        "example.net",
        "users.noreply.github.com",
    }
)

ENV_FILE_RE = re.compile(r"^(?:\.env|\.dev\.vars)(?:\..+)?$", re.IGNORECASE)
ENV_TEMPLATE_SUFFIX_RE = re.compile(r"\.(?:example|sample|template|dist)$", re.IGNORECASE)
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
HTML_IMG_SRC_RE = re.compile(r"""<img\b[^>]*\bsrc=["']([^"']+)["']""", re.IGNORECASE)
HTML_A_HREF_RE = re.compile(r"""<a\b[^>]*\bhref=["']([^"']+)["']""", re.IGNORECASE)
FILL_TOKEN_RE = re.compile(r"\{\{FILL:[^}\n]+\}\}")
SHA40_USE_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")

# Constructed dynamically so validator never triggers its own privacy/secret scan
GITHUB_PLACEHOLDER = "<YOUR_" + "GITHUB_USERNAME>"
LOCAL_URI_MARKERS = ("conversation" + "://", "file" + ":///")
WIN_USER_PATH_RE = re.compile(r"[A-Za-z]:[/\\](?:Users|Documents and Settings)[/\\][A-Za-z0-9_.\-]+")
WIN_CJK_PATH_RE = re.compile(r"[A-Za-z]:[/\\][^\s\"'\)\`]*[\u4e00-\u9fff]")
POSIX_USER_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/[A-Za-z0-9_.\-]+/")
EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![A-Za-z0-9.-])")
UUID_V4_RE = re.compile(
    r"(?<![0-9a-fA-F])[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}(?![0-9a-fA-F])"
)
REPO_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("STRIPE_LIVE_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk_" + "live_" + r"[A-Za-z0-9]{16,}")),
    ("OPENAI_PROJECT_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk-" + "proj-" + r"[A-Za-z0-9_-]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "sk-" + "ant-" + r"[A-Za-z0-9_-]{20,}")),
    ("GITHUB_PAT", re.compile(r"(?<![A-Za-z0-9_])(?:" + "gh" + "p_|" + "gh" + "o_|" + "github_" + "pat_)" + r"[A-Za-z0-9_]{20,}")),
    ("AWS_ACCESS_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "AK" + "IA" + r"[0-9A-Z]{16}(?![A-Za-z0-9])")),
    ("GOOGLE_API_KEY", re.compile(r"(?<![A-Za-z0-9_])" + "AI" + "za" + r"[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])")),
    ("PEM_PRIVATE_KEY", re.compile(r"-----" + "BEGIN " + r"(?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?" + "PRIVATE KEY" + r"-----")),
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _no_pyc_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _run_py(script: Path, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(script), *args],
        cwd=str(cwd) if cwd else None,
        env=_no_pyc_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        shell=False,
    )


def strip_markdown_code(text: str) -> str:
    out_lines: list[str] = []
    in_fence = False
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out_lines.append(re.sub(r"`[^`\n]+`", "", line))
    return "\n".join(out_lines)


def parse_yaml_frontmatter(text: str) -> tuple[dict[str, Any], str, list[str]]:
    errors: list[str] = []
    norm = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = norm.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, norm, ["Missing opening '---' YAML frontmatter delimiter."]

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        return {}, norm, ["Missing closing '---' YAML frontmatter delimiter."]

    data: dict[str, Any] = {}
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    idx = 0
    while idx < len(fm_lines):
        raw = fm_lines[idx]
        idx += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            errors.append(f"Tab indentation forbidden in YAML frontmatter (line {idx + 1}).")
            continue
        if raw.startswith(" "):
            errors.append(f"Unexpected indented line in YAML frontmatter (line {idx + 1}).")
            continue
        if ":" not in raw:
            errors.append(f"Invalid YAML line (line {idx + 1}): {raw}")
            continue
        key, val = raw.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val in (">-", ">", "|", "|-"):
            block: list[str] = []
            while idx < len(fm_lines):
                nxt = fm_lines[idx]
                if not nxt.strip():
                    block.append("")
                    idx += 1
                    continue
                if "\t" in nxt:
                    errors.append(f"Tab indentation in YAML block scalar (line {idx + 2}).")
                    idx += 1
                    continue
                if nxt.startswith("  "):
                    block.append(nxt[2:] if val.startswith("|") else nxt.strip())
                    idx += 1
                    continue
                break
            if val.startswith("|"):
                data[key] = "\n".join(block).strip("\n")
            else:
                data[key] = " ".join(p for p in block if p).strip()
        elif val == "{}":
            data[key] = {}
        elif val == "":
            nested: dict[str, Any] = {}
            while idx < len(fm_lines):
                nxt = fm_lines[idx]
                if not nxt.strip() or nxt.lstrip().startswith("#"):
                    idx += 1
                    continue
                if "\t" in nxt:
                    errors.append(f"Tab indentation in nested YAML mapping (line {idx + 2}).")
                    idx += 1
                    continue
                if nxt.startswith("  "):
                    idx += 1
                    if ":" not in nxt:
                        errors.append(f"Invalid nested YAML line (line {idx + 1}): {nxt}")
                        continue
                    nk, nv = nxt.strip().split(":", 1)
                    nv = nv.strip()
                    if (nv.startswith('"') and nv.endswith('"')) or (
                        nv.startswith("'") and nv.endswith("'")
                    ):
                        nv = nv[1:-1]
                    nested[nk.strip()] = nv
                    continue
                break
            data[key] = nested
        else:
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            data[key] = val
    return data, body, errors


class ValidationErrors:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def fail(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def self_test_yaml_parser(ve: ValidationErrors) -> None:
    sample_crlf = (
        "---\r\n"
        "name: demo-skill\r\n"
        "description: >-\r\n"
        "  Line one with: colon\r\n"
        "  and line two.\r\n"
        "notes: |\r\n"
        "  alpha\r\n"
        "  beta\r\n"
        "empty_map: {}\r\n"
        'url: "https://example.com:8443/path"\r\n'
        "metadata:\r\n"
        '  version: "1.2.3"\r\n'
        "  author: 'demo:team'\r\n"
        "---\r\n"
        "# Body\r\n"
    )
    parsed, body, errs = parse_yaml_frontmatter(sample_crlf)
    if errs:
        ve.fail(f"YAML parser self-test failed on valid CRLF fixture: {errs}")
        return
    if parsed.get("name") != "demo-skill":
        ve.fail("YAML self-test: scalar mismatch.")
    if parsed.get("description") != "Line one with: colon and line two.":
        ve.fail(f"YAML self-test: folded scalar mismatch: {parsed.get('description')!r}")
    if parsed.get("notes") != "alpha\nbeta":
        ve.fail(f"YAML self-test: literal scalar mismatch: {parsed.get('notes')!r}")
    if parsed.get("empty_map") != {}:
        ve.fail(f"YAML self-test: empty dict mismatch: {parsed.get('empty_map')!r}")
    if parsed.get("url") != "https://example.com:8443/path":
        ve.fail(f"YAML self-test: colon-in-quotes mismatch: {parsed.get('url')!r}")
    if not isinstance(parsed.get("metadata"), dict) or parsed["metadata"].get("version") != "1.2.3":
        ve.fail(f"YAML self-test: nested dict mismatch: {parsed.get('metadata')!r}")
    if "# Body" not in body:
        ve.fail("YAML self-test: body extraction failed.")

    tab_fixture = "---\nname: bad\nmetadata:\n\tversion: 1.0\n---\n"
    _, _, tab_errs = parse_yaml_frontmatter(tab_fixture)
    if not tab_errs:
        ve.fail("YAML self-test: failed to reject tab indentation.")


def check_required_files(ve: ValidationErrors) -> None:
    for rel in REQUIRED_REPO_FILES:
        if not (REPO_ROOT / rel).is_file():
            ve.fail(f"Missing required repository file: {rel}")


def check_skill_and_plugin_metadata(ve: ValidationErrors, release: bool) -> None:
    if not SKILL_MD.is_file():
        ve.fail("Missing skills/zero-to-launch/SKILL.md")
        return

    skill_text = SKILL_MD.read_text(encoding="utf-8")
    total_lines = len(skill_text.splitlines())
    if total_lines > 250:
        ve.fail(f"SKILL.md has {total_lines} lines (target <= 250 lines).")

    fm, _, errs = parse_yaml_frontmatter(skill_text)
    for err in errs:
        ve.fail(f"SKILL.md YAML error: {err}")

    name = str(fm.get("name", ""))
    if name != "zero-to-launch" or name != SKILL_DIR.name:
        ve.fail(f"SKILL.md name '{name}' must match parent directory '{SKILL_DIR.name}'.")
    if not KEBAB_CASE_RE.match(name) or len(name) > 64:
        ve.fail(f"SKILL.md name '{name}' must be kebab-case and <= 64 chars.")

    desc = str(fm.get("description", ""))
    if not desc or len(desc) > 1024:
        ve.fail(f"SKILL.md description must be 1..1024 chars (got {len(desc)}).")

    compat = str(fm.get("compatibility", ""))
    if not compat or len(compat) > 500:
        ve.fail(f"SKILL.md compatibility must be 1..500 chars (got {len(compat)}).")

    if fm.get("license") != "MIT":
        ve.fail(f"SKILL.md license must be 'MIT' (got {fm.get('license')!r}).")

    meta = fm.get("metadata")
    skill_ver = meta.get("version") if isinstance(meta, dict) else None
    if not skill_ver:
        ve.fail("SKILL.md metadata.version is missing.")

    # plugin.json check
    if not PLUGIN_JSON.is_file():
        ve.fail("Missing plugin.json")
        return
    try:
        plugin_data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        ve.fail(f"Invalid JSON in plugin.json: {exc}")
        return

    if not isinstance(plugin_data, dict):
        ve.fail("plugin.json root must be a JSON object.")
        return

    extra_keys = set(plugin_data.keys()) - PLUGIN_JSON_WHITELIST
    if extra_keys:
        ve.fail(f"plugin.json contains non-whitelist top-level keys: {sorted(extra_keys)}")

    if plugin_data.get("name") != "zero-to-launch":
        ve.fail("plugin.json name must be 'zero-to-launch'.")

    prompts = plugin_data.get("suggestedPrompts")
    if not isinstance(prompts, list) or len(prompts) != 3 or not all(isinstance(p, str) and p.strip() for p in prompts):
        ve.fail("plugin.json suggestedPrompts must be an array of exactly 3 non-empty strings.")

    plugin_ver = plugin_data.get("version")
    if not isinstance(plugin_ver, str) or not plugin_ver.strip():
        ve.fail("plugin.json version must be a non-empty string.")

    # CHANGELOG.md 3-way version parity
    if CHANGELOG_MD.is_file():
        cl_text = CHANGELOG_MD.read_text(encoding="utf-8")
        m_ver = re.search(r"^##\s+\[([^\]]+)\]", cl_text, flags=re.MULTILINE)
        cl_ver = m_ver.group(1) if m_ver else None
        if not cl_ver:
            ve.fail("CHANGELOG.md missing '## [<version>]' heading.")
        elif len({skill_ver, plugin_ver, cl_ver}) != 1:
            ve.fail(
                f"3-way version mismatch: SKILL.md={skill_ver!r}, plugin.json={plugin_ver!r}, CHANGELOG.md={cl_ver!r}"
            )
    else:
        ve.fail("Missing CHANGELOG.md")

    if release:
        repo_url = str(plugin_data.get("repository", ""))
        if not repo_url.startswith("https://") or "<" in repo_url or ">" in repo_url:
            ve.fail(f"Release check failed: plugin.json repository must be a concrete https:// URL (got {repo_url!r}).")


def check_workflow_security(ve: ValidationErrors) -> None:
    if not WORKFLOW_YML.is_file():
        ve.fail("Missing .github/workflows/validate-skill.yml")
        return
    text = WORKFLOW_YML.read_text(encoding="utf-8")
    if "contents: read" not in text:
        ve.fail("CI workflow must set minimal 'contents: read' permission.")
    if "persist-credentials: false" not in text:
        ve.fail("CI workflow checkout step must set 'persist-credentials: false'.")

    uses_count = 0
    for line_no, line in enumerate(text.splitlines(), start=1):
        m = SHA40_USE_RE.match(line)
        if m:
            uses_count += 1
            ref = m.group(1)
            if not re.search(r"@[0-9a-f]{40}$", ref):
                ve.fail(f"CI workflow line {line_no} action '{ref}' is not pinned to a 40-char commit SHA.")
    if uses_count == 0:
        ve.fail("CI workflow has no 'uses:' actions.")


def check_markdown_links_and_containment(ve: ValidationErrors) -> None:
    skill_dir_resolved = SKILL_DIR.resolve()
    repo_resolved = REPO_ROOT.resolve()

    for md_path in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in md_path.parts:
            continue
        rel_md = md_path.relative_to(REPO_ROOT).as_posix()
        text = md_path.read_text(encoding="utf-8", errors="replace")
        cleaned = strip_markdown_code(text)
        in_skill = False
        try:
            md_path.resolve().relative_to(skill_dir_resolved)
            in_skill = True
        except ValueError:
            in_skill = False

        raw_targets: list[str] = [m.group(1).strip() for m in MD_LINK_RE.finditer(cleaned)]
        raw_targets.extend(m.group(1).strip() for m in HTML_IMG_SRC_RE.finditer(cleaned))
        raw_targets.extend(m.group(1).strip() for m in HTML_A_HREF_RE.finditer(cleaned))

        for raw_target in raw_targets:
            if not raw_target:
                continue
            # Handle optional angle-bracket or title syntax: (path "title")
            target_part = raw_target.split()[0].strip("<>")
            lower = target_part.lower()
            if lower.startswith(("http://", "https://", "mailto:", "tel:")) or target_part.startswith("#"):
                continue

            path_only = target_part.split("#", 1)[0].split("?", 1)[0]
            if not path_only:
                continue
            path_only = urllib.parse.unquote(path_only)

            resolved = (md_path.parent / path_only).resolve(strict=False)
            try:
                resolved.relative_to(repo_resolved)
            except ValueError:
                ve.fail(f"Markdown link escapes repository root in {rel_md}: ({raw_target})")
                continue

            if not resolved.exists():
                ve.fail(f"Broken relative Markdown link in {rel_md}: ({raw_target}) -> {resolved}")

            if in_skill:
                try:
                    resolved.relative_to(skill_dir_resolved)
                except ValueError:
                    ve.fail(
                        f"Self-containment violation in {rel_md}: link ({raw_target}) escapes skills/zero-to-launch/"
                    )


def check_privacy_secrets_and_release(ve: ValidationErrors, release: bool) -> None:
    forbidden_names = {".DS_Store", "Thumbs.db"}

    for root, dirs, files in os.walk(str(REPO_ROOT), topdown=True, followlinks=False):
        root_path = Path(root)
        # Skip .git only
        if ".git" in dirs:
            dirs.remove(".git")

        for d in list(dirs):
            rel_d = (root_path / d).relative_to(REPO_ROOT).as_posix()
            if d in (".zero-to-launch", "__pycache__"):
                ve.fail(f"Forbidden directory present in repository: {rel_d}")

        for fname in files:
            fpath = root_path / fname
            rel = fpath.relative_to(REPO_ROOT).as_posix()
            if fname in forbidden_names or fpath.suffix.lower() in (".pyc", ".pyo"):
                ve.fail(f"Forbidden artifact file present in repository: {rel}")
                continue
            if ENV_FILE_RE.match(fname) and not ENV_TEMPLATE_SUFFIX_RE.search(fname):
                ve.fail(f"Forbidden secret env file present in repository: {rel}")
                continue

            try:
                raw_text = fpath.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            for line_no, line in enumerate(raw_text.splitlines(), start=1):
                if WIN_USER_PATH_RE.search(line):
                    ve.fail(f"Local Windows user profile path leaked in {rel}:{line_no}")
                if WIN_CJK_PATH_RE.search(line):
                    ve.fail(f"Local Windows non-ASCII path leaked in {rel}:{line_no}")
                if POSIX_USER_PATH_RE.search(line):
                    ve.fail(f"Local POSIX user home path leaked in {rel}:{line_no}")
                for marker in LOCAL_URI_MARKERS:
                    if marker in line:
                        ve.fail(f"Local URI scheme '{marker}' leaked in {rel}:{line_no}")
                if UUID_V4_RE.search(line):
                    ve.fail(f"UUID v4 identifier found in {rel}:{line_no} (potential private ID leak)")
                for m_em in EMAIL_RE.finditer(line):
                    domain = m_em.group(1).lower()
                    if domain not in ALLOWED_EMAIL_DOMAINS:
                        ve.fail(f"Non-placeholder email domain '@{domain}' found in {rel}:{line_no}")
                for rule_id, pat in REPO_SECRET_PATTERNS:
                    if pat.search(line):
                        ve.fail(f"Probable secret ({rule_id}) found in {rel}:{line_no}")

            if release:
                # 1. Scan .md / .json / .yml / .yaml + root LICENSE (including code blocks!) for username placeholder
                is_placeholder_target = (
                    fpath.suffix.lower() in (".md", ".json", ".yml", ".yaml")
                    or rel == "LICENSE"
                )
                if is_placeholder_target and GITHUB_PLACEHOLDER in raw_text:
                    ve.fail(f"Release check failed: unresolved placeholder '{GITHUB_PLACEHOLDER}' in {rel}")

                # 2. Scan non-template doc/config files (code stripped) for {{FILL:...}}
                is_template = rel.startswith("skills/zero-to-launch/assets/") and rel.endswith(".template.md")
                if fpath.suffix.lower() in (".md", ".json", ".yml", ".yaml") and not is_template:
                    cleaned = strip_markdown_code(raw_text) if fpath.suffix.lower() == ".md" else raw_text
                    m_fill = FILL_TOKEN_RE.search(cleaned)
                    if m_fill:
                        ve.fail(f"Release check failed: unresolved '{m_fill.group(0)}' in {rel}")


def check_python_syntax_and_help(ve: ValidationErrors) -> None:
    for py_path in sorted(REPO_ROOT.rglob("*.py")):
        if ".git" in py_path.parts:
            continue
        rel = py_path.relative_to(REPO_ROOT).as_posix()
        src = py_path.read_text(encoding="utf-8")
        try:
            ast.parse(src, filename=str(py_path))
            compile(src, str(py_path), "exec")
        except SyntaxError as exc:
            ve.fail(f"Python syntax error in {rel}: {exc}")

    for script in (INIT_SCRIPT, GATE_SCRIPT):
        proc = _run_py(script, ["--help"])
        if proc.returncode != 0:
            ve.fail(f"{script.name} --help failed (rc={proc.returncode}): {proc.stderr.strip()}")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _build_valid_full_project(proj: Path) -> None:
    proc = _run_py(INIT_SCRIPT, ["--target", str(proj), "--stage", "all"])
    assert proc.returncode == 0, f"init_workspace --stage all failed: {proc.stderr}"

    # Fill STATE.md with English YAML enums + Chinese body (verifies Language Mirroring + Immunity)
    state_md = (
        "---\n"
        "schema_version: 1\n"
        "current_stage: 5\n"
        "attempt_number: 1\n"
        "product_type: web-saas\n"
        "monetization: subscription\n"
        "cross_border: false\n"
        "redteam_rounds: 1\n"
        "validation_retries: 0\n"
        "validation_pivots: 0\n"
        "fast_track_override: false\n"
        "fast_track_unvalidated: false\n"
        "blocker_retries: {}\n"
        "---\n\n"
        "# 项目状态\n\n"
        "当前已完成核心 MVP 构建并通过内部测试。\n"
    )
    _write_text(proj / ".zero-to-launch" / "STATE.md", state_md)
    _write_text(proj / ".zero-to-launch" / "00-profile.md", "# 用户画像\n- 预算上限：$200\n")

    spec = proj / ".zero-to-launch" / "spec"
    _write_text(
        spec / "RUN_THIS_PLAN.md",
        "# 执行蓝图\n\n注意示例占位符 `{{FILL:code_span_ignored}}` 位于行内代码内，不应报错。\n\n```text\n{{FILL:fenced_ignored}}\n```\n",
    )
    _write_text(
        spec / "PRD.md",
        "# 产品需求文档\n\n产品名称：TodoPulse（支持日常 TODO 列表管理，普通词 TODO 不应误报）。\n",
    )
    _write_text(spec / "ARCHITECTURE.md", "# 架构设计\n\n前后端分离，服务端校验权限。\n")
    _write_text(
        spec / "TASKS.md",
        "# 任务清单\n\n"
        "<!-- LAUNCH_BLOCKERS_START -->\n"
        "- [x] T1 完成核心鉴权与数据库迁移\n"
        "- [x] T2 完成自动化集成测试\n"
        "<!-- LAUNCH_BLOCKERS_END -->\n\n"
        "## 迭代项（Post-MVP，非上线阻塞）\n"
        "- [ ] P1 增加暗黑主题切换\n",
    )
    _write_text(
        spec / "HUMAN_HANDOFF.md",
        "# 人工交接清单\n\n"
        "<!-- LAUNCH_BLOCKERS_START -->\n"
        "- [x] H1 绑定生产域名与自定义 SMTP\n"
        "<!-- LAUNCH_BLOCKERS_END -->\n\n"
        "## 非阻塞项\n"
        "- [ ] 后续申请商标\n",
    )
    _write_text(spec / "DEPLOY_RUNBOOK.md", "# 发布与回滚手册\n\n支持一键回滚至上一版本。\n")
    _write_text(proj / "src" / "app.py", "def re_match_something_very_long_identifier(x: str) -> bool:\n    return bool(x)\n")


def run_init_workspace_unit_tests(ve: ValidationErrors) -> None:
    with tempfile.TemporaryDirectory(prefix="ztl_init_test_") as tmp_str:
        tmp = Path(tmp_str)

        # 1. Path guards: root, home, SKILL_DIR, repo root, UNC, nonexistent parent, dir with SKILL.md
        fs_root = Path(tmp.anchor)
        bad_targets = [
            str(fs_root),
            str(Path.home()),
            str(SKILL_DIR),
            str(REPO_ROOT),
            r"\\server\share\proj",
            "//server/share/proj",
            str(tmp / "nonexistent_parent" / "child"),
        ]
        fake_skill = tmp / "fake_skill_pkg"
        fake_skill.mkdir()
        _write_text(fake_skill / "SKILL.md", "---\nname: fake\n---\n")
        bad_targets.append(str(fake_skill))

        for bad in bad_targets:
            proc = _run_py(INIT_SCRIPT, ["--target", bad, "--stage", "init"])
            if proc.returncode == 0:
                ve.fail(f"init_workspace.py FAILED to reject forbidden target: {bad}")

        # 2. Valid temp subdir: --stage init
        proj = tmp / "my_product"
        proj.mkdir()
        _write_text(proj / ".gitignore", "node_modules/\n")

        p1 = _run_py(INIT_SCRIPT, ["--target", str(proj), "--stage", "init"])
        if p1.returncode != 0:
            ve.fail(f"init_workspace --stage init failed: {p1.stderr}")
            return
        if "[WARN] .gitignore exists" not in p1.stdout:
            ve.fail("init_workspace did not warn about root .gitignore missing '.zero-to-launch/'.")
        gi = proj / ".zero-to-launch" / ".gitignore"
        if not gi.is_file() or "*\n" not in gi.read_text(encoding="utf-8"):
            ve.fail("init_workspace did not create Secure-by-Default .zero-to-launch/.gitignore with '*'.")
        if not (proj / ".zero-to-launch" / "STATE.md").is_file():
            ve.fail("init_workspace --stage init did not create STATE.md.")
        if not (proj / ".zero-to-launch" / "00-profile.md").is_file():
            ve.fail("init_workspace --stage init did not create 00-profile.md.")
        if (proj / ".zero-to-launch" / "spec").exists():
            ve.fail("init_workspace --stage init should NOT create spec/ directory.")

        # 3. Idempotency: modify STATE.md, rerun --stage init
        marker_state = "USER_CUSTOM_STATE_MARKER"
        _write_text(proj / ".zero-to-launch" / "STATE.md", marker_state)
        p2 = _run_py(INIT_SCRIPT, ["--target", str(proj), "--stage", "init"])
        if p2.returncode != 0 or (proj / ".zero-to-launch" / "STATE.md").read_text(encoding="utf-8") != marker_state:
            ve.fail("init_workspace --stage init was not idempotent (overwrote STATE.md without --force).")

        # 4. --stage spec creates .gitignore if removed + 6 spec files, preserves STATE.md
        gi.unlink()
        p3 = _run_py(INIT_SCRIPT, ["--target", str(proj), "--stage", "spec"])
        if p3.returncode != 0:
            ve.fail(f"init_workspace --stage spec failed: {p3.stderr}")
            return
        if not gi.is_file():
            ve.fail("init_workspace --stage spec failed to recreate missing .zero-to-launch/.gitignore.")
        for spec_name in (
            "RUN_THIS_PLAN.md",
            "PRD.md",
            "ARCHITECTURE.md",
            "TASKS.md",
            "HUMAN_HANDOFF.md",
            "DEPLOY_RUNBOOK.md",
        ):
            if not (proj / ".zero-to-launch" / "spec" / spec_name).is_file():
                ve.fail(f"init_workspace --stage spec missing {spec_name}.")
        if (proj / ".zero-to-launch" / "STATE.md").read_text(encoding="utf-8") != marker_state:
            ve.fail("init_workspace --stage spec unexpectedly modified STATE.md.")

        # 5. --stage spec --force overwrites spec/ ONLY, preserves STATE.md
        _write_text(proj / ".zero-to-launch" / "spec" / "PRD.md", "STALE_PRD")
        p4 = _run_py(INIT_SCRIPT, ["--target", str(proj), "--stage", "spec", "--force"])
        if p4.returncode != 0:
            ve.fail(f"init_workspace --stage spec --force failed: {p4.stderr}")
            return
        if (proj / ".zero-to-launch" / "spec" / "PRD.md").read_text(encoding="utf-8") == "STALE_PRD":
            ve.fail("init_workspace --stage spec --force did not overwrite spec/PRD.md.")
        if (proj / ".zero-to-launch" / "STATE.md").read_text(encoding="utf-8") != marker_state:
            ve.fail("init_workspace --stage spec --force violated contract by overwriting STATE.md!")


def _run_gate_json(proj: Path, extra_args: list[str] | None = None) -> tuple[int, dict[str, Any], str]:
    args = ["--target", str(proj), "--json", *(extra_args or [])]
    proc = _run_py(GATE_SCRIPT, args)
    raw = proc.stdout.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"parse_error": raw, "stderr": proc.stderr}
    return proc.returncode, data, raw + "\n" + proc.stderr


def _rule_ids(data: dict[str, Any], severity: str | None = None) -> set[str]:
    findings = data.get("findings", [])
    if severity is None:
        return {f["rule_id"] for f in findings}
    return {f["rule_id"] for f in findings if f.get("severity") == severity}


def run_check_launch_gate_unit_tests(ve: ValidationErrors, release: bool) -> None:
    # 1. Valid Chinese-prose full project passes cleanly (non-Git emits WARN only)
    with tempfile.TemporaryDirectory(prefix="ztl_gate_pass_") as tmp_str:
        proj = Path(tmp_str) / "valid_app"
        proj.mkdir()
        _build_valid_full_project(proj)
        rc, data, _ = _run_gate_json(proj)
        if rc != 0 or data.get("status") != "PASS":
            ve.fail(f"Valid full project unexpectedly failed gate: {data}")
        if "GIT_NOT_INITIALIZED" not in _rule_ids(data, "WARN"):
            ve.fail("Non-Git directory should emit WARN GIT_NOT_INITIALIZED.")

    # 2. Invalid tbd enum + unresolved {{FILL:...}} + inverted delimiters + unchecked blocker
    with tempfile.TemporaryDirectory(prefix="ztl_gate_spec_") as tmp_str:
        proj = Path(tmp_str) / "spec_fail"
        proj.mkdir()
        _build_valid_full_project(proj)
        state = (proj / ".zero-to-launch" / "STATE.md").read_text(encoding="utf-8")
        _write_text(
            proj / ".zero-to-launch" / "STATE.md",
            state.replace("product_type: web-saas", "product_type: tbd"),
        )
        _write_text(proj / ".zero-to-launch" / "spec" / "PRD.md", "# PRD\nOwner: {{FILL:owner_name}}\n")
        _write_text(
            proj / ".zero-to-launch" / "spec" / "TASKS.md",
            "<!-- LAUNCH_BLOCKERS_END -->\n- [x] Done\n<!-- LAUNCH_BLOCKERS_START -->\n",
        )
        _write_text(
            proj / ".zero-to-launch" / "spec" / "HUMAN_HANDOFF.md",
            "<!-- LAUNCH_BLOCKERS_START -->\n- [ ] Unfinished domain DNS\n<!-- LAUNCH_BLOCKERS_END -->\n",
        )
        rc, data, _ = _run_gate_json(proj)
        fails = _rule_ids(data, "FAIL")
        for expected in (
            "INVALID_PRODUCT_TYPE",
            "UNRESOLVED_PLACEHOLDER",
            "MISSING_BLOCKER_DELIMITERS",
            "UNCHECKED_LAUNCH_BLOCKER",
        ):
            if expected not in fails:
                ve.fail(f"check_launch_gate missed expected FAIL rule '{expected}': got {fails}")
        if rc == 0:
            ve.fail("check_launch_gate returned exit 0 on spec failures.")

    # 3. Secret scanning + archive/ scan + redaction + local .env/.dev.vars + prod MOCK flag
    with tempfile.TemporaryDirectory(prefix="ztl_gate_sec_") as tmp_str:
        proj = Path(tmp_str) / "sec_test"
        proj.mkdir()
        _build_valid_full_project(proj)

        # Dynamically construct fake secrets at runtime (zero literal secrets in source!)
        fake_stripe = "sk_" + "live_" + "9876543210abcdef123456"
        fake_resend = "re" + "_" + "AbCdEfGhIjKlMnOpQrStUvWx"
        fake_pem = "-----" + "BEGIN " + "PRIVATE KEY" + "-----"
        fake_db_pw = "SuperSecretDbPass99"
        fake_jwt = "XyZ9876543210SecretJwtTokenValue"
        fake_pub = "pub_secret_live_value_99887766"
        fake_archive_key = "sk-" + "proj-" + "AbCdEf0123456789_xyz987654"

        _write_text(
            proj / "src" / "leaks.ts",
            "\n".join(
                [
                    f'const a = "{fake_stripe}";',
                    f'const b = "{fake_resend}";',
                    f'// {fake_pem}',
                    f'const db = "postgres://admin:{fake_db_pw}@db.example.com:5432/app";',
                    f'const JWT_SECRET = "{fake_jwt}";',
                ]
            )
            + "\n",
        )
        # Archive directory MUST still be scanned!
        _write_text(proj / ".zero-to-launch" / "archive" / "attempt-1.md", f"old key: {fake_archive_key}\n")
        # Untracked local .env.local holding server secret (allowed) + NEXT_PUBLIC_*SECRET* (MUST FAIL!) + local MOCK_AI (allowed)
        _write_text(
            proj / ".env.local",
            f"STRIPE_SECRET_KEY={fake_stripe}\n"
            f"NEXT_PUBLIC_API_SECRET={fake_pub}\n"
            "MOCK_AI=true\n",
        )
        # Untracked .dev.vars holding server secret (allowed)
        _write_text(proj / ".dev.vars", f"RESEND_API_KEY={fake_resend}\n")
        # Production config enabling MOCK_PAYMENT=true (MUST FAIL!)
        _write_text(proj / ".env.production", "MOCK_PAYMENT=true\n")

        rc, data, raw_out = _run_gate_json(proj)
        fails = _rule_ids(data, "FAIL")
        for expected in (
            "LEAKED_STRIPE_LIVE_KEY",
            "LEAKED_RESEND_KEY",
            "LEAKED_PEM_PRIVATE_KEY",
            "LEAKED_DB_URI_PASSWORD",
            "HARDCODED_SERVER_SECRET",
            "LEAKED_OPENAI_PROJECT_KEY",
            "FRONTEND_PUBLIC_SECRET",
            "PROD_MOCK_FLAG_ENABLED",
        ):
            if expected not in fails:
                ve.fail(f"Secret scan missed expected rule '{expected}': got {fails}")
        if rc == 0:
            ve.fail("Secret scan unexpectedly exited 0.")

        # Ensure ZERO plaintext secret leaked into stdout/stderr/JSON!
        for secret_val in (fake_stripe, fake_resend, fake_db_pw, fake_jwt, fake_pub, fake_archive_key):
            if secret_val in raw_out:
                ve.fail("CRITICAL: check_launch_gate leaked plaintext secret in output!")

        # Also verify Markdown output leaks zero plaintext secrets
        md_proc = _run_py(GATE_SCRIPT, ["--target", str(proj)])
        for secret_val in (fake_stripe, fake_resend, fake_db_pw, fake_jwt, fake_pub, fake_archive_key):
            if secret_val in md_proc.stdout or secret_val in md_proc.stderr:
                ve.fail("CRITICAL: check_launch_gate leaked plaintext secret in Markdown output!")

    # 4. Packaging isolation & Fail-Closed --max-files & standalone mode
    with tempfile.TemporaryDirectory(prefix="ztl_gate_pkg_") as tmp_str:
        proj = Path(tmp_str) / "pkg_test"
        proj.mkdir()
        _build_valid_full_project(proj)

        _write_text(proj / "Dockerfile", "FROM python:3.12-slim\n")
        _write_text(proj / "wrangler.jsonc", '{ "name": "demo" }\n')
        _write_text(proj / "package.json", '{"name": "demo-cli", "version": "0.1.0"}\n')
        _write_text(proj / "dist" / ".zero-to-launch" / "STATE.md", "leaked")

        rc, data, _ = _run_gate_json(proj)
        fails = _rule_ids(data, "FAIL")
        for expected in (
            "MISSING_DOCKERIGNORE_EXCLUSION",
            "PAAS_ROOT_IGNORE_MISSING",
            "NPM_PUBLISH_LEAK_RISK",
            "BUILD_OUTPUT_ZTL_LEAK",
        ):
            if expected not in fails:
                ve.fail(f"Packaging check missed expected rule '{expected}': got {fails}")

        # Fix Docker, Wrangler (via root .gitignore), package.json, and remove dist leak
        _write_text(proj / ".dockerignore", ".zero-to-launch\n.env\n")
        _write_text(proj / ".gitignore", ".zero-to-launch/\n.env\n.dev.vars\n")
        _write_text(proj / "vercel.json", "{}\n")
        _write_text(proj / "package.json", '{"name": "demo-cli", "private": true}\n')
        shutil.rmtree(proj / "dist")
        rc_ok, data_ok, _ = _run_gate_json(proj)
        if rc_ok != 0 or data_ok.get("status") != "PASS":
            ve.fail(f"Fixed packaging project should PASS, got: {data_ok}")

        # Dedicated .assetsignore missing .dev.vars must FAIL
        _write_text(proj / ".assetsignore", ".zero-to-launch/\n")
        rc_cf, data_cf, _ = _run_gate_json(proj)
        if rc_cf == 0 or "PAAS_IGNORE_MISSING_EXCLUSION" not in _rule_ids(data_cf, "FAIL"):
            ve.fail(f"Incomplete .assetsignore should trigger PAAS_IGNORE_MISSING_EXCLUSION: {data_cf}")
        (proj / ".assetsignore").unlink()

        # Fail-Closed --max-files 1
        rc_cap, data_cap, _ = _run_gate_json(proj, ["--max-files", "1"])
        if rc_cap == 0 or "INCOMPLETE_SCAN" not in _rule_ids(data_cap, "FAIL"):
            ve.fail(f"--max-files 1 should Fail-Closed with INCOMPLETE_SCAN: {data_cap}")

        # Standalone mode on a clean repo without .zero-to-launch/
        standalone_proj = Path(tmp_str) / "existing_app"
        standalone_proj.mkdir()
        _write_text(standalone_proj / "index.js", "console.log('hello');\n")
        rc_st, data_st, _ = _run_gate_json(standalone_proj, ["--mode", "standalone"])
        if rc_st != 0 or data_st.get("status") != "PASS":
            ve.fail(f"Standalone mode failed on clean existing repo: {data_st}")

    # 5. Git-enabled tests (required in --release and CI)
    git_exe = shutil.which("git")
    if not git_exe:
        if release:
            ve.fail("Release check requires 'git' on PATH to execute Git safety unit tests.")
        else:
            ve.warn("Skipping Git-enabled unit tests because 'git' is not yet installed in PATH.")
        return

    with tempfile.TemporaryDirectory(prefix="ztl_gate_git_") as tmp_str:
        proj = Path(tmp_str) / "git_app"
        proj.mkdir()
        _build_valid_full_project(proj)

        def _git(*gargs: str) -> None:
            p = subprocess.run(
                [git_exe, *gargs],
                cwd=str(proj),
                capture_output=True,
                text=True,
                timeout=15,
                shell=False,
            )
            if p.returncode != 0:
                raise RuntimeError(f"git {' '.join(gargs)} failed: {p.stderr}")

        _git("init", "-b", "main")
        _git("config", "user.name", "Test Bot")
        _git("config", "user.email", "test@example.com")

        # Properly ignored .env and .dev.vars + tracked .env.example + allowlisted spec/PRD.md -> PASS
        _write_text(proj / ".gitignore", ".env\n.env.*\n!.env.example\n.dev.vars\n!.dev.vars.example\n")
        _write_text(proj / ".env", "API_KEY=local_only_value_12345678\n")
        _write_text(proj / ".dev.vars", "CF_SECRET=local_only_value_12345678\n")
        _write_text(proj / ".env.example", "API_KEY=your_api_key_here\n")
        _write_text(proj / ".dev.vars.example", "CF_SECRET=your_cf_secret_here\n")
        _write_text(
            proj / ".zero-to-launch" / ".gitignore",
            "*\n!.gitignore\n!spec/\n!spec/RUN_THIS_PLAN.md\n!spec/PRD.md\n!spec/ARCHITECTURE.md\n!spec/TASKS.md\n!spec/DEPLOY_RUNBOOK.md\n",
        )
        _git("add", ".gitignore", ".env.example", ".dev.vars.example", "src/app.py", ".zero-to-launch/.gitignore", ".zero-to-launch/spec/PRD.md")
        rc_ok, data_ok, _ = _run_gate_json(proj)
        if rc_ok != 0 or data_ok.get("status") != "PASS":
            ve.fail(f"Clean Git repo with allowlisted spec/ and ignored .env/.dev.vars failed: {data_ok}")

        # Now violate: unignored ?? .env.staging + ?? .dev.vars.local + tracked .zero-to-launch/00-profile.md + tracked .env
        _write_text(proj / ".gitignore", "# empty ignore\n")
        _write_text(proj / ".dev.vars.local", "SECRET=abc1234567890\n")
        _git("add", "-f", ".env", ".zero-to-launch/00-profile.md")
        rc_bad, data_bad, _ = _run_gate_json(proj)
        fails = _rule_ids(data_bad, "FAIL")
        for expected in ("TRACKED_ENV_SECRET_FILE", "TRACKED_ZTL_PRIVATE_FILE", "UNIGNORED_ENV_FILE"):
            if expected not in fails:
                ve.fail(f"Git safety check missed expected rule '{expected}': got {fails}")
        if rc_bad == 0:
            ve.fail("Git safety check unexpectedly exited 0 on tracked secret/private files.")


def check_no_bytecode_left_behind(ve: ValidationErrors) -> None:
    for root, dirs, files in os.walk(str(REPO_ROOT), topdown=True, followlinks=False):
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            ve.fail(f"Bytecode directory generated during validation: {Path(root) / '__pycache__'}")
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                ve.fail(f"Bytecode file generated during validation: {Path(root) / f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate zero-to-launch repository metadata, links, privacy, and unit tests."
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Enforce strict release gates (zero username/FILL placeholders, concrete repo URL, Git tests required).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = parse_args(argv)
    ve = ValidationErrors()

    self_test_yaml_parser(ve)
    check_required_files(ve)
    check_skill_and_plugin_metadata(ve, release=args.release)
    check_workflow_security(ve)
    check_markdown_links_and_containment(ve)
    check_privacy_secrets_and_release(ve, release=args.release)
    check_python_syntax_and_help(ve)
    run_init_workspace_unit_tests(ve)
    run_check_launch_gate_unit_tests(ve, release=args.release)
    check_no_bytecode_left_behind(ve)

    mode_label = "RELEASE" if args.release else "DEV"
    for w in ve.warnings:
        print(f"[WARN] {w}")
    if ve.errors:
        print(f"[FAIL] Repository validation ({mode_label}) failed with {len(ve.errors)} error(s):")
        for err in ve.errors:
            print(f"  - {err}")
        return 1

    print(f"[PASS] Repository validation ({mode_label}) succeeded with 0 errors and {len(ve.warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
