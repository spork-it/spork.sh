---
title: Documentation
description: Install Spork, learn its core language model, use Python libraries directly, and take a project from source to distribution.
section: start
group: start
project: spork-lang
order: 0
nav-title: Overview
changefreq: weekly
priority: 0.9
---
Spork is a Lisp dialect hosted on CPython. It compiles forms to Python's abstract syntax tree, uses Python objects and exceptions directly, and adds the language features and project workflow expected from a modern Lisp.

## What to expect

Spork keeps its core model compact. Parentheses form calls and special forms, square brackets create persistent vectors, curly braces create persistent maps, and `#{...}` creates persistent sets. Hyphenated names are idiomatic in Spork and normalize naturally when code crosses into Python.

```spork
(defn greet [name]
  (fmt "Hello, {}!" name))

(for [name ["Ada" "Grace" "Edsger"]]
  (greet name))
; => ["Hello, Ada!" "Hello, Grace!" "Hello, Edsger!"]
```

The guides here focus on the shortest route to useful code. Continue with the complete [language reference](/docs/reference/language/), [standard library reference](/docs/reference/standard-library/), and [tooling reference](/docs/reference/tooling/).

> Spork is young and evolving. Projects declare a compatible `:spork-version` range so their toolchain remains explicit and reproducible.
