---
title: Getting started with spork-site
description: Configure a source factory, synchronize the provider, and understand the publishing model.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 651
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

A site is an ordinary source-only Spork project. Add `spork-site`, configure `:site :target`, and return an immutable site value from that source function. The package owns the complete `spork site` command; no separate application entry point or Python adapter is required.

## Minimal site

Create `spork.it` at the project root:

```spork
{:name "example-site"
 :version "0.1.0"
 :spork-version ">=0.6,<0.7"
 :dependencies ["spork-site>=0.1,<0.2"]
 :source-paths ["src"]
 :site
 {:target "example.site:make-site"
  :watch ["spork.it" "src" "content" "static"]}}
```

Then define the configured source function in `src/example/site.spork`:

```spork
(ns example.site
  (:require
    [spork-site.build :as build]
    [spork-site.core :refer [element fragment markup]]
    [spork-site.routing :as routing]))

(defn make-site []
  (build.site
    * :output "public"
      :pages
      [(routing.page "/"
         (markup
           ($main
             ($h1 "Hello from Spork")
             ($p "This page is an immutable node tree."))))]))
```

Synchronize dependencies once, validate the complete plan, and build:

```bash
spork sync
spork site check
spork site build
```

The generated homepage is `public/index.html`. Continue with [builds and commands](/docs/packages/spork-site/builds-and-commands/) for output safety and the full command reference, or start [development serving](/docs/packages/spork-site/development-server/).

## Capabilities

- immutable `Element`, `Fragment`, `Text`, and `RawHtml` nodes;
- locally scoped `(markup ...)` blocks with `$tag` lowering;
- deterministic, escaped-by-default HTML serialization with explicit trusted raw HTML;
- CommonMark AST conversion into the shared node model;
- YAML front matter and recursive Markdown discovery;
- eager persistent filtering, sorting, and limiting of content collections;
- generated clean routes and duplicate/conflicting output detection;
- ordinary functions for components and layouts;
- Pygments syntax highlighting over structural code nodes;
- static asset discovery and copying;
- deterministic full builds with safe output cleanup;
- a full-rebuild development server with isolated generations and browser reload;
- a project-local `spork site ...` command provider for source-only sites;
- XML sitemap, RSS 2.0, and Atom 1.0 generation;
- generic immutable post-order node transformations.
