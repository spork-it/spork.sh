---
title: Project commands
description: Reference for project-aware commands and standalone file execution.
section: reference
group: tooling
project: spork-lang
order: 340
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

The commands in this reference belong to the `spork-lang` launcher. Package-owned commands, such as `spork site`, use the same dispatch and result contracts but own their subcommands and arguments.

| Command | Behavior |
| --- | --- |
| `spork new <name>` | Scaffolds a project in a new directory. |
| `spork repl` | Starts a REPL with project source paths and `.venv` packages available. Creates the environment if it is missing. |
| `spork add <package...>` | Adds or updates runtime requirements in the nearest `spork.it`. |
| `spork remove <package...>` | Removes runtime requirements from the nearest `spork.it`. |
| `spork sync` | Creates `.venv` and installs manifest dependencies plus a toolchain satisfying `:spork-version`. |
| `spork run [args...]` | Loads and calls the configured entry point. Creates the environment if it is missing. |
| `spork test` | Discovers and runs declared Spork tests. |
| `spork check` | Checks project structure, imports, exports, and compilation without writing build output. |
| `spork build` | Compiles all `.spork` files under `:source-paths` into `.spork-out/`. |
| `spork dist` | Builds compiled output, then creates a wheel and source distribution in `dist/`. |
| `spork clean` | Removes `.venv/`. |
| `spork clean --all` | Also removes build and distribution artifacts. |
| `spork lsp` | Starts the Language Server Protocol server on standard input/output. |
| `spork version` | Prints the Spork, Python, and platform versions. |
| `spork plugin add <requirement>` | Installs a command provider in its own managed global environment. |
| `spork plugin remove <package>` | Removes one managed global provider. |
| `spork plugin list` | Lists managed providers, commands, versions, and environment status. |
| `spork plugin which <command>` | Explains the active provider and any shadowed providers. |

Use `spork <command> --help` for command-specific options. Install any project-specific development dependencies before testing with `spork sync --dev`. The `plugin` command is a non-delegated bootstrap command: inside a project it still manages global conveniences, while normal project providers remain dependencies synchronized into `.venv`.

## Standalone commands

A manifest is not required for individual files or command-line expressions:

```bash
spork script.spork
spork -c '(print (+ 1 2 3))'
spork -e script.spork       # print generated Python
spork -i script.spork       # run, then enter the REPL
spork --nrepl               # start the editor-facing nREPL server
```

Run `spork` without arguments to start a standalone REPL. The `--nrepl-client` flag is a diagnostic client for testing an nREPL server rather than an ordinary editing workflow.
