---
title: Namespaces and entry points
description: Map source paths to namespaces and load project entry points through the reusable runtime.
section: reference
group: tooling
project: spork-lang
order: 330
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Project source paths determine how `.spork` files map to importable namespaces. Entry-point targets then select an exported value or callable using `namespace:name` syntax.

## Source paths and namespaces

A namespace maps to a `.spork` file below a source path. For example:

```text
src/acme/tools/core.spork
```

contains:

```spork
(ns acme.tools.core)
```

and can be required as:

```spork
(ns acme.app
  (:require [acme.tools.core :as tools]))
```

Hyphens in Spork identifiers are normalized to underscores for Python compatibility. Use the Lisp-style spelling in Spork source and keep namespace declarations consistent with their paths.

A public package namespace can also live at `acme/tools/__init__.spork`. This allows `(:require [acme.tools :as tools])` while implementation namespaces remain below the package. Public package initializers are normally generated through `:api`.

## Entry points and arguments

Given this manifest entry:

```spork
:main "hello-spork.core:main"
```

`spork run` loads the namespace and calls `main`. If `:main` contains only a namespace, the function name defaults to `main`.

```spork
(ns hello-spork.core)

(defn main [& args]
  (print "arguments:" args)
  0)
```

Pass command-line arguments after `run`:

```bash
spork run one two
```

Arguments arrive as strings. If the entry point returns an integer, Spork uses it as the process exit status. Override the manifest entry point for one invocation with:

```bash
spork run --main other.namespace:start one two
```

## Reusable source project runtime

`ProjectRuntime` provides the same source loading path used by `spork run`. It resolves configured source roots and installed Spork namespaces without requiring `.spork-out/` or a Python-importable adapter:

```python
from spork.project import ProjectConfig, ProjectRuntime


def load_project_entries():
    config = ProjectConfig.load()
    runtime = ProjectRuntime(config)
    site = runtime.load_entry("hello-spork.site:make-site")
    status = runtime.invoke_entry("hello-spork.core:main", ["one", "two"])
    return site, status
```

`load_entry` returns any exported value without calling it. `invoke_entry` requires a callable, passes string arguments positionally, uses an integer result as the process status, and treats other results as success. A target containing only a namespace defaults to its `main` function. The runtime preserves source filenames and locations in exceptions.

Command providers receive the same operations through `CommandContext.load_entry(...)` and `CommandContext.invoke_entry(...)`. `CommandContext.require_project()` returns the selected `ProjectConfig` or raises an actionable error when the command is outside a project. Its `project_root`, provider provenance, and context fields are read-only.
