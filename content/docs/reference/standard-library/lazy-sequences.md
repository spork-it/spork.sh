---
title: Lazy sequences and realization
description: Generator-backed transformations, finite realization, and effect-only consumption.
section: reference
group: standard-library
project: spork-lang
order: 430
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Lazy sequence functions defer work by returning Python generators. This page distinguishes lazy transformations from realization helpers and eager persistent results.

## Lazy sequence functions

These functions return Python generators unless a section states otherwise. Calling a generator function does not realize its result; use `vec`, `doall`, iteration, or a reducer to consume it. `cycle`, `partition`, `partition-all`, and `reverse` materialize their input when first consumed and therefore are not suitable for infinite inputs. `sort` and related helpers also realize their inputs but return concrete values.

### `map`
Applies a function to each element of one or more collections.
```spork
; Single collection
(map inc [1 2 3])              ; => (2 3 4)
(map str [1 2 3])              ; => ("1" "2" "3")

; Multiple collections (stops at shortest)
(map + [1 2 3] [10 20 30])     ; => (11 22 33)
(map + [1 2] [10 20 30])       ; => (11 22)
(map (fn [a b] [a b]) [1 2 3] [:a :b :c])
; => ([1 :a] [2 :b] [3 :c])

; With anonymous function
(map (fn [x] (* x x)) [1 2 3 4])  ; => (1 4 9 16)

; With keyword (extracts from maps)
(map :name [{:name "Alice"} {:name "Bob"}])  ; => ("Alice" "Bob")
```

### `filter`
Returns elements for which predicate returns true.
```spork
(filter even? [1 2 3 4 5 6])      ; => (2 4 6)
(filter odd? [1 2 3 4 5 6])       ; => (1 3 5)
(filter pos? [-2 -1 0 1 2])       ; => (1 2)
(filter #(isinstance % str) [1 "a" 2 "b"]) ; => ("a" "b")

; Filter with keyword (truthy values)
(filter :active [{:active true :name "A"}
                 {:active false :name "B"}
                 {:active true :name "C"}])
; => ({:active true :name "A"} {:active true :name "C"})

; Filter with set membership
(filter #(contains? #{2 4 6} %) [1 2 3 4 5 6]) ; => (2 4 6)
```

### `take`
Returns first n elements.
```spork
(take 3 [1 2 3 4 5])       ; => (1 2 3)
(take 10 [1 2 3])          ; => (1 2 3)
(take 0 [1 2 3])           ; => ()
(take 5 (range))           ; => (0 1 2 3 4)
```

### `take-while`
Returns elements while predicate is true, stops at first false.
```spork
(take-while pos? [1 2 3 0 -1 5])     ; => (1 2 3)
(take-while even? [2 4 6 7 8 10])    ; => (2 4 6)
(take-while #(< % 5) [1 2 3 4 5 6])  ; => (1 2 3 4)
```

### `drop`
Drops first n elements, returns rest.
```spork
(drop 2 [1 2 3 4 5])       ; => (3 4 5)
(drop 10 [1 2 3])          ; => ()
(drop 0 [1 2 3])           ; => (1 2 3)
```

### `drop-while`
Drops elements while predicate is true, returns rest.
```spork
(drop-while pos? [1 2 3 0 -1 5])     ; => (0 -1 5)
(drop-while even? [2 4 6 7 8 10])    ; => (7 8 10)
(drop-while #(< % 5) [1 2 3 4 5 6])  ; => (5 6)
```

### `concat`
Concatenates sequences together.
```spork
(concat [1 2] [3 4])           ; => (1 2 3 4)
(concat [1 2] [3 4] [5 6])     ; => (1 2 3 4 5 6)
(concat [1 2] nil [3 4])       ; => (1 2 3 4)
(concat "ab" "cd")             ; => ("a" "b" "c" "d")
```

### `repeat`
Returns a sequence of `x` repeated `n` times, using `(repeat x n)`. Without `n`, the result is infinite.
```spork
(repeat "x" 3)              ; => ("x" "x" "x")
(repeat 0 5)                ; => (0 0 0 0 0)
(take 4 (repeat :a))        ; => (:a :a :a :a)
(vec (repeat [1 2] 3))      ; => [[1 2] [1 2] [1 2]]
```

### `cycle`
Returns an infinite cycle of collection elements.
```spork
(take 7 (cycle [1 2 3]))    ; => (1 2 3 1 2 3 1)
(take 5 (cycle [:a :b]))    ; => (:a :b :a :b :a)
(take 6 (cycle "ab"))       ; => ("a" "b" "a" "b" "a" "b")
```

### `iterate`
Returns infinite sequence: x, (f x), (f (f x)), ...
```spork
(take 5 (iterate inc 0))        ; => (0 1 2 3 4)
(take 5 (iterate #(* 2 %) 1))   ; => (1 2 4 8 16)
(take 4 (iterate rest [1 2 3])) ; => ([1 2 3] (2 3) (3) nil)
```

### `range`
Returns an integer range with Python's `range` semantics. With no arguments it is an infinite generator starting at zero.
```spork
(range 5)            ; => (0 1 2 3 4)
(range 1 5)          ; => (1 2 3 4)
(range 0 10 2)       ; => (0 2 4 6 8)
(range 10 0 -1)      ; => (10 9 8 7 6 5 4 3 2 1)
(take 5 (range))     ; => (0 1 2 3 4)
```

### `interleave`
Interleaves elements from multiple sequences. Stops at shortest.
```spork
(interleave [1 2 3] [:a :b :c])        ; => (1 :a 2 :b 3 :c)
(interleave [1 2] [:a :b :c])          ; => (1 :a 2 :b)
(interleave [1 2 3] [:a :b :c] ["x" "y" "z"])
; => (1 :a "x" 2 :b "y" 3 :c "z")
```

