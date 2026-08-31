---
title: Macros
description: Define macros with quasiquoting, unquoting, and hygienic generated symbols.
section: reference
group: language
project: spork-lang
order: 180
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Macros run during compilation, receive unevaluated Spork forms, and return forms for the compiler to continue processing. This page covers declarations, template construction, hygiene helpers, and expansion inspection. The fixed syntax and expansion rules for quote, quasiquote, `~`, and `~@` are defined in the [reader macro reference](/docs/reference/language/reader-macros/#quasiquote-and-unquote).

## Defining Macros

```spork
(defmacro unless [test & body]
  `(if ~test nil (do ~@body)))
```

## Using quasiquote in macros

Reader macros provide the template operations; macro code combines them to return a complete form:

```spork
; ` creates a template
; ~ inserts one evaluated value
; ~@ inserts each value from a sequence into the surrounding form

(defmacro debug [expr]
  `(let [val# ~expr]
     (print '~expr "=" val#)
     val#))
```

## Auto-gensym

Inside a quasiquoted template, appending `#` to a symbol creates a unique generated symbol. Repeated uses of the same suffixed name within that template resolve to the same generated symbol, preventing accidental capture of a caller's bindings:

```spork
(defmacro swap! [a b]
  `(let [tmp# ~a]
     (set! ~a ~b)
     (set! ~b tmp#)))
```
