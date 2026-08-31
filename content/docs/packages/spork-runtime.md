---
title: spork-runtime
description: The compiler-free Python runtime and standard namespaces used by generated Spork programs.
section: package
group: packages
nav-path: [packages, spork-runtime]
project: spork-runtime
order: 620
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

`spork-runtime` is the runtime distribution for Spork programs. It contains:

- the runtime types and helpers emitted Python code depends on;
- persistent collection integration backed by [`spork-pds`](/docs/packages/spork-pds/);
- namespace and protocol support;
- JSON support and declared-test descriptors; and
- the Spork standard library implemented as ordinary Python modules.

It intentionally contains no reader, compiler, import hook, or `.spork` source files. A compiled Spork application can therefore depend on `spork-runtime` without installing `spork-lang` or compiling the standard library during installation.

## Install

```bash
pip install spork-runtime
```

## Python API

```python
from spork.runtime import Keyword, assoc, get, hash_map, vec
from spork.std import map as maps
from spork.std import string

users = hash_map(Keyword("count"), 1)
users = maps.update(users, Keyword("count"), lambda value: value + 1)
assert get(users, Keyword("count")) == 2
assert string.join(", ", vec("Spork", "Python")) == "Spork, Python"
```

Python standard-library modules mirror the Spork namespaces:

| Spork namespace | Python module |
| --- | --- |
| `std.string` | `spork.std.string` |
| `std.map` | `spork.std.map` |
| `std.json` | `spork.std.json` |

`spork.std.prelude.MACROS` exposes the built-in macro implementations as Python callables for the compiler to install into its macro environment.

## Runtime boundary

The supported public surface is exported from `spork.runtime` and the `spork.std` modules listed in the table. Compiler modules, reader forms, and project APIs belong to `spork-lang` and are not runtime dependencies. Generated code may use lower-level `spork.runtime` helpers, but application authors should prefer the documented package exports and standard-library APIs.

## Generated-code contract

A compiled module initializes the runtime and imports required Spork namespaces as ordinary Python modules. The runtime supplies keyword and symbol values, persistent collection constructors and operations, protocol dispatch, namespace registration, JSON conversion, declared-test descriptors, and prelude macro callables used by the compiler. It does not compile `.spork` source at installation or import time.

## Namespace packaging

`spork-runtime` and `spork-pds` distribute their top-level `spork` directories as namespace-package portions. When `spork-lang` is installed, its `spork` package extends that path. The distributions can therefore contribute separate modules under one Python namespace without making the compiler a runtime requirement.

## Related references

- [Standard library reference](/docs/reference/standard-library/)
- [spork-lang package](/docs/packages/spork-lang/)
- [Source](https://github.com/spork-it/spork-runtime)
- [PyPI](https://pypi.org/project/spork-runtime/0.1.1/)
