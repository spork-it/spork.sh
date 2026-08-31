#!/usr/bin/env python3
"""Execute documentation examples and validate intentionally non-runnable fences."""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from markdown_it import MarkdownIt
from spork.compiler import get_source_location, read_str
from spork.runtime.types import Symbol

ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)
DOCS = tuple(sorted((ROOT / "content" / "docs").rglob("*.md")))
MARKDOWN = MarkdownIt("commonmark")
MARKER_RE = re.compile(r"<!--\s*verify-docs:\s*(.*?)\s*-->", re.DOTALL)
MARKER_BODY_RE = re.compile(
    r"(skip|compile|expect-error)\s*=\s*([A-Za-z][A-Za-z0-9_.-]*)"
)
SPORK_LANGUAGES = {"clojure", "spork"}
SHELL_LANGUAGES = {"bash", "sh", "shell"}

FIXTURES = r"""
(ns docs.verify
  (:import [types :refer [SimpleNamespace]]
           [docs_fixtures :refer [docs_equal some_func make_request f some_context create_pipe]]))

(def x 1)
(def a 1)
(def b 2)
(def c 3)
(def i 10)
(def n 2)
(def condition true)
(def then-expr :then)
(def else-expr :else)
(def data {:valid true})
(def v [1 2 3])
(def v1 [1 2])
(def v2 [3 4])
(def m {:a 1})
(def s #{1 2 3})
(def s1 #{1 2 3})
(def s2 #{2 3 4})
(def sv (sorted-vec [1 3 5]))
(def lst '(1 2 3))
(def coll [1 2 3])
(def my-vec [0 1 2 3 4 5])
(def person {:name "Alice" :age 30})
(def user {:name "Alice"})
(def users [{:name "Alice" :email "alice@example.com" :active true}
            {:name "Bob" :email "bob@example.com" :active false}])
(def item 1)
(def items [{:name "one" :score 10} {:name "two" :score 20}])
(def new-item {:name "three" :score 30})
(def repos ["one/repo" "two/repo"])
(def h {})
(def default :default)
(def val 42)
(def value 1)
(def message {:type :ready :payload 42})
(def names ["Ada"])
(def index 0)
(def start 0)
(def stop 2)
(def end 2)
(def step 1)
(def pos1 1)
(def pos2 2)
(def arg 1)
(def args [1 2])
(def arg1 1)
(def arg2 2)
(def large-collection [1 2 3])

(defn valid? [value] true)
(defn lookup [id] "Alice")
(defn do-something [] nil)
(defn do-more [] nil)
(defn do-work [] nil)
(defn process [& values] nil)
(defn save [& values] nil)
(defn save-to-db [value] nil)
(defn redirect [path] path)
(defn authenticated? [user] false)
(defn fetch-stars [repo] 1)
(defn risky-operation [] :ok)
(defn cleanup [] nil)

(defclass DocObject []
  (defn __init__ [self]
    (set! self.attr 1))
  (defn method [self & args]
    args))
(def obj (DocObject))
(def SomeClass DocObject)
(def Point DocObject)

(defclass SomePythonLib []
  (defn configure [self config]
    (assoc! config :configured true))
  (defn load-config [self config]
    (assoc! config :loaded true)))
(def some-python-lib (SomePythonLib))

(defclass Circle []
  (defn __init__ [self radius]
    (set! self.radius radius)))
(defclass Rectangle []
  (defn __init__ [self width height]
    (set! self.width width)
    (set! self.height height)))
(defclass Square []
  (defn __init__ [self side]
    (set! self.side side)))
(def my-circle (Circle 2))
(def my-rectangle (Rectangle 2 3))
(def my-object my-circle)

(defprotocol IShape
  (area [self])
  (perimeter [self]))
(defprotocol Showable
  (show [self]))
(defprotocol Measurable
  (length [self])
  (width [self]))

(extend-type Circle
  IShape
  (area [self] (* 3.14 self.radius self.radius))
  (perimeter [self] (* 2 3.14 self.radius)))
(extend-type Rectangle
  IShape
  (area [self] (* self.width self.height))
  (perimeter [self] (* 2 (+ self.width self.height))))

(def tv (transient [1 2 3]))
"""


@dataclass(frozen=True)
class Example:
    path: Path
    line: int
    language: str
    source: str
    directive: str | None
    directive_value: str | None

    @property
    def location(self) -> str:
        return f"{self.path.relative_to(ROOT)}:{self.line}"


