---
title: Prelude macros
description: Automatically loaded control flow, threading, utility, composition, predicate, and protocol macros.
section: reference
group: standard-library
project: spork-lang
order: 470
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

The prelude is automatically loaded in every Spork namespace. No import required.

## Control Flow

The prelude supplies `when`, `unless`, and `cond`, while their evaluation semantics and examples live in [control flow](/docs/reference/language/forms-and-control-flow/#control-flow) in the language reference:

| Macro | Behavior |
|-------|----------|
| `when` | Evaluate its body when the test is truthy; otherwise return `nil` |
| `unless` | Evaluate its body when the test is falsy; otherwise return `nil` |
| `cond` | Return the result for the first truthy test, or `nil` when none matches |

## Threading Macros

### `->`
Thread-first: inserts x as second item (first argument) in each form.
```spork
(-> 5
    (+ 3)
    (* 2))     ; => 16

(-> {:a 1}
    (assoc :b 2)
    (assoc :c 3))
; => {:a 1 :b 2 :c 3}

(-> [1 2 3]
    (conj 4)
    (conj 5))
; => [1 2 3 4 5]

; Without arrow:
(conj (conj (assoc {:a 1} :b 2) [:c 3]) [:d 4])
; => {:a 1 :b 2 :c 3 :d 4}

; With arrow:
(-> {:a 1}
    (assoc :b 2)
    (conj [:c 3])
    (conj [:d 4]))
; => {:a 1 :b 2 :c 3 :d 4}
```

### `->>`
Thread-last: inserts x as last item (last argument) in each form.
```spork
(->> [1 2 3 4 5]
     (filter even?)   ; (filter even? [1 2 3 4 5])
     (map inc)        ; (map inc (filter even? ...))
     (reduce +))      ; (reduce + (map inc ...))
; => 8

(->> (range 10)
     (filter odd?)
     (map #(* % %))
     (take 3))
; => (1 9 25)

; Sequence transformations commonly use thread-last
(->> users
     (filter :active)
     (map :email)
     (take 10))
```

## Utility Macros

### `comment`
Ignores body. Useful for commenting out code blocks while keeping them syntactically valid.
```spork
(comment
  (this code is ignored)
  (but remains syntactically valid)
  (useful for REPL experimentation))

(def result 42)
(comment
  ; Old implementation:
  (def result (expensive-calculation)))
```

### `fmt`
Python-style string formatting with {} placeholders.
```spork
; Positional
(fmt "Hello, {}!" "World")          ; => "Hello, World!"
(fmt "{} + {} = {}" 1 2 3)          ; => "1 + 2 = 3"

; Indexed
(fmt "{1} before {0}" "B" "A")      ; => "A before B"
(fmt "{0} {0} {0}" "echo")          ; => "echo echo echo"

; Named (using *{} kwargs)
(fmt "Hello {name}!" *{:name "Alice"})
; => "Hello Alice!"

(fmt "{name} is {age} years old" *{:name "Bob" :age 30})
; => "Bob is 30 years old"

; Format specifiers
(fmt "{:.2f}" 3.14159)              ; => "3.14"
(fmt "{:>10}" "hi")                 ; => "        hi"
(fmt "{:<10}" "hi")                 ; => "hi        "
(fmt "{:05d}" 42)                   ; => "00042"
```

### `assert`
Raises `AssertionError` when the test is falsy. An optional second form supplies the exception message.
```spork
(assert (> x 0) "x must be positive")
(assert (valid? data))

(defn withdraw [balance amount]
  (assert (<= amount balance) "Insufficient balance")
  (- balance amount))
```

## Collection Iteration Macros

### `mapv`
Applies a function to one collection eagerly and returns a vector.
```spork
(mapv inc [1 2 3])          ; => [2 3 4]
(mapv str [1 2 3])          ; => ["1" "2" "3"]
```

### `filterv`
Filters one collection eagerly and returns a vector.
```spork
(filterv even? [1 2 3 4 5]) ; => [2 4]
(filterv pos? [-1 0 1 2])   ; => [1 2]
```

### `doseq`
Executes the body for each value from one binding pair and returns `nil`. Use it when only side effects are needed.
```spork
(doseq [x [1 2 3]]
  (print x))
; prints each value on its own line: 1, 2, 3

(doseq [item items]
  (process item)
  (save item))
```

## Function Composition

### `comp`
Composes single-argument functions from right to left. With no functions it returns an identity function; with one, it returns that function.
```spork
((comp) 5)                      ; => 5
((comp str inc) 5)              ; => "6"
((comp inc inc inc) 0)          ; => 3
((comp first rest) [1 2 3])     ; => 2

(def process (comp str inc abs))
(process -5)                    ; => "6"
```

### `partial`
Partial function application.
```spork
((partial + 10) 5)              ; => 15
((partial + 1 2) 3 4)           ; => 10

(def add10 (partial + 10))
(add10 5)                       ; => 15

(def greet (partial + "Hello, "))
(greet "World")                 ; => "Hello, World"
```

### `identity`
Expands to its argument unchanged.
```spork
(identity 42)                   ; => 42
(identity nil)                  ; => nil
```

`identity` is a macro, not a first-class function binding. Use `(fn [x] x)` when an identity function must be passed as a value.

### `constantly`
Returns a function that ignores its arguments and evaluates the supplied form as its result. Because `constantly` is a macro, a non-literal result form is evaluated on every call rather than when the function is created.
```spork
((constantly 42) :anything)     ; => 42
((constantly :default) 1 2 3)   ; => :default

(map (constantly 0) [1 2 3])    ; => (0 0 0)
```

### `complement`
Returns a variadic function that calls its input function and negates the result's truth value.
```spork
((complement even?) 3)          ; => true
((complement even?) 4)          ; => false

(def odd? (complement even?))
(filter (complement (fn [x] (= x nil))) [1 nil 2 nil]) ; => (1 2)
```

## Type Predicates

These predicates are prelude macros based on Python type checks. `number?` recognizes `int` and `float` only; because `bool` subclasses `int`, booleans also satisfy `int?` and `number?`. `fn?` is equivalent to Python `callable`, so callable objects and classes also satisfy it.

The collection predicates are intentionally narrow. `vector?` recognizes only `Vector`; `map?` recognizes only persistent `Map`; `list?` recognizes `Cons` and Python `list`; `seq?` recognizes only `Cons`; and `dict?` recognizes only Python `dict`. `coll?` recognizes `Vector`, `Map`, `Cons`, Python `list`, and Python `dict`. Typed vectors, sorted vectors, and sets are not included.

```spork
; Nil checks
(nil? nil)          ; => true
(nil? false)        ; => false
(some? nil)         ; => false
(some? false)       ; => true

; Type checks
(string? "hello")   ; => true
(string? 123)       ; => false
(number? 42)        ; => true
(number? 3.14)      ; => true
(number? true)      ; => true
(int? 42)           ; => true
(int? 3.14)         ; => false
(float? 3.14)       ; => true
(bool? true)        ; => true
(fn? inc)           ; => true

; Symbol/Keyword checks
(symbol? 'foo)      ; => true
(keyword? :foo)     ; => true

; Collection checks
(vector? [1 2 3])   ; => true
(vector? (vec-i64 1 2)) ; => false
(map? {:a 1})       ; => true
(list? '(1 2 3))    ; => true
(seq? (rest [1 2])) ; => true
(coll? [1 2 3])     ; => true
(coll? {:a 1})      ; => true
(coll? #{1 2})      ; => false
(dict? (dict [["a" 1]])) ; => true
```

## Collection Predicates and Accessors

`not-empty` returns its original argument when nonempty. `butlast` is lazy, while the other accessors return a single value; `last` raises `IndexError` for an empty collection.

```spork
; Empty check
(empty? [])         ; => true
(empty? [1 2 3])    ; => false
(empty? nil)        ; => true

; Not-empty (returns coll or nil)
(not-empty [1 2])   ; => [1 2]
(not-empty [])      ; => nil

; Accessors
(second [1 2 3])    ; => 2
(ffirst [[1 2] [3 4]])  ; => 1
(last [1 2 3])      ; => 3
(butlast [1 2 3])   ; => (1 2)
```

## Numeric Predicates

```spork
(even? 4)           ; => true
(even? 3)           ; => false
(odd? 3)            ; => true
(odd? 4)            ; => false
(pos? 5)            ; => true
(pos? 0)            ; => false
(neg? -5)           ; => true
(neg? 0)            ; => false
(zero? 0)           ; => true
(zero? 1)           ; => false
```

## Protocol Forms

These prelude macros support the protocol language forms:

| Macro | Purpose |
|-------|---------|
| `defprotocol` | Define a protocol and its dispatcher functions |
| `extend-type` | Implement one or more protocols for a type |
| `extend-protocol` | Implement one protocol for several types |

See [protocols](/docs/reference/language/classes-and-protocols/#protocols) in the language reference for syntax, examples, dispatch rules, structural protocols, and `isinstance` behavior.
