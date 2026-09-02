---
title: spork-lang
description: The Spork compiler, source runner, project manager, command system, REPL, and language server.
section: package
group: packages
nav-path: [packages, spork-lang]
project: spork-lang
order: 610
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

`spork-lang` is the development toolchain for Spork source. It reads Lisp forms, compiles them to Python AST, executes source directly, manages project environments, checks namespaces, runs declared tests, and builds Python distributions.

## Install

```bash
python -m pip install "spork-lang==0.6.3"
spork version
```

The hosted [installer](/docs/getting-started/) creates a managed environment and launcher without modifying shell configuration.

## What the package owns

- the reader, macro expansion environment, compiler, and source maps;
- direct file execution, expression execution, and the REPL;
- `spork.it` project discovery, synchronization, checks, tests, builds, and distributions;
- project-toolchain delegation, metadata-only command-provider discovery, and isolated managed global plugins, including temporary-wheel installation from local Spork projects;
- the source import hook, LSP server, and nREPL integration.

Compiled applications normally depend on [`spork-runtime`](/docs/packages/spork-runtime/), not the compiler. Persistent collection storage is supplied by [`spork-pds`](/docs/packages/spork-pds/).

## References

- [Language reference](/docs/reference/language/)
- [Standard library reference](/docs/reference/standard-library/)
- [Tooling reference](/docs/reference/tooling/)
- [Source](https://github.com/spork-it/spork-lang)
- [PyPI](https://pypi.org/project/spork-lang/0.6.3/)
- [Release](https://github.com/spork-it/spork-lang/releases/tag/v0.6.3)