def examples() -> list[Example]:
    result: list[Example] = []
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        markers = list(MARKER_RE.finditer(text))
        parsed_markers: dict[int, tuple[str, str]] = {}
        for marker in markers:
            parsed = MARKER_BODY_RE.fullmatch(marker.group(1).strip())
            if not parsed:
                line = text.count("\n", 0, marker.start()) + 1
                raise ValueError(f"{path.relative_to(ROOT)}:{line}: invalid verify-docs marker")
            parsed_markers[marker.start()] = (parsed.group(1), parsed.group(2))

        lines = text.splitlines(keepends=True)
        offsets = [0]
        for line_text in lines:
            offsets.append(offsets[-1] + len(line_text))

        used_markers: set[int] = set()
        for token in MARKDOWN.parse(text):
            if token.type != "fence" or token.map is None:
                continue
            start_line = token.map[0]
            start = offsets[start_line]
            adjacent = next(
                (
                    marker
                    for marker in reversed(markers)
                    if marker.end() <= start
                    and not text[marker.end() : start].strip()
                ),
                None,
            )
            if adjacent is None:
                directive, directive_value = None, None
            else:
                directive, directive_value = parsed_markers[adjacent.start()]
                used_markers.add(adjacent.start())
            info = token.info.strip().split()
            language = info[0].lower() if info else "text"
            if directive and language not in SPORK_LANGUAGES | {"python"}:
                line = text.count("\n", 0, adjacent.start()) + 1
                raise ValueError(
                    f"{path.relative_to(ROOT)}:{line}: verify-docs marker requires a Spork or Python fence"
                )
            result.append(
                Example(
                    path=path,
                    line=start_line + 1,
                    language=language,
                    source=token.content,
                    directive=directive,
                    directive_value=directive_value,
                )
            )

        unused = next(
            (marker for marker in markers if marker.start() not in used_markers), None
        )
        if unused:
            line = text.count("\n", 0, unused.start()) + 1
            raise ValueError(
                f"{path.relative_to(ROOT)}:{line}: verify-docs marker must immediately precede a fence"
            )
    return result


def module_prelude(example: Example) -> str:
    if example.path.parent.name == "standard-library":
        namespaces = {
            "string.md": "[std.string :as str]",
            "map.md": "[std.map :as m]",
            "json.md": "[std.json :as json]",
        }
        required = namespaces.get(example.path.name)
        if required is not None:
            return f"(ns docs.verify (:require {required}))\n"
    if example.path.parent.name == "spork-state":
        return """\
(ns docs.verify (:require [spork-state :refer :all]))
(def validator (fn [candidate] (>= candidate 0)))
(def reference (atom 0))
(def expected (deref reference))
(def new-value 1)
(def key :docs)
(def callback (fn [& values] nil))
"""
    if example.path.parent.name == "spork-site":
        return """\
(ns docs.verify
  (:require
    [spork-site.build :as build]
    [spork-site.collections :as collections]
    [spork-site.content :as content-api]
    [spork-site.core :as site :refer [element fragment markup]]
    [spork-site.feeds :as feeds]
    [spork-site.routing :as routing]
    [spork-site.sitemap :as sitemap]))
(def documents (content-api.load-documents "content"))
(def posts documents)
(def content-pages [])
(def sitemap-output "<xml></xml>")
(def rss-output "<rss></rss>")
(def atom-output "<feed></feed>")
(def source "## Example\n\n```spork\n(+ 1 2)\n```")
(def content (site.render-markdown source))
"""
    return ""


def _form_span(source: str, start_line: int) -> tuple[int, int]:
    """Find the source span of a top-level form whose first token is known."""
    line_offsets = [0]
    for match in re.finditer("\\n", source):
        line_offsets.append(match.end())
    start = line_offsets[start_line - 1]
    while start < len(source) and source[start] in " \t\r\n":
        start += 1

    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    in_string = False
    escaped = False
    index = start
    saw_string = False
    while index < len(source):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
                saw_string = True
            index += 1
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == ";":
            if not stack:
                return start, index
            newline = source.find("\n", index)
            index = len(source) if newline < 0 else newline + 1
            continue
        if char in "([{":
            stack.append(char)
        elif char in pairs:
            if stack and stack[-1] == pairs[char]:
                stack.pop()
            if not stack:
                return start, index + 1
        elif not stack and (char.isspace() or char == ","):
            return start, index
        index += 1
        if saw_string and not stack:
            # Handles ordinary strings and tagged string reader literals.
            if index == len(source) or source[index].isspace() or source[index] == ";":
                return start, index
    return start, index


