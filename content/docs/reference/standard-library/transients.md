---
title: Transient operations
description: Mutable builders for efficient batches over persistent collections.
section: reference
group: standard-library
project: spork-lang
order: 420
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

Transients are mutable builders initialized from persistent collections. Operations ending in `!` mutate a transient in place; do not apply them to persistent collections. Convert the builder back with `persistent!` when the batch is complete.

## `transient`
Creates a mutable builder from a persistent `Vector`, `DoubleVector`, `IntVector`, `Map`, `Set`, or `SortedVector`.
```spork
(def tv (transient [1 2 3]))
(def tm (transient {:a 1}))
(def ts (transient #{1 2}))
```

## `persistent!`
Converts a transient back to a persistent collection and invalidates the transient. Later access to the transient raises `RuntimeError`.
```spork
(persistent! (transient [1 2 3]))  ; => [1 2 3]

; Common pattern: build then persist
(-> (transient [])
    (conj! 1)
    (conj! 2)
    (conj! 3)
    (persistent!))  ; => [1 2 3]
```

## `conj!`
Mutates a transient by adding one value and returns that transient. A transient map requires a two-item key/value pair.
```spork
(def tv (transient []))
(conj! tv 1)
(conj! tv 2)
(persistent! tv)  ; => [1 2]
```

## `assoc!`
Associates a key in a `TransientMap` or an index in a general `TransientVector` and returns the transient. Vector indices may be negative. Typed-vector and sorted-vector transients do not support this operation.
```spork
(def tm (transient {:a 1}))
(assoc! tm :b 2)
(assoc! tm :c 3)
(persistent! tm)  ; => {:a 1 :b 2 :c 3}

(def tv (transient [1 2 3]))
(assoc! tv 1 42)
(persistent! tv)  ; => [1 42 3]
```

## `dissoc!`
Removes from a transient map.
```spork
(def tm (transient {:a 1 :b 2 :c 3}))
(dissoc! tm :b)
(persistent! tm)  ; => {:a 1 :c 3}
```

## `disj!`
Removes a value from a transient set or sorted vector.
```spork
(def ts (transient #{1 2 3 4}))
(disj! ts 2)
(disj! ts 4)
(persistent! ts)  ; => #{1 3}
```

## `pop!`
Removes the final element from a general `TransientVector`. Typed-vector and sorted-vector transients do not support this operation.
```spork
(def tv (transient [1 2 3 4]))
(pop! tv)
(pop! tv)
(persistent! tv)  ; => [1 2]
```

## SortedVector Transient Operations

SortedVector has its own transient type with methods that maintain sorted order:

```spork
; Create transient from sorted vector
(def sv (sorted-vec [1 3 5 7]))
(def tsv (transient sv))

; Add elements while maintaining sorted order
(conj! tsv 2)
(conj! tsv 4)
(conj! tsv 6)

; Remove one matching value; an absent value is a no-op
(disj! tsv 3)
(disj! tsv 99)

; Convert back to persistent
(def result (persistent! tsv))  ; => sorted_vec(1, 2, 4, 5, 6, 7)

; A transient preserves its source's key function and reverse ordering
(def tsv
  (transient
    (sorted-vec [{:score 10} {:score 20}]
                *{:key :score :reverse true})))
(conj! tsv {:score 15})
(vec (persistent! tsv))
; => [{:score 20} {:score 15} {:score 10}]
```

## `with-mutable`
Binds a transient initialized from the supplied collection, executes the body, and returns that transient's persistent result. The body's own result is ignored. This macro is the shortest form for a scoped batch of mutations.

```spork
(with-mutable [v [10 20]]
  (conj! v 30)
  :ignored-body-result)
; => [10 20 30]
```

**Python-style Mutable APIs:**

Transient maps, vectors, and sets are registered with Python's mutable collection ABCs:

- `TransientMap` passes `isinstance` checks for `MutableMapping`
- `TransientVector` passes `isinstance` checks for `MutableSequence`
- `TransientSet` passes `isinstance` checks for `MutableSet`

ABC registration enables type checks but does not supply every Python mixin method: for example, transient vectors have no `.insert`, and transient maps have no `.update`. They can be passed to Python code that relies only on supported operations. Typed-vector and sorted-vector transients have smaller, type-specific APIs.

```spork
; TransientVector supports .append, .extend, indexing, and iteration
(with-mutable [v []]
  (v.extend [1 2 3])
  (v.append 4))
; => [1 2 3 4]

; TransientMap supports .get, .keys, .values, .items, and iteration
(with-mutable [m {}]
  (assoc! m :a 1)
  (assert (= (m.get :a) 1)))
; => {:a 1}

; TransientSet supports .add, .discard, .remove, .clear, and iteration
(with-mutable [s #{}]
  (s.add 1)
  (s.add 2)
  (s.discard 1))
; => #{2}
```

For example, Python's `random.shuffle` mutates a transient vector through the mutable-sequence protocol, and `with-mutable` retains the mutation in its persistent result:

```spork
(ns example.shuffle
  (:import [random :refer [shuffle]]))

(def shuffled
  (with-mutable [v [1 2 3 4]]
    (shuffle v)))

; The order is random, but the persistent result contains the same values
(vec (sorted shuffled)) ; => [1 2 3 4]
```

**Typical Transient Pattern:**
```spork
(defn build-vector [n]
  (loop [tv (transient [])
         i 0]
    (if (< i n)
      (recur (conj! tv i) (inc i))
      (persistent! tv))))

(build-vector 5)  ; => [0 1 2 3 4]
```
