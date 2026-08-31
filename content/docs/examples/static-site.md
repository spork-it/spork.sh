---
title: Static site
description: Build a source-only deterministic website using immutable markup and the package-owned top-level spork site command.
section: example
group: examples
project: spork-lang
order: 850
package-version: "0.6.0"
changefreq: monthly
priority: 0.6
---

Create a normal Spork project with a site factory independent from any application `:main`:

<!-- verify-docs: compile=manifest-fragment -->
```spork
{:name "tiny-site"
 :version "0.1.0"
 :spork-version "==0.6.0"
 :dependencies ["spork-site==0.1.1"]
 :source-paths ["src"]
 :site {:target "tiny-site.site:make-site"
        :watch ["spork.it" "src" "static"]}}
```

Define `src/tiny_site/site.spork`:

```spork
(ns tiny-site.site
  (:require
    [spork-site.build :as build]
    [spork-site.core :refer [element fragment markup]]
    [spork-site.routing :as routing]))

(defn home []
  (markup
    ($html {:lang "en"}
      ($head ($meta {:charset "utf-8"}) ($title "Tiny site"))
      ($body ($main ($h1 "Hello from Spork"))))))

(defn make-site []
  (build.site
    * :output "public"
      :pages [(routing.page "/" (home))]
      :assets (build.discover-assets "static")))
```

Create an empty `static/` directory, synchronize, and run:

```bash
spork sync
spork site check
spork site serve --open
spork site build
```

`check` validates the complete plan without writing. Production output is deterministic, while development serving builds isolated generations and injects reload support only into served HTML. Continue with the [spork-site reference](/docs/packages/spork-site/).
