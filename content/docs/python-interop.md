---
title: Python interoperability
description: Use Python modules and objects directly from Spork, and compile Spork packages into ordinary importable Python distributions.
section: guide
group: guides
project: spork-lang
order: 30
changefreq: weekly
priority: 0.8
---
Spork is hosted on CPython and compiles to Python AST. Interoperability is therefore the normal execution model, not a separate subsystem: Python modules load through Python's importer, calls use Python's calling convention, and exceptions are Python exceptions.

## Import Python from Spork

Use `:import` in a namespace declaration to refer Python values directly:

```spork
(ns digest.core
  (:import [hashlib :refer [sha256]]
           [pathlib :refer [Path]]))

(defn file-digest [path]
  (.hexdigest (sha256 (.read-bytes (Path path)))))

(print (file-digest "README.md"))
```

Modules can also be aliased:

```spork
(ns clocks.core
  (:import [datetime :as datetime]))

(def now (datetime.datetime.now datetime.timezone.utc))
(print (now.isoformat))
```

Python dependencies are normal package requirements in `spork.it`. There is no separate Spork package mirror or FFI declaration.

## Objects stay Python objects

Imported classes create their usual instances. Attribute access, methods, iteration, slicing, context managers, exceptions, decorators, async protocols, and type checks operate on those values directly.

```spork
(ns files.core
  (:import [pathlib :refer [Path]]))

(def sources
  (for [path (.rglob (Path "src") "*.spork")]
    {:name path.name
     :bytes (getattr (path.stat) "st_size")}))
```

Spork normalizes identifiers for Python compatibility:

- `some-name` becomes `some_name`;
- `ready?` becomes `ready_q`;
- dotted access preserves the object path while normalizing each identifier.

That makes idiomatic Spork names usable with idiomatic Python APIs without adapters.

## Python-backed standard namespaces

The separately distributed `spork-runtime` package provides `std.*` namespaces over useful Python standard-library modules. They are required like Spork namespaces and keep common imports concise.

```spork
(ns config.core
  (:require [std.json :as json]))

(def encoded (json.dumps {:language "Spork" :host "CPython"}))
(print encoded)
```

You can always import the underlying Python module directly when that is clearer.

## Import Spork from Python

During source development, importing `spork` once installs the `.spork` import hook:

<!-- verify-docs: skip=requires-project-fixture -->
```python
import spork
from greetings.core import greet

print(greet("Python"))
```

For deployment, `spork build` compiles source namespaces into readable Python modules and copies source-map sidecars. Generated modules initialize the runtime themselves, so consumers do not need to install the compiler or activate an import hook.

```bash
spork build --clean
python -c 'from greetings.core import greet; print(greet("Python"))'
```

## Publish one API to both languages

Libraries can declare a canonical implementation namespace and generate package-level Spork and Python APIs from it:

```spork
:api
{:from "acme.widgets.core"
 :spork {:namespace "acme.widgets"
         :exports ["Widget" "make-widget" "widget?"]}
 :python {:package "acme.widgets"
          :exports ["Widget" "make-widget" "widget?"]
          :aliases {"widget?" "is-widget"}
          :version true
          :typed true}}
```

The build generates explicit package initializers, version metadata, `.pyi` stubs, and `py.typed`. Spork callers retain Lisp-style names while Python callers receive normalized names and optional conventional aliases.

## Know where semantics come from

Interop is direct, but it is not magic. Python APIs retain their Python behavior: mutable objects can still mutate, iterators can be one-shot, calls can perform I/O, and extension modules can impose platform constraints. Spork's persistent collections add a strong immutable foundation without pretending every imported object has the same semantics.

Read the complete [Python interoperability reference](/docs/reference/language/python-interop/) and [build and distribution reference](/docs/reference/tooling/builds-and-distributions/) for advanced usage.
