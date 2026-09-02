---
title: Numeric and bitwise operations
description: Arithmetic helpers, comparisons, shifts, bit operations, and collection aliases.
section: reference
group: standard-library
project: spork-lang
order: 450
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

These automatically available functions cover arithmetic, comparison, integer bit operations, and related predicates. Python numeric coercion and exception behavior apply unless a function states a narrower contract.

## Numeric functions

### `inc` / `dec`
Increment/decrement by 1.
```spork
(inc 5)         ; => 6
(inc -1)        ; => 0
(inc 0.5)       ; => 1.5

(dec 5)         ; => 4
(dec 0)         ; => -1
(dec 1.5)       ; => 0.5
```

### `+` / `-` / `*` / `/`
Direct arithmetic operator forms accept one or more operands. With one operand, each direct form returns it unchanged; with several, evaluation proceeds from left to right. When `-` or `/` is passed as a first-class runtime callable, its one-argument behavior is unary negation or reciprocal instead.
```spork
; Addition
(+ 5)           ; => 5
(+ 1 2)         ; => 3
(+ 1 2 3 4 5)   ; => 15

; Subtraction
(- 5)           ; => 5
(- 0 5)         ; => -5
(- 10 3)        ; => 7
(- 10 3 2 1)    ; => 4

; Multiplication
(* 5)           ; => 5
(* 2 3)         ; => 6
(* 2 3 4)       ; => 24

; Division
(/ 5)           ; => 5
(/ 10 2)        ; => 5.0
(/ 20 2 2)      ; => 5.0
(/ 7 2)         ; => 3.5

; First-class runtime callables retain conventional unary behavior
(apply - [5])   ; => -5
(apply / [5])   ; => 0.2
```

### `mod`
Modulus (remainder), also spelled `%` in operator position. The result has the same sign as the divisor.
```spork
(mod 10 3)      ; => 1
(mod 11 3)      ; => 2
(mod -10 3)     ; => 2
(mod 10 -3)     ; => -2
```

### `quot`
Integer floor division, equivalent to the `//` operator and matching Python's negative-number semantics.
```spork
(quot 10 3)     ; => 3
(quot 11 3)     ; => 3
(quot -10 3)    ; => -4
(quot 10 -3)    ; => -4
```

### `max` / `min`
Return the maximum or minimum of arguments, or of one iterable argument.
```spork
(max 1 5 3)         ; => 5
(max -1 -5 -3)      ; => -1
(max [1 5 3])       ; => 5

(min 1 5 3)         ; => 1
(min -1 -5 -3)      ; => -5
(min [1 5 3])       ; => 1
```

### `abs`
Absolute value.
```spork
(abs 5)         ; => 5
(abs -5)        ; => 5
(abs 0)         ; => 0
(abs -3.14)     ; => 3.14
```

## Bitwise operations

Bitwise operations have verbose names and symbol aliases. The same functions also implement persistent set operations; `bit-or`/`|` additionally merge maps, with later values winning.

```spork
; Bitwise OR - bit-or or |
(bit-or 1 2)           ; => 3
(| 5 3)                ; => 7

; Bitwise AND - bit-and or &
(bit-and 7 3)          ; => 3
(& 5 3)                ; => 1

; Bitwise AND NOT (clear bits)
(difference 7 2)       ; => 5
(difference 15 3)      ; => 12

; Bitwise XOR - bit-xor or ^
(bit-xor 5 3)          ; => 6
(^ 7 7)                ; => 0

; Bitwise NOT (complement) - bit-not or ~
(bit-not 0)            ; => -1
(~ -1)                 ; => 0
(~ 5)                  ; => -6

; Left shift - bit-shift-left or <<
(bit-shift-left 1 4)   ; => 16
(<< 3 2)               ; => 12

; Right shift - bit-shift-right or >>
(bit-shift-right 16 2) ; => 4
(>> 15 2)              ; => 3
```

### Symbol Aliases Summary

| Verbose Name      | Symbol | Description              |
|-------------------|--------|--------------------------|
| `bit-or`          | `\|`   | Bitwise OR               |
| `bit-and`         | `&`    | Bitwise AND              |
| `bit-xor`         | `^`    | Bitwise XOR              |
| `bit-not`         | `~`    | Bitwise NOT (complement) |
| `bit-shift-left`  | `<<`   | Left shift               |
| `bit-shift-right` | `>>`   | Right shift              |

`union`, `intersection`, and `difference` are aliases for `bit-or`, `bit-and`, and numeric AND-NOT respectively. For sets, `difference` performs set difference. The symbol operators also work with sets and maps:

```spork
(def s1 #{1 2 3})
(def s2 #{2 3 4})

(| s1 s2)              ; => #{1 2 3 4}
(& s1 s2)              ; => #{2 3}
(^ s1 s2)              ; => #{1 4}

; Map union keeps the rightmost value for a duplicate key
(| {:a 1} {:a 2 :b 3}) ; => {:a 2 :b 3}
```
