"""Child-process side of the ``python`` invocation interface.

Run as ``python -I _python_runner.py <module:function>`` with the capability
directory as the working directory. Standard library only, and no imports
from the Builder: this file is executed by path, not as part of the package.

Protocol (the same one ``subprocess`` capabilities speak): argument object as
JSON on stdin; exit 0 with the result as JSON on stdout; exit 1 with
``{"error": message}`` on stdout when the capability raises ``ValueError``.
Any other exception is a crash: traceback on stderr, exit 2.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    module_name, function_name = sys.argv[1].split(":")
    arguments = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    try:
        path = Path.cwd().joinpath(*module_name.split(".")).with_suffix(".py")
        spec = importlib.util.spec_from_file_location("capability_entrypoint", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {path.name}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function = getattr(module, function_name)
        try:
            payload, status = function(arguments), 0
        except ValueError as error:
            payload, status = {"error": str(error)}, 1
        encoded = json.dumps(payload).encode("utf-8")
    except Exception:  # noqa: BLE001 - every crash must become exit status 2
        traceback.print_exc()
        return 2
    sys.stdout.buffer.write(encoded)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
