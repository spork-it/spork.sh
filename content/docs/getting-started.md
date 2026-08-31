---
title: Getting started
description: Install Spork, run a source file, explore the REPL, and create a project with its own reproducible toolchain.
section: start
group: start
project: spork-lang
order: 10
changefreq: weekly
priority: 0.9
---
Spork supports CPython 3.10 through 3.14. The recommended installation keeps the command-line tool in an isolated environment.

## Install the CLI

On Linux, macOS, or WSL, install the latest release with the script hosted on this site:

```bash
curl -fsSL https://spork.sh/install | sh
```

<!-- installer-verification -->

The script checks for CPython 3.10 or newer, creates an isolated environment under `~/.spork`, installs `spork-lang` from PyPI, and links the command to `~/.local/bin/spork`. It never uses `sudo` or edits shell configuration. During an update it moves the old managed environment aside, restores it if installation fails, and deletes it only after the replacement and launcher are verified. [Read the script](https://spork.sh/install) before running it.

Install with [`pipx`](https://pipx.pypa.io/) instead when you already use it to manage command-line tools:

```bash
pipx install spork-lang
```

Use `pip` when Spork belongs in an existing virtual environment:

```bash
python -m pip install spork-lang
```

Confirm the selected Spork, Python, and platform versions:

```bash
spork version
```

## Run one file

Create `hello.spork`:

```spork
(defn greet [name]
  (fmt "Hello, {}!" name))

(print (greet "Spork"))
```

Run it directly:

```text
$ spork hello.spork
Hello, Spork!
```

A file is enough for experiments and small tools. It can import Python modules, define macros, use async functions, and access the same runtime as a full project.

## Explore at the REPL

Running `spork` without arguments opens the interactive REPL:

```text
$ spork
Spork REPL - A Lisp for Python
user> (+ 1 2 3)
6
user> (assoc {:language "Spork"} :host "Python")
{:language 'Spork' :host 'Python'}
```

Use the REPL to inspect Python objects and try language forms. Inside a project, `spork repl` also adds project source paths and installed dependencies.

## Create a project

Scaffold an application when you want dependencies, tests, checks, builds, and a declared entry point:

```bash
spork new hello-spork
cd hello-spork
spork sync
spork check
spork test
spork run
```

The generated layout is intentionally conventional:

```text
hello-spork/
├── spork.it
├── src/
│   └── hello_spork/
│       └── core.spork
├── tests/
│   └── hello_spork/
│       └── core_test.spork
├── .gitignore
└── README.md
```

`spork sync` creates `.venv`, installs the project's Python dependencies, and selects a `spork-lang` version compatible with the manifest. Later project commands automatically delegate to that local toolchain.

## Add a Python dependency

Dependencies are ordinary Python package requirements. Add one from any directory beneath the project root:

```bash
spork add "httpx>=0.27"
spork sync
```

Then import it directly in Spork:

<!-- verify-docs: skip=external-network -->
```spork
(ns hello-spork.core
  (:import [httpx :refer [get]]))

(def response (get "https://example.com"))
(print response.status-code)
```

Hyphens in Spork identifiers normalize to underscores for Python compatibility, so `status-code` accesses Python's `status_code` attribute.

## Where next?

Continue with the [language tour](/docs/language/) to learn the core forms, or read [projects and tooling](/docs/projects/) to understand the project lifecycle in detail. The [Python interop guide](/docs/python-interop/) covers the boundary in both directions.
