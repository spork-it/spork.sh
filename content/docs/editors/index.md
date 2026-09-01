---
title: Editors
description: Maintained Emacs and Neovim integrations for Spork source, evaluation, diagnostics, and navigation.
section: editor
group: editors
project: spork-lang
order: 700
nav-title: Editor integrations
package-version: "0.6.2"
changefreq: monthly
priority: 0.6
---

Spork ships editor integrations beside the language source so syntax and tooling can evolve with the compiler. Both integrations invoke the installed `spork` launcher and therefore honor project-local toolchain delegation.

## Choose an integration

- [Neovim](/docs/editors/neovim/) provides filetype detection, syntax, indentation, and Language Server Protocol setup.
- [Emacs](/docs/editors/emacs/) provides a major mode and an nREPL-driven interactive development workflow.

Install the [documented Spork release](/docs/getting-started/) first, then point the editor integration at the corresponding directory in a `spork-lang` checkout.
