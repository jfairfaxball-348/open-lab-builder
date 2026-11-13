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
from .paths import data_root, repo_root


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


def _cmd_world_build(args: argparse.Namespace) -> int:
    from .worlds import BuildError, build_world

    if args.publish:
        out = data_root() / "worlds"
    elif args.out:
        out = Path(args.out)
    else:
        out = (repo_root() or Path.cwd()) / "releases"
    try:
        result = build_world(Path(args.source), out)
    except BuildError as error:
        print("Build FAILED; no release was written.")
        for problem in error.problems:
            print(f"        {problem}")
        return 1
    manifest = result.manifest
    verb = "Already built, unchanged:" if result.reused else "Built"
    print(f"{verb} {manifest['world_id']} {manifest['version']} "
          f"({len(manifest['capabilities'])} capabilities, self-tests passed)")
    print(f"  directory:      {result.release_dir}")
    print(f"  content digest: sha256:{manifest['content_digest']['value']}")
    return 0


def _cmd_world_verify(args: argparse.Namespace) -> int:
    from .worlds import verify_release

    release = Path(args.release_dir)
    if not release.is_dir():
        print(f"FAIL  {release}: not a directory")
        return 1
    problems = verify_release(release, self_tests=args.self_test)
    for problem in problems:
        print(f"        {problem}")
    tested = " and self-tests passed" if args.self_test else ""
    print("Release FAILED verification" if problems else f"Release is intact{tested}")
    return 1 if problems else 0


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

    world = commands.add_parser("world", help="Build or verify a world release.")
    world_commands = world.add_subparsers(dest="world_command", required=True)
    build = world_commands.add_parser(
        "build", help="Validate a world source tree, run its self-tests and write a release."
    )
    build.add_argument("source", help="World source directory, e.g. worlds/minimal.")
    where = build.add_mutually_exclusive_group()
    where.add_argument("--out", help="Directory to build into. Default: releases/ in the checkout.")
    where.add_argument(
        "--publish", action="store_true",
        help="Build into the shared data root ($OPEN_LAB_DATA/worlds) for the Simulation to use.",
    )
    build.set_defaults(func=_cmd_world_build)
    verify = world_commands.add_parser(
        "verify", help="Check a built release against its manifest and digests."
    )
    verify.add_argument("release_dir", help="Release directory: <out>/<world_id>/<version>.")
    verify.add_argument(
        "--self-test", action="store_true", help="Also re-run every capability self-test."
    )
    verify.set_defaults(func=_cmd_world_verify)

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
