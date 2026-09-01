---
title: Type annotations
description: Emit Python-compatible annotations and describe persistent collection types.
section: reference
group: language
project: spork-lang
order: 140
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

Spork uses the adjacent `^type` reader prefix for Python-compatible type annotations. An annotation is source metadata consumed by the compiler: it emits a standard Python annotation, appears in generated signatures and stubs, and can be resolved through `typing.get_type_hints`.

Annotations normally describe values; they do not validate, convert, or freeze them at runtime. Two features deliberately use type syntax for additional behavior: typed multi-arity clauses participate in runtime pattern dispatch, and exact annotated vector definitions can select specialized native storage.

## Annotation positions

| Position | Spork syntax | Generated Python shape |
| --- | --- | --- |
| `def` binding | `(def ^int count 0)` | `count: int = 0` |
| Parameter | `[^str name]` | `name: str` |
| Return value | `(defn ^str name [...] ...)` | `def name(...) -> str` |
| Class field | `(field name str)` | `name: str` |

The `^` prefix must be adjacent to its annotation expression: write `^int` or `^(List int)`, not `^ int`. Return annotations, compiler flags, and function decorators appear after `defn` and before the function name; their relative order may vary. Class fields use their dedicated type position rather than `^`; see [class fields](/docs/reference/language/classes-and-protocols/#class-fields).

## Variable Annotations

A type-decorated `def` with a simple symbol emits a Python annotated assignment. Destructuring definitions bind several names and therefore do not accept one shared variable annotation.

```spork
(def ^int max-retries 3)
(def ^str name "Alice")
(def ^float pi 3.14159)
(def ^bool enabled true)

; Generated shape:
; max_retries: int = 3
; name: str = "Alice"
```

The initializer is still an ordinary expression. Its runtime type is not checked against the annotation:

```spork
(def ^(List int) described-as-python-list [1 2 3])
(isinstance described-as-python-list Vector) ; => true
```

Use matching constructors when an exact runtime type matters. A `List[int]` annotation does not turn a persistent vector literal into a Python `list`.

## Function Parameter Annotations

Place each annotation immediately before the parameter it describes. Annotated and unannotated parameters may be mixed, and annotations work with defaults, rest parameters, keyword-only parameters, and `**` keyword capture.

```spork
(defn greet [^str name]
  (fmt "Hello, {}" name))

(defn add [^int x ^int y]
  (+ x y))

(defn format-message [^str prefix message]
  (fmt "{}: {}" prefix message))

; Defaults and rest arguments retain their ordinary parameter syntax.
; ^str before & annotates each additional positional argument.
(defn collect-labels [^str head ^str (fallback "none") ^str & rest]
  [head fallback rest])
```

In an ordinary single-arity function these annotations do not insert `isinstance` checks. Calling `greet` with a non-string reaches the function body normally and succeeds or fails according to the operations performed there.

Destructured parameters can carry annotations on their bound components where supported by the pattern syntax. See [functions](/docs/reference/language/functions/) for defaults, rest values, keyword-only values, and destructuring rules.

## Return Type Annotations

Place the return annotation between `defn` and the function name. It describes every normal return path and does not check the value at runtime.

```spork
(defn ^int square [^int x]
  (* x x))

; Generated shape:
; def square(x: int) -> int:
;     return x * x

(defn ^str greet-formally [^str name]
  (fmt "Hello, {}!" name))
```

Compiler flags and decorators can coexist with a return annotation. For example, `(defn ^async ^(Optional str) load-name [...] ...)` declares an async function whose awaited result is described as optional. The flags themselves are documented under [reader decoration](/docs/reference/language/reader-macros/#decoration).

## Generic Types

A parenthesized type form means generic subscription in annotation position: `^(List int)` emits `list[int]`, not a call to `List`. Multiple arguments become a subscription tuple, so `^(Dict str int)` emits `dict[str, int]`.

Common Python and `typing` constructors are available without imports. The annotation still does not choose the value's runtime collection type:

```spork
; Python collection annotations paired with Python collection values
(def ^(List int) numbers (list [1 2 3]))
(def ^(Dict str int) ages (dict [["alice" 30]]))
(def ^(Set str) tags (set ["a" "b"]))
(isinstance numbers list) ; => true
(isinstance ages dict)    ; => true
(isinstance tags set)     ; => true

; Optional values
(defn ^(Optional str) find-name [^int id]
  (if (valid? id)
    (lookup id)
    nil))

; A union of alternatives
(def ^(Union int str) value 42)
```

Qualified and imported names are also valid. If a type is not part of the default environment, import or define it in the namespace exactly as code using that type would.

### Callable annotations

`Callable` accepts parameter types followed by the return type. A nested vector gives the equivalent Python-shaped spelling. Use `...` when any argument list is accepted.

```spork
; Callable[[int], int]
(defn apply-fn [^(Callable int int) function ^int value]
  (function value))

; The explicit parameter-vector spelling is equivalent
(defn apply-fn2 [^(Callable [[int] int]) function ^int value]
  (function value))

; Callable[..., int]
(defn ^int apply-update [^(Callable [[...] int]) function ^int value]
  (function value))
```

For several fixed parameters, list each before the result: `^(Callable str int bool)` means `Callable[[str, int], bool]`.

### User-defined generics

User-defined generic classes import `Generic` and `TypeVar` from Python's `typing` module. A parenthesized `Generic` base emits subscription syntax rather than a function call, and capitalized generic forms are recognized as annotations.

```spork
(ns example.box
  (:import [typing :refer [Generic TypeVar]]))

(def T (TypeVar "T"))

(defclass Box [(Generic T)]
  (defn __init__ [self ^T value]
    (set! self.value value))

  (defn ^(Box T) typed-self [self]
    self))

(defn ^(Box T) box [^T value]
  (Box value))
```

Postponed annotation evaluation allows the `Box[T]` method return to refer to its containing class safely.

## Available Type Constructors

These names are installed in the ordinary Spork runtime environment:

| Name | Emitted meaning |
| --- | --- |
| `Any` | `typing.Any` |
| `Optional` | `typing.Optional` |
| `Union` | `typing.Union` |
| `List` | Python `list` |
| `Dict` | Python `dict` |
| `Set` | Python `set` |
| `Tuple` | Python `tuple` |
| `Callable` | `typing.Callable` |
| `Iterable` | `typing.Iterable` |
| `Iterator` | `typing.Iterator` |
| `Sequence` | `typing.Sequence` |
| `Mapping` | `typing.Mapping` |
| `Generator` | `typing.Generator` |
| `Type` | Python `type` |

Built-in types such as `int`, `float`, `bool`, `str`, `bytes`, `list`, and user-defined class names can also appear directly. The table describes name resolution, not a closed whitelist: the compiler accepts qualified and imported annotation names as well.

## Multi-Arity with Types

A shared return annotation applies to the generated dispatcher. Parameter annotations in multi-arity clauses are also type patterns: clauses of the same arity are tried in source order and a typed clause requires `isinstance` to succeed.

```spork
(defn ^str classify
  ([^int value] "integer")
  ([^str value] "string")
  ([value] "other"))

(classify 10)     ; => "integer"
(classify "ten")  ; => "string"
(classify 10.0)   ; => "other"
```

The untyped final clause is a fallback. Without a matching clause, the dispatcher raises `MatchError`. This runtime use is specific to patterned multi-arity dispatch; a parameter annotation on a normal single-arity function remains descriptive. See [pattern-dispatched functions](/docs/reference/language/pattern-matching/#pattern-dispatched-functions) for complete matching semantics.

## Persistent Data Structure Types

Spork's persistent data structure classes support generic subscription in annotations:

```spork
(def ^(Vector int) nums [1 2 3])
(def ^(Map str int) scores {"alice" 100})
(def ^(Cons int) items (cons 1 (cons 2 nil)))
(def ^(SortedVector int) ordered (sorted-vec [3 1 2]))
```

The unqualified `Set` type constructor describes Python's builtin `set`. Import `spork.pds` when an annotation must specifically name the persistent set class:

```spork
(ns persistent-set-annotations
  (:import [spork.pds :as pds]))

(def ^(pds.Set str) tags #{"stable" "typed"})
```

| Type | Description |
| --- | --- |
| `Vector[T]` | Persistent vector |
| `Map[K, V]` | Persistent hash map |
| `pds.Set[T]` | Persistent hash set with an explicit module alias |
| `SortedVector[T]` | Persistent ordered collection |
| `Cons[T]` | Linked-list cell |
| `DoubleVector` | Specialized vector of `float64` values |
| `IntVector` | Specialized vector of signed `int64` values |

### Specialized vector definitions

Two exact definition forms combine an annotation with compiler-selected storage:

```spork
(def ^(Vector float) floats [1.0 2.0 3.0])
(def ^(Vector int) ints [1 2 3])

(isinstance floats DoubleVector) ; => true
(isinstance ints IntVector)      ; => true
```

This selection occurs only when all three conditions hold:

1. the form is `def` with a simple symbol binding;
2. the annotation is exactly `(Vector float)` or `(Vector int)`; and
3. the initializer is a vector literal.

The annotation does not specialize a function return, parameter, `let` binding, or non-literal initializer. Use `vec-f64` or `vec-i64` explicitly when construction occurs in those positions. Specialized vectors enforce their native element representation during construction and updates.

## Runtime Introspection

Compiled modules use postponed annotation evaluation, so raw `__annotations__` entries may be strings and forward references remain safe on every supported Python version. Use `typing.get_type_hints` when resolved runtime objects are needed:

```spork
(ns annotation-example
  (:import [typing :refer [get_type_hints]]))

(defn ^int add [^int x ^int y] (+ x y))
(def hints (get_type_hints add))

(= (get hints "x") int)      ; => true
(= (get hints "y") int)      ; => true
(= (get hints "return") int) ; => true
```

`get_type_hints` resolves names in the compiled function's module namespace and can raise the same errors as Python when an annotation name is unavailable. Runtime consumers should prefer it over assuming a particular raw annotation representation.

## Build output

A project API configured with `:typed true` carries these annotations into generated `.pyi` files and adds `py.typed` to the package. Normalized Python names and declared generic signatures are therefore visible to Python type checkers without executing Spork source. See [generated public APIs](/docs/reference/tooling/builds-and-distributions/#generated-public-apis-and-typing) for manifest configuration and artifact ownership.
