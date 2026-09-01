---
title: Builds and distributions
description: Compile source, generate public APIs, and publish wheels and source distributions.
section: reference
group: tooling
project: spork-lang
order: 360
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork can compile project source into inspectable Python modules and package those modules as standard Python distributions. This page separates generated build output from wheel and source-distribution creation.

## Build output

```bash
spork build --clean
```

The default output is `.spork-out/`. Each source module produces Python source plus a source-map sidecar:

```text
.spork-out/
├── pyproject.toml
└── hello_spork/
    ├── __init__.py
    ├── core.py
    ├── core.spork
    └── core.spork.map.json
```

The generated Python initializes the Spork runtime and lowers project `:require` clauses to normal Python imports, so it can be imported without the Spork CLI. Original `.spork` files are copied beside it for source inspection and for Spork consumers of an installed package. Hand-written `.py`, `.pyi`, and `py.typed` files under source roots are also copied for projects that do not configure a generated API.

Choose another output directory with `spork build --out-dir PATH`.

## Generated public APIs and typing

Libraries can expose idiomatic package-level APIs to both languages without maintaining facade files by adding `:api` to `spork.it`:

```spork
:api
{:from "my-spork-library.core"
 :spork {:namespace "my-spork-library"
         :exports ["Widget" "make-widget" "widget?"]}
 :python {:package "my-spork-library"
          :exports ["Widget" "make-widget" "widget?"]
          :aliases {"widget?" "is-widget"}
          :version true
          :typed true}}
```

`:from` identifies the one canonical implementation namespace. The `:spork` section generates `my_spork_library/__init__.spork`, making `(:require [my-spork-library :as library])` resolve to the declared public exports. The `:python` section generates explicit imports in `my_spork_library/__init__.py`, including both `widget_q` and its `is_widget` alias. Each target has its own export list so Spork APIs can retain names such as `swap!` and `atom?` while Python exposes conventional identifiers.

With `:version true`, the Python initializer receives `__version__` directly from the manifest. With `:typed true`, every compiled Spork module receives a generated `.pyi`, the Python package receives `__init__.pyi`, and `py.typed` is created automatically. Existing non-empty hand-written files at generated paths are rejected rather than overwritten. Either the `:spork` or `:python` section may be omitted when a library only needs one target.

Spork annotations become Python signatures and generic stubs:

```spork
(ns my-spork-library.core
  (:import [typing :refer [Callable Generic TypeVar]]))

(def T (TypeVar "T"))

(defclass Box [(Generic T)]
  (defn __init__ [self ^T value]
    (set! self._value value))

  (defn ^property ^T value [self]
    self._value))

(defn ^(Box T) box [^T value]
  (Box value))

(defn ^T update [^(Box T) boxed ^(Callable [[...] T]) function]
  (function boxed.value))
```

A parenthesized `Generic` base compiles to Python subscription syntax (`Generic[T]`). Capitalized generic return types such as `^(Box T)` are recognized as annotations, and `Callable` accepts `...` for arbitrary arguments. AOT modules use postponed annotation evaluation, so forward and recursive generic references are safe.

The generated package files are build artifacts: do not add source `__init__.spork`, `__init__.py`, `__init__.pyi`, module `.pyi`, or `py.typed` files at paths owned by `:api`.

## Build distributions

```bash
spork dist --clean
```

By default this rebuilds `.spork-out/` and creates both a wheel and source distribution in `dist/`. The configured `:spork-version` is checked against the delegated project compiler at build time. Generated package metadata directly requires `spork-runtime`—not `spork-lang`—alongside the project dependencies, optional extras, README, license, authors, classifiers, and project URLs from `spork.it`. Declared package commands become versioned `spork.commands.v1` entry points after their source and compiled payloads are validated. `--clean` removes stale build and distribution output before rebuilding.

Useful variants:

```bash
spork dist --wheel-only
spork dist --sdist-only
spork dist --no-build       # reuse existing compiled output
spork dist --dist-dir artifacts
```

## Consuming a published Spork library

Add the normal PyPI requirement to another project's manifest:

```spork
:dependencies ["my-spork-library>=1,<2"]
```

After `spork sync`, packaged Spork source is discovered directly from the project's site-packages and can be required normally:

<!-- verify-docs: skip=external-package -->
```spork
(ns my.app
  (:require [my-spork-library :as library]))
```

The same wheel exposes its compiled modules to Python using normalized package names:

```pycon
>>> from my_spork_library.core import public_function
```
