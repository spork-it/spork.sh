---
title: Exceptions
description: Catch, throw, finalize, and assert with Python exception values.
section: reference
group: language
project: spork-lang
order: 200
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Spork uses Python exception objects and propagation rules. The forms on this page add expression-oriented handling, cleanup, assertions, and explicit raising without introducing a separate exception hierarchy.

## Try / Catch / Finally

```spork
(try
  (risky-operation)
  (catch ValueError e
    (print "Value error:" e)
    :error)
  (catch Exception e
    (print "General error:" e)
    :error)
  (finally
    (cleanup)))
```

## Throw

<!-- verify-docs: expect-error=ValueError -->
```spork
(throw (ValueError "invalid input"))
```

## Assert

The prelude `assert` macro raises `AssertionError` when its test is falsy. See [`assert`](/docs/reference/standard-library/prelude-macros/#assert) in the standard library reference for usage.
