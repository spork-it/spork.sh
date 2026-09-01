---
title: Async and generators
description: Write async functions, eager async iteration, and Python generators.
section: reference
group: language
project: spork-lang
order: 190
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork maps asynchronous functions, awaiting, asynchronous iteration, and generators onto Python’s execution model. The forms on this page retain Spork’s expression and persistent-collection conventions where noted.

## Async Functions

Place the `^async` compiler flag before the function name. `await` and `async-for` may only appear inside an async function. Like `for`, `async-for` eagerly returns a persistent vector after consuming the asynchronous iterable; it does not return a lazy async iterator.

```spork
(defn ^async fetch-data [url]
  (let [response (await (http.get url))]
    (await (response.json))))

; Eagerly transform an asynchronous iterable
(defn ^async load-items []
  (async-for [item (async-iterator)]
    (await (transform item))))
```

## Generators

Place `^generator` before the function name when its body uses `yield` or `yield-from`.

```spork
(defn ^generator count-up [start]
  (loop [n start]
    (yield n)
    (recur (inc n))))

; Yield from (delegation)
(defn ^generator chain [& iterables]
  (doseq [it iterables]
    (yield-from it)))
```
