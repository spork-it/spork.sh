---
title: Projects and tooling
description: Declare a reproducible Spork project, synchronize its isolated environment, check and test source, then build or publish it.
section: guide
group: guides
project: spork-lang
order: 40
changefreq: weekly
priority: 0.8
---
A Spork project is source plus a `spork.it` manifest. Commands search the current directory and its parents for the nearest manifest, so the same workflow is available anywhere in the tree.

## The manifest

A typical application declares metadata, a compatible compiler range, Python dependencies, source and test roots, and an entry point:

```spork
{:name "weather-report"
 :version "0.1.0"
 :description "Print a small weather report"
 :requires-python ">=3.10"
 :spork-version ">=0.6,<0.7"
 :dependencies ["httpx>=0.27"]
 :dev-dependencies []
 :source-paths ["src"]
 :test-paths ["tests"]
 :main "weather-report.core:main"}
```

Paths are relative to the directory containing the manifest. Package-specific keys are preserved for installed tools; this site, for example, declares a `:site` target owned by `spork-site`.

## Synchronize once

```bash
spork sync
```

Synchronization creates `.venv`, installs dependencies, and selects a `spork-lang` toolchain within `:spork-version`. It pins the compatible active launcher when possible and otherwise asks `pip` to resolve the declared range. Project-aware commands then delegate to that environment automatically. A globally installed launcher can therefore enter projects that intentionally use different compatible toolchains.

Add and remove requirements without hand-editing the vector:

```bash
spork add "httpx>=0.27" rich
spork remove rich
spork sync
```

Requirements use normal `pip` syntax and resolve from the Python package ecosystem.

## Run the entry point

Given `:main "weather-report.core:main"`, `spork run` loads the namespace and invokes `main`:

```spork
(ns weather-report.core)

(defn ^int main [& args]
  (print "arguments:" args)
  0)
```

```bash
spork run london --units metric
```

Arguments arrive as strings. An integer return value becomes the process status. Override the configured target for one invocation with `spork run --main other.namespace:start`.

## Check before execution

`spork check` reads every source and test namespace and reports structural and compilation diagnostics without writing build output.

```bash
spork check
spork check --json
spork check --warnings-as-errors
```

Checks include namespace paths, duplicate declarations, `:require` exports, Python imports, compiler errors, the configured entry point, generated API declarations, and package command targets. Diagnostics use stable `SPK` codes and original `.spork` source locations.

## Declare and run tests

Tests are ordinary top-level declarations. Their bodies are registered when the namespace loads but run only through `spork test`.

<!-- verify-docs: skip=requires-project-fixture -->
```spork
(ns weather-report.core-test
  (:require [weather-report.core :refer [format-temperature]]))

(deftest formats-celsius
  (assert (= (format-temperature 21 :celsius) "21 °C")))

(deftest ^async fetches-report
  (def report (await (fetch-fixture)))
  (assert (= (:status report) :ok)))
```

```bash
spork test
```

Each declaration runs independently, and test files are isolated in separate processes.

## Compile readable Python

```bash
spork build --clean
```

The default `.spork-out` directory contains generated Python, original Spork source, and source-map sidecars. The output can be imported without the Spork compiler because generated modules depend on the smaller `spork-runtime` package.

A source namespace such as `src/weather_report/core.spork` becomes:

```text
.spork-out/
├── pyproject.toml
└── weather_report/
    ├── core.py
    ├── core.spork
    └── core.spork.map.json
```

## Build a distribution

Libraries and applications can produce standard Python artifacts:

```bash
spork dist --clean
python -m twine check dist/*
```

The wheel contains compiled Python, source maps, and original `.spork` files. Normal package metadata comes from `spork.it`, including dependencies, optional extras, project URLs, classifiers, license information, and generated public APIs.

## Extend the command line

A dependency can own one complete top-level command. Providers declare metadata in their manifest and receive the same project context and source loader as built-in operations.

```spork
:commands
{"report" {:main "weather-report.cli:command"
            :description "Generate a weather report"}}
```

After installation, the package contributes `spork report ...`. Provider discovery inspects package metadata without importing every plugin, and project-local providers outrank providers installed with the active launcher. While developing a provider, run `spork plugin add .` from its project root to build and install an isolated local snapshot before publishing it. See the [command-provider reference](/docs/reference/tooling/command-providers/) for replacement, removal, and precedence behavior.

This website uses that system rather than a bespoke executable: its dependency on `spork-site` contributes `spork site check`, `spork site routes`, `spork site build`, and `spork site serve`.

## Everyday command set

```text
spork repl       project-aware interactive session
spork add        add Python dependencies
spork sync       prepare the isolated project environment
spork run        invoke the configured entry point
spork test       run declared tests
spork check      validate the project without writing output
spork build      compile source namespaces to Python
spork dist       build a wheel and source distribution
spork lsp        start the language server
```

The complete [tooling reference](/docs/reference/tooling/) documents manifest fields, diagnostics, generated APIs, command providers, and distribution behavior.
