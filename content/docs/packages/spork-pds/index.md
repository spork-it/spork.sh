---
title: spork-pds
description: Fast immutable persistent collections, transient builders, typed vectors, and native free-threading support.
section: package
group: packages
nav-path: [packages, spork-pds]
project: spork-pds
order: 630
package-version: "0.1.4"
changefreq: monthly
priority: 0.7
---

`spork-pds` is the standalone CPython extension behind Spork’s persistent collection values. It has no dependency on the language or runtime and can be used directly from Python.

## Install

```bash
python -m pip install "spork-pds==0.1.4"
```

Published wheels cover supported CPython versions and platforms. A C compiler and Python development headers are required when building the source distribution.

## Collection families

- `Vector`, `Map`, and `Set` provide general persistent sequence, mapping, and set semantics.
- `SortedVector` retains duplicates in a persistent red-black tree.
- `DoubleVector` and `IntVector` store unboxed numeric values and export read-only buffers.
- `Cons` provides immutable linked-list cells.
- Single-use transients make large controlled update batches efficient.

Persistent operations return new values while sharing unchanged structure. Existing versions remain unchanged. Immutability is shallow: Python objects stored inside a collection retain their own behavior.

## Package reference

- [Practical guide](/docs/packages/spork-pds/guide/)
- [API reference](/docs/packages/spork-pds/api/)
- [Design and operation costs](/docs/packages/spork-pds/design/)
- [Native free-threading contract](/docs/packages/spork-pds/free-threading/)
- [Benchmark methodology](/docs/packages/spork-pds/benchmarks/)
- [Source](https://github.com/spork-it/spork-pds)
- [PyPI](https://pypi.org/project/spork-pds/0.1.4/)
