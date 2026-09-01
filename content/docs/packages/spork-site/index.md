---
title: spork-site
description: Structural markup, CommonMark content, deterministic static publishing, and full-rebuild development serving.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 650
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

`spork-site` is a source-first static publishing library that owns the top-level `spork site` command. Sites remain ordinary Spork projects: a configured source function returns an immutable site value, and the package command checks, builds, inspects, or serves it.

## Install

Declare the package and a source factory in `spork.it`:

<!-- verify-docs: compile=manifest-fragment -->
```spork
{:spork-version "==0.6.1"
 :dependencies ["spork-site==0.1.1"]
 :source-paths ["src"]
 :site {:target "example.site:make-site"
        :watch ["spork.it" "src" "content" "static"]}}
```

Then synchronize and inspect the complete plan:

```bash
spork sync
spork site check
spork site routes
spork site build
```

## Complete reference

- [Getting started](/docs/packages/spork-site/getting-started/)
- [Content and front matter](/docs/packages/spork-site/content/)
- [Document collections](/docs/packages/spork-site/collections/)
- [Routing and layouts](/docs/packages/spork-site/routing-and-layouts/)
- [Builds and commands](/docs/packages/spork-site/builds-and-commands/)
- [Development server](/docs/packages/spork-site/development-server/)
- [Feeds and sitemaps](/docs/packages/spork-site/feeds-and-sitemaps/)
- [Markup](/docs/packages/spork-site/markup/)
- [Markdown and transforms](/docs/packages/spork-site/markdown-and-transforms/)
- [Node API](/docs/packages/spork-site/node-api/)

## Contracts

- Markup and Markdown produce the same immutable node representation.
- Routes, content discovery, feeds, sitemaps, static assets, and output plans are deterministic.
- Unsafe output paths and route or target conflicts fail before deletion or writing.
- `check` and `routes` validate complete plans without modifying output.
- Development serving rebuilds in a fresh worker process and activates only complete successful generations.
- A failed rebuild retains the last successful generation.
- Browser reload code is injected only into served HTML, never generated files.

This website is a source-only production consumer of the package. Its [`make-site` source](https://github.com/spork-it/spork.sh/blob/main/src/spork_sh/site.spork) composes Markdown documents, generated outputs, and byte-for-byte static assets without a separate Python application entry point.

- [Source](https://github.com/spork-it/spork-site)
- [PyPI](https://pypi.org/project/spork-site/0.1.1/)
- [Release](https://github.com/spork-it/spork-site/releases/tag/v0.1.1)