def _expected_form(raw: str) -> str | None:
    """Translate an exact `; =>` value into an executable Spork form."""
    value = raw.strip()
    value = value.split(" - ", 1)[0].rstrip()
    value = value.split(", nothing", 1)[0].rstrip()
    # Parenthetical text following a value is explanatory prose. Parenthesized
    # values themselves are the reference's notation for logical sequences.
    sequence_with_note = re.fullmatch(r"(\(.*\))\s+\([^()]*\)", value)
    if sequence_with_note:
        value = sequence_with_note.group(1)
    elif not value.startswith("("):
        value = re.sub(r"\s+\(.*\)\s*$", "", value)
    descriptions = (
        "sorted by",
        "formatted ",
        "same result",
        "now contains",
        "some_func(",
        "<class ",
        "DoubleVector",
        "IntVector",
        "file contents",
        "match object",
        "datetime with",
        "true/false",
        "True/False",
        "Get ",
        "Set ",
        "iterator",
        "writes ",
        "computed ",
        "x = ",
        "UTC",
    )
    if not value or value.startswith(descriptions):
        return None
    if "/" in value and not value.startswith(('"', "'")) and " " not in value:
        value = f'"{value}"'
    if value == "()":
        return "[]"
    if value.startswith("sorted_vec(") and value.endswith(")"):
        value = "[" + value[len("sorted_vec(") : -1] + "]"
    elif value.startswith("(") and value.endswith(")"):
        inner = value[1:-1]
        without_strings = re.sub(r'"(?:\\\\.|[^"\\\\])*"', "", inner)
        bare_symbols = [
            match.group(0)
            for match in re.finditer(r"(?<![:A-Za-z0-9_.-])[A-Za-z][A-Za-z0-9_.-]*", without_strings)
            if match.group(0) not in {"true", "false", "nil"}
        ]
        if bare_symbols:
            value = "'" + value
        else:
            converted: list[str] = []
            in_expected_string = False
            escaped_expected = False
            for char in value:
                if in_expected_string:
                    converted.append(char)
                    if escaped_expected:
                        escaped_expected = False
                    elif char == "\\":
                        escaped_expected = True
                    elif char == '"':
                        in_expected_string = False
                elif char == '"':
                    in_expected_string = True
                    converted.append(char)
                elif char == "(":
                    converted.append("[")
                elif char == ")":
                    converted.append("]")
                else:
                    converted.append(char)
            value = "".join(converted)
    # Commas are visual separators in a few Python-style expected values, but
    # commas are ordinary symbol characters in Spork. Remove only unquoted ones.
    pieces: list[str] = []
    in_string = False
    escaped = False
    for char in value:
        if in_string:
            pieces.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            pieces.append(char)
        elif char != ",":
            pieces.append(char)
    value = "".join(pieces)
    value = re.sub(r"\bNone\b", "nil", value)
    value = re.sub(r"\bTrue\b", "true", value)
    value = re.sub(r"\bFalse\b", "false", value)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", value) and value not in {
        "nil",
        "true",
        "false",
    }:
        value = "'" + value
    # Python reprs with class objects and colon-separated dict entries are output
    # descriptions rather than Spork value syntax.
    if "<class" in value:
        return None
    try:
        if len(read_str(value)) != 1:
            return None
    except Exception:
        return None
    return value


