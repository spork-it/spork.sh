---
title: Dependencies and environments
description: Manage requirements, isolated environments, synchronization, and compatible project toolchains.
section: reference
group: tooling
project: spork-lang
order: 320
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Each dependency is a normal `pip` requirement string:

```spork
:dependencies ["requests>=2.32"
               "numpy>=2,<3"]
```

Add or remove runtime dependencies from any directory below the project root:

```bash
spork add httpx "rich>=13"
spork remove httpx rich
```

Each command reports the absolute path of the nearest `spork.it` it changes. Requirements added with `spork add` use normal `pip` syntax. `spork remove` accepts a distribution name and removes its configured requirement even when that requirement contains extras or a version constraint.

After changing dependencies, run:

```bash
spork sync
```

This creates an isolated `.venv/` when needed and installs the dependencies and a compatible `spork-lang` toolchain, which brings in `spork-runtime`. When the active CLI satisfies `:spork-version`, synchronization pins that exact release (or its editable source checkout). Otherwise, pip resolves a release from the declared range. Include development tools when working on the project with:

```bash
spork sync --dev
```

After synchronization, project-aware CLI invocations delegate to the compatible `spork-lang` installed in `.venv`, even when the launcher on `PATH` is a different version. `spork sync` bootstraps a missing or incompatible project toolchain; `spork clean` deliberately remains with the launcher so it can remove `.venv`. An existing environment is not automatically upgraded within its compatible range on every command.

A launcher release that predates project-toolchain delegation cannot bootstrap a newer compiler retroactively. Upgrade that launcher once, run `spork sync`, and subsequent commands will use the project-local toolchain.
