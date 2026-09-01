---
title: Forms and control flow
description: Definitions, bindings, conditionals, eager iteration, and tail recursion.
section: reference
group: language
project: spork-lang
order: 120
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

This page defines Spork’s binding, sequencing, and control-flow forms. Spork is expression-oriented, but it compiles to Python AST and retains a distinction between value-producing positions and statement positions. Unless a form states otherwise, a body evaluates from top to bottom and its final executed expression supplies the body's value.

## Special Forms

### Definition

`def` evaluates its initializer once and binds the result in the current module or function scope. A binding name is normalized to its Python spelling, so `max-retries` becomes `max_retries` in generated Python. Vector and map binding patterns destructure the initializer.

`set!` assigns a simple binding or object attribute. In a value position it returns the assigned value; this makes assignment inside a larger expression explicit rather than relying on Python statement syntax.

```spork
; Define a value
(def x 42)

; Define with destructuring
(def [a b] [1 2])
(def {:keys [name age]} person)

; Reassign a binding or object attribute
(set! x 100)
(set! obj.attr value)

; The assigned value can be retained
(def assigned (set! x 125))
[x assigned]           ; => [125 125]
```

Use `assoc`, `conj`, and the other persistent update operations rather than `set!` to change a persistent collection. Complete binding-pattern behavior is documented under [destructuring](/docs/reference/language/functions/#destructuring-in-parameters).

### Test Declarations

`deftest` declares a named, parameterless test at module top level. Its body is compiled and registered but only invoked by `spork test`, so inline tests may live beside regular definitions without running during normal program execution.

```spork
(deftest addition-works
  "An optional docstring may precede the body."
  (assert (= (+ 2 3) 5)))

(deftest ^async async-operation-works
  (def result (await (fetch-result)))
  (assert (= result 42)))
```

A test passes when its body returns normally and fails when it raises an uncaught exception. Return values are ignored. `^async` is the only supported test metadata. Names must be valid unqualified symbols, duplicate normalized names in one file are invalid, and `deftest` cannot be nested in a function or expression. Discovery is documented under [testing](/docs/reference/tooling/checks-and-tests/#testing).

### Let Bindings

`let` takes a vector of alternating binding patterns and initializer expressions. Initializers run once, from left to right, and each later initializer can use earlier bindings. The names are local to the `let` body. An empty body has the value `nil`.

```spork
; Basic let
(let [x 1
      y 2]
  (+ x y))  ; => 3

; Later bindings see earlier ones
(let [x 1
      y (+ x 1)]
  y)  ; => 2

; Destructuring in let
(let [[a b] [1 2]
      {:keys [name]} {:name "Alice"}]
  (fmt "{}: {}, {}" name a b))  ; => "Alice: 1, 2"
```

The binding vector must contain an even number of forms. A binding may be a symbol, a nested vector pattern, or a map destructuring pattern; `loop` is stricter and accepts only simple symbols.

### Do Blocks

`do` groups zero or more forms wherever one form is expected. It evaluates them in order and returns the final value; an empty `do` returns `nil`.

```spork
(do
  (print "side effect")
  (+ 1 2))  ; => 3

(do) ; => nil
```

## Control Flow

### Truthiness and boolean forms

Conditions use Python truth testing. `nil`, `false`, numeric zero, empty strings, and empty collections are falsey; non-empty collections and other ordinary objects are truthy. This differs from Lisps in which only `nil` and `false` are falsey.

```spork
(if 0 :truthy :falsey)   ; => :falsey
(if "" :truthy :falsey)  ; => :falsey
(if [] :truthy :falsey)  ; => :falsey
(if [0] :truthy :falsey) ; => :truthy
```

`and` and `or` short-circuit and return one of their operands rather than coercing it to `bool`. `not` returns a boolean.

```spork
(and "ready" 3)      ; => 3
(or nil "fallback") ; => "fallback"
(not [])             ; => true
```

### If

`if` evaluates its test once and then evaluates exactly one branch. The else branch is optional and defaults to `nil`.

```spork
(if condition
  then-expr
  else-expr)

(if (> x 0) "positive")
```

Both branches may contain forms that require statement lowering, such as `let`, `try`, `with`, or `loop`; the selected branch still supplies the `if` value.

### Cond (Multi-way Conditional)

`cond` takes test/result pairs. Tests run from left to right, and only the result paired with the first truthy test is evaluated. If no test matches, the result is `nil`. The conventional final test `:else` is a truthy keyword and acts as a fallback.

```spork
(cond
  (< x 0) "negative"
  (> x 0) "positive"
  :else "zero")

(cond false :first false :second) ; => nil
```

### When / Unless

`when` evaluates its body only for a truthy test; `unless` evaluates its body only for a falsey test. Their bodies are implicit `do` blocks. A skipped body returns `nil`, while an executed body returns its final value.

```spork
(when condition
  (do-something)
  (do-more))

(unless condition
  (do-something))

(when true 1 2)   ; => 2
(unless true 1 2) ; => nil
```

### While Loop

`while` tests before every iteration and executes its body for effects while the test remains truthy. It is statement-oriented. To retain a computed value, update a binding and place the desired result after the loop in a surrounding `let` or `do` body.

```spork
(def counted
  (let [i 0]
    (while (< i 3)
      (set! i (inc i)))
    i))
counted ; => 3
```

### `for` expression

`for` accepts exactly one binding pair, eagerly evaluates its body once for each input, and returns a persistent vector of the final body values. It never returns a lazy iterator. `nil` results are retained, and the binding position supports vector or map destructuring.

```spork
(def squares
  (for [x (range 10)] (* x x)))
; => [0 1 4 9 16 25 36 49 64 81]

; Conditional values are retained, including nil
(for [x (range 10)]
  (if (even? x) (* x 2) nil))
; => [0 nil 4 nil 8 nil 12 nil 16 nil]

; Destructuring binds each input item
(def pairs [[1 2] [3 4] [5 6]])
(for [[a b] pairs] (+ a b))
; => [3 7 11]

; Earlier body forms run for effects; the final value is retained
(def recorded (list))
(for [x (range 5)]
  (recorded.append x)
  (let [sq (* x x)] (+ sq 1)))
; => [1 2 5 10 17]
```

The input expression is evaluated once. Because `for` is an ordinary value form, its vector can be passed to calls, selected by conditionals, returned from functions, or embedded in markup. The former `[for ...]` vector-comprehension syntax is no longer supported.

[`async-for`](/docs/reference/language/async-and-generators/#async-functions) provides the corresponding eager vector expression for Python asynchronous iterables and must run in an async context.

### Effect-only Iteration

Use `doseq` when body results are intentionally discarded. It evaluates eagerly and returns `nil` without constructing a result vector.

```spork
(doseq [x [1 2 3]]
  (print x))
; prints 1, 2, and 3; returns nil
```

Like `for`, `doseq` accepts one binding pair and supports destructuring. Use `for` when values are part of the result and `doseq` when the body exists only for effects.

### `sorted-for` expression

`sorted-for` accepts one binding pair and exactly one body expression, evaluates it eagerly for every input, and returns a `SortedVector`. Optional `:key` and `:reverse` values follow the body expression.

```spork
(sorted-for [x (range 10)] (* x x))
; => sorted_vec(0, 1, 4, 9, 16, 25, 36, 49, 64, 81)

; Sort by a derived key
(sorted-for [s ["banana" "apple" "fig"]] s :key len)
; => sorted_vec("fig", "apple", "banana")

; Reverse the configured order; duplicates remain
(sorted-for [x [3 1 4 1 5]] x :reverse true)
; => sorted_vec(5, 4, 3, 1, 1)

; Keywords are lookup functions and can be sort keys
(def score-items
  [{:name "alpha" :score 8} {:name "beta" :score 13}])
(def ranked-items
  (sorted-for [item score-items]
    {:name (:name item) :score (:score item)}
    :key :score :reverse true))
(isinstance ranked-items SortedVector) ; => true
(vec ranked-items)
; => [{:name "beta" :score 13} {:name "alpha" :score 8}]
```

The input expression and option expressions are each evaluated once. The configured keys must be mutually comparable. Destructuring is supported in the binding position.

### Loop / Recur (Tail-Call Optimization)

`loop` supplies initial values for simple symbol bindings and evaluates its body until a tail position returns a result. `recur` computes one replacement value for every loop binding and begins the next iteration without growing the Python call stack.

```spork
(loop [i 0
       acc 0]
  (if (>= i 10)
    acc
    (recur (inc i) (+ acc i))))  ; => 45
```

The binding vector must contain alternating symbols and initializers; destructuring is not supported there. `recur` must:

- appear in a tail position of the nearest `loop`;
- supply exactly one value for each loop binding; and
- be reached through tail-position `if`, `cond`, `let`, or `do` forms.

All replacement expressions are evaluated before any loop binding is changed, so values can be swapped safely:

```spork
(loop [left 1 right 2 iteration 0]
  (if (= iteration 1)
    [left right]
    (recur right left (inc iteration))))
; => [2 1]
```

`recur` is local loop control, not general recursive function dispatch. Ordinary recursive calls still use Python call frames.

## Expression and statement contexts

Python distinguishes statements, which produce no value, from expressions. Spork determines the required context from a form's position:

- A top-level form or a non-final form in a body has its value discarded.
- A binding initializer, function argument, conditional branch, or value-returning final form must produce a value.
- `do`, `let`, `if`, `try`, `with`, and `loop` may appear in value positions.
- Declarations such as `def` and `deftest`, and effect loops such as `while`, are statement-oriented.

When a block-shaped construct must produce a value, the compiler moves it into a generated helper function and calls that function immediately. For example:

```spork
(def result (let [x 1] (+ x 2)))
```

compiles roughly to:

```python
def _wrapper():
    x = 1
    return x + 2

result = _wrapper()
```

Generated helpers are an implementation technique, not a separate user-visible scope construct. Source locations remain attached to generated AST so exceptions still point back to the corresponding `.spork` form.