def instrument_expected_values(example: Example) -> tuple[str, int]:
    """Rewrite exact value examples so their `; =>` claims become assertions."""
    forms = read_str(example.source)
    located: list[tuple[object, int]] = []
    for form in forms:
        location = get_source_location(form)
        if location is not None:
            located.append((form, location.line))

    replacements: list[tuple[int, int, str]] = []
    assertion_count = 0
    claim_count = len(re.findall(r";\s*=>\s*.*", example.source))
    lines = example.source.splitlines()
    for index, (form, start_line) in enumerate(located):
        end_line = located[index + 1][1] - 1 if index + 1 < len(located) else len(lines)
        region = "\n".join(lines[start_line - 1 : end_line])
        matches = re.findall(r";\s*=>\s*(.*)", region)
        if len(matches) != 1:
            continue
        expected = _expected_form(matches[0])
        if expected is None:
            raise ValueError(
                f"{example.location}: cannot assert `; => {matches[0].strip()}`"
            )
        start, end = _form_span(example.source, start_line)
        original = example.source[start:end]
        name = f"__docs_actual_{assertion_count}"
        message = f"{example.location} value assertion {assertion_count}"
        if (
            isinstance(form, list)
            and form
            and isinstance(form[0], Symbol)
            and form[0].name == "def"
            and len(form) >= 2
            and isinstance(form[1], Symbol)
        ):
            replacement = (
                original
                + f'\n(assert (docs-equal {form[1].name} {expected}) "{message}")'
            )
        elif (
            isinstance(form, list)
            and form
            and isinstance(form[0], Symbol)
            and form[0].name in {"print", "set!"}
        ):
            continue
        else:
            replacement = (
                f"(def {name} {original})\n"
                f'(assert (docs-equal {name} {expected}) "{message}")'
            )
        replacements.append((start, end, replacement))
        assertion_count += 1

    if assertion_count != claim_count:
        raise ValueError(
            f"{example.location}: found {claim_count} `; =>` claims but generated "
            f"{assertion_count} assertions"
        )

    source = example.source
    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    return source, assertion_count


def expected_error(example: Example) -> str | None:
    if example.directive == "expect-error":
        return example.directive_value
    return None


def skip_reason(example: Example) -> str | None:
    if example.directive == "skip":
        return example.directive_value
    return None


def write_fake_namespaces(directory: Path) -> None:
    files = {
        "docs_fixtures.py": """\
from collections.abc import Iterable, Mapping, Set
from contextlib import contextmanager
import os


def _normalize(value):
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, Mapping):
        return {_normalize(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, Set):
        return frozenset(_normalize(item) for item in value)
    if isinstance(value, (str, bytes, bytearray)) or value is None:
        return value
    if isinstance(value, Iterable):
        return [_normalize(item) for item in value]
    return value


def docs_equal(actual, expected):
    return _normalize(actual) == _normalize(expected)


def some_func(*args, **kwargs):
    return args, kwargs


def make_request(*args, **kwargs):
    return args, kwargs


def f(*args, **kwargs):
    return args, kwargs


@contextmanager
def some_context():
    yield None


@contextmanager
def create_pipe():
    yield (object(), object())
""",
        "acme/tools/core.spork": "(ns acme.tools.core)\n(defn helper [] nil)\n",
        "my/utils.spork": "(ns my.utils)\n(defn helper-fn [& args] nil)\n",
        "external/lib.spork": "(ns external.lib)\n(def external-value 1)\n",
        "my/macros.spork": """(ns my.macros)\n(defmacro my-macro [& args] nil)\n(defmacro some-macro [& args] nil)\n""",
        "other/lib.spork": """(ns other.lib)\n(defmacro some-macro [& args] nil)\n(def foo 1)\n""",
    }
    for relative, source in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")


def verify_spork(example: Example) -> tuple[bool, str]:
    reason = skip_reason(example)
    if reason:
        return True, f"classified: {reason}"

    expected = expected_error(example)
    with tempfile.TemporaryDirectory(prefix="spork-docs-") as temp_name:
        temp = Path(temp_name)
        write_fake_namespaces(temp)
        (temp / "README.md").write_text("fixture", encoding="utf-8")
        (temp / "config.txt").write_text("fixture", encoding="utf-8")
        (temp / "data.json").write_text('{"ready": true}', encoding="utf-8")
        (temp / "file.txt").write_text("fixture", encoding="utf-8")
        (temp / "in.txt").write_text("fixture", encoding="utf-8")
        (temp / "main.py").write_text("", encoding="utf-8")
        (temp / "src").mkdir()
        (temp / "content").mkdir()
        (temp / "content" / "post.md").write_text(
            "---\ntitle: Fixture post\ndate: 2026-08-30T12:00:00Z\n---\n\n## Fixture\n",
            encoding="utf-8",
        )
        (temp / "static").mkdir()
        (temp / "static" / "site.css").write_text("body {}\n", encoding="utf-8")

        checked_source, assertion_count = (
            (example.source, 0)
            if expected
            else instrument_expected_values(example)
        )
        source = FIXTURES + module_prelude(example) + checked_source
        script = temp / "example.spork"
        script.write_text(source, encoding="utf-8")
        command = [str(PYTHON), "-m", "spork"]
        if example.directive == "compile":
            command.append("-e")
        command.append(str(script))
        result = subprocess.run(
            command,
            cwd=temp,
            text=True,
            capture_output=True,
            timeout=30,
        )

    output = result.stdout + result.stderr
    if expected:
        if result.returncode != 0 and expected in output:
            return True, f"expected {expected}"
        return False, f"expected {expected}, exit={result.returncode}: {output[-500:]}"
    if result.returncode:
        return False, output[-1000:]
    return True, f"executed:{assertion_count}"


