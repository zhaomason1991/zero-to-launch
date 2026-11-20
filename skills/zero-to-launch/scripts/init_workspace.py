#!/usr/bin/env python3
"""Initialize a `.zero-to-launch/` workspace safely with cross-platform path guards.

Standard library only (Python 3.9+). Uses UTF-8 I/O and atomic file replacement.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_DIR / "assets"

SPEC_TEMPLATES = (
    ("RUN_THIS_PLAN.template.md", "RUN_THIS_PLAN.md"),
    ("PRD.template.md", "PRD.md"),
    ("ARCHITECTURE.template.md", "ARCHITECTURE.md"),
    ("TASKS.template.md", "TASKS.md"),
    ("HUMAN_HANDOFF.template.md", "HUMAN_HANDOFF.md"),
    ("DEPLOY_RUNBOOK.template.md", "DEPLOY_RUNBOOK.md"),
)

DEFAULT_PRIVATE_GITIGNORE = (
    "# Secure-by-Default: ignore all private strategy, profile, and handoff files.\n"
    "# Never commit 00-profile.md, HUMAN_HANDOFF.md, 03-validation-log.md, ops/, or backups/.\n"
    "# See spec/RUN_THIS_PLAN.md for the exact 8-line allowlist if a team intentionally tracks spec/.\n"
    "*\n"
)

DEFAULT_PROFILE_TEMPLATE = (
    "# Stage 0: User Profile & Hard Constraints\n\n"
    "- **North Star & Commercial Mode**: {{FILL:north_star}}\n"
    "- **Team & Technical Baseline**: {{FILL:team_and_tech}}\n"
    "- **Employment Hygiene / Daytime SLA**: {{FILL:employment_hygiene}}\n"
    "- **Hard Cash Cap**: {{FILL:cash_cap}}\n"
    "- **Total & Effective Pre-Launch Hours (70%)**: {{FILL:effective_hours}}\n"
    "- **Post-Launch Ops Hours / Week**: {{FILL:post_launch_hours}}\n"
    "- **Unfair Advantages & Existing Reach Assets**: {{FILL:advantages_and_reach}}\n"
    "- **Psychological Red Lines**: {{FILL:psychological_red_lines}}\n"
    "- **Audience Geography & Developer Jurisdiction**: {{FILL:geography_and_jurisdiction}}\n"
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _norm(path: Path) -> Path:
    return Path(os.path.normcase(str(path.resolve(strict=False))))


def _is_same_or_child(candidate: Path, base: Path) -> bool:
    c = _norm(candidate)
    b = _norm(base)
    try:
        return c == b or c.is_relative_to(b)
    except AttributeError:
        c_str = str(c)
        b_str = str(b).rstrip("\\/")
        return c_str == b_str or c_str.startswith(b_str + os.sep)


def validate_target_dir(raw_target: str) -> Path:
    if not raw_target or not raw_target.strip():
        raise ValueError("Target directory must be non-empty.")

    # Reject UNC network paths explicitly (\\server\share or //server/share)
    if raw_target.startswith("\\\\") or raw_target.startswith("//"):
        raise ValueError(f"Refusing UNC network path as target: {raw_target}")

    expanded = Path(raw_target).expanduser()
    resolved = expanded.resolve(strict=False)

    # Require target or its immediate parent to exist (prevents typo deep mkdir)
    if not resolved.exists() and not resolved.parent.exists():
        raise ValueError(
            f"Parent directory does not exist for target: {resolved}. "
            "Create the parent folder first or pass an existing project directory."
        )
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"Target path exists and is not a directory: {resolved}")

    # 1. Exact-match ONLY bans: filesystem roots (C:\, D:\, /) and user home (~)
    if _norm(resolved) == _norm(resolved.parent):
        raise ValueError(f"Refusing filesystem root as target: {resolved}")

    try:
        home_dir = Path.home().resolve(strict=False)
        if _norm(resolved) == _norm(home_dir):
            raise ValueError(f"Refusing user home directory as target: {resolved}")
    except RuntimeError:
        home_dir = None

    # 2. Subtree bans: OS system directories (do NOT ban broad /var or /tmp)
    system_subtrees: list[Path] = [
        Path("/etc"),
        Path("/usr"),
        Path("/bin"),
        Path("/sbin"),
        Path("/System"),
        Path("/Library"),
        Path("/proc"),
        Path("/sys"),
        Path("/dev"),
        Path("/var/log"),
        Path("/var/lib"),
        Path("/var/run"),
    ]
    for env_key in ("WINDIR", "SystemRoot", "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA"):
        val = os.environ.get(env_key)
        if val:
            system_subtrees.append(Path(val))

    for sys_dir in system_subtrees:
        if _is_same_or_child(resolved, sys_dir):
            raise ValueError(f"Refusing OS system directory or subtree: {resolved}")

    # 3. Subtree bans: AI agent global config roots
    if home_dir is not None:
        for cfg_name in (".gemini", ".claude", ".cursor", ".codex", ".agents"):
            cfg_dir = home_dir / cfg_name
            if _is_same_or_child(resolved, cfg_dir):
                raise ValueError(f"Refusing AI agent config directory or subtree: {resolved}")

    # 4. Subtree bans: SKILL_DIR itself or its containing Skill repository root
    if _is_same_or_child(resolved, SKILL_DIR):
        raise ValueError(f"Refusing SKILL_DIR or its subtree as target: {resolved}")

    if SKILL_DIR.parent.name == "skills":
        repo_root = SKILL_DIR.parent.parent
        if (repo_root / "plugin.json").exists() and _is_same_or_child(resolved, repo_root):
            raise ValueError(f"Refusing zero-to-launch repository directory as target: {resolved}")

    # Also refuse any target directory that directly houses SKILL.md or plugin.json
    if resolved.exists() and (
        (resolved / "SKILL.md").is_file() or (resolved / "plugin.json").is_file()
    ):
        raise ValueError(
            f"Refusing skill/plugin package directory containing SKILL.md or plugin.json: {resolved}"
        )

    return resolved


def atomic_write_text(dest: Path, content: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".ztl_tmp_", dir=str(dest.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(str(tmp_path), str(dest))
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def write_if_allowed(dest: Path, content: str, force: bool) -> str:
    if dest.exists() and not force:
        return "skipped"
    atomic_write_text(dest, content)
    return "overwritten" if force and dest.exists() else "created"


def check_root_ignore_warnings(target: Path) -> list[str]:
    warnings: list[str] = []
    ignore_candidates = (
        ".gitignore",
        ".dockerignore",
        ".npmignore",
        ".vercelignore",
        ".cfignore",
        ".assetsignore",
    )
    for name in ignore_candidates:
        fpath = target / name
        if fpath.is_file():
            try:
                text = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if ".zero-to-launch" not in text:
                warnings.append(
                    f"[WARN] {name} exists at project root but does not list '.zero-to-launch/'."
                )
    return warnings


def init_workspace(target: Path, stage: str, force: bool) -> int:
    target.mkdir(parents=True, exist_ok=True)
    ztl_dir = target / ".zero-to-launch"
    ops_dir = ztl_dir / "ops"
    spec_dir = ztl_dir / "spec"
    ztl_dir.mkdir(parents=True, exist_ok=True)

    actions: list[tuple[str, Path]] = []

    # Always ensure .zero-to-launch/.gitignore exists (never overwrite user customization on --stage spec)
    gitignore_path = ztl_dir / ".gitignore"
    if not gitignore_path.exists():
        atomic_write_text(gitignore_path, DEFAULT_PRIVATE_GITIGNORE)
        actions.append(("created", gitignore_path))
    else:
        actions.append(("kept", gitignore_path))

    if stage in ("init", "all"):
        ops_dir.mkdir(parents=True, exist_ok=True)
        state_src = ASSETS_DIR / "STATE.template.md"
        if not state_src.is_file():
            raise FileNotFoundError(f"Missing template: {state_src}")
        state_content = state_src.read_text(encoding="utf-8")
        state_dest = ztl_dir / "STATE.md"
        state_force = force and stage in ("init", "all")
        existed = state_dest.exists()
        if not existed or state_force:
            atomic_write_text(state_dest, state_content)
            actions.append(("overwritten" if existed else "created", state_dest))
        else:
            actions.append(("skipped", state_dest))

        profile_dest = ztl_dir / "00-profile.md"
        existed_prof = profile_dest.exists()
        if not existed_prof or state_force:
            atomic_write_text(profile_dest, DEFAULT_PROFILE_TEMPLATE)
            actions.append(("overwritten" if existed_prof else "created", profile_dest))
        else:
            actions.append(("skipped", profile_dest))

    if stage in ("spec", "all"):
        spec_dir.mkdir(parents=True, exist_ok=True)
        # Note: --stage spec --force ONLY overwrites spec/ templates, NEVER STATE.md or logs!
        for template_name, out_name in SPEC_TEMPLATES:
            src = ASSETS_DIR / template_name
            if not src.is_file():
                raise FileNotFoundError(f"Missing template: {src}")
            content = src.read_text(encoding="utf-8")
            dest = spec_dir / out_name
            existed_spec = dest.exists()
            if not existed_spec or force:
                atomic_write_text(dest, content)
                actions.append(("overwritten" if existed_spec else "created", dest))
            else:
                actions.append(("skipped", dest))

    print(f"[OK] Workspace initialized: {ztl_dir} (stage={stage})")
    for status, path in actions:
        rel = path.relative_to(target)
        print(f"  - {status:11s} {rel.as_posix()}")

    for warn in check_root_ignore_warnings(target):
        print(warn)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely initialize `.zero-to-launch/` state and spec files inside a target project directory."
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Target product project directory (default: current working directory).",
    )
    parser.add_argument(
        "--stage",
        choices=("init", "spec", "all"),
        default="init",
        help="Which templates to initialize: init (STATE + 00-profile + .gitignore), spec (6 spec files), or all.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files within the selected stage scope only.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = parse_args(argv)
    try:
        target = validate_target_dir(args.target)
        return init_workspace(target, args.stage, args.force)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
