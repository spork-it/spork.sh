---
title: Sequence operations
description: Core sequence access, persistent updates, conversion, and sequence predicates.
section: reference
group: standard-library
project: spork-lang
order: 410
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

Sequence operations provide one vocabulary across persistent Spork collections and supported Python values. Return types and behavior for empty or unsupported inputs are documented per operation.

## Core operations

### `first`
Returns the first element of a collection, or `nil` if empty. On a one-shot Python iterator, retrieving the first element consumes it.
```spork
(first [1 2 3])      ; => 1
(first '(a b c))     ; => a
(first "hello")      ; => "h"
(first [])           ; => nil
(first nil)          ; => nil

; The first map key is unspecified
(def first-key (first {:a 1 :b 2}))
(contains? {:a 1 :b 2} first-key) ; => true
```

### `rest`
Returns a sequence of all elements except the first. Returns `nil` when there is no remaining element.
```spork
(rest [1 2 3])    ; => (2 3)
(rest [1])        ; => nil
(rest [])         ; => nil
(rest nil)        ; => nil
(rest "hello")    ; => ("e" "l" "l" "o")
```

### `seq`
Eagerly converts an iterable to a `Cons` sequence, or returns `nil` for an empty input. Map entries become two-element vectors. Use the original lazy functions when eager conversion is not needed.
```spork
(seq [1 2 3])     ; => (1 2 3)
(seq [])          ; => nil
(seq nil)         ; => nil
(seq "hi")        ; => ("h" "i")
(seq {:a 1})      ; => ([:a 1])

; Common pattern for checking if collection has elements
(if (seq coll)
  (print "has elements")
  (print "empty"))
```

### `nth`
Returns the element at zero-based index `n`. An out-of-range access raises `IndexError` unless a default is provided. Use nonnegative indices for portable behavior; indexable collection types may additionally support Python-style negative indices.
```spork
(nth [1 2 3] 0)          ; => 1
(nth [1 2 3] 1)          ; => 2
(nth [1 2 3] 2)          ; => 3
(nth [1 2 3] 5 :default) ; => :default
(nth "hello" 1)          ; => "e"

; Works with any sequential collection
(nth '(a b c) 1)         ; => b
```

### `conj`
Adds one value and returns a new collection. The position depends on the type: the end for vectors, sorted position for sorted vectors, the front for `Cons` lists, set membership for sets, and key association for a map entry. On `nil`, it creates a one-element `Cons`. As a Python fallback, an append-capable input is copied into a new Python `list` before the value is appended.
```spork
; Vectors add at end
(conj [1 2] 3)           ; => [1 2 3]

; Lists add at front
(conj '(1 2) 0)          ; => (0 1 2)

; Sets add element
(conj #{1 2} 3)          ; => #{1 2 3}
(conj #{1 2} 2)          ; => #{1 2}

; Maps add entry
(conj {:a 1} [:b 2])     ; => {:a 1 :b 2}
```

### `assoc`
Associates a key with a value in a persistent map, vector, or Python `dict`, returning a new collection. Associating a non-integer key into `nil` creates a persistent map.
```spork
; Maps
(assoc {:a 1} :b 2)           ; => {:a 1 :b 2}
(assoc {:a 1} :a 99)          ; => {:a 99}

; Vectors (by index)
(assoc [1 2 3] 1 42)          ; => [1 42 3]
(assoc [1 2 3] 0 :first)      ; => [:first 2 3]
```

### `dissoc`
Removes a key from a persistent map or Python `dict`, returning a new collection. A missing key is a no-op, and `nil` remains `nil`.
```spork
(dissoc {:a 1 :b 2} :a)       ; => {:b 2}
(dissoc {:a 1 :b 2} :c)       ; => {:a 1 :b 2}
```

### `disj`
Removes an element from a persistent or Python set, or one matching occurrence from a `SortedVector`, returning a new collection. If the value is absent, the original value is returned unchanged; `nil` remains `nil`.
```spork
(disj #{1 2 3} 2)        ; => #{1 3}
(disj #{1 2 3} 5)        ; => #{1 2 3}

; Also removes one matching value from a SortedVector
(disj (sorted-vec [1 2 2 3]) 2) ; => sorted_vec(1, 2, 3)
```

