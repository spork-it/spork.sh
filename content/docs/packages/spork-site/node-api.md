---
title: Node API
description: Construct immutable elements, fragments, escaped text, and explicit trusted raw HTML.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 660
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

The node API is the shared representation beneath authored markup and parsed Markdown. Use it directly when a component needs explicit elements, fragments, escaped text, or trusted raw HTML.

**Namespace:** require `spork-site.core` with an alias such as `site`.

```spork
(site.element :a {:class ["button" "primary"]
                  :style {:display "inline-flex" :gap "0.5rem"}
                  :href "/docs/"}
  "Read the docs")

(site.fragment
  (site.text "escaped: <tag>")
  (site.raw-html "<strong>trusted HTML</strong>"))
```

Child rules are intentionally small:

- nodes are retained;
- fragments and deterministic sequences are recursively flattened;
- strings and printable scalars become `Text` nodes;
- `nil` emits nothing;
- maps and unordered sets are rejected as children;
- `RawHtml` is the explicit escape hatch for trusted, unescaped markup.

Attributes are normalized during construction. `:class` accepts nested sequences and ignores `nil`; `:style` accepts a string or deterministically ordered map. `nil` and `false` attributes are omitted, while `true` attributes serialize in HTML boolean form.

## Public namespace map

```text
src/spork_site/
├── build.spork        # deterministic output planning and execution
├── cli.spork          # top-level site command and its subcommands
├── collections.spork  # eager document filtering and sorting
├── content.spork      # front matter, discovery, and document loading
├── core.spork         # general public facade
├── dev.spork          # generation server, watcher, workers, and browser reload
├── feeds.spork        # RSS and Atom
├── highlight.spork    # structural Pygments integration
├── markdown.spork     # CommonMark AST conversion
├── markup.spork       # locally scoped $tag macro
├── nodes.spork        # immutable nodes and normalization
├── render.spork       # deterministic HTML serialization
├── routing.spork      # routes and generated pages
├── sitemap.spork      # sitemap XML
├── transforms.spork   # generic immutable tree transformations
└── xml.spork          # shared XML/date/URL helpers
```

Focused namespaces are supported APIs; `spork-site.core` re-exports the general application-facing surface.
