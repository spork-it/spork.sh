---
title: Async HTTP
description: Use async functions, async context managers, await, and an ordinary Python dependency.
section: example
group: examples
project: spork-lang
order: 820
package-version: "0.6.1"
changefreq: monthly
priority: 0.6
---

This project requests one JSON object from `jsonplaceholder.typicode.com`. It requires network access and the remote response may change.

## Manifest

```spork
;; Spork Project Manifest
;; See https://spork.sh/docs/reference/tooling/ for manifest documentation

{:name "async"
 :version "0.1.0"

 ;; Dependencies (pip-style specifications)
 :dependencies ["aiohttp>=3.10,<4"]

 ;; Source code locations
 :source-paths ["src"]

 ;; Entry point for 'spork run'
 :main "async.core:main"}
```

## Source

<!-- verify-docs: skip=external-network-dependency -->
```spork
;; async - Core module
(ns async.core
  (:import [aiohttp] [asyncio]))

;; Define an asynchronous function with the ^async metadata
(defn ^async fetch-data [^str url]
  (async-with [session (aiohttp.ClientSession)]
    (async-with [resp (session.get url)]
      (await (resp.json)))))

;; Run it on the event loop
(defn main []
  (let [url "https://jsonplaceholder.typicode.com/todos/1"
        data (asyncio.run (fetch-data url))]
    (print "Received data:")
    (print data)))

```

Run it from the project directory:

```bash
spork sync
spork run
```

The `aiohttp` package supplies Python asynchronous context managers and coroutines; Spork’s `async-with` and `await` forms compile directly to their Python equivalents. See [async and generators](/docs/reference/language/async-and-generators/).
