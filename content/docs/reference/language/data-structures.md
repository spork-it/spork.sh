---
title: Data structures
description: Understand Spork’s persistent collection literals and sequence model.
section: reference
group: language
project: spork-lang
order: 110
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork collection literals use the persistent types supplied by the native `spork-pds` package. They are ordinary Python objects with Spork-oriented value semantics: updates return new collections, prior versions remain valid, and unchanged structure is shared internally.

## Persistence and value semantics

Persistent collections do not expose in-place update operations. Functions such as `assoc`, `conj`, `dissoc`, and `disj` return a new value instead:

```spork
(def original [10 20 30])
(def updated (assoc original 1 99))

original ; => [10 20 30]
updated  ; => [10 99 30]
(conj original 40) ; => [10 20 30 40]
```

Immutability is shallow. A vector cannot replace one of its own slots in place, but a mutable Python object stored in that slot can still change. Structural sharing is an implementation detail: programs should rely on value equality and persistence, not node identity.

For a batch of updates, use a single-owner [transient collection](/docs/reference/language/transients/) and convert it back to a persistent value when finished.

## Collection families

The core runtime types are:

- `Vector` — persistent vector (32-way bit-partitioned trie)
- `Map` — persistent hash map (HAMT)
- `Set` — persistent hash set (HAMT)
- `DoubleVector` — type-specialized vector for `float64` values
- `IntVector` — type-specialized vector for signed `int64` values
- `SortedVector` — persistent sorted collection (red-black tree)
- `Cons` — immutable linked-list cells

`Vector`, `Map`, and `Set` have literal syntax. `SortedVector` and the specialized vectors use constructors or, in a narrow case, an annotated vector definition.

## Literal rules

Collection delimiters determine the constructed runtime value:

| Source form | Runtime value | Empty form |
| --- | --- | --- |
| `[item ...]` | `Vector` | `[]` |
| `{key value ...}` | `Map` | `{}` |
| `#{item ...}` | `Set` | `#{}` |
| `'(item ...)` | `Cons` chain | `'()` evaluates to `nil` |

Vector elements, map keys and values, and set members are ordinary expressions evaluated when the literal is constructed. A map requires an even number of forms. Commas are not separators; use whitespace between forms.

Parentheses have a different role: an unquoted parenthesized form is a call or special form, not a list literal. Quoting prevents evaluation and constructs list data. See [lexical syntax](/docs/reference/language/lexical-syntax/#delimiters-and-collection-forms) and the [quote reader macro](/docs/reference/language/reader-macros/#quote).

## Vectors

Square brackets create a persistent `Vector` and preserve source order:

```spork
(def values [1 (+ 1 1) 3])
values                ; => [1 2 3]
(nth values 1)        ; => 2
(assoc values 1 20)   ; => [1 20 3]
```

Indexed lookup and replacement use integer positions. `conj` appends, while `assoc` replaces an existing position without changing the original vector. Slices produce persistent vectors as well.

A vector literal normally creates `Vector`. An exact `(def ^(Vector float) name [...])` or `(def ^(Vector int) name [...])` form can select specialized storage, as described under [persistent data structure types](/docs/reference/language/types/#persistent-data-structure-types).

See [`Vector`](/docs/reference/standard-library/collection-types/#vector) for constructors and the complete collection API.

## Maps

Curly braces containing alternating keys and values create a persistent `Map`:

```spork
(def person {:name "Alice" :age (+ 29 1)})
(:name person)          ; => "Alice"
(get person :age)       ; => 30
(assoc person :active true)
; => {:name "Alice" :age 30 :active true}
```

Keys must be hashable. Keywords, strings, numbers, tuples, and hashable persistent collections can be used as keys. If a literal repeats an equal key, the later value replaces the earlier one:

```spork
(get {:mode :old :mode :new} :mode) ; => :new
```

Map iteration order is not a language-level ordering contract. Use an explicit ordering operation before producing output whose byte order matters. See [`Map`](/docs/reference/standard-library/collection-types/#map) for lookup, update, and view operations.

## Sets

`#{...}` creates a persistent `Set`:

```spork
(def permissions #{:read :write :read})
(count permissions)             ; => 2
(contains? permissions :write)  ; => true
(disj permissions :write)       ; => #{:read}
```

Members must be hashable, repeated equal values collapse to one member, and iteration order is unspecified. Set operations and updates return persistent sets rather than mutating the receiver. See [`Set`](/docs/reference/standard-library/collection-types/#set) for membership, update, and set operations.

## Lists (Cons Cells)

Quoting a parenthesized form produces immutable list data instead of evaluating a call:

```spork
'(1 2 3)       ; => (1 2 3)
'()            ; => nil
'(add 1 2)     ; the symbol and numbers are data, not a call
```

A non-empty list is a chain of `Cons` cells whose final rest is `nil`. Quoted contents are not evaluated. To build a list from evaluated runtime values, use `cons` or eagerly convert an iterable with `seq`:

```spork
(cons (+ 1 1) (cons 3 nil)) ; => (2 3)
(seq [1 (+ 1 1) 3])         ; => (1 2 3)
```

See [`Cons`](/docs/reference/standard-library/collection-types/#cons-linked-list) for construction and sequence operations.

## SortedVector

Persistent sorted vectors maintain elements in configured order using a red-black tree. There is no dedicated literal; construct one with `sorted-vec` or `sorted-for`. Indexed lookup, insertion, removal, membership, and rank queries are O(log n); full iteration is O(n). Duplicates are retained.

`sorted-vec` is the idiomatic Spork spelling. It resolves to the Python binding `sorted_vec` through identifier normalization, which is also why the value's representation uses an underscore.

The optional `:key` function derives sort keys, and `:reverse true` reverses the configured ordering:

```spork
(def words-longest-first
  (sorted-vec ["pear" "fig" "banana"] *{:key len :reverse true}))
(vec words-longest-first) ; => ["banana" "pear" "fig"]
```

Without a key function, members must support comparison with one another. With a key function, the derived keys must be comparable. See [`SortedVector`](/docs/reference/standard-library/collection-types/#sortedvector) for construction, lookup, rank, update, and transient APIs.

## Sequence Abstraction

Persistent collections participate in Spork's sequence operations alongside Python iterables. `first` returns the first item or `nil`; `rest` returns the remaining items as a sequence; and `seq` eagerly converts an iterable to a `Cons` sequence, returning `nil` for an empty input. Calling `seq` on a map produces two-element key/value vectors.

Sequence operations do not erase collection distinctions. A literal vector remains a persistent `Vector`, while Python's lowercase constructors create Python builtins:

```spork
(def persistent [1 2 3])
(def mutable (list [1 2 3]))

(isinstance persistent Vector) ; => true
(isinstance mutable list)      ; => true
```

Use persistent values for value-oriented updates and Python `list`, `dict`, `set`, and tuple values when an API specifically requires mutable or exact Python collection semantics. See [core sequence operations](/docs/reference/standard-library/sequences/#core-operations) for realization behavior, conversions, and functions such as `into`, `map`, and `filter`.