def python_environment(example: Example) -> dict[str, object]:
    namespace: dict[str, object] = {"__name__": "__docs_example__"}
    if example.path.parent.name == "spork-pds":
        exec("from spork.pds import *", namespace)
        exec(
            """
numbers = Vector([1, 2, 3])
config = Map({"host": "localhost", "port": 8000})
roles = Set(["reader", "writer"])
base = Map({"host": "localhost", "port": 8000})
vector = Vector([1, 2, 3])
tags = Set(["stable", "documented"])
floats = vec_f64(1, 2.5, 3)
original = Map({"count": 1})
changes = {"count": 2}
""",
            namespace,
        )
    elif example.path.parent.name == "spork-state":
        exec("from spork_state import *", namespace)
        exec(
            """
value = 0
validator = lambda candidate: candidate >= 0
reference = Atom(0)
expected = reference.value
new_value = 1
key = "docs"
callback = lambda *values: None
""",
            namespace,
        )
    return namespace


def verify_python(example: Example) -> tuple[bool, str]:
    reason = skip_reason(example)
    if reason:
        return True, f"classified: {reason}"

    try:
        code = compile(
            "\n" * example.line + example.source,
            example.location,
            "exec",
        )
        if example.directive != "compile":
            with contextlib.redirect_stdout(io.StringIO()):
                exec(code, python_environment(example))
    except Exception as error:
        expected = expected_error(example)
        detail = f"{type(error).__name__}: {error}"
        if expected and expected in detail:
            return True, f"expected {expected}"
        return False, detail

    expected = expected_error(example)
    if expected:
        return False, f"expected {expected}, but example passed"
    return True, "executed:0"


def verify_shell(example: Example) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="spork-shell-docs-") as temp_name:
        script = Path(temp_name) / "example.sh"
        script.write_text(example.source, encoding="utf-8")
        result = subprocess.run(
            ["/bin/sh", "-n", str(script)],
            text=True,
            capture_output=True,
            timeout=30,
        )
    if result.returncode:
        return False, (result.stdout + result.stderr)[-1000:]
    return True, "executed:0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    counts = {
        "executed": 0,
        "assertions": 0,
        "expected-error": 0,
        "classified": 0,
    }
    failures: list[str] = []
    skipped: list[tuple[str, str]] = []

    print("Verifying documentation examples...", flush=True)
    try:
        documentation_examples = examples()
    except ValueError as error:
        print(f"\n  ✗ {error}", file=sys.stderr)
        return 1

    for example in documentation_examples:
        try:
            if example.language in SPORK_LANGUAGES:
                ok, detail = verify_spork(example)
            elif example.language == "python":
                ok, detail = verify_python(example)
            elif example.language in SHELL_LANGUAGES:
                ok, detail = verify_shell(example)
            else:
                continue

            if not ok:
                failures.append(f"{example.location} [{example.language}]: {detail}")
            elif detail.startswith("expected"):
                counts["expected-error"] += 1
            elif detail.startswith("classified"):
                counts["classified"] += 1
                skipped.append((example.location, example.directive_value or "unspecified"))
            else:
                counts["executed"] += 1
                counts["assertions"] += int(detail.partition(":")[2] or 0)
        except Exception as error:
            failures.append(f"{example.location} [{example.language}]: {error}")

    if failures:
        print(f"\n  ✗ {len(failures)} documentation example(s) failed", file=sys.stderr)
        for failure in failures:
            print(f"\n    {failure}", file=sys.stderr)
        return 1

    print(f"  ✓ Runnable examples passed   {counts['executed']:>4}")
    print(f"  ✓ Documented values checked  {counts['assertions']:>4}")
    print(f"  ✓ Expected failures verified {counts['expected-error']:>4}")
    print(f"  • Explicitly skipped         {counts['classified']:>4}")
    for location, reason in skipped:
        print(f"      {location} — {reason}")
    print("\n✓ Documentation verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
