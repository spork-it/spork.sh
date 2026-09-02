---
title: Command provider
description: Declare, validate, build, install, and invoke a package-owned top-level Spork command.
section: example
group: examples
project: spork-lang
order: 840
package-version: "0.6.3"
changefreq: monthly
priority: 0.6
---

A provider package declares one complete top-level command and owns every argument after that name.

## Manifest

```spork
{:name "spork-greeter"
 :version "0.1.0"
 :description "Minimal Spork command provider"
 :requires-python ">=3.10"
 :spork-version ">=0.6,<0.7"
 :dependencies []
 :source-paths ["src"]
 :test-paths []
 :commands
 {"greet" {:main "spork-greeter.cli:command"
            :description "Print a greeting"}}}
```

## Provider source

```spork
(ns spork-greeter.cli)

(defn ^int command [context argv]
  (print "Hello from a Spork command provider")
  0)
```

Validate it, then install the current checkout for an end-to-end command test:

```bash
spork check
spork plugin add .
spork plugin which greet
spork greet
```

The local installation compiles a temporary wheel and installs a validated snapshot in an isolated managed environment. It does not use or modify the project's `.spork-out/` or `dist/` directories. Run `spork plugin add .` again after editing, and remove the snapshot with `spork plugin remove spork-greeter` when testing is complete.

Build the publication artifacts separately:

```bash
spork dist --clean
```

The distribution contains a `spork.commands.v1` entry point. After adding the published package or wheel as a consumer dependency and synchronizing, invoke it with `spork greet`. Top-level discovery reads package metadata without importing the provider; only selection loads the compiled function. See the complete [command-provider contract](/docs/reference/tooling/command-providers/).
