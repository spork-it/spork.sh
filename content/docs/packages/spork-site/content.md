---
title: Content and front matter
description: Discover CommonMark documents with persistent metadata, structural content, and canonical routes.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 652
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

Markdown documents use optional YAML front matter:

````markdown
---
title: First Post
date: 2026-08-30T12:00:00Z
summary: A post built with Spork.
tags: [spork, release]
---
## Hello

```python
print("Spork")
```
````

Discovering a content directory returns an eager persistent vector of document maps:

```spork
(ns example.content
  (:require [spork-site.content :as content]))

(def documents (content.load-documents "content"))
```

Each document contains front-matter fields at the top level plus canonical fields:

```text
{:source-path   #p"content/blog/first.md"
 :relative-path "blog/first.md"
 :id            "blog/first"
 :slug          "first"
 :route         "/blog/first/"
 :metadata      {:title "First Post" :tags ["spork" "release"]}
 :body          "## Hello\n..."
 :content       (Fragment [...])
 :title         "First Post"
 :date          #inst"2026-08-30T12:00:00Z"}
```

YAML mappings and sequences become persistent maps and vectors. YAML dates remain Python `date`/`datetime` values. Front-matter sets are rejected because they are unordered.

Routes are derived from relative paths:

| Source | Route | Output |
|---|---|---|
| `index.md` | `/` | `index.html` |
| `docs/index.md` | `/docs/` | `docs/index.html` |
| `blog/hello.md` | `/blog/hello/` | `blog/hello/index.html` |

Use `slug`, `route`, `permalink`, or `url` front matter to override the derived route. Explicit routes are validated and canonicalized.

Pass `:patterns` to select several deterministic globs, or disable highlighting when loading:

```spork
(ns example.options
  (:require [spork-site.content :as content]))

(content.load-documents
  "content"
  * :patterns ["docs/**/*.md" "blog/**/*.md"]
    :highlight? false)
```
