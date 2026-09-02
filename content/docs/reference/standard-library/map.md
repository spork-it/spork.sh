---
title: std.map
description: Persistent map traversal, nested updates, merging, selection, filtering, and transformation.
section: reference
group: standard-library
project: spork-lang
order: 490
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

The `std.map` namespace provides persistent nested updates, key transformations, merging, selection, and inversion. Require it explicitly; these names are not installed into every namespace.

**Usage:** `(ns my-file (:require [std.map :as m]))`

## `m.keys` / `m.vals`
Return keys or values as persistent vectors. Their order follows the map's unspecified iteration order.
```spork
(def ks (m.keys {:a 1 :b 2 :c 3}))
(vector? ks)                      ; => true
(= (set ks) (set [:a :b :c]))    ; => true

(def vs (m.vals {:a 1 :b 2 :c 3}))
(vector? vs)                      ; => true
(= (set vs) (set [1 2 3]))       ; => true

(m.keys {})                       ; => []
(m.vals {})                       ; => []
```

## `m.entries`
Get key-value pairs as vector of vectors.
```spork
(into {} (m.entries {:a 1 :b 2})) ; => {:a 1 :b 2}
(m.entries {:x 10})               ; => [[:x 10]]
```

## `m.update`
Applies a function to the current value and associates the result. If the key is absent, the function receives `nil`.
```spork
(m.update {:a 1} :a inc)          ; => {:a 2}
(m.update {:a 1 :b 2} :b #(* % 10))  ; => {:a 1 :b 20}
(m.update {:count 5} :count dec)  ; => {:count 4}
```

## `m.update-with`
Like `m.update`, but supplies `default` when the key is absent. A stored `nil` remains `nil` and is not replaced by the default.
```spork
(m.update-with {:a 1} :a inc 0)   ; => {:a 2}
(m.update-with {:a 1} :b inc 0)   ; => {:a 1 :b 1}
(m.update-with {} :count inc 0)   ; => {:count 1}
```

## `m.get-in`
Traverses a sequence of keys through nested maps. It returns `nil` when a lookup fails; an empty key path returns the original map.
```spork
(m.get-in {:a {:b {:c 1}}} [:a :b :c])  ; => 1
(m.get-in {:a {:b 2}} [:a :b])          ; => 2
(m.get-in {:a 1} [:a])                  ; => 1
(m.get-in {:a {:b 2}} [:a :c])          ; => nil
```

## `m.get-in-or`
Get-in with a default value. A stored `nil` is treated the same as a missing path.
```spork
(m.get-in-or {:a {:b 1}} [:a :b] 42)   ; => 1
(m.get-in-or {:a {}} [:a :b] 42)       ; => 42
(m.get-in-or {} [:a :b :c] :missing)   ; => :missing
```

## `m.assoc-in`
Associates a value at a nonempty path, creating missing intermediate maps. Existing intermediate values must themselves support map lookup and association.
```spork
(m.assoc-in {:a {}} [:a :b] 1)         ; => {:a {:b 1}}
(m.assoc-in {} [:a :b :c] 42)          ; => {:a {:b {:c 42}}}
(m.assoc-in {:a {:b 1}} [:a :b] 99)    ; => {:a {:b 99}}
(m.assoc-in {:a {:b 1}} [:a :c] 2)     ; => {:a {:b 1 :c 2}}
```

## `m.update-in`
Updates a value at a nonempty path. Missing intermediate maps are created, and a missing final value is passed to the function as `nil`.
```spork
(m.update-in {:a {:b 1}} [:a :b] inc)  ; => {:a {:b 2}}
(m.update-in {:a {:b {:c 5}}} [:a :b :c] #(* % 10))
; => {:a {:b {:c 50}}}
(m.update-in {:stats {:count 0}} [:stats :count] inc)
; => {:stats {:count 1}}
```

## `m.select-keys`
Select only specified keys from map.
```spork
(m.select-keys {:a 1 :b 2 :c 3} [:a :c])  ; => {:a 1 :c 3}
(m.select-keys {:a 1 :b 2} [:a :b :c])    ; => {:a 1 :b 2}
(m.select-keys {:a 1 :b 2} [:x :y])       ; => {}
(m.select-keys {:a 1 :b 2} [])            ; => {}
```

