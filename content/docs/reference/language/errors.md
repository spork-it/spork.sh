---
title: Errors and source mapping
description: Understand source-mapped runtime, type, assertion, and syntax errors.
section: reference
group: language
project: spork-lang
order: 230
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Spork provides **source-mapped error reporting**. When runtime errors occur, tracebacks point to the original `.spork` source files with accurate line numbers and code context—not the generated Python code.

## Traceback Example

Given this Spork code:

<!-- verify-docs: expect-error=ZeroDivisionError -->
```spork
;; example.spork
(defn divide [a b]
  (/ a b))

(defn nested-call [x]
  (let [y (divide x 0)]
    (+ y 10)))

(defn deep-stack []
  (nested-call 42))

(deep-stack)
```

Running it produces a traceback whose source-mapped portion is:

```text
Error: division by zero
Traceback (most recent call last):
  File "example.spork", line 12, in <module>
    (deep-stack)
    ~~~~~^~~~~~~
  File "example.spork", line 10, in deep_stack
    (nested-call 42))
    ^^^^^^^^^^^^^^^^
  File "example.spork", line 6, in nested_call
    (let [y (divide x 0)]
            ^^^^^^^^^^^^
  File "example.spork", line 3, in divide
    (/ a b))
    ^^^^^^^
ZeroDivisionError: division by zero
```

## Error Types

Spork surfaces Python's standard exception types with Spork source locations:

| Error Type | Example Cause |
|------------|---------------|
| `ZeroDivisionError` | `(/ x 0)` |
| `TypeError` | `(+ 1 "string")` — type mismatch in operations |
| `NameError` | Using an undefined variable like `undefined-var` |
| `AttributeError` | `(. nil some-method)` — attribute access on nil |
| `IndexError` | `(nth [1 2] 10)` — index out of bounds |
| `AssertionError` | `(assert false "message")` |
| `SyntaxError` | Missing closing parenthesis, unterminated string |
| `KeyError` | A Python mapping operation that requires a missing key |

## Undefined Variable Errors

<!-- verify-docs: expect-error=NameError -->
```spork
(defn calculate [x]
  (+ x undefined-var))

(calculate 10)
```

Relevant traceback excerpt:

```text
Error: name 'undefined_var' is not defined
  File "example.spork", line 2, in calculate
    (+ x undefined-var))
         ~~~~~~~~~^~~~
NameError: name 'undefined_var' is not defined
```

Note that the error message shows the normalized Python name (`undefined_var`) but the source location points to the original Spork code.

## Type Errors

<!-- verify-docs: expect-error=TypeError -->
```spork
(defn add-numbers [a b]
  (+ a b))

(add-numbers 10 "oops")
```

Relevant traceback excerpt:

```text
Error: unsupported operand type(s) for +: 'int' and 'str'
  File "example.spork", line 2, in add_numbers
    (+ a b))
    ^^^^^^^
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

## Assertion Errors

<!-- verify-docs: expect-error=AssertionError -->
```spork
(defn validate-positive [n]
  (assert (> n 0) "Expected positive number")
  n)

(validate-positive -5)
```

Relevant traceback excerpt:

```text
Error: Expected positive number
  File "example.spork", line 2, in validate_positive
    (assert (> n 0) "Expected positive number")
AssertionError: Expected positive number
```

## Syntax Errors

Syntax errors are caught at compile time and include location information:

<!-- verify-docs: expect-error=SyntaxError -->
```spork
(defn broken [x]
  (let [y 10]
    (+ x y)
; Missing closing parens
```

Relevant error:

```text
SyntaxError: unterminated list at line 2, expected )
```

## How Source Mapping Works

Spork compiles to Python AST with source location information preserved:

1. The Spork reader tracks line and column numbers for every form
2. The compiler attaches these locations to generated AST nodes via `lineno` and `col_offset`
3. The compiled code object references the original `.spork` filename
4. Python's traceback mechanism uses this information to display the original source

This means you can debug Spork code naturally using standard Python tools (debuggers, profilers, exception handlers) without needing to understand the generated Python.
