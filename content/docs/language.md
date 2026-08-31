---
title: Language tour
description: A compact tour of Spork's syntax, functions, immutable collections, control flow, destructuring, macros, and async support.
section: guide
group: guides
project: spork-lang
order: 20
changefreq: weekly
priority: 0.8
---
Spork code is made of values and forms. Most forms are calls, while a small set of special forms provide definitions, bindings, control flow, classes, namespaces, and other language structure.

## Values and calls

Numbers, strings, booleans, and `nil` are Python values. Keywords evaluate to themselves and double as map lookup functions.

```spork
(def person {:name "Ada" :languages ["Analytical Engine" "Spork"]})

(:name person)              ; => "Ada"
(:missing person "unknown") ; => "unknown"
(first (:languages person)) ; => "Analytical Engine"
```

Parenthesized forms call the first value with the remaining values as arguments:

```spork
(+ 1 2 3)
(print "hello")
(max 10 42)
```

Spork identifiers conventionally use hyphens. They normalize to underscores when compiled, and a trailing question mark normalizes to `_q`.

## Functions and local bindings

Functions return the value of their final expression. `let` introduces sequential local bindings, so later values can use earlier ones.

```spork
(defn rectangle-area [width height]
  (let [validated-width (max width 0)
        validated-height (max height 0)]
    (* validated-width validated-height)))

(rectangle-area 6 7) ; => 42
```

Functions support positional, optional, keyword-only, variadic, and destructured parameters. The anonymous-function reader macro uses `%`, `%2`, and `%&` placeholders:

```spork
(def double #(* % 2))
(map double [1 2 3])
```

## Persistent collections

Vector, map, and set literals produce persistent data structures; `sorted-vec` constructs a persistent `SortedVector`. Operations such as `assoc`, `conj`, and `dissoc` return new values instead of mutating their inputs. Immutability is shallow: a stored Python object retains its own mutation behavior.

```spork
(def languages ["Spork" "Python"])
(def expanded (conj languages "Clojure"))

(print languages) ; ["Spork" "Python"]
(print expanded)  ; ["Spork" "Python" "Clojure"]

(def settings {:theme :dark :line-numbers true})
(def updated (assoc settings :theme :light))
```

Structural sharing makes this practical: unchanged internal structure is reused. Transient variants are available when an algorithm needs an efficient mutation phase before returning a persistent result.

## Expression-oriented control flow

`if`, `cond`, `when`, `unless`, `let`, `do`, `match`, and iteration forms all fit in expression positions.

```spork
(defn classify [value]
  (cond
    (< value 0) :negative
    (> value 0) :positive
    :else :zero))

(def labels
  (for [value [-2 0 4]]
    {:value value :kind (classify value)}))
```

`for` evaluates eagerly and returns a persistent vector. Use `doseq` for effect-only iteration; it avoids allocating a result and returns `nil`.

```spork
(for [x (range 5)] (* x x))
; => [0 1 4 9 16]

(doseq [name ["Ada" "Grace"]]
  (print (fmt "Hello, {}" name)))
```

`sorted-for` eagerly returns a persistent `SortedVector` and can accept a key or reverse ordering.

## Destructuring and matching

Bindings can pull values from sequential and associative structures. The same model is available in `def`, `let`, function parameters, and iteration.

```spork
(def user {:name "Grace" :role :admin})
(def {:keys [name role]} user)

(for [[key value] [[:language "Spork"] [:host "Python"]]]
  (fmt "{} = {}" key value))
```

Pattern matching handles literals, captures, sequence patterns, map patterns, class patterns, guards, and alternatives while compiling to Python's native match machinery.

<!-- verify-docs: compile=fragment -->
```spork
(match message
  {:kind :text :body body} (print body)
  {:kind :quit}             :done
  _                         :unknown)
```

## Namespaces and Python modules

An `ns` form declares a namespace and its dependencies. `:require` loads Spork namespaces; `:import` uses Python's import system.

```spork
(ns report.core
  (:require [std.json :as json])
  (:import [datetime :refer [datetime timezone]]
           [pathlib :refer [Path]]))
```

There is no separate foreign-function syntax after import. Constructors, methods, exceptions, iterators, context managers, and async values remain their normal Python objects.

## Macros

Spork code is represented by the same list and persistent collection values available to a running program. Macros receive unevaluated forms and return forms for the compiler to continue compiling.

<!-- verify-docs: compile=fragment -->
```spork
(defmacro unless-empty [value & body]
  `(if (seq ~value)
     (do ~@body)))

(unless-empty names
  (print "names were present"))
```

Quoting, quasiquoting, unquote, and unquote-splicing provide the usual tools for constructing expansions. Macros execute during compilation and should be treated as trusted project code.

## Async, classes, and protocols

Async functions and generators interoperate with Python event loops and async libraries:

```spork
(defn ^async fetch-all [client url-stream]
  (async-for [url url-stream]
    (await (client.get url))))
```

Spork also supports Python-compatible classes, decorators, type annotations, protocols, properties, exception handling, context managers, and generators. These features use Python objects and semantics rather than parallel runtime abstractions.

## Full reference

This tour introduces the working model rather than every form. Continue with the complete [language reference](/docs/reference/language/) for semantics and edge cases, and use the [standard library reference](/docs/reference/standard-library/) for built-in values and functions.
