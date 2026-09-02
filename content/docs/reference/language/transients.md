---
title: Transient data structures
description: Use scoped mutable builders without changing persistent originals.
section: reference
group: language
project: spork-lang
order: 210
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Transients are mutable builders for `Vector`, `Map`, `Set`, `SortedVector`, `DoubleVector`, and `IntVector`. Operations ending in `!` mutate the builder; `persistent!` returns an immutable value and invalidates the transient. The original persistent collection is never changed.

`with-mutable` scopes that lifecycle and returns the persistent result automatically:

```spork
(def original [1 2 3])
(def updated
  (with-mutable [builder original]
    (conj! builder 4)))

original ; => [1 2 3]
updated  ; => [1 2 3 4]
```

The available mutation operations and Python-compatible mutable APIs vary by transient type. See [transient operations](/docs/reference/standard-library/transients/) in the standard library reference for the complete API and interoperability examples.
