#!/usr/bin/env python3
"""Build the deterministic Spork package archive used by the browser playground."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "tools" / "playground-lock.json"
DEFAULT_OUTPUT = ROOT / "build" / "playground-runtime" / "assets" / "playground-runtime"
DEFAULT_WORK = ROOT / "build" / "playground-runtime" / "work"
BRIDGE_SOURCE = ROOT / "tools" / "spork_playground_bridge.py"
SOURCE_DATE_EPOCH = "315532800"  # 1980-01-01, the earliest portable ZIP date.
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
EXPECTED_PACKAGES = {"spork-lang", "spork-runtime", "spork-pds"}
MAX_BUNDLE_BYTES = 400 * 1024


class BuildError(RuntimeError):
    """A focused, user-facing playground build failure."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read {path}: {error}") from error
    if not isinstance(value, dict):
        raise BuildError(f"{path} must contain a JSON object")
    return value


def required_string(mapping: dict[str, Any], key: str, location: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise BuildError(f"{location}.{key} must be a non-empty string")
    return value


def load_lock(path: Path) -> dict[str, Any]:
    lock = read_json(path)
    if lock.get("format") != 1:
        raise BuildError(f"{path}: unsupported lock format {lock.get('format')!r}")

    for key in ("pyodide", "buildTools", "packages"):
        if not isinstance(lock.get(key), dict):
            raise BuildError(f"{path}: {key} must be an object")

    pyodide = lock["pyodide"]
    for key in (
        "version",
        "pyodideBuild",
        "python",
        "emscripten",
        "abi",
        "platformTag",
        "cdnBase",
    ):
        required_string(pyodide, key, "pyodide")
    if not pyodide["cdnBase"].endswith("/"):
        raise BuildError("pyodide.cdnBase must end with '/'")
    if f"/v{pyodide['version']}/" not in pyodide["cdnBase"]:
        raise BuildError("pyodide.cdnBase does not contain the locked version")

    tools = lock["buildTools"]
    for key in ("setuptools", "wheel"):
        required_string(tools, key, "buildTools")

    packages = lock["packages"]
    if set(packages) != EXPECTED_PACKAGES:
        raise BuildError(
            "packages must be exactly " + ", ".join(sorted(EXPECTED_PACKAGES))
        )
    for name, package in packages.items():
        if not isinstance(package, dict):
            raise BuildError(f"packages.{name} must be an object")
        for key in ("version", "artifact", "url", "sha256"):
            required_string(package, key, f"packages.{name}")
        if not re.fullmatch(r"[0-9a-f]{64}", package["sha256"]):
            raise BuildError(f"packages.{name}.sha256 must be a lowercase SHA-256")
        if not package["url"].startswith("https://files.pythonhosted.org/"):
            raise BuildError(f"packages.{name}.url must use files.pythonhosted.org")
        if not package["url"].endswith("/" + package["artifact"]):
            raise BuildError(f"packages.{name}.url does not match its artifact")

    expected_artifacts = {
        "spork-lang": f"spork_lang-{packages['spork-lang']['version']}-py3-none-any.whl",
        "spork-runtime": (
            f"spork_runtime-{packages['spork-runtime']['version']}-py3-none-any.whl"
        ),
        "spork-pds": f"spork_pds-{packages['spork-pds']['version']}.tar.gz",
    }
    for name, expected in expected_artifacts.items():
        if packages[name]["artifact"] != expected:
            raise BuildError(
                f"packages.{name}.artifact must be {expected!r}, "
                f"not {packages[name]['artifact']!r}"
            )

    return lock


def documented_versions(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    return dict(re.findall(r'"(spork-(?:lang|runtime|pds))"\s+"([^"]+)"', source))


def validate_documented_versions(lock: dict[str, Any]) -> None:
    documented = documented_versions(ROOT / "src" / "spork_sh" / "docs.spork")
    expected = {
        name: package["version"] for name, package in lock["packages"].items()
    }
    if documented != expected:
        raise BuildError(
            "playground package versions do not match src/spork_sh/docs.spork: "
            f"lock={expected!r}, docs={documented!r}"
        )


def distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError as error:
        raise BuildError(
            f"required build tool {name!r} is not installed; see README.md"
        ) from error


def run_output(arguments: list[str], *, env: dict[str, str] | None = None) -> str:
    try:
        completed = subprocess.run(
            arguments,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
    except FileNotFoundError as error:
        raise BuildError(f"required command not found: {arguments[0]}") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise BuildError(f"command failed: {' '.join(arguments)}\n{detail}") from error
    return completed.stdout.strip()


def validate_toolchain(lock: dict[str, Any]) -> tuple[str, Path]:
    pyodide = lock["pyodide"]
    expected_tools = {
        "pyodide-build": pyodide["pyodideBuild"],
        "setuptools": lock["buildTools"]["setuptools"],
        "wheel": lock["buildTools"]["wheel"],
    }
    actual_tools = {name: distribution_version(name) for name in expected_tools}
    if actual_tools != expected_tools:
        raise BuildError(
            "browser build tools do not match the lock; install: "
            + " ".join(f"{name}=={version}" for name, version in expected_tools.items())
            + f" (found {actual_tools!r})"
        )

    executable = shutil.which("pyodide")
    if executable is None:
        raise BuildError("pyodide CLI is not on PATH")

    platform_match = re.fullmatch(
        r"pyemscripten_(\d+_\d+)_wasm32", pyodide["platformTag"]
    )
    if platform_match is None:
        raise BuildError("pyodide.platformTag is not a pyemscripten wasm32 tag")
    expected_config = {
        "python_version": pyodide["python"],
        "emscripten_version": pyodide["emscripten"],
        "pyemscripten_platform_version": platform_match.group(1),
    }
    actual_config = {
        key: run_output([executable, "config", "get", key])
        for key in expected_config
    }
    if actual_config != expected_config:
        raise BuildError(
            f"Pyodide cross-build environment does not match the lock: "
            f"expected {expected_config!r}, found {actual_config!r}. Run "
            f"'pyodide xbuildenv install {pyodide['version']}'."
        )

    emsdk = Path(run_output([executable, "config", "get", "emsdk_dir"]))
    if not (emsdk / "emsdk_env.sh").is_file():
        raise BuildError(
            f"Emscripten is not installed at {emsdk}; run "
            "'pyodide xbuildenv install-emscripten'"
        )
    return executable, emsdk


def download(package: dict[str, Any], destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / package["artifact"]
    expected = package["sha256"]
    if target.is_file() and sha256_file(target) == expected:
        return target

    target.unlink(missing_ok=True)
    request = urllib.request.Request(
        package["url"], headers={"User-Agent": "spork.sh-playground-builder/1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            value = response.read()
    except OSError as error:
        raise BuildError(f"cannot download {package['url']}: {error}") from error
    actual = sha256_bytes(value)
    if actual != expected:
        raise BuildError(
            f"digest mismatch for {package['artifact']}: expected {expected}, got {actual}"
        )
    target.write_bytes(value)
    return target


def safe_extract_tar(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        for member in members:
            resolved = (destination / member.name).resolve()
            if root not in resolved.parents and resolved != root:
                raise BuildError(f"unsafe path in {archive.name}: {member.name}")
            if member.issym() or member.islnk():
                raise BuildError(f"links are not allowed in {archive.name}: {member.name}")
            if not member.isfile() and not member.isdir():
                raise BuildError(
                    f"special files are not allowed in {archive.name}: {member.name}"
                )
        source.extractall(destination, members=members)

    entries = [entry for entry in destination.iterdir() if entry.name != ".DS_Store"]
    if len(entries) != 1 or not entries[0].is_dir():
        raise BuildError(f"{archive.name} must contain one source directory")
    return entries[0]


def build_pds_wheel(
    lock: dict[str, Any], archive: Path, work: Path, executable: str, emsdk: Path
) -> Path:
    source_parent = work / "pds-source"
    wheel_dir = work / "wheels"
    shutil.rmtree(source_parent, ignore_errors=True)
    shutil.rmtree(wheel_dir, ignore_errors=True)
    source = safe_extract_tar(archive, source_parent)
    wheel_dir.mkdir(parents=True)

    command = [
        "bash",
        "-c",
        'emsdk="$1"; shift; source "$emsdk/emsdk_env.sh" >/dev/null && exec "$@"',
        "spork-playground-build",
        str(emsdk),
        executable,
        "build",
        "--no-isolation",
        str(source),
        "-o",
        str(wheel_dir),
    ]
    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    environment["EMSDK_QUIET"] = "1"
    try:
        subprocess.run(command, check=True, env=environment)
    except subprocess.CalledProcessError as error:
        raise BuildError(f"Pyodide spork-pds build failed with status {error.returncode}") from error

    wheels = sorted(wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise BuildError(f"expected one spork-pds wheel, found {len(wheels)}")
    pyodide = lock["pyodide"]
    package = lock["packages"]["spork-pds"]
    expected = (
        f"spork_pds-{package['version']}-{pyodide['abi']}-{pyodide['abi']}-"
        f"{pyodide['platformTag']}.whl"
    )
    if wheels[0].name != expected:
        raise BuildError(f"expected wheel {expected}, built {wheels[0].name}")
    return wheels[0]


def safe_wheel_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def merge_wheels(paths: list[Path]) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(paths, key=lambda value: value.name):
        with zipfile.ZipFile(path) as wheel:
            for member in wheel.infolist():
                if member.is_dir():
                    continue
                if not safe_wheel_member(member.filename):
                    raise BuildError(f"unsafe wheel member in {path.name}: {member.filename}")
                value = wheel.read(member)
                if member.filename in files and files[member.filename] != value:
                    raise BuildError(
                        f"conflicting wheel member {member.filename!r} in {path.name}"
                    )
                files[member.filename] = value
    return files


def installed_content_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(files.items()):
        encoded = name.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    return digest.hexdigest()


def json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    else:
        text = json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n"
    return text.encode("utf-8")


def write_bundle(lock: dict[str, Any], wheels: list[Path], output: Path) -> tuple[Path, Path]:
    files = merge_wheels(wheels)
    bridge = BRIDGE_SOURCE.read_bytes()
    files["spork_playground_bridge.py"] = bridge
    content_digest = installed_content_digest(files)
    package_versions = {
        name: package["version"] for name, package in sorted(lock["packages"].items())
    }
    internal_manifest = {
        "format": 1,
        "contentSha256": content_digest,
        "pyodide": {
            key: lock["pyodide"][key]
            for key in ("version", "python", "emscripten", "abi", "platformTag")
        },
        "packages": package_versions,
        "bridgeSha256": sha256_bytes(bridge),
        "sources": {
            name: {
                "artifact": package["artifact"],
                "sha256": package["sha256"],
            }
            for name, package in sorted(lock["packages"].items())
        },
    }
    files["spork-playground.json"] = json_bytes(internal_manifest)

    output.mkdir(parents=True, exist_ok=True)
    temporary = output / "spork-playground.zip.tmp"
    with zipfile.ZipFile(
        temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as bundle:
        for name, value in sorted(files.items()):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(
                info, value, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )

    bundle_digest = sha256_file(temporary)
    bundle_name = f"spork-playground-{bundle_digest[:16]}.zip"
    bundle_path = output / bundle_name
    temporary.replace(bundle_path)
    if bundle_path.stat().st_size > MAX_BUNDLE_BYTES:
        raise BuildError(
            f"playground bundle is {bundle_path.stat().st_size} bytes; "
            f"limit is {MAX_BUNDLE_BYTES}"
        )

    runtime = {
        "format": 1,
        "pyodide": {
            "version": lock["pyodide"]["version"],
            "indexURL": lock["pyodide"]["cdnBase"],
        },
        "bundle": {
            "url": f"/playground-runtime/{bundle_name}",
            "sha256": bundle_digest,
            "bytes": bundle_path.stat().st_size,
        },
        "packages": package_versions,
    }
    runtime_path = output / "runtime.json"
    runtime_path.write_bytes(json_bytes(runtime, pretty=True))
    return runtime_path, bundle_path


def build(lock: dict[str, Any], output: Path, work: Path) -> tuple[Path, Path]:
    validate_documented_versions(lock)
    executable, emsdk = validate_toolchain(lock)
    downloads = work / "downloads"
    artifacts = {
        name: download(package, downloads)
        for name, package in lock["packages"].items()
    }
    pds_wheel = build_pds_wheel(
        lock, artifacts["spork-pds"], work, executable, emsdk
    )
    return write_bundle(
        lock,
        [pds_wheel, artifacts["spork-runtime"], artifacts["spork-lang"]],
        output,
    )


def replace_outputs(generated: Path, output: Path) -> None:
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True, exist_ok=True)
    for source in generated.iterdir():
        if source.is_file():
            shutil.copyfile(source, output / source.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--work", type=Path, default=DEFAULT_WORK)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        lock = load_lock(args.lock.resolve())
        output = args.output.resolve()
        static_root = (ROOT / "static").resolve()
        if output == static_root or static_root in output.parents:
            raise BuildError("generated playground runtime must not be written under static/")
        args.work.resolve().mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="output-", dir=args.work.resolve()
        ) as temporary:
            generated = Path(temporary)
            runtime, bundle = build(lock, generated, args.work.resolve())
            replace_outputs(generated, output)
            print(
                f"playground runtime built: {bundle.name} "
                f"({bundle.stat().st_size} bytes, {sha256_file(bundle)})"
            )
            print(f"runtime manifest: {runtime.name}")
    except (BuildError, OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        print(f"playground runtime build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
