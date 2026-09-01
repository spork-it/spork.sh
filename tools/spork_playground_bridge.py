"""Bounded JSON bridge between the browser worker and Spork's REPL backend."""

from __future__ import annotations

import contextlib
import io
import json
import traceback as traceback_module
from importlib.metadata import version
from typing import Any

from spork.compiler import MACRO_ENV
from spork.repl.backend import ReplBackend, ResultType

MAX_SOURCE_BYTES = 64 * 1024
MAX_OUTPUT_CHARS = 64 * 1024
MAX_VALUE_CHARS = 64 * 1024
MAX_TRACEBACK_CHARS = 32 * 1024


class BoundedWriter(io.TextIOBase):
    """A text stream that retains a fixed prefix and records truncation."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.parts: list[str] = []
        self.length = 0
        self.truncated = False

    @property
    def encoding(self) -> str:
        return "utf-8"

    def writable(self) -> bool:
        return True

    def write(self, value: str) -> int:
        if not isinstance(value, str):
            raise TypeError("playground output must be text")
        original_length = len(value)
        remaining = self.limit - self.length
        if remaining > 0:
            kept = value[:remaining]
            self.parts.append(kept)
            self.length += len(kept)
        if original_length > max(remaining, 0):
            self.truncated = True
        return original_length

    def value(self) -> str:
        result = "".join(self.parts)
        if self.truncated:
            result += "\n… output truncated by playground …\n"
        return result


def bounded_text(value: Any, limit: int, label: str) -> tuple[str, bool]:
    text = str(value)
    if len(text) <= limit:
        return text, False
    return text[:limit] + f"\n… {label} truncated by playground …", True


def format_value(value: Any) -> tuple[str, bool]:
    if value is None:
        text = "nil"
    elif value is True:
        text = "true"
    elif value is False:
        text = "false"
    elif isinstance(value, str):
        text = repr(value)
    else:
        text = str(value)
    return bounded_text(text, MAX_VALUE_CHARS, "value")


_backend = ReplBackend()


def evaluate(source: str) -> str:
    """Evaluate one request and return a bounded JSON response."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        return json.dumps(
            {
                "kind": "error",
                "errorType": "SourceLimitError",
                "error": f"Source exceeds the {MAX_SOURCE_BYTES}-byte playground limit",
                "stdout": "",
                "stderr": "",
                "namespace": _backend.state.namespace,
                "truncated": [],
            },
            separators=(",", ":"),
        )

    stdout = BoundedWriter(MAX_OUTPUT_CHARS)
    stderr = BoundedWriter(MAX_OUTPUT_CHARS)
    bridge_error: BaseException | None = None
    result = None
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            # spork-lang 0.6.1's backend stores session macros separately while
            # one macro-expansion call still consults the process environment.
            # Keep the two views synchronized until that release is retired.
            MACRO_ENV.update(_backend.macro_env)
            result = _backend.eval(source, capture_output=False)
            MACRO_ENV.update(_backend.macro_env)
        except BaseException as error:  # User code may raise SystemExit or KeyboardInterrupt.
            bridge_error = error

    truncated: list[str] = []
    if stdout.truncated:
        truncated.append("stdout")
    if stderr.truncated:
        truncated.append("stderr")

    response: dict[str, Any] = {
        "kind": result.type.value if result is not None else "error",
        "stdout": stdout.value(),
        "stderr": stderr.value(),
        "namespace": _backend.state.namespace,
        "truncated": truncated,
    }

    if bridge_error is not None:
        error_text, error_truncated = bounded_text(
            bridge_error, MAX_VALUE_CHARS, "error"
        )
        traceback_text, traceback_truncated = bounded_text(
            "".join(
                traceback_module.format_exception(
                    type(bridge_error), bridge_error, bridge_error.__traceback__
                )
            ),
            MAX_TRACEBACK_CHARS,
            "traceback",
        )
        response.update(
            {
                "errorType": type(bridge_error).__name__,
                "error": error_text,
                "traceback": traceback_text,
            }
        )
        if error_truncated:
            truncated.append("error")
        if traceback_truncated:
            truncated.append("traceback")
    elif result is not None and result.type == ResultType.VALUE:
        try:
            value, value_truncated = format_value(result.value)
            response["value"] = value
            if value_truncated:
                truncated.append("value")
        except BaseException as error:
            response["kind"] = "error"
            response["errorType"] = type(error).__name__
            response["error"], error_truncated = bounded_text(
                error, MAX_VALUE_CHARS, "error"
            )
            if error_truncated:
                truncated.append("error")
    elif result is not None and result.type == ResultType.ERROR:
        response["errorType"] = result.error_type or "Error"
        response["error"], error_truncated = bounded_text(
            result.error or "", MAX_VALUE_CHARS, "error"
        )
        response["traceback"], traceback_truncated = bounded_text(
            result.traceback or "", MAX_TRACEBACK_CHARS, "traceback"
        )
        if error_truncated:
            truncated.append("error")
        if traceback_truncated:
            truncated.append("traceback")

    return json.dumps(response, separators=(",", ":"))


def runtime_info() -> str:
    import spork_pds

    return json.dumps(
        {
            "packages": {
                "spork-lang": version("spork-lang"),
                "spork-runtime": version("spork-runtime"),
                "spork-pds": version("spork-pds"),
            },
            "extension": spork_pds.__file__,
        },
        separators=(",", ":"),
    )
