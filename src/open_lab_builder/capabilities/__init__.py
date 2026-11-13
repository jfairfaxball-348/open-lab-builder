"""Running capabilities from their manifests, for build-time self-tests only."""

from .invoker import (
    CAPABILITY_ERROR,
    EXECUTION_ERROR,
    INVALID_INPUT,
    INVALID_OUTPUT,
    TIMEOUT,
    UNSUPPORTED_INTERFACE,
    InvocationResult,
    entrypoint_file,
    invoke,
    run_self_test,
)

__all__ = [
    "CAPABILITY_ERROR",
    "EXECUTION_ERROR",
    "INVALID_INPUT",
    "INVALID_OUTPUT",
    "TIMEOUT",
    "UNSUPPORTED_INTERFACE",
    "InvocationResult",
    "entrypoint_file",
    "invoke",
    "run_self_test",
]
