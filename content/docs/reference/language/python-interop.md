---
title: Python interoperability reference
description: Call Python, access attributes, use operators, context managers, and slices.
section: reference
group: language
project: spork-lang
order: 220
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Spork calls Python objects directly and follows Python’s attribute, indexing, argument, iteration, and exception behavior. This page records the precise source forms used at that boundary.

## Calling Python with Keyword Arguments

The [keyword-argument call syntax](/docs/reference/language/functions/#keyword-arguments) also applies to Python callables. Inside a splat, Spork keyword keys become Python keyword names. Outside a splat, a keyword remains a Spork `Keyword` value.

```spork
; Keyword keys in a splat become Python string keys
(dict *{:name "Alice" :age 30})
; => {"name" "Alice" "age" 30}

; Python methods accept the same syntax
(def template "{name} is {age}")
(template.format *{:name "Bob" :age 25})
; => "Bob is 25"

; Multiple splats may follow the positional arguments
(dict *{:a 1} *{:b 2 :c 3})
; => {"a" 1 "b" 2 "c" 3}

; Without `*`, :name is a value and can be called as a map lookup
(:name {:name "Alice"})            ; => "Alice"
(dict * :name "Alice")             ; => {"name" "Alice"}
```

## Attribute and Method Access

Prefer dotted symbols when the receiver has a name:

```spork
obj.attr                    ; obj.attr
(obj.method arg1 arg2)      ; obj.method(arg1, arg2)
(set! obj.attr val)         ; obj.attr = val
```

A dotted symbol must begin with a symbol. The leading-dot form remains supported for compatibility and is useful when the receiver is a literal or computed expression:

```spork
(.upper "hello")                ; "hello".upper()
(.method (DocObject) arg1)      ; DocObject().method(arg1)
```

`call` is an explicit receiver-first equivalent. The general dot form accesses attributes and subscripts; because it produces an ordinary value, it can also be placed in call position:

```spork
(call obj method arg1)           ; obj.method(arg1)
(. obj attr)                     ; obj.attr
((. (DocObject) method) arg1)    ; DocObject().method(arg1)
(. coll 0)                       ; coll[0]
(. coll (+ index 1))             ; coll[index + 1]
(. coll (slice start stop))      ; coll[start:stop]
```

In the general dot form, a symbol after the object names an attribute; an integer or expression is a subscript. Use `get` for ordinary dynamic indexing. All method-call spellings remain supported, but documentation and new code should use `(obj.method args...)` whenever the receiver can begin a dotted symbol.

## Python Builtins

Common Python built-in functions are available:

```spork
(print "hello")
(len [1 2 3])                    ; => 3
(= (type 42) int)                ; => true
(isinstance 42 int)              ; => true
(str 42)                         ; => "42"
(int "42")                       ; => 42
(= (type (list [1 2 3])) list)  ; => true
(= (type (dict [["name" "Alice"]])) dict) ; => true
```

## Operators

Operators are written as the first item in a parenthesized call. Thus `(^ a b)` is bitwise XOR, `(~ x)` is bitwise NOT, and `(& a b)` is bitwise AND. These are distinct from prefix `^type` metadata, `~form` unquote syntax, and `& rest` in a parameter vector.

```spork
; Comparison (chainable)
(= a b c)             ; a == b == c
(!= a b)              ; a != b
(not= a b)            ; a != b (Lisp-style alias)
(< 1 5 10)            ; 1 < 5 < 10
(<= a b c)            ; a <= b <= c
(> a b)               ; a > b
(>= a b)              ; a >= b

; Logical
(and a b c)
(or a b c)
(not x)

; Bitwise (symbol and verbose forms)
(| a b)               ; bitwise or  (also: bit-or)
(& a b)               ; bitwise and (also: bit-and)
(^ a b)               ; bitwise xor (also: bit-xor)
(~ x)                 ; bitwise not (also: bit-not)
(<< x n)              ; left shift  (also: bit-shift-left)
(>> x n)              ; right shift (also: bit-shift-right)

; Membership
(in item coll)        ; item in coll
```

## Context Managers (with)

The binding vector normally contains alternating binding and context-manager expressions. It may contain several pairs, a destructuring pattern, or a context-manager call with no preceding binding.

```spork
; Basic with
(with [f (open "file.txt" "r")]
  (print (f.read)))

; Multiple bindings
(with [f1 (open "in.txt")
       f2 (open "out.txt" "w")]
  (f2.write (f1.read)))

; Without binding (for side effects)
(with [(some-context)]
  (do-work))

; Destructuring
(with [[reader writer] (create-pipe)]
  (process reader writer))
```

## Slice Syntax

The `#[start stop step]` reader macro creates a Python slice; `_` marks an omitted bound. Pass the resulting slice to `get` or use a `slice` expression in the general dot form:

```spork
(get coll #[2 8 2])
(. coll (slice 2 8 2))
```

See the [slice reader macro](/docs/reference/language/reader-macros/#slice-literal) for the complete bound rules and examples.
