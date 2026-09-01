---
title: Tooling reference
description: Create and operate Spork projects with the manifest and package-aware CLI.
section: reference
group: tooling
project: spork-lang
order: 300
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Spork project commands find the nearest `spork.it`, prepare an isolated environment, and use the compatible project-local toolchain declared by that manifest. This section is the complete tooling contract for Spork 0.6.1.

## Create a project

```bash
spork new hello-spork
cd hello-spork
spork sync
spork check
spork test
spork run
```

`spork new` creates a project with this layout:

```text
hello-spork/
├── spork.it
├── src/
│   └── hello_spork/
│       └── core.spork
├── tests/
│   └── hello_spork/
│       └── core_test.spork
├── .gitignore
└── README.md
```

Project names are normalized to lower-case Lisp-style names. Underscores become hyphens and unsupported characters are removed.

Project-aware commands locate a project by searching the current directory and its parents for `spork.it`. They use the first (nearest) manifest found, so they may be run from any subdirectory of the project.
