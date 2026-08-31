---
title: Development server
description: Serve isolated full-build generations, retain successful output after failures, and reload browsers safely.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 656
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

Start the default development server from any directory below the project root:

```bash
spork site serve
spork site serve --host 0.0.0.0 --port 8000 --open
```

Development mode performs correct full builds rather than mutating loaded source namespaces. The supervisor:

1. launches each build in a fresh project `spork` process;
2. writes it into a new temporary generation directory;
3. switches HTTP serving only after that complete build succeeds;
4. retains the last successful generation when a rebuild fails;
5. broadcasts a server-sent reload event after successful rebuilds.

HTML responses receive a small reload client while they are served. The generated files themselves are never modified, and `serve` does not write to the site's configured output directory. Static responses include an `X-Spork-Site-Generation` header for development inspection.

The `:site :watch` vector controls watched project-relative files and directories:

```spork
:site
{:target "example.site:make-site"
 :watch ["spork.it" "src" "content" "static"]}
```

When omitted, those four paths are the defaults. Related filesystem events are debounced into one rebuild. The configured output plus `.venv`, `.spork-out`, VCS metadata, Python caches, and common tool caches are ignored. If the first build fails, the reload-enabled server starts with a temporary error response and continues watching for a successful repair.

Use `--open` to launch the development URL in the default browser. `--port 0` selects an available port. `--no-reload` builds and serves one immutable generation without watching, SSE, or HTML client injection. Stop either mode with Ctrl-C.
