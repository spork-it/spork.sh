---
title: Reader macros
description: Quote forms, decorate declarations, create anonymous functions and slices, discard forms, use tagged literals, and evaluate trusted compile-time values.
section: reference
group: language
project: spork-lang
order: 105
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Reader macros are fixed prefix syntax recognized while Spork source is read into forms. They run before ordinary compilation and are distinct from user-defined macros created with `defmacro`. This page defines every reader-macro prefix in Spork 0.6.3.

Comments, scalar tokens, and delimiters are covered by [lexical syntax](/docs/reference/language/lexical-syntax/). Although it also begins with `#`, `#{...}` is a persistent set literal rather than a reader-macro transformation.

## Form summary

| Syntax | Reader behavior |
| --- | --- |
| `'form` | Quote `form` without evaluating it |
| `` `form `` | Build a quasiquoted form template |
| `~form` | Evaluate and insert one value inside quasiquote |
| `~@form` | Evaluate and splice values inside a quasiquoted sequence |
| `^decoration` | Decorate or annotate the form that follows |
| `#(...)` | Create an anonymous function with `%` placeholders |
| `#[start stop step]` | Create a Python `slice`; `_` omits a bound |
| `#_form` | Read and discard the next form |
| `#f"..."` | Build a string with embedded Spork expressions |
| `#p"..."` | Create a `pathlib.Path` |
| `#r"..."` | Compile a regular expression |
| `#uuid"..."` | Create a validated `uuid.UUID` |
| `#inst"..."` | Create a validated `datetime.datetime` |
| `#=form` | Evaluate trusted code during compilation and embed its result |

Adjacency matters for `^` and `~`. They are reader prefixes when attached directly to the expression they introduce, as in `^int` or `~value`. With separating whitespace, they remain ordinary operator symbols: `(^ a b)` is bitwise XOR and `(~ value)` is bitwise NOT.

## Quote

A leading apostrophe expands to `(quote form)`. Quote prevents name lookup and call evaluation, turning source into runtime data instead. Symbols become `Symbol` values, parenthesized forms become persistent `Cons` lists, and vector, map, and set forms become their persistent collection values.

```spork
(def quoted-symbol 'total)
(str quoted-symbol)                   ; => "total"

(def quoted-call '(+ 1 2))
(list? quoted-call)                   ; => true
(str (first quoted-call))             ; => "+"

(def quoted-vector '[alpha beta])
(vector? quoted-vector)               ; => true
(str (first quoted-vector))           ; => "alpha"
```

Numbers, strings, booleans, `nil`, and keywords are already self-evaluating, so quoting them does not trigger lookup or a call.

## Quasiquote and unquote

A backtick starts a quasiquoted template. Most nested forms remain data, while `~` evaluates one expression and inserts its result. `~@` evaluates an iterable and splices each value into the surrounding sequential template. Unquote forms are meaningful only inside quasiquote.

```spork
(def value 10)
(def tail '(20 30))
(def form `(+ ~value ~@tail))

