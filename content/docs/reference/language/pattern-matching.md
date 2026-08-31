---
title: Pattern matching
description: Match values and define pattern-dispatched functions.
section: reference
group: language
project: spork-lang
order: 150
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Pattern matching tests one value against ordered structural patterns. It supports literals, bindings, sequence and map destructuring, predicates, guards, alternatives, and function clauses.

## Match Expression

`match` evaluates its target once, then tests alternating pattern and result forms in source order. The first match wins; if no pattern matches, it raises `MatchError`. Use `_` as an explicit fallback.

<!-- verify-docs: skip=grammar-template -->
```spork
(match value
  pattern1 result1
  pattern2 result2
  _ default-result)
```

## Pattern Types

```spork
; Literal patterns compare by value; `_` matches anything
(match x
  1 "one"
  2 "two"
  _ "other")

; `^type` checks the value's type, then binds the following name
(match x
  (^int n) (fmt "integer: {}" n)
  (^str s) (fmt "string: {}" s)
  _ "unknown")

; Vector patterns bind by position; `&` binds the unmatched tail
(match coll
  [] "empty"
  [x] (fmt "one: {}" x)
  [x y] (fmt "two: {}, {}" x y)
  [x & rest] (fmt "many, first: {}" x))

; Map patterns require literal entries and bind symbols to other values
(match m
  {:type :circle :radius r} (* 3.14 r r)
  {:type :square :side s} (* s s)
  _ 0)

; `:when` accepts a match only when its guard is truthy
(match x
  (n :when (> n 0)) "positive"
  (n :when (< n 0)) "negative"
  _ "zero")
```

A map pattern matches only when every listed key is present. This differs from ordinary binding destructuring, where a missing map entry binds `nil`.

## Pattern-Dispatched Functions

Multi-arity `defn` clauses may use destructuring patterns and a `:when` guard. Clauses with the same arity are tested in source order, and the first matching clause runs. If no arity, pattern, and guard match, the function raises `MatchError`.

```spork
(defn area
  ([{:keys [type radius]} :when (= type :circle)]
   (* 3.14 radius radius))
  ([{:keys [type width height]} :when (= type :rectangle)]
   (* width height))
  ([{:keys [type side]} :when (= type :square)]
   (* side side)))
```