### `get`
Returns the value for a key, with optional default. Works on maps, indexed collections, slices, and strings.
```spork
; Maps
(get {:a 1 :b 2} :a)         ; => 1
(get {:a 1} :b)              ; => nil
(get {:a 1} :b :not-found)   ; => :not-found

; Vectors (by index)
(get [1 2 3] 1)              ; => 2
(get [1 2 3] 10)             ; => nil
(get [1 2 3] 10 :oops)       ; => :oops

; Strings
(get "hello" 1)              ; => "e"
```

### `count`
Returns the number of elements in a collection.
```spork
(count [1 2 3])         ; => 3
(count {:a 1 :b 2})     ; => 2
(count #{1 2 3 4})      ; => 4
(count "hello")         ; => 5
(count nil)             ; => 0
(count [])              ; => 0
```

### `contains?`
For maps it checks keys, for sets and sorted vectors it checks values, and for vectors, Python lists, and tuples it checks whether a nonnegative integer index exists. Other iterable types use Python membership.
```spork
; Maps (checks keys)
(contains? {:a 1 :b 2} :a)   ; => true
(contains? {:a 1 :b 2} :c)   ; => false

; Sets (checks elements)
(contains? #{1 2 3} 2)       ; => true
(contains? #{1 2 3} 5)       ; => false

; Vectors check an index, not a stored value
(contains? [1 2 3] 0)        ; => true
(contains? [1 2 3] 2)        ; => true
(contains? [1 2 3] 5)        ; => false
```

### `empty`
Returns an empty value for persistent `Vector`, `Map`, `Set`, `SortedVector`, and `Cons` collections and for Python `list`, `dict`, and `set`. Unsupported inputs, including strings and typed vectors, return `nil`. A `SortedVector` result uses default ascending ordering rather than preserving custom key or reverse settings.
```spork
(empty [1 2 3])         ; => []
(empty {:a 1 :b 2})     ; => {}
(empty #{1 2 3})        ; => #{}
(empty '(1 2 3))        ; => nil
```

### `into`
Adds every input element to a supported persistent destination: a vector, map, set, sorted vector, `Cons` list, or `nil`. This is useful for conversion and batch construction.
```spork
; Convert list to vector
(into [] '(1 2 3))           ; => [1 2 3]

; Convert vector to set
(into #{} [1 2 2 3 3 3])     ; => #{1 2 3}

; Build map from pairs
(into {} [[:a 1] [:b 2]])    ; => {:a 1 :b 2}

; Add to an existing collection
(into [0] [1 2 3])           ; => [0 1 2 3]

; A list destination receives each new item at the front
(into '(0) [1 2 3])          ; => (3 2 1 0)

; Realize a lazy transformation into a chosen collection
(into [] (map inc [1 2 3]))   ; => [2 3 4]
```

## Sequence predicates

### `some`
Returns first truthy result of (pred item), or nil if none.
```spork
(some even? [1 3 5 6 7])         ; => true
(some even? [1 3 5 7])           ; => nil
(some #(> % 5) [1 2 3 4])        ; => nil
(some #(> % 5) [1 2 6 4])        ; => true

; Find an element using set membership
(some #(if (contains? #{3 5 7} %) %) [1 2 3 4]) ; => 3

; Return actual matching value
(some #(if (> % 5) %) [1 3 6 2]) ; => 6
```

### `every`
Returns true if `(pred item)` is truthy for every item. Empty inputs, including `nil`, return true.
```spork
(every even? [2 4 6 8])         ; => true
(every even? [2 4 5 6])         ; => false
(every pos? [1 2 3])            ; => true
(every #(isinstance % str) ["a" "b" "c"]) ; => true
(every (fn [x] x) [1 2 nil 3]) ; => false
```

### `not-every`
Returns true if the predicate is falsy for at least one item. It returns false for an empty input.
```spork
(not-every even? [2 4 6 8])     ; => false
(not-every even? [2 4 5 6])     ; => true
(not-every pos? [1 -1 2])       ; => true
(not-every even? [])             ; => false
```

### `not-any`
Returns true if the predicate is falsy for every item, including when the input is empty.
```spork
(not-any even? [1 3 5 7])       ; => true
(not-any even? [1 3 4 5])       ; => false
(not-any neg? [1 2 3])          ; => true
(not-any #(isinstance % str) [1 2 3]) ; => true
(not-any even? [])                   ; => true
```