(count form)                          ; => 4
(str (nth form 0))                    ; => "+"
(nth form 1)                          ; => 10
(nth form 2)                          ; => 20
(nth form 3)                          ; => 30
```

The long spellings are `(quasiquote form)`, `(unquote form)`, and `(unquote-splicing form)`. Quasiquote is primarily used to construct forms returned by user-defined macros:

```spork
(defmacro unless [test & body]
  `(if ~test nil (do ~@body)))
```

Symbols ending in `#` inside a quasiquoted template are auto-gensyms. Their hygiene and reuse rules are defined under [macros](/docs/reference/language/macros/#auto-gensym).

## Decoration

`^decoration` reads a decoration expression for the immediately following declaration, name, parameter, or field. The enclosing compiler form decides what that decoration means.

| Example | Context |
| --- | --- |
| `(def ^int count 0)` | Variable type annotation |
| `(defn ^str name [^int id] ...)` | Return and parameter annotations |
| `^(List int)` | Composite `typing` annotation |
| `(defn ^async load [] ...)` | Async compiler flag |
| `(defn ^generator values [] ...)` | Generator compiler flag |
| `(defclass ^dataclass User [] ...)` | Python decorator |
| `(defprotocol ^structural Closeable ...)` | Structural protocol flag |

```spork
(def ^int retries 3)
retries                               ; => 3

(defn ^int square [^int value]
  (* value value))

(square 4)                            ; => 16
```

Annotations are documented under [type annotations](/docs/reference/language/types/); function and class decorators are documented under [classes and protocols](/docs/reference/language/classes-and-protocols/#decorators); async and generator flags are documented under [async and generators](/docs/reference/language/async-and-generators/).

## Hash-prefixed transforms

### Anonymous functions

`#(...)` creates an anonymous Python-callable function and infers its parameters from placeholders in its one expression body. Placeholders are special only inside that reader form, and a nested `#(...)` has its own placeholder scope.

| Placeholder | Meaning |
| --- | --- |
| `%` or `%1` | First positional argument |
| `%2`, `%3`, ... | Second, third, and subsequent positional arguments |
| `%&` | All remaining positional arguments |

`#(+ % 1)` is shorthand for `(fn [value] (+ value 1))`:

```spork
(def increment #(+ % 1))
(increment 2)                         ; => 3

(def add #(+ %1 %2))
(add 3 4)                             ; => 7

(def sum-all #(apply + %&))
(sum-all 1 2 3 4 5)                   ; => 15

; Use `do` when the body needs several effects or expressions
(def announce #(do (print %) (str %)))
(announce "ready")                    ; => "ready"
```

Use ordinary `(fn [parameters] body...)` when parameter names, destructuring, annotations, keyword-only parameters, or several body forms should be explicit. See [functions](/docs/reference/language/functions/).

### Slice literal

`#[...]` creates a Python `slice` using one to three space-delimited bounds. `_` omits a bound.

| Spork | Python equivalent | Meaning |
| --- | --- | --- |
| `#[5]` | `[:5]` | Start through index 5, exclusive |
| `#[2 5]` | `[2:5]` | Index 2 through index 5, exclusive |
| `#[_ 5]` | `[:5]` | Omitted start |
| `#[5 _]` | `[5:]` | Omitted stop |
| `#[0 8 2]` | `[0:8:2]` | Every second item in the range |
| `#[_ _ -1]` | `[::-1]` | Reverse |

```spork
(def values [0 1 2 3 4 5 6 7 8 9])

(get values #[5])          ; => [0 1 2 3 4]
(get values #[2 5])        ; => [2 3 4]
(get values #[_ _ -1])     ; => [9 8 7 6 5 4 3 2 1 0]
(get values #[0 8 2])      ; => [0 2 4 6]
(get values #[5 _])        ; => [5 6 7 8 9]

; Slicing a Python list returns another Python list
(def py-slice (get (list [1 2 3 4 5]) #[1 4]))
(isinstance py-slice list) ; => true
(vec py-slice)             ; => [2 3 4]

(get "hello world" #[0 5]) ; => "hello"
```

The bounds may be expressions evaluated when the slice is created. Zero bounds or more than three bounds are syntax errors. See [Python slice interoperability](/docs/reference/language/python-interop/#slice-syntax) for the equivalent general dot form.

### Discard

`#_` reads and discards exactly one following form. The discarded form must still be syntactically valid, but it is not compiled or executed. This makes `#_` useful for temporarily removing a structurally complete form.

```spork
; The discarded call is never compiled or executed
(+ 1 2 #_(print "debug") 3)          ; => 6

; Remove vector elements
[1 #_2 3 #_4 5]                      ; => [1 3 5]

; Remove a complete nested form
(def x #_(some-expensive-call) 42)
x                                      ; => 42

; A map key and value are separate forms, so discard both
{:name "Alice"
 #_:debug #_true
 :age 30}                            ; => {:name "Alice" :age 30}

; Each nested marker consumes one following form
(+ 1 #_#_2 3 4)                      ; => 8
```

## Tagged string and data literals

### F-string literal

`#f"..."` compiles a string template as a Python f-string. Balanced Spork forms inside `{...}` are evaluated at runtime and formatted using Python f-string conversion.

```spork
(def name "World")
#f"Hello, {name}!"                    ; => "Hello, World!"

#f"1 + 1 = {(+ 1 1)}"                ; => "1 + 1 = 2"

(def a 10)
(def b 20)
#f"{a} + {b} = {(+ a b)}"            ; => "10 + 20 = 30"

(def word "hello")
#f"Upper: {(word.upper)}"             ; => "Upper: HELLO"

(def items [1 2 3])
#f"Count: {(count items)}"            ; => "Count: 3"
```

Embedded forms must be balanced. Literal-brace escaping is not part of the documented syntax.

### Path literal

`#p"..."` creates a `pathlib.Path`. The result supports ordinary Python `Path` attributes and methods.

```spork
(def src-path #p"src/main.spork")
(isinstance src-path (type #p"."))    ; => true

(def base-path #p"base")
(str (base-path.joinpath "subdir" "file.txt"))
; => "base/subdir/file.txt"

(def nested-path #p"a/b/c")
(str nested-path.parent)              ; => "a/b"
src-path.suffix                       ; => ".spork"
src-path.stem                         ; => "main"

; Predicates depend on the current filesystem
(def project-root #p".")
(project-root.exists)
(project-root.is-dir)
(src-path.is-file)

(def out-path #p"out.txt")
(out-path.write-text "content")       ; => 7
(out-path.read-text)                  ; => "content"
```

### Regex literal

`#r"..."` preserves regex backslashes, validates the pattern during compilation, and creates a compiled `re.Pattern`.

```spork
(def pattern #r"\d{3}-\d{4}")
(def phone-match (pattern.search "Call 555-1234"))
(phone-match.group 0)                 ; => "555-1234"

; Python regex methods return Python lists; convert when a vector is wanted
(def digits #r"\d+")
(vec (digits.findall "a1b22c333"))    ; => ["1" "22" "333"]

(def email-pattern #r"(\w+)@(\w+)")
(def match-value (email-pattern.search "user@domain"))
(match-value.group 1)                 ; => "user"
(match-value.group 2)                 ; => "domain"

(def whitespace #r"\s+")
(whitespace.sub " " "too   many   spaces") ; => "too many spaces"

(def separators #r"[,;]")
(vec (separators.split "a,b;c,d"))    ; => ["a" "b" "c" "d"]
```

Invalid regex syntax fails during compilation:

<!-- verify-docs: expect-error=SyntaxError -->
```spork
#r"[invalid"
```

### UUID literal

`#uuid"..."` validates its text during compilation and creates a `uuid.UUID`. Hyphenated, unhyphenated, and brace-wrapped UUID spellings accepted by Python normalize to the same value.

```spork
(def id #uuid"550e8400-e29b-41d4-a716-446655440000")
(= (type id) (type #uuid"00000000-0000-0000-0000-000000000000")) ; => true
id.version                            ; => 4
id.hex                                ; => "550e8400e29b41d4a716446655440000"

(= id #uuid"550e8400e29b41d4a716446655440000")       ; => true
(= id #uuid"{550e8400-e29b-41d4-a716-446655440000}") ; => true
```

<!-- verify-docs: expect-error=SyntaxError -->
```spork
#uuid"not-a-uuid"
```

### Instant literal

`#inst"..."` validates ISO-8601 text during compilation and creates a `datetime.datetime`. `Z` and explicit offsets produce aware values; a date or date-time without an offset produces a naive value. A date-only literal represents midnight.

```spork
(def created #inst"2025-12-10T00:00:00Z")
(= (type created) (type #inst"2000-01-01")) ; => true
created.year                          ; => 2025
created.month                         ; => 12
created.day                           ; => 10
(str created.tzinfo)                  ; => "UTC"

(def event #inst"2024-06-15T14:30:45Z")
event.hour                            ; => 14
event.minute                          ; => 30
event.second                          ; => 45

(def east #inst"2024-01-01T12:00:00+05:30")
(def west #inst"2024-01-01T12:00:00-08:00")
(def east-offset (east.utcoffset))
(def west-offset (west.utcoffset))
(east-offset.total-seconds)           ; => 19800.0
(west-offset.total-seconds)           ; => -28800.0

(str #inst"2024-01-01")               ; => "2024-01-01 00:00:00"
```

<!-- verify-docs: expect-error=SyntaxError -->
```spork
#inst"not-a-date"
```

## Read-time evaluation

`#=form` evaluates `form` during compilation and embeds the result in generated code. The expression runs in the compiler's macro execution environment, which includes selected Python builtins, persistent collection constructors, and Spork core sequence and arithmetic helpers.

```spork
(def computed #=(+ 100 200))
computed                              ; => 300

(def upper #=(.upper "hello"))
upper                                 ; => "HELLO"

(def tau #=(* 2 3.14159265359))
tau                                   ; => 6.28318530718
```

Ordinary runtime definitions and modules imported by the surrounding `ns` form are not automatically available. The result must be representable in generated Python code.

`#=` executes trusted code while compiling. Avoid side effects, filesystem or network reads, wall-clock values, and other environment-dependent results when reproducible builds matter.
