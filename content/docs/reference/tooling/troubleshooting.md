---
title: Tooling troubleshooting
description: Resolve project discovery, namespace, dependency, and editor integration problems.
section: reference
group: tooling
project: spork-lang
order: 380
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Start with the relevant failure category, then run the smallest relevant diagnostic command. Errors preserve original `.spork` paths and locations whenever source compilation is involved.

## Project not found

Run the command inside the directory containing `spork.it` or one of its descendants. Check that the filename is exactly `spork.it`.

## Namespace not found

Verify all three locations agree:

1. the directory below a configured `:source-paths` entry;
2. the `.spork` filename;
3. the name in the file's `(ns ...)` declaration.

For `src/acme/core.spork`, the expected namespace is `acme.core`.

## A dependency cannot be imported

Run `spork sync` after editing `:dependencies`. If the environment is stale or damaged, recreate it:

```bash
spork clean
spork sync
```

## Editor integration

Use `spork lsp` for LSP clients or `spork --nrepl` for nREPL clients. Maintained integrations are documented for [Emacs](/docs/editors/emacs/) and [Neovim](/docs/editors/neovim/).
