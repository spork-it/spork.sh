---
title: std.json
description: Encode and decode Spork persistent values with Python-compatible JSON behavior.
section: reference
group: standard-library
project: spork-lang
order: 500
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

The `std.json` namespace serializes and parses JSON while converting persistent Spork collections, keywords, and symbols at the boundary. Require it explicitly when source code needs JSON text or files.

**Usage:** `(ns my-file (:require [std.json :as json]))`

## Encoding

`json.dumps` uses Python's standard single-line JSON formatting. `json.dumps-pretty` uses an indentation level of two. `json.generate` is an alias for `json.dumps`.

```spork
(def encoded (json.dumps {:name "Spork" :items [1 2 3]}))
; typical encoded value: "{\"name\": \"Spork\", \"items\": [1, 2, 3]}"
; JSON object key order follows the map's unspecified iteration order
(json.loads encoded true) ; => {:name "Spork" :items [1 2 3]}

(json.dumps-pretty {:ready true})
; => "{\n  \"ready\": true\n}"

(json.generate {:status "ok"})
; => "{\"status\": \"ok\"}"
```

The encoder converts values recursively:

| Spork value | JSON representation |
| --- | --- |
| `nil` | `null` |
| booleans, numbers, and strings | corresponding JSON scalar |
| `Map` | object; keyword and symbol keys use their names, and every other non-string key is stringified |
| `Vector`, `DoubleVector`, `IntVector`, `SortedVector` | array |
| `Set` | array; order is unspecified |
| `Cons` | array |
| `TransientMap`, `TransientVector`, `TransientSet` | their current mutable contents |
| keyword used as a value | string with a leading `:` |
| symbol used as a value | string |

`json.dump` and `json.dump-pretty` write to a file-like object and return `nil`:

```spork
(with [out (open "data.json" "w")]
  (json.dump-pretty {:name "Spork" :ready true} out))

(json.loads (.read-text #p"data.json") true)
; => {:name "Spork" :ready true}
```

## Decoding

`json.loads` parses a string and recursively converts JSON objects to persistent `Map` values and arrays to persistent `Vector` values. `json.parse` is an alias for `json.loads`.

```spork
(def data (json.loads "{\"name\": \"Spork\", \"items\": [1, 2]}"))
(get data "name")             ; => "Spork"
(get data "items")            ; => [1 2]

; Pass true to convert object keys to keywords at every nesting level
(def keyed (json.loads "{\"ready\": true}" true))
(:ready keyed)                 ; => true

(json.parse "[1, 2, 3]")      ; => [1 2 3]
```

`json.load` reads from a file-like object and accepts the same optional keywordization flag:

```spork
(with [in (open "data.json" "r")]
  (json.load in true))
; => {:ready true}
```

JSON has no set, symbol, or keyword type, so those distinctions do not round-trip automatically. Stringification can also make distinct map keys collide in a JSON object. Invalid JSON and unsupported encoded values raise the corresponding Python `json` exceptions.
