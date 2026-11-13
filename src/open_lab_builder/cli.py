"""``olb`` command-line interface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .contracts import validate_file
from .health import STATE_PATH, example_files, run_checks
from .paths import repo_root


def _cmd_validate(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.paths]
    if not paths:
        root = repo_root()
        if root is None:
            print("No paths given and no source checkout to take examples from.", file=sys.stderr)
            return 2
        paths = [p for files in example_files(root).values() for p in files]
    failures = 0
    for path in paths:
        if not path.is_file():
            print(f"FAIL  {path}: file not found")
            failures += 1
            continue
        issues = validate_file(path)
        print(f"{'FAIL' if issues else 'ok  '}  {path}")
        for issue in issues:
            print(f"        {issue}")
        failures += bool(issues)
    print(f"{len(paths) - failures} valid, {failures} invalid")
    return 1 if failures else 0


def _cmd_diagnose(args: argparse.Namespace) -> int:
    from .diagnostics import collect, render_text, sanitise

    raw = collect()
    clean = sanitise(raw)
    if args.save_raw:
        root = repo_root() or Path.cwd()
        target = root / ".local" / "diagnostics"
        target.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        (target / f"raw-{stamp}.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")
        print("Raw report saved under .local/diagnostics/ (ignored by Git).", file=sys.stderr)
    print(json.dumps(clean, indent=2) if args.json else render_text(clean))
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    failed = False
    for result in run_checks():
        if result.skipped:
            print(f"SKIP  {result.name} ({result.skipped})")
            continue
        print(f"{'ok  ' if result.ok else 'FAIL'}  {result.name}")
        for problem in result.problems:
            print(f"        {problem}")
        failed |= not result.ok
    if args.tests:
        code = subprocess.call([sys.executable, "-m", "pytest"], cwd=repo_root())  # noqa: S603
        print(f"{'ok  ' if code == 0 else 'FAIL'}  Test suite")
        failed |= code != 0
    print("Health check " + ("FAILED" if failed else "passed"))
    return 1 if failed else 0


def _cmd_state(_: argparse.Namespace) -> int:
    root = repo_root()
    if root is None:
        print("No source checkout found.", file=sys.stderr)
        return 2
    state = json.loads((root / STATE_PATH).read_text(encoding="utf-8"))
    done = ", ".join(m["id"] for m in state["completed_milestones"]) or "none"
    nxt = state["next_milestone"]
    print(f"Completed:  {done}")
    print(f"Next:       {nxt['id']} {nxt.get('title', '')} (in {nxt['repository']})")
    print(f"Validation: {state['validation']['status']} at {state['validation']['ran_at']}")
    for label, key in (("Blocker", "blockers"), ("Known issue", "known_issues"),
                       ("Open decision", "open_decisions")):
        for item in state[key]:
            human = " [needs human]" if item.get("needs_human") else ""
            print(f"{label}: {item['id']}{human} - {item['summary']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="olb", description="Open Laboratory World Builder.")
    parser.add_argument("--version", action="version", version=f"olb {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate", help="Validate contract documents (.json) or event logs (.jsonl)."
    )
    validate.add_argument("paths", nargs="*", help="Files to validate. Default: all examples.")
    validate.set_defaults(func=_cmd_validate)

    diagnose = commands.add_parser(
        "diagnose", help="Audit this machine. Prints a sanitised report."
    )
    diagnose.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    diagnose.add_argument(
        "--save-raw", action="store_true",
        help="Also save the unsanitised report under .local/diagnostics/ (never committed).",
    )
    diagnose.set_defaults(func=_cmd_diagnose)

    check = commands.add_parser("check", help="Run the project health check.")
    check.add_argument("--tests", action="store_true", help="Also run the test suite.")
    check.set_defaults(func=_cmd_check)

    state = commands.add_parser("state", help="Show development progress and the next milestone.")
    state.set_defaults(func=_cmd_state)
    return parser


def main(argv: list[str] | None = None) -> int:
    # Windows consoles may default to a legacy code page.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
