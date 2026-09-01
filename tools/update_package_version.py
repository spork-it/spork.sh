#!/usr/bin/env python3
"""Update one package version across versioned documentation content.

The canonical package version lives in ``src/spork_sh/docs.spork``. This tool
updates that value and every Markdown front matter block whose ``project``
matches the selected package and already declares ``package-version``.
Unversioned utility pages are intentionally left unchanged.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_PATH = Path("src/spork_sh/docs.spork")
CONTENT_PATH = Path("content")
PACKAGE_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[A-Za-z0-9]+(?:[._+-][A-Za-z0-9]+)*$")
PROJECT_RE = re.compile(
    r"^project:[ \t]*(?:"
    r'"(?P<double>[^"]+)"|'
    r"'(?P<single>[^']+)'|"
    r"(?P<plain>[^\s#]+))[ \t]*$",
    re.MULTILINE,
)
CONTENT_VERSION_RE = re.compile(
    r"^package-version:[ \t]*(?:"
    r'"(?P<double>[^"]+)"|'
    r"'(?P<single>[^']+)'|"
    r"(?P<plain>[^\s#]+))[ \t]*$",
    re.MULTILINE,
)


class VersionUpdateError(RuntimeError):
    """Raised when package metadata cannot be updated safely."""


@dataclass(frozen=True)
class FileChange:
    path: Path
    content: str


def _selected_value(match: re.Match[str]) -> str:
    for group in ("double", "single", "plain"):
        value = match.group(group)
        if value is not None:
            return value
    raise AssertionError("version metadata regex matched without a value")


def _front_matter(path: Path, content: str) -> tuple[int, int, str] | None:
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            start = len(lines[0])
            end = sum(len(item) for item in lines[:index])
            return start, end, content[start:end]
    raise VersionUpdateError(f"{path}: unterminated Markdown front matter")


def _canonical_version_change(
    root: Path, package: str, version: str
) -> tuple[str, FileChange | None]:
    path = root / VERSIONS_PATH
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise VersionUpdateError(f"could not read {path}: {error}") from error

    pattern = re.compile(
        rf'^(?P<indent>[ \t]*)(?P<open>[{{]?)"{re.escape(package)}"'
        rf'\s+"(?P<version>[^"]+)"(?P<suffix>[ \t]*(?:[}}][)])?)$',
        re.MULTILINE,
    )
    matches = list(pattern.finditer(content))
    if len(matches) != 1:
        raise VersionUpdateError(
            f"{path}: expected exactly one canonical entry for {package!r}, "
            f"found {len(matches)}"
        )
    match = matches[0]
    current = match.group("version")
    if current == version:
        return current, None
    replacement = (
        f'{match.group("indent")}{match.group("open")}'
        f'"{package}" "{version}"{match.group("suffix")}'
    )
    updated = content[: match.start()] + replacement + content[match.end() :]
    return current, FileChange(path, updated)


def plan_changes(
    root: Path, package: str, version: str
) -> tuple[str, list[FileChange], int]:
    """Validate and plan a package version update without writing files."""
    if not PACKAGE_RE.fullmatch(package):
        raise VersionUpdateError(
            "package must use lowercase letters, digits, dots, and hyphens"
        )
    if not VERSION_RE.fullmatch(version):
        raise VersionUpdateError(
            "version must be a non-empty package version without whitespace"
        )

    root = root.resolve()
    current, canonical_change = _canonical_version_change(root, package, version)
    changes = [] if canonical_change is None else [canonical_change]
    versioned_files = 0
    unversioned_files = 0
    content_root = root / CONTENT_PATH
    if not content_root.is_dir():
        raise VersionUpdateError(f"content directory does not exist: {content_root}")

    for path in sorted(content_root.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as error:
            raise VersionUpdateError(f"could not read {path}: {error}") from error
        front_matter = _front_matter(path, content)
        if front_matter is None:
            continue
        start, end, metadata = front_matter
        project_matches = list(PROJECT_RE.finditer(metadata))
        if len(project_matches) > 1:
            raise VersionUpdateError(f"{path}: duplicate project fields")
        if not project_matches or _selected_value(project_matches[0]) != package:
            continue

        version_matches = list(CONTENT_VERSION_RE.finditer(metadata))
        if len(version_matches) > 1:
            raise VersionUpdateError(f"{path}: duplicate package-version fields")
        if not version_matches:
            unversioned_files += 1
            continue

        versioned_files += 1
        match = version_matches[0]
        declared = _selected_value(match)
        if declared not in {current, version}:
            raise VersionUpdateError(
                f"{path}: package-version {declared!r} does not match "
                f"canonical version {current!r}"
            )
        if declared == version:
            continue
        updated_metadata = (
            metadata[: match.start()]
            + f'package-version: "{version}"'
            + metadata[match.end() :]
        )
        changes.append(
            FileChange(path, content[:start] + updated_metadata + content[end:])
        )

    if versioned_files == 0:
        raise VersionUpdateError(
            f"no versioned Markdown content found for project {package!r}"
        )
    return current, changes, unversioned_files


def _atomic_write(change: FileChange) -> None:
    mode = stat.S_IMODE(change.path.stat().st_mode)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="",
            dir=change.path.parent,
            prefix=f".{change.path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(change.content)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, change.path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="Package/project name, such as spork-lang")
    parser.add_argument("version", help="New version without a leading v")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and list changes without writing files",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        current, changes, unversioned = plan_changes(
            args.root, args.package, args.version
        )
    except VersionUpdateError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    action = "Would update" if args.dry_run else "Updating"
    for change in changes:
        try:
            display = change.path.relative_to(args.root.resolve())
        except ValueError:
            display = change.path
        print(f"{action}: {display}")
    if not args.dry_run:
        try:
            for change in changes:
                _atomic_write(change)
        except OSError as error:
            print(
                f"Error: could not write package version update: {error}",
                file=sys.stderr,
            )
            return 1

    if changes:
        verb = "Would update" if args.dry_run else "Updated"
        print(
            f"{verb} {args.package} {current} -> {args.version} "
            f"across {len(changes)} files; left {unversioned} unversioned "
            "content files unchanged."
        )
    else:
        print(
            f"{args.package} is already synchronized at {args.version}; "
            f"left {unversioned} unversioned content files unchanged."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
