---
title: Reductions and transformations
description: Reduce collections, inspect intermediate values, group, sort, split, and transform.
section: reference
group: standard-library
project: spork-lang
order: 440
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Reduction and transformation functions consume sequences to produce scalar values or eager persistent collections. Functions documented as eager fully consume their input before returning.

## Reduction functions

### `reduce`
Reduces a collection using a function. Without an explicit initial value, the first element becomes the accumulator. For an empty collection with no initial value, `reduce` calls the reducing function with zero arguments.
```spork
; Sum
(reduce + [1 2 3 4])             ; => 10
(reduce + 0 [1 2 3 4])           ; => 10
(reduce + 100 [1 2 3 4])         ; => 110

; Product (`*` is call syntax, so wrap it when passing it as a value)
(reduce #(* %1 %2) [1 2 3 4])    ; => 24

; Build string
(reduce + ["a" "b" "c"])         ; => "abc"

; Custom accumulator
(reduce (fn [acc x] (conj acc (* x 2)))
        []
        [1 2 3])                 ; => [2 4 6]

; Find max
(reduce max [3 1 4 1 5 9])       ; => 9

; The zero-argument identity of `+` is used for an empty collection
(reduce + [])                     ; => 0
```

### `reductions`
Returns a lazy sequence of intermediate accumulator values. An explicit initial value appears first; an empty collection without one produces an empty sequence.
```spork
(reductions + [1 2 3 4])         ; => (1 3 6 10)
(reductions + 0 [1 2 3 4])       ; => (0 1 3 6 10)
(reductions #(* %1 %2) [1 2 3 4]) ; => (1 2 6 24)
(reductions conj [] [1 2 3])     ; => ([] [1] [1 2] [1 2 3])
```

## Collection transformations

### `zipmap`
Creates a map from parallel key and value sequences, stopping when either input is exhausted.
```spork
(zipmap [:a :b :c] [1 2 3])      ; => {:a 1 :b 2 :c 3}
(zipmap [1 2 3] [:a :b :c])      ; => {1 :a 2 :b 3 :c}
(zipmap [:a :b] [1 2 3])         ; => {:a 1 :b 2}

; Create lookup from list
(zipmap (range) ["a" "b" "c"])   ; => {0 "a" 1 "b" 2 "c"}
```

### `group-by`
Groups elements by each hashable result of `f`, returning vectors in encounter order.
```spork
(group-by even? [1 2 3 4 5 6])
; => {false [1 3 5] true [2 4 6]}

(group-by count ["a" "bb" "ccc" "dd" "e"])
; => {1 ["a" "e"] 2 ["bb" "dd"] 3 ["ccc"]}

(group-by :type [{:type :a :v 1} {:type :b :v 2} {:type :a :v 3}])
; => {:a [{:type :a :v 1} {:type :a :v 3}] :b [{:type :b :v 2}]}

(group-by first ["apple" "ant" "banana" "bear"])
; => {"a" ["apple" "ant"] "b" ["banana" "bear"]}
```

### `frequencies`
Returns a map from each hashable input value to its count.
```spork
(frequencies [1 1 2 3 2 1])      ; => {1 3 2 2 3 1}
(frequencies "abracadabra")      ; => {"a" 5 "b" 2 "r" 2 "c" 1 "d" 1}
(frequencies [:a :b :a :c :a :b]); => {:a 3 :b 2 :c 1}
```

### `reverse`
Returns reversed sequence.
```spork
(reverse [1 2 3 4])              ; => (4 3 2 1)
(reverse "hello")                ; => ("o" "l" "l" "e" "h")
(reverse '(a b c))               ; => (c b a)
(apply + (reverse "hello"))      ; => "olleh"
```

### `sort`
Realizes its input and returns a stably sorted `Vector`. Optional Python-style `:key` and `:reverse-order` keyword arguments control ordering.
```spork
(sort [3 1 4 1 5 9 2 6])                    ; => [1 1 2 3 4 5 6 9]
(sort ["c" "a" "b"])                        ; => ["a" "b" "c"]
(sort [3 1 4 1 5] * :reverse-order true)     ; => [5 4 3 1 1]
(sort ["aaa" "b" "cc"] * :key len)           ; => ["b" "cc" "aaa"]
```

### `sort-by`
Realizes its input and returns a `Vector` ordered by a key function.
```spork
(sort-by count ["aaa" "b" "cc"]) ; => ["b" "cc" "aaa"]
(sort-by :age [{:age 30} {:age 20} {:age 25}])
; => [{:age 20} {:age 25} {:age 30}]

(sort-by :name [{:name "Charlie"} {:name "Alice"} {:name "Bob"}])
; => [{:name "Alice"} {:name "Bob"} {:name "Charlie"}]
```

Use `sort` with `:reverse-order true` when descending order is required.

### `split-at`
Realizes the input and returns a Python tuple containing two vectors. Negative `n` values use Python slicing semantics.
```spork
(split-at 2 [1 2 3 4 5])         ; => ([1 2], [3 4 5])
(split-at 0 [1 2 3])             ; => ([], [1 2 3])
(split-at 10 [1 2 3])            ; => ([1 2 3], [])
```

### `split-with`
Realizes the input and returns a Python tuple of two vectors, split at the first falsy predicate result.
```spork
(split-with #(< % 3) [1 2 3 4 1 2]) ; => ([1 2], [3 4 1 2])
(split-with pos? [1 2 0 3 4])        ; => ([1 2], [0 3 4])
(split-with even? [2 4 6 7 8])       ; => ([2 4 6], [7 8])
```