## `m.dissoc-in`
Removes the final key at a nonempty nested path. The parent path should exist; when an intermediate key is missing, the current implementation associates `nil` at that point.
```spork
(m.dissoc-in {:a {:b 1 :c 2}} [:a :b])    ; => {:a {:c 2}}
(m.dissoc-in {:a {:b {:c 1}}} [:a :b :c]) ; => {:a {:b {}}}
(m.dissoc-in {:x {:y 1}} [:x :y])         ; => {:x {}}
(m.dissoc-in {} [:x :y])                   ; => {:x nil}
```

## `m.merge`
Merges zero or more maps into a new persistent map. Later values override earlier ones, and `nil` inputs are ignored.
```spork
(m.merge {:a 1} {:b 2})               ; => {:a 1 :b 2}
(m.merge {:a 1} {:a 2})               ; => {:a 2}
(m.merge {:a 1} {:b 2} {:c 3})        ; => {:a 1 :b 2 :c 3}
(m.merge {:a 1 :b 1} {:b 2} {:b 3})   ; => {:a 1 :b 3}
(m.merge {:a 1} nil {:b 2})           ; => {:a 1 :b 2}
```

## `m.merge-with`
Merge using function to combine values for duplicate keys.
```spork
(m.merge-with + {:a 1} {:a 2})        ; => {:a 3}
(m.merge-with + {:a 1 :b 2} {:a 3 :b 4})  ; => {:a 4 :b 6}
(m.merge-with into {:a [1]} {:a [2]})     ; => {:a [1 2]}
(m.merge-with into {:a #{1}} {:a #{2 3}}) ; => {:a #{1 2 3}}
```

## `m.rename-keys`
Renames keys according to a mapping. If several source keys resolve to the same target, one overwrites the others according to the source map's unspecified iteration order.
```spork
(m.rename-keys {:a 1 :b 2} {:a :x})        ; => {:x 1 :b 2}
(m.rename-keys {:a 1 :b 2} {:a :x :b :y})  ; => {:x 1 :y 2}
(m.rename-keys {:a 1 :b 2} {:c :z})        ; => {:a 1 :b 2}
(m.rename-keys {:old-name "value"} {:old-name :new-name})
; => {:new-name "value"}
```

## `m.invert`
Swaps keys and values. Values must be hashable; duplicate values collapse to one entry according to unspecified map iteration order.
```spork
(m.invert {:a 1 :b 2})            ; => {1 :a 2 :b}
(m.invert {:x "hello" :y "world"}) ; => {"hello" :x "world" :y}
(m.invert {1 :a 2 :b})            ; => {:a 1 :b 2}
```

## `m.map-keys` / `m.map-vals`
Transform keys or values. Results from `m.map-keys` must be hashable, and key collisions overwrite according to unspecified map iteration order.
```spork
; Map over keys
(m.map-keys (fn [k] k.name) {:a 1 :b 2}) ; => {"a" 1 "b" 2}
(m.map-keys str {1 :a 2 :b})      ; => {"1" :a "2" :b}
(m.map-keys inc {1 :a 2 :b})      ; => {2 :a 3 :b}

; Map over values
(m.map-vals inc {:a 1 :b 2})      ; => {:a 2 :b 3}
(m.map-vals str {:a 1 :b 2})      ; => {:a "1" :b "2"}
(m.map-vals count {:a [1 2] :b [1 2 3]})  ; => {:a 2 :b 3}
```

## `m.filter-keys` / `m.filter-vals`
Filter by predicate on keys or values.
```spork
; Filter by keys
(m.filter-keys #(isinstance % Keyword) {:a 1 "b" 2}) ; => {:a 1}
(m.filter-keys #(= :a %) {:a 1 :b 2})     ; => {:a 1}

; Filter by values
(m.filter-vals even? {:a 1 :b 2 :c 3 :d 4})  ; => {:b 2 :d 4}
(m.filter-vals pos? {:a -1 :b 0 :c 1 :d 2})  ; => {:c 1 :d 2}
(m.filter-vals #(not (= % nil)) {:a 1 :b nil :c 2}) ; => {:a 1 :c 2}
```

## `m.deep-merge`
Recursively merges values when both sides are persistent Spork maps. In every other conflict, the later value replaces the earlier one.
```spork
(m.deep-merge {:a {:b 1}} {:a {:c 2}})
; => {:a {:b 1 :c 2}}

(m.deep-merge {:a {:b {:c 1}}} {:a {:b {:d 2}}})
; => {:a {:b {:c 1 :d 2}}}

(m.deep-merge {:a {:x 1}} {:a {:x 2}})
; => {:a {:x 2}}

(m.deep-merge {:config {:debug false :port 8080}}
              {:config {:debug true}})
; => {:config {:debug true :port 8080}}
```
