---
title: Python builtins
description: Python constructors, introspection, iteration, numeric functions, and object attributes available to Spork.
section: reference
group: standard-library
project: spork-lang
order: 510
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork source can call ordinary Python builtins alongside runtime bindings installed by the language. This page identifies the boundary and the names whose Spork binding differs from Python’s builtin of the same name.

## Related language features

The following topics are language behavior rather than standard-library APIs and are documented in the [language reference](/docs/reference/language/):

- [protocol definitions and extension](/docs/reference/language/classes-and-protocols/#protocols);
- [namespaces, `:require`, and Python `:import`](/docs/reference/language/namespaces/);
- [keyword arguments](/docs/reference/language/functions/#keyword-arguments) and [attribute access](/docs/reference/language/python-interop/#attribute-and-method-access);
- [exceptions](/docs/reference/language/exceptions/);
- [async functions and generators](/docs/reference/language/async-and-generators/).

Python builtins remain accessible unless a Spork runtime binding overrides the same name. Notably, `map`, `filter`, `min`, `max`, and `abs` documented on this page are Spork runtime functions, while constructors such as `list`, `dict`, and `set` create Python built-in collections.

```spork
(print "hello" "world")
(len [1 2 3])                  ; => 3
(= (type 42) int)              ; => true
(str 42)                       ; => "42"
(int "42")                     ; => 42
(float "3.14")                 ; => 3.14

; Python collection constructors retain their Python types
(def py-list (list (range 5)))
(isinstance py-list list)      ; => true
(vec py-list)                  ; => [0 1 2 3 4]

(def py-dict (dict [[:a 1] [:b 2]]))
(isinstance py-dict dict)      ; => true
(get py-dict :a)               ; => 1

(def py-set (set [1 2 2 3]))
(isinstance py-set set)        ; => true
(contains? py-set 3)           ; => true

(vec (sorted [3 1 2]))         ; => [1 2 3]
(vec (reversed [1 2 3]))       ; => [3 2 1]
(vec (map vec (enumerate ["a" "b" "c"])))
; => [[0 "a"] [1 "b"] [2 "c"]]
(vec (map vec (zip [1 2] ["a" "b"])))
; => [[1 "a"] [2 "b"]]

(doall (map inc [1 2 3]))      ; => [2 3 4]
(doall (filter even? [1 2 3 4])) ; => [2 4]
(any [false false true])       ; => true
(all [true true true])         ; => true
(sum [1 2 3 4])                ; => 10
(min 1 2 3)                    ; => 1
(max 1 2 3)                    ; => 3
(abs -5)                       ; => 5
(round 3.7)                    ; => 4
(callable inc)                 ; => true
(hasattr "hello" "upper")     ; => true
((getattr "hello" "upper"))    ; => "HELLO"

(def Box (type "Box" (tuple) (dict)))
(def box (Box))
(setattr box "attr" 42)
(getattr box "attr")           ; => 42
```
