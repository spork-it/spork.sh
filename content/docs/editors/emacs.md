---
title: Emacs
description: Install spork-mode and use nREPL evaluation, documentation, navigation, inspection, and completion.
section: editor
group: editors
project: spork-lang
order: 720
package-version: "0.6.0"
changefreq: monthly
priority: 0.6
---

`spork-mode` is an Emacs major mode for [Spork](/docs/packages/spork-lang/) with nREPL integration. It provides interactive evaluation, navigation, completion, and inspection for Spork source.

## Requirements

- Emacs 26.1 or later
- Spork CLI installed (`spork` command available)

## Installation

### Manual

1. Add the checked-out `spork-lang/editors/emacs` directory to your Emacs load path, or copy `spork-mode.el` into an existing load-path directory.
2. Load the mode from your init file:

```elisp
(add-to-list 'load-path "/path/to/spork-lang/editors/emacs")
(require 'spork-mode)
```

### use-package

```elisp
(use-package spork-mode
  :load-path "/path/to/spork-lang/editors/emacs"
  :mode "\\.spork\\'")
```

## Features

### Core Features

- Syntax highlighting for Spork code
- Lisp-style indentation and navigation
- Start/stop nREPL server
- Connect to running nREPL server
- Evaluate forms, regions, and buffers
- Load files into the REPL
- REPL buffer with history
- Auto-completion
- Pretty-printed results

### Runtime Features

- Documentation lookup with rich metadata (type, arglists, protocols)
- Macroexpansion - see what your macros expand to
- Jump to definition (M-.) with xref integration
- Interactive value inspector - drill into data structures
- Protocol browser - list all registered protocols

## Usage

### Getting Started

1. Open a `.spork` file (spork-mode activates automatically)
2. Start the nREPL server with `M-x spork-jack-in` or `C-c C-j`
3. Start evaluating code!

Alternatively, connect to an existing nREPL server:

```text
M-x spork-connect
```

## Key Bindings

### Connection

| Key         | Command         | Description                    |
|-------------|-----------------|--------------------------------|
| `C-c C-j`   | `spork-jack-in` | Start server and connect       |
| `C-c C-q`   | `spork-quit`    | Quit connection                |

### Evaluation

| Key         | Command                    | Description                  |
|-------------|----------------------------|------------------------------|
| `C-c C-c`   | `spork-eval-current-sexp`  | Eval form at point           |
| `C-c C-e`   | `spork-eval-last-sexp`     | Eval form before point       |
| `C-c C-r`   | `spork-eval-region`        | Eval region                  |
| `C-c C-b`   | `spork-eval-buffer`        | Eval entire buffer           |
| `C-c C-k`   | `spork-load-current-buffer`| Load current buffer          |
| `C-c C-z`   | `spork-switch-to-repl`     | Switch to REPL buffer        |

### Namespaces

| Key           | Command           | Description              |
|---------------|-------------------|--------------------------|
| `C-c C-n`     | `spork-set-ns`    | Switch to namespace      |
| `C-c n`       | `spork-current-ns`| Show current namespace   |
| `C-c C-S-n`   | `spork-list-ns`   | List all namespaces      |

### Documentation & Info

| Key         | Command               | Description                        |
|-------------|-----------------------|------------------------------------|
| `C-c C-d`   | `spork-doc`           | Show documentation                 |
| `C-c i`     | `spork-info`          | Show rich info (type, arglists)    |
| `C-c C-m`   | `spork-macroexpand`   | Macroexpand form at point          |
| `C-c C-t`   | `spork-transpile`     | Transpile form to Python           |
| `C-c C-p`   | `spork-list-protocols`| List all protocols                 |

### Navigation

| Key       | Command                          | Description                |
|-----------|----------------------------------|----------------------------|
| `M-.`     | `spork-find-definition`          | Jump to definition         |
| `M-,`     | `spork-pop-find-definition-stack`| Pop back from definition   |
| `C-c g`   | `spork-find-definition`          | Jump to definition (alt)   |
| `C-c b`   | `spork-pop-find-definition-stack`| Pop back (alt)             |

### Inspector

| Key         | Command                  | Description              |
|-------------|--------------------------|--------------------------|
| `C-c C-i`   | `spork-inspect-last-sexp`| Inspect last sexp        |

**In Inspector buffer:**

| Key     | Command                    | Description                  |
|---------|----------------------------|------------------------------|
| `n`     | `spork-inspector-nav-index`| Navigate by index            |
| `k`     | `spork-inspector-nav-key`  | Navigate by key              |
| `b`     | `spork-inspector-back`     | Go back                      |
| `q`     | `spork-inspector-quit`     | Quit inspector               |
| `RET`   | `spork-inspector-nav-index`| Navigate by index            |

## Customization

```elisp
;; REPL buffer name
(setq spork-repl-buffer "*spork-repl*")

;; Default nREPL host
(setq spork-default-host "127.0.0.1")

;; Default nREPL port
(setq spork-default-port 7888)

;; Spork CLI command
(setq spork-command "spork")
```

## Source

The integration source is maintained in the [`spork-lang` editor directory](https://github.com/spork-it/spork-lang/tree/v0.6.0/editors/emacs/).
