---
title: Checks and tests
description: Validate complete projects and run isolated synchronous or asynchronous test declarations.
section: reference
group: tooling
project: spork-lang
order: 350
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Project checks analyze source without running it; project tests execute declarations created by `deftest`. Both commands use the nearest manifest and its delegated project toolchain.

## Project checks

Run a complete project check from anywhere below the directory containing `spork.it`:

```bash
spork check
```

The command reads every `.spork` file below `:source-paths` and `:test-paths`, builds a project namespace and symbol index, and reports all diagnostics it can find in one run. It checks:

- reader and compiler errors;
- missing source roots and missing namespace declarations in source files;
- namespace names against their source-relative paths, including the conventional `_`-to-`-` mapping and package `__init__.spork` files;
- duplicate namespace declarations;
- unresolved Spork namespaces and Python modules;
- names requested through `:refer` that the target namespace does not export;
- the configured `:main` namespace and function;
- package `:commands` source namespaces, functions, and target kinds;
- generated `:api` source exports, normalized names, and hand-written-file conflicts; and
- both ordinary and generated package-level Spork namespaces.

Test namespaces normally match their path. A mirrored test such as `tests/acme/core.spork` may also declare `acme.core-test`; test files without an `ns` form remain valid. Exclude all configured test paths when checking only distributable sources:

```bash
spork check --no-tests
```

`spork check` does not create `.spork-out/`, create a virtual environment, install dependencies, or run ordinary top-level forms. If a project environment already exists, its site-packages are used. A missing Python dependency is reported with a suggestion to run `spork sync`. User-defined macros must execute at compile time so their expansions can be checked; macros and read-time evaluation therefore remain trusted code, as they are during a build.

The human format uses compiler-style, 1-based locations and stable diagnostic codes:

```text
src/acme/core.spork:3:14: error SPK007: Namespace 'acme.util' does not export 'missing'
Checked 4 files; 1 error, 0 warnings
```

For editor, CI, or other machine consumers, request versioned JSON:

```bash
spork check --format json
spork check --json             # equivalent shorthand
```

The top-level object contains `version`, `project`, `projectRoot`, `filesChecked`, `namespacesChecked`, `errors`, `warnings`, `success`, and `diagnostics`. Each diagnostic contains `path`, `line`, `column`, `endLine`, `endColumn`, `severity`, `code`, and `message`. JSON line and column values are 1-based. Paths inside the project are project-relative and use `/` separators.

| Code | Meaning |
| --- | --- |
| `SPK001` | Source parse/read error or manifest loading error. |
| `SPK002` | Missing namespace declaration in a source file. |
| `SPK003` | Declared namespace does not match the source path. |
| `SPK004` | Namespace is declared by multiple project files. |
| `SPK005` | Invalid namespace clause or require specification. |
| `SPK006` | Required Spork namespace cannot be resolved. |
| `SPK007` | A referred symbol is not exported by its namespace. |
| `SPK008` | Imported Python module cannot be resolved. |
| `SPK009` | Compilation failed after structural checks. |
| `SPK010` | The configured `:main` target is invalid. |
| `SPK011` | The generated `:api` configuration is invalid. |
| `SPK012` | A configured source root does not exist. |
| `SPK013` | No Spork source files were found. |
| `SPK014` | A package `:commands` source target is invalid. |

The command exits with status zero when no errors are present and status one otherwise. `--warnings-as-errors` also makes warnings fail the command while preserving their warning severity in output.

## Testing

Declare a test with the top-level `deftest` form. Test bodies are registered when a namespace loads but are not executed by `spork run`, direct file execution, normal namespace loading, or project builds.

```spork
(ns hello-spork.core)

(defn greet [name]
  (+ "Hello, " name "!"))

(deftest greet-works
  (assert (= (greet "Spork") "Hello, Spork!")))
```

`spork test` discovers any `.spork` file containing a direct top-level `deftest` below either `:source-paths` or `:test-paths`. File names do not affect discovery, and files without declarations are ignored.

Each declared test runs independently, and an uncaught exception marks only that declaration as failed. Async declarations written as `(deftest ^async name ...)` are awaited by the runner. Files are isolated in separate processes.

A `deftest` name must be a valid unqualified symbol, declarations take no parameters, `^async` is the only supported test metadata, and duplicate normalized names in one file are rejected. Test files should not mix declarations with top-level assertions because top-level code runs while the file is being loaded, before declared tests begin.