### `interpose`
Interposes separator between elements.
```spork
(interpose :sep [1 2 3])          ; => (1 :sep 2 :sep 3)
(interpose ", " ["a" "b" "c"])    ; => ("a" ", " "b" ", " "c")
(apply + (map str (interpose "-" [1 2 3]))) ; => "1-2-3"
```

### `partition`
Returns groups of `n` elements. The default step is `n`, and an incomplete final group is dropped. Optional `step` and `pad` arguments follow the collection; padding is emitted only if `pad` supplies enough values to complete the group.
```spork
(partition 2 [1 2 3 4 5 6])       ; => ([1 2] [3 4] [5 6])
(partition 2 [1 2 3 4 5])         ; => ([1 2] [3 4])
(partition 3 [1 2 3 4 5 6 7 8 9]) ; => ([1 2 3] [4 5 6] [7 8 9])

; A smaller step creates sliding windows
(partition 2 [1 2 3 4] 1)         ; => ([1 2] [2 3] [3 4])
(partition 3 [1 2 3 4 5] 1)       ; => ([1 2 3] [2 3 4] [3 4 5])

; A fourth argument supplies padding for the final group
(partition 3 [1 2 3 4] 3 [0 0])   ; => ([1 2 3] [4 0 0])
```

### `partition-all`
Like `partition`, but includes every incomplete group and does not take a padding argument.
```spork
(partition-all 2 [1 2 3 4 5])     ; => ([1 2] [3 4] [5])
(partition-all 3 [1 2 3 4 5])     ; => ([1 2 3] [4 5])
(partition-all 3 [1 2])           ; => ([1 2])

; Optional step follows the collection
(partition-all 3 [1 2 3 4] 1)     ; => ([1 2 3] [2 3 4] [3 4] [4])
```

### `keep`
Returns non-nil results of (f item).
```spork
(keep #(if (even? %) %) [1 2 3 4 5 6])  ; => (2 4 6)
(keep (fn [x] x) [1 nil 2 nil 3])      ; => (1 2 3)
(keep :name [{:name "A"} {} {:name "B"}])  ; => ("A" "B")

; Difference from filter: keep uses the RESULT of f
(keep #(if (pos? %) (* % 10)) [-1 0 1 2])  ; => (10 20)
```

### `keep-indexed`
Like keep but f receives index and item.
```spork
(keep-indexed #(if (even? %1) %2) [:a :b :c :d :e])
; => (:a :c :e)

(keep-indexed #(if (> %1 1) %2) [:a :b :c :d])
; => (:c :d)
```

### `map-indexed`
Like map but f receives index and item.
```spork
(map-indexed (fn [i x] [i x]) [:a :b :c])
; => ([0 :a] [1 :b] [2 :c])
(map-indexed #(.format "{}: {}" %1 %2) ["a" "b" "c"])
; => ("0: a" "1: b" "2: c")

(map-indexed (fn [i x] {:index i :value x}) [10 20 30])
; => ({:index 0 :value 10} {:index 1 :value 20} {:index 2 :value 30})
```

### `dedupe`
Removes consecutive duplicates.
```spork
(dedupe [1 1 2 2 3 1 1])     ; => (1 2 3 1)
(dedupe [1 2 3 4])           ; => (1 2 3 4)
(dedupe [:a :a :a :b :b :a]) ; => (:a :b :a)
```

### `distinct`
Removes duplicate hashable values, preserving their first occurrence. Unhashable Python objects are compared by identity rather than equality.
```spork
(distinct [1 2 1 3 2 4 3])   ; => (1 2 3 4)
(distinct [:a :b :a :c :b])  ; => (:a :b :c)
(distinct "abracadabra")     ; => ("a" "b" "r" "c" "d")
```

### `flatten`
Recursively flattens any nested iterable except strings and bytes. Maps therefore contribute keys through their normal iteration protocol.
```spork
(flatten [[1 2] [3 4]])              ; => (1 2 3 4)
(flatten [[1 [2 3]] [[4] 5]])        ; => (1 2 3 4 5)
(flatten [1 [2 [3 [4 [5]]]]])        ; => (1 2 3 4 5)
(flatten [1 2 3])                    ; => (1 2 3)
```

### `mapcat`
Maps over one or more collections and concatenates each non-`nil` result. It is equivalent to applying `concat` to the results of `map`.
```spork
(mapcat #(repeat % 2) [1 2 3])       ; => (1 1 2 2 3 3)
(mapcat reverse [[1 2] [3 4]])       ; => (2 1 4 3)
(mapcat #(range %) [1 2 3])          ; => (0 0 1 0 1 2)

; Useful for "expanding" each element
(mapcat (fn [x] [x (* x 10)]) [1 2 3])  ; => (1 10 2 20 3 30)
```

## Sequence realization

### `doall`
Consumes an iterable and returns its results as a persistent `Vector`.
```spork
(doall (map print [1 2 3]))      ; => [nil nil nil]
; also prints each value on its own line
(def realized (doall (map inc (range 5))))
realized                          ; => [1 2 3 4 5]
```

### `dorun`
Consumes an iterable and returns `nil`. Unlike `doall`, it does not retain the yielded values.
```spork
(dorun (map print [1 2 3]))      ; => nil
; also prints each value on its own line
```

### `realized?`
Distinguishes raw Python generator objects from concrete or sequence values. It returns false for a generator even after that generator has been partly or fully consumed; it does not track realization progress.
```spork
(def lazy-nums (map inc [1 2 3]))
(realized? lazy-nums)            ; => false
(first lazy-nums)                ; => 2
(realized? lazy-nums)            ; => false
(realized? (doall lazy-nums))    ; => true
```
