---
title: Collection types
description: Persistent vectors, maps, sets, linked lists, sorted collections, keywords, and symbols.
section: reference
group: standard-library
project: spork-lang
order: 400
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

Spork’s persistent collection types are supplied by the native `spork-pds` package. This page defines their Spork-facing constructors, type-specific behavior, update direction, ordering, and Python interoperability. Literal syntax itself is covered under [language data structures](/docs/reference/language/data-structures/), while individual operations are specified under [sequence operations](/docs/reference/standard-library/sequences/).

This page also covers the Python-implemented `Keyword` and `Symbol` runtime values used by source forms and macro APIs.

## Choosing a collection

| Type | Primary use | Ordering | Duplicate policy | `conj` behavior |
| --- | --- | --- | --- | --- |
| `Vector` | General indexed values | Source/insertion order | Retained | Append |
| `DoubleVector` | Unboxed float64 values | Source/insertion order | Retained | Append |
| `IntVector` | Unboxed signed int64 values | Source/insertion order | Retained | Append |
| `Map` | Key/value lookup | Unspecified | Later equal key replaces value | Associate a key/value pair |
| `Set` | Membership and set algebra | Unspecified | Collapsed | Add member |
| `Cons` | Linked sequences and efficient prepending | List order | Retained | Prepend |
| `SortedVector` | Ordered values and rank queries | Configured sorted order | Retained | Insert in sorted position |

Choose persistent collections when old versions must remain valid, updates branch into several histories, or immutable snapshots are shared. Python's lowercase `list`, `dict`, and `set` are usually simpler when one owner mutates only the latest value.

## Shared behavior

Persistent updates return a value and leave the receiver unchanged. Unchanged branches are structurally shared internally, but object identity and the amount of sharing are not API contracts.

```spork
(def base {:items [1 2]})
(def updated (assoc base :items (conj (:items base) 3)))

base    ; => {:items [1 2]}
updated ; => {:items [1 2 3]}
```

Immutability is shallow. A collection cannot replace its own entries in place, but a mutable Python object stored inside it retains its normal mutation behavior. Use immutable nested values when the whole value must be stable.

Persistent collections implement the corresponding Python collection protocols and are iterable, generic, picklable, and hashable when the contents required for their hash are hashable. Map keys and set members must be hashable when inserted. No-op updates may return the original object; compare values rather than relying on identity.

For repeated updates where intermediate versions are not needed, use a [transient collection](/docs/reference/standard-library/transients/) as a single-owner builder.

## Vector

Persistent vectors provide efficient random access and updates. Vectors are created using square bracket syntax.

```spork
; Creating vectors
[1 2 3 4 5]           ; literal syntax
(vec 1 2 3)           ; => [1 2 3]

; Basic operations
(conj [1 2] 3)        ; => [1 2 3]
(nth [1 2 3] 1)       ; => 2
(nth [1 2] 5 :default) ; => :default
(assoc [1 2 3] 1 42)  ; => [1 42 3]
(count [1 2 3])       ; => 3
(first [1 2 3])       ; => 1
(rest [1 2 3])        ; => (2 3)
(last [1 2 3])        ; => 3
(.pop [1 2 3])        ; => [1 2]
```

`nth` and `get` accept zero-based indexes. Native vectors also support Python-style negative indexing and persistent slicing. `assoc` replaces an existing index and accepts `count` as the append position. By contrast, `contains?` checks whether an index exists; it does not search stored values.

```spork
(get [10 20 30] -1)       ; => 30
(get [10 20 30] #[1 3])   ; => [20 30]
(assoc [10 20] 2 30)      ; => [10 20 30]
(contains? [10 20 30] 2)  ; => true
(contains? [10 20 30] 20) ; => false
(.sort [3 1 2])            ; => [1 2 3]
```

Direct persistent methods include `.nth`, `.conj`, `.assoc`, `.pop`, `.sort`, and `.transient`. Slicing and `.sort` return vectors; `rest` deliberately returns a `Cons` sequence so the shared sequence vocabulary has one tail representation.

### Specialized vectors

`DoubleVector` stores C `double` values and `IntVector` stores signed 64-bit integers:

```spork
; DoubleVector - Optimized for 64-bit floats
(isinstance (vec-f64 1.0 2.0 3.0) DoubleVector) ; => true

; an annotated vector literal can select specialized storage
(def ^(Vector float) v [1.0 2.0 3.0])
(isinstance v DoubleVector) ; => true

; IntVector - Optimized for 64-bit integers
(isinstance (vec-i64 1 2 3) IntVector) ; => true
```

`vec-f64` converts numeric inputs to float64. `vec-i64` requires values representable as signed int64. Both types support length, iteration, indexing, negative indexing, slicing, hashing, `nth`, `conj`, and focused transients; slicing preserves the specialized type.

