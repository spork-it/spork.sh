---
title: Command providers
description: Publish package-owned top-level commands and understand metadata-only discovery and dispatch.
section: reference
group: tooling
project: spork-lang
order: 370
package-version: "0.6.0"
changefreq: monthly
priority: 0.7
---

Installed packages can contribute complete top-level `spork` commands through versioned distribution metadata. Discovery remains metadata-only until a selected provider is dispatched.

## Package command providers

A package can publish a complete top-level CLI by declaring `:commands`:

```spork
:commands
{"greet" {:main "hello-spork.cli:command"
          :description "Print a project greeting"}}
```

The target is an ordinary source function with the command-provider contract:

```spork
(ns hello-spork.cli)

(defn ^int command [context argv]
  (print "Hello from Spork")
  0)
```

A provider receives the selected `CommandContext` and a fresh Python list containing only the exact argument strings after its top-level command name. It returns an integer status or `nil` for success and owns any nested parsing and help. Packages normally declare one top-level name and implement all nested verbs behind it. A declaration without a description may use the string shorthand:

```spork
:commands {"greet" "hello-spork.cli:command"}
```

Command names use lower-case letters, digits, and single hyphens, beginning with a letter. Core names such as `run`, `build`, and `plugin` are reserved. Targets must use `namespace:function` form, normalize to valid Python module and function names, and identify a function defined in project source.

`ProjectConfig.commands` exposes typed `CommandConfig` values. `spork check` validates each source target without importing or executing provider code. `spork dist` repeats command validation, verifies the generated module and function are included in the package, and writes normalized entry points under `spork.commands.v1`:

```toml
[project.entry-points."spork.commands.v1"]
greet = "hello_spork.cli:command"
```

The resulting provider distribution depends on `spork-runtime`, not `spork-lang`, unless the package separately uses compiler APIs. See the [command-provider walkthrough](/docs/examples/command-provider/) for a complete minimal package.

## Command discovery and dispatch

After a consumer declares and synchronizes a provider as an ordinary dependency, its complete CLI is available through the provider's top-level name:

```bash
spork sync
spork greet nested --format json
spork greet --help
```

Spork first checks static core commands, then `spork.commands.v1` metadata in the project's `.venv`, and then providers installed in the active launcher environment. A project provider shadows an active provider with the same name. Multiple providers for one name in the same scope are an error; malformed project metadata also prevents silent fallback to an active provider. Spork 0.6.0 does not provide a managed-global plugin installation workflow: declare providers as project dependencies or install them deliberately in the launcher environment.

Discovery reads distribution and entry-point metadata only. It does not import provider modules for top-level help or while considering other commands. Only the selected entry point is loaded. `spork --help` lists each valid extension with its distribution, version, and scope, while provider-owned forms such as `spork greet --help` pass through unchanged.

The provider receives `CommandContext` and a fresh list containing the exact strings after the top-level command. Returning `nil`/`None` means success, and an exact integer becomes the process status. Booleans and other result types are invalid. Broken selected entry points produce concise diagnostics; unexpected provider exceptions are not hidden. Project-backed contexts expose the selected manifest and source runtime.

Compatible project toolchains receive extension candidates through the same delegation used for project-aware core commands. The top-level command and every remaining argument are preserved. Missing or stale project toolchains retain the existing `spork sync` guidance. The top-level name `plugin` is reserved by the launcher and is never delegated to a provider.

Core and installed provider names are commands. Explicit paths and names ending in `.spork` remain files, so `spork ./greet` can execute a file even when `greet` is installed. An unknown bare name is reported as an unknown command and may suggest a close core or extension name.
