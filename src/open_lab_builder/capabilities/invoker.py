"""Minimal capability invoker, used by the Builder only to run self-tests.

This is not the Simulation's tool host and gives no isolation beyond a child
process and a timeout. It exists so that a world release is only produced
from capabilities that demonstrably work. The invocation protocol it follows
is documented in ``docs/architecture/CONTRACTS.md``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

DEFAULT_TIMEOUT_S = 30
_RUNNER = Path(__file__).with_name("_python_runner.py")

# Error kinds. ``capability_error`` is the capability declining the request
# (for example division by zero); the others are faults around it.
INVALID_INPUT = "invalid_input"
CAPABILITY_ERROR = "capability_error"
EXECUTION_ERROR = "execution_error"
TIMEOUT = "timeout"
INVALID_OUTPUT = "invalid_output"
UNSUPPORTED_INTERFACE = "unsupported_interface"


@dataclass(frozen=True)
class InvocationResult:
    status: str  # "ok" or "error"
    output: dict[str, Any] | None = None
    error_kind: str | None = None
    message: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == "ok"


def _error(kind: str, message: str) -> InvocationResult:
    return InvocationResult("error", error_kind=kind, message=message)


def _first_error(schema: dict[str, Any], instance: Any) -> str | None:
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda e: [str(part) for part in e.absolute_path],
    )
    if not errors:
        return None
    where = "".join(f"/{part}" for part in errors[0].absolute_path) or "<root>"
    return f"{where}: {errors[0].message}"


def entrypoint_file(capability_dir: Path, entrypoint: str) -> Path:
    """The file a ``python`` entrypoint names, relative to the capability directory."""
    module = entrypoint.split(":")[0]
    return capability_dir.joinpath(*module.split(".")).with_suffix(".py")


def _command(manifest: dict[str, Any], capability_dir: Path) -> list[str] | InvocationResult:
    invocation = manifest["invocation"]
    interface = invocation["interface"]
    if interface == "python":
        if not entrypoint_file(capability_dir, invocation["entrypoint"]).is_file():
            return _error(EXECUTION_ERROR, f"entrypoint file not found: {invocation['entrypoint']}")
        # -I: ignore PYTHON* variables and the user site, and keep the working
        # directory off the import path. -B: never write bytecode into a release.
        return [sys.executable, "-I", "-B", str(_RUNNER), invocation["entrypoint"]]
    if interface == "subprocess":
        command = list(invocation["command"])
        # "python" on PATH may be a different interpreter, or absent.
        if command[0] == "python":
            command[0] = sys.executable
        return command
    return _error(
        UNSUPPORTED_INTERFACE, f"the Builder cannot invoke '{interface}' capabilities"
    )


def invoke(
    manifest: dict[str, Any],
    capability_dir: Path,
    arguments: Any,
    *,
    timeout_s: float | None = None,
    workspace: Path | None = None,
    service=None,
) -> InvocationResult:
    """Invoke a capability once. The manifest must already be a valid capability document."""
    problem = _first_error(manifest["input_schema"], arguments)
    if problem:
        return _error(INVALID_INPUT, problem)
    if manifest["invocation"] == {"interface": "mcp", "server": "supervisor-gateway",
                                  "tool": "models.ask"} and service is not None:
        payload = service(arguments)
        problem = _first_error(manifest["output_schema"], payload)
        return (_error(INVALID_OUTPUT, problem) if problem
                else InvocationResult("ok", output=payload))
    command = _command(manifest, capability_dir)
    if isinstance(command, InvocationResult):
        return command
    if timeout_s is None:
        timeout_s = manifest.get("resources", {}).get("timeout_s", DEFAULT_TIMEOUT_S)

    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    environment.pop("OPEN_LAB_WORKSPACE", None)
    if workspace is not None and manifest["permissions"]["filesystem"] != "none":
        environment["OPEN_LAB_WORKSPACE"] = str(workspace.resolve())
    try:
        done = subprocess.run(  # noqa: S603 - argument vector, never a shell
            command,
            input=json.dumps(arguments).encode("utf-8"),
            capture_output=True,
            cwd=capability_dir,
            # A release directory must stay byte-identical after a self-test.
            env=environment,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _error(TIMEOUT, f"no result within {timeout_s} s")
    except OSError as error:
        return _error(EXECUTION_ERROR, f"could not start: {error.strerror or error}")

    try:
        payload = json.loads(done.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None
    if done.returncode != 0:
        reported = isinstance(payload, dict) and set(payload) == {"error"}
        if reported and isinstance(payload["error"], str):
            return _error(CAPABILITY_ERROR, payload["error"])
        lines = done.stderr.decode("utf-8", errors="replace").strip().splitlines()
        detail = lines[-1] if lines else "no error output"
        return _error(EXECUTION_ERROR, f"exit status {done.returncode}: {detail}")
    if payload is None:
        return _error(INVALID_OUTPUT, "output is not JSON")
    problem = _first_error(manifest["output_schema"], payload)
    if problem:
        return _error(INVALID_OUTPUT, problem)
    return InvocationResult("ok", output=payload)


def run_self_test(manifest: dict[str, Any], capability_dir: Path) -> list[str]:
    """Run the manifest's self-test demonstrations. An empty list means they all passed."""
    problems = []
    demonstrations = {demo["id"]: demo for demo in manifest["demonstrations"]}
    timeout_s = manifest["self_test"].get("timeout_s")
    for demo_id in manifest["self_test"]["demonstrations"]:
        demo = demonstrations[demo_id]
        # Each demonstration starts with an empty disposable workspace. Never
        # inherit an operator's workspace or write into the immutable release.
        with tempfile.TemporaryDirectory(prefix="olb-self-test-") as directory:
            result = invoke(manifest, capability_dir, demo["input"], timeout_s=timeout_s,
                            workspace=Path(directory),
                            service=lambda arguments: {"text": "Build-time fake specialist reply."})
        label = f"{manifest['id']} demonstration '{demo_id}'"
        if not result.ok:
            problems.append(f"{label}: {result.error_kind}: {result.message}")
        elif demo.get("deterministic", True) and result.output != demo["expected_output"]:
            problems.append(
                f"{label}: expected {json.dumps(demo['expected_output'], sort_keys=True)}, "
                f"got {json.dumps(result.output, sort_keys=True)}"
            )
    return problems