Their storage exports a one-dimensional read-only Python buffer, allowing consumers such as `memoryview` and NumPy to read contiguous values without making the persistent collection writable. The exact annotated `def` optimization and its limits are documented under [specialized vector definitions](/docs/reference/language/types/#specialized-vector-definitions).

## Map

Persistent hash maps accept any hashable key. Maps are created using curly brace syntax.

```spork
; Creating maps
{:a 1 :b 2}              ; literal syntax
(hash-map :a 1 :b 2)     ; => {:a 1 :b 2}

; Basic operations
(assoc {:a 1} :b 2)      ; => {:a 1 :b 2}
(dissoc {:a 1 :b 2} :a)  ; => {:b 2}
(get {:a 1} :a)          ; => 1
(get {:a 1} :b)          ; => nil
(get {:a 1} :b 42)       ; => 42
(:a {:a 1})              ; => 1
(:missing {:a 1} "nope") ; => "nope"
(count {:a 1 :b 2})      ; => 2
(contains? {:a 1} :a)    ; => true
(.keys {:a 1 :b 2})      ; iterable view of keys
(.values {:a 1 :b 2})    ; iterable view of values
```

`contains?` checks keys, not values. Direct map iteration also yields keys, while `seq` produces two-element key/value vectors. Key iteration order is unspecified and should be explicitly sorted before deterministic output is emitted.

Map union uses Python `dict` precedence: the right operand wins, and the result remains persistent.

```spork
(def merged
  (| {:left 1 :shared "old"}
     {:right 2 :shared "new"}))
merged ; => {:left 1 :right 2 :shared "new"}

(seq {:only 1}) ; => ([:only 1])
```

`assoc` adds or replaces one key, while `dissoc` is a no-op for a missing key. Maps are hashable only when both keys and values are hashable; that permits a fully hashable map to serve as another map's key.

## Set

Persistent sets. Sets are created using `#{}` syntax.

```spork
; Creating sets
#{1 2 3}               ; literal syntax
(hash-set [1 2 3])     ; => #{1 2 3}

; Basic operations
(conj #{1 2} 3)        ; => #{1 2 3}
(disj #{1 2 3} 2)      ; => #{1 3}
(contains? #{1 2} 1)   ; => true
(contains? #{1 2} 5)   ; => false
(count #{1 2 3})       ; => 3

; Set operations
(| #{1 2} #{2 3})      ; => #{1 2 3}
(& #{1 2} #{2 3})      ; => #{2}
(- #{1 2 3} #{2})      ; => #{1 3}
(^ #{1 2 3} #{3 4})    ; => #{1 2 4}

; Proper-subset and subset comparisons
(< #{1} #{1 2})        ; => true
(<= #{1 2} #{1 2})     ; => true
```

`hash-set` accepts zero or one iterable rather than variadic members; use a literal or pass a vector for several values. Set iteration order is unspecified. Operators `|`, `&`, `-`, and `^` return persistent sets, and comparisons use mathematical subset/superset semantics. A set is itself hashable only when all members are hashable.

## Cons (Linked List)

Singly linked lists created by `cons`, quoting, and eager sequence conversion with `seq`.

```spork
; Creating lists
(cons 1 nil)              ; => (1)
(cons 1 (cons 2 nil))     ; => (1 2)
(cons 0 '(1 2 3))         ; => (0 1 2 3)

; Basic operations
(first (cons 1 (cons 2 nil)))  ; => 1
(rest (cons 1 (cons 2 nil)))   ; => (2)
(first nil)                    ; => nil
(rest nil)                     ; => nil
```

`nil` is the empty list representation; there is no separate empty `Cons` object. `conj` and `cons` prepend in O(1) and share the existing tail. Indexed lookup and `count` must walk the chain, so use a vector when repeated random access matters.

`seq` eagerly converts an iterable to a `Cons` chain. Quoted lists contain unevaluated data, whereas `seq` and `cons` receive already evaluated runtime values. Cons chains support iteration, equality, hashing when their elements are hashable, generic annotations, and pickle.

## Keyword

Keywords are named, hashable values that evaluate to themselves and begin with `:`. Equality and hashing depend on the complete keyword name, whose punctuation is retained. Keywords are also callable map-lookup functions.

```spork
; Keywords as values
:my-key
:build.status
(= :my-key :my-key)              ; => true

; Keywords as functions (map lookup)
(:name {:name "Alice" :age 30})  ; => "Alice"
(:missing {:name "Alice"})       ; => nil
(:missing {:name "Alice"} "default")  ; => "default"

; A keyword can therefore extract the same key from several maps
(map :name [{:name "Alice"} {:name "Bob"}]) ; => ("Alice" "Bob")
```

## Symbol

A symbol represents an identifier in source or code-as-data. An unquoted symbol resolves as a binding, operator, or dotted access; quoting produces the `Symbol` value itself. Quoted symbols retain their source spelling rather than applying Python identifier normalization.

```spork
(def my-value 10)
my-value         ; => 10
'my-value        ; the symbol my-value
'foo.bar         ; one dotted symbol value
```

Symbols appear most often in quoted data, macro input and output, and namespace metadata. Source locations may be attached while forms are read, but location is compiler metadata rather than part of a symbol's printed spelling.

## SortedVector

Persistent sorted vectors retain duplicates in sorted order using a red-black tree. Indexed lookup, insertion, removal, membership, and rank queries are O(log n); full iteration is O(n). `sorted-vec` is the idiomatic spelling, while representations use the normalized runtime name `sorted_vec`.

```spork
; Creating sorted vectors
(sorted-vec [3 1 4 1 5 9])      ; => sorted_vec(1, 1, 3, 4, 5, 9)
(sorted-vec)                     ; => sorted_vec()

; A key function sorts by a derived value (string length here)
(sorted-vec ["banana" "apple" "cherry"] *{:key len})
; => sorted_vec("apple", "banana", "cherry")

; A keyword is callable and can be the key for map-like values
(sorted-vec [{:name "Bob" :age 25} {:name "Alice" :age 30}] *{:key :age})
; => sorted_vec({:name "Bob" :age 25}, {:name "Alice" :age 30})

; Reverse order
(sorted-vec [3 1 4] *{:reverse true}) ; => sorted_vec(4, 3, 1)

; Combine a key and reverse ordering
(def score-items
  [{:name "one" :score 10} {:name "two" :score 20}])
(def ranked (sorted-vec score-items *{:key :score :reverse true}))
(isinstance ranked SortedVector) ; => true
(vec ranked)
; => [{:name "two" :score 20} {:name "one" :score 10}]
```

**Basic Operations:**
```spork
(def sv (sorted-vec [5 2 8 1 9]))

(count sv)           ; => 5
(first sv)           ; => 1
(last sv)            ; => 9
(nth sv 2)           ; => 5
(nth sv 10 :default) ; => :default
(get sv 0)           ; => 1
(get sv -1)          ; => 9
```

**Adding and Removing Elements:**

`conj` inserts in configured sorted position and retains duplicates. `disj` removes one matching occurrence and is a no-op when the value is absent.

```spork
(def sv (sorted-vec [1 3 5]))

(conj sv 2)          ; => sorted_vec(1, 2, 3, 5)
(conj sv 3)          ; => sorted_vec(1, 3, 3, 5)
(disj sv 3)          ; => sorted_vec(1, 5)
(disj sv 99)         ; => sorted_vec(1, 3, 5)
```

**Search Operations:**

`index-of` (Python: `index_of`) returns the index of an equal value or `-1`. `rank` returns the insertion index under the vector's configured ordering.

```spork
(def sv (sorted-vec [10 20 30 40 50]))

(contains? sv 30)    ; => true
(contains? sv 25)    ; => false
(sv.index-of 30)    ; => 2
(sv.index-of 25)    ; => -1
(sv.rank 25)        ; => 2
(sv.rank 100)       ; => 5
```

**Iteration:**
```spork
; Iterates in sorted order for effects
(doseq [x (sorted-vec [3 1 4 1 5])]
  (print x))
; prints one value per line: 1, 1, 3, 4, 5

; Convert to vector
(vec (sorted-vec [3 1 4]))  ; => [1 3 4]
```

**Sorted Iteration Expression:**

`sorted-for` is an eager language expression rather than a library function. See [sorted-for expression](/docs/reference/language/forms-and-control-flow/#sorted-for-expression) in the language reference.

**Transient Operations:**

Sorted-vector transients preserve key and reverse settings. Their mutation API is documented under [`SortedVector` transient operations](/docs/reference/standard-library/transients/#sortedvector-transient-operations).

**Equality and Hashing:**
```spork
; Equal if same elements in same order
(= (sorted-vec [3 1 2]) (sorted-vec [1 2 3]))  ; => true
(= (sorted-vec [1 2]) (sorted-vec [1 2 3]))    ; => false

; Can be used as map keys (hashable)
(def cache {(sorted-vec [1 2 3]) "result"})
```

Ordering policy is retained by `conj`, `disj`, and transient conversion. Without `:key`, members must be mutually comparable; with `:key`, the derived keys must be comparable. A keyed sorted vector can be pickled only when its key function is also picklable.

## Conversion and Python boundaries

Persistent constructors and lowercase Python constructors intentionally produce different families:

```spork
(def persistent-vector [1 2 3])
(def python-list (list [1 2 3]))
(def persistent-map {:name "Spork"})
(def python-dict (dict [["name" "Spork"]]))

(isinstance persistent-vector Vector) ; => true
(isinstance python-list list)         ; => true
(isinstance persistent-map Map)       ; => true
(isinstance python-dict dict)         ; => true
```

Use `into` when converting to a chosen persistent destination, such as `(into [] iterable)`, `(into {} pairs)`, or `(into #{} iterable)`. Use `list`, `dict`, `set`, or `tuple` when an API requires an exact Python builtin. Conversion changes only the outer representation; nested objects are reused.

The complete native Python method surface, operator compatibility, buffer behavior, and transient lifecycle are documented in the [`spork-pds` API](/docs/packages/spork-pds/api/).
