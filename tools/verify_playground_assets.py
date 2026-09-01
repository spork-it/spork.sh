#!/usr/bin/env python3
"""Verify the generated playground manifest and package archive structurally."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PACKAGES = {"spork-lang", "spork-runtime", "spork-pds"}
MAX_BUNDLE_BYTES = 400 * 1024


def fail(message: str) -> None:
    raise ValueError(message)


def object_value(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def content_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(files.items()):
        encoded = name.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    return digest.hexdigest()


def validate(public: Path) -> tuple[str, int]:
    runtime_path = public / "playground-runtime" / "runtime.json"
    runtime = object_value(json.loads(runtime_path.read_text(encoding="utf-8")), "runtime")
    if runtime.get("format") != 1:
        fail("unsupported runtime manifest format")
    pyodide = object_value(runtime.get("pyodide"), "runtime.pyodide")
    bundle_info = object_value(runtime.get("bundle"), "runtime.bundle")
    packages = object_value(runtime.get("packages"), "runtime.packages")
    if set(packages) != EXPECTED_PACKAGES:
        fail("runtime manifest has an unexpected package set")
    if not re.fullmatch(r"\d+(?:\.\d+)+", str(pyodide.get("version", ""))):
        fail("runtime Pyodide version is invalid")
    expected_index = (
        f"https://cdn.jsdelivr.net/pyodide/v{pyodide['version']}/full/"
    )
    if pyodide.get("indexURL") != expected_index:
        fail("runtime Pyodide URL is not the pinned jsDelivr release")

    bundle_url = bundle_info.get("url")
    bundle_hash = bundle_info.get("sha256")
    bundle_bytes = bundle_info.get("bytes")
    if not isinstance(bundle_url, str) or not re.fullmatch(
        r"/playground-runtime/spork-playground-[0-9a-f]{16}\.zip", bundle_url
    ):
        fail("runtime bundle URL is invalid")
    if not isinstance(bundle_hash, str) or not re.fullmatch(
        r"[0-9a-f]{64}", bundle_hash
    ):
        fail("runtime bundle digest is invalid")
    if not isinstance(bundle_bytes, int) or not 0 < bundle_bytes <= MAX_BUNDLE_BYTES:
        fail("runtime bundle size is invalid")
    if f"spork-playground-{bundle_hash[:16]}.zip" not in bundle_url:
        fail("runtime bundle filename does not match its digest")

    bundle_path = public / bundle_url.removeprefix("/")
    value = bundle_path.read_bytes()
    if len(value) != bundle_bytes:
        fail("runtime bundle size does not match the manifest")
    if hashlib.sha256(value).hexdigest() != bundle_hash:
        fail("runtime bundle SHA-256 does not match the manifest")

    archives = sorted((public / "playground-runtime").glob("spork-playground-*.zip"))
    if archives != [bundle_path]:
        fail(f"stale or missing playground archives: {archives!r}")

    files: dict[str, bytes] = {}
    with zipfile.ZipFile(bundle_path) as archive:
        if archive.testzip() is not None:
            fail("runtime bundle has a corrupt ZIP member")
        for member in archive.infolist():
            if member.is_dir():
                continue
            path = PurePosixPath(member.filename)
            if path.is_absolute() or ".." in path.parts:
                fail(f"unsafe runtime bundle path: {member.filename}")
            if member.filename in files:
                fail(f"duplicate runtime bundle path: {member.filename}")
            files[member.filename] = archive.read(member)

    required = {
        "spork/__init__.py",
        "spork/pds.py",
        "spork/runtime/__init__.py",
        "spork/repl/backend.py",
        "spork_playground_bridge.py",
        "spork-playground.json",
    }
    missing = required - files.keys()
    if missing:
        fail(f"runtime bundle is missing {sorted(missing)!r}")
    extensions = [
        name
        for name in files
        if re.fullmatch(r"spork_pds\.cpython-\d+-wasm32-emscripten\.so", name)
    ]
    if len(extensions) != 1:
        fail(f"expected one Emscripten spork-pds extension, found {extensions!r}")

    internal = object_value(
        json.loads(files.pop("spork-playground.json")), "internal manifest"
    )
    if internal.get("format") != 1:
        fail("unsupported internal manifest format")
    if internal.get("packages") != packages:
        fail("internal and external package versions differ")
    internal_pyodide = object_value(internal.get("pyodide"), "internal pyodide")
    if internal_pyodide.get("version") != pyodide["version"]:
        fail("internal and external Pyodide versions differ")
    if internal.get("contentSha256") != content_digest(files):
        fail("installed-content digest does not match the runtime bundle")
    if internal.get("bridgeSha256") != hashlib.sha256(
        files["spork_playground_bridge.py"]
    ).hexdigest():
        fail("playground bridge digest does not match")

    return bundle_hash, bundle_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("public", nargs="?", type=Path, default=ROOT / "public")
    args = parser.parse_args()
    try:
        digest, size = validate(args.public.resolve())
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f"playground asset verification failed: {error}", file=sys.stderr)
        return 1
    print(f"playground assets verified: {size} bytes, sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
