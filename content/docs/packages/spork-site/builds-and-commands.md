---
title: Builds and commands
description: Construct deterministic site plans and use package-owned build, check, routes, serve, clean, and version commands.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 655
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

This page defines how a site becomes a validated output plan and how the package-owned top-level `spork site` command checks, builds, inspects, serves, and cleans that plan.

**Namespaces:** site values come from `spork-site.build`; pages and raw output files come from `spork-site.routing`.

## Complete build

A site is an ordinary persistent map constructed by `build.site`:

```spork
(defn make-site []
  (build.site
    * :output "public"
      :pages [content-pages
              (routing.output-file "/sitemap.xml" sitemap-output)
              (routing.output-file "/feed.xml" rss-output)
              (routing.output-file "/atom.xml" atom-output)]
      :assets (build.discover-assets "static")
      :transforms []))
```

The factory is an ordinary source function. Configure it independently from the application's `:main`:

```spork
{:name "example"
 :version "0.1.0"
 :spork-version ">=0.6,<0.7"
 :dependencies ["spork-site>=0.1,<0.2"]
 :source-paths ["src"]

 :site
 {:target "example.site:make-site"
  :watch ["spork.it" "src" "content" "static"]}

 :main "example.app:main"}
```

Synchronize once, then use the project-local provider:

```bash
spork sync
spork site check
spork site routes
spork site build
spork site clean
spork site serve
```

`spork-site` loads `example.site:make-site` directly from configured source paths through the Spork command context. The site does not need an ahead-of-time build, a Python-importable adapter, a replacement application entry point, or manual virtualenv activation.

A build:

1. validates and canonicalizes every route;
2. detects duplicate, page/asset, and parent/child path conflicts;
3. renders all page content and transformations;
4. validates asset sources and output safety;
5. cleans the output directory by default;
6. writes pages and assets in lexical output-path order;
7. returns a persistent summary map.

```spork
{:output #p"/project/public"
 :pages 4
 :assets 1
 :written ["atom.xml" "feed.xml" "index.html" "site.css" "sitemap.xml"]}
```

Set `:clean? false` to retain unrelated output files. Output paths cannot be the project directory, an ancestor of it, or a filesystem root. Asset sources inside a cleaned output directory are rejected before deletion.

## Site commands

The package owns one complete top-level CLI:

```text
spork site build [--output PATH] [--no-clean] [--json]
spork site check [--json]
spork site clean [--output PATH]
spork site routes [--json]
spork site serve [--host HOST] [--port PORT] [--open] [--no-reload]
spork site version
```

`check` loads the source factory and constructs the complete rendered page, asset, conflict, and output plan without creating, cleaning, or writing the output directory. `routes` performs the same validation and reports canonical route/output pairs. `clean` uses the factory's configured output by default and applies the same project-root and filesystem-root protections as builds. `version` reports the selected provider version, Spork host version, command API, and project/active scope.
