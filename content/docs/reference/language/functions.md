---
title: Functions
description: Anonymous, named, multi-arity, variadic, keyword, and destructured functions.
section: reference
group: language
project: spork-lang
order: 130
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork functions are Python callables with Lisp parameter syntax, lexical closures, defaults, variadic parameters, destructuring, and optional multi-arity dispatch. This page defines invocation and function declaration forms.

## Anonymous Functions

```spork
(fn [x] (* x x))

(fn [x y]
  (let [sum (+ x y)]
    (* sum sum)))
```

### Reader shorthand

The [`#(...)` reader macro](/docs/reference/language/reader-macros/#anonymous-functions) provides a compact anonymous-function form with `%` placeholders. Use `fn` when names, destructuring, annotations, keyword-only parameters, or multiple body forms should be explicit.

## Named Functions

`defn` binds a function name. A string immediately after the parameter vector becomes the function's Python docstring.

```spork
(defn square [x]
  (* x x))

; With docstring
(defn greet [name]
  "Returns a greeting string."
  (fmt "Hello, {}!" name))
```

## Multi-Arity Functions

Instead of one parameter vector, a function may contain several parenthesized clauses. Each clause starts with its own parameter vector, and calls dispatch by argument count.

```spork
(defn greet
  ([name]
   (greet name "Hello"))
  ([name greeting]
   (fmt "{}, {}!" greeting name)))

(greet "Alice")           ; => "Hello, Alice!"
(greet "Alice" "Hi")      ; => "Hi, Alice!"
```

## Variadic Functions

Within a parameter vector, `& name` collects the remaining positional arguments under `name`.

```spork
; Rest arguments
(defn sum [& nums]
  (reduce + 0 nums))

(sum 1 2 3 4)  ; => 10

; Mixed positional and rest
(defn log [level & msgs]
  (print level ":" (.join "" (map str msgs))))
```

## Keyword Arguments

In a parameter vector, `*` separates positional parameters from keyword-only parameters. A bare name after `*` is required; `(name default)` supplies a default. `** name` instead collects otherwise-unbound keyword arguments into a persistent map.

At a call site, `*{:key value}` converts entries to Python keyword arguments. The inline spelling `* :key value` is equivalent. A map variable can be splatted as `*{options}`; map variables and literal entries can also be combined inside the braces. More than one splat may follow the positional arguments.

```spork
; `age` and `email` are required keyword-only parameters
(defn create-user [name * age email]
  {:name name :age age :email email})

(create-user "Alice" *{:age 30 :email "alice@example.com"})
; => {:name "Alice" :age 30 :email "alice@example.com"}

; A two-item list declares a keyword-only parameter and its default
(defn config [host * (port 8080) (debug false)]
  {:host host :port port :debug debug})

(config "localhost")
; => {:host "localhost" :port 8080 :debug false}
(config "example.com" *{:port 3000})
; => {:host "example.com" :port 3000 :debug false}

; Inline keyword arguments follow a bare `*`
(config "example.com" * :port 3000 :debug true)
; => {:host "example.com" :port 3000 :debug true}

; `*{options}` splats every entry in a map variable
(def options {:port 4000 :debug true})
(config "example.com" *{options})
; => {:host "example.com" :port 4000 :debug true}

; Literal entries and map variables may share one splat
(def debug-options {:debug true})
(config "example.com" *{:port 5000 debug-options})
; => {:host "example.com" :port 5000 :debug true}

; `** opts` captures keyword arguments not bound to named parameters
(defn flexible [required ** opts]
  {:required required :opts opts})

(flexible "value" *{:a 1 :b 2})
; => {:required "value" :opts {:a 1 :b 2}}

; The same call syntax works with Python functions and methods
(def template "{name} is {age}")
(template.format *{:name "Alice" :age 30}) ; => "Alice is 30"
```

## Destructuring in Parameters

A vector parameter pattern binds values by position and may nest. `&` binds the remaining positions as a persistent vector. Too few positional values raise `IndexError`.

A map pattern using `{:keys [name age]}` creates local bindings from the map's `:name` and `:age` entries. The explicit form `{local :source-key}` can rename a keyword lookup, and a string may replace the source keyword. A missing map entry binds `nil`.

```spork
(defn process-point [[x y]]
  (+ x y))

(process-point [3 4]) ; => 7

(defn split-head [[head & tail]]
  [head tail])

(split-head [1 2 3]) ; => [1 [2 3]]

(defn greet-person [{:keys [name age]}]
  (fmt "{} is {} years old" name age))

(greet-person {:name "Mina" :age 29}) ; => "Mina is 29 years old"

(defn display-name [{label :name}]
  label)

(display-name {:name "Spork"}) ; => "Spork"
```
