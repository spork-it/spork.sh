---
title: Command providers
description: Publish package-owned top-level commands and understand metadata-only discovery and dispatch.
section: reference
group: tooling
project: spork-lang
order: 370
package-version: "0.6.3"
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

Spork checks static core commands, `spork.commands.v1` metadata in the project's `.venv`, providers installed in the active launcher environment, and finally explicitly managed global providers. A project provider shadows active and global versions of the same command, and an active provider shadows a managed global version. Multiple providers for one name in the same scope are an error; malformed higher-precedence metadata prevents silent fallback.

Discovery reads distribution and entry-point metadata only. It does not import provider modules for top-level help or while considering other commands. Only the selected entry point is loaded. `spork --help` lists each valid extension with its distribution, version, and scope, while provider-owned forms such as `spork greet --help` pass through unchanged.

## Managed global providers

Install a published provider explicitly when its commands should be convenient outside a synchronized project:

```bash
spork plugin add spork-greeter
spork plugin add 'spork-greeter>=0.1,<0.2'
spork plugin list
spork plugin which greet
spork plugin remove spork-greeter
```

Before publishing, install a local Spork project directly from its root:

```bash
cd /path/to/spork-greeter
spork plugin add .
spork plugin which greet
spork greet --help
```

A local path must identify a directory containing `spork.it`, or the manifest itself, and the project must declare at least one `:commands` entry. Spork validates the manifest and command targets, compiles the project into a wheel under temporary managed staging, and installs that wheel through the same isolated validation flow used for published providers. It does not write the project's `.spork-out/` or `dist/` directories.

Local installation is a snapshot rather than an editable link. Run `spork plugin add .` again after changing the source; a valid reinstall atomically replaces the previous environment, while a build, dependency, metadata, or collision failure leaves the working installation untouched. The registry retains the canonical source location so repair diagnostics can direct Spork back to the same checkout. Bare local-path installation is specific to Spork projects; a Python provider project can use a named PEP 508 direct reference such as `spork-greeter @ file:///absolute/path`.

Each requested distribution gets an isolated virtual environment containing the provider, its dependencies, and a compatible `spork-lang` command host. Spork keeps these environments and an atomic locked registry in the platform user-data directory. Set `SPORK_HOME` to replace that directory for a portable or administratively managed installation. A broken or missing environment is not silently ignored: command discovery reports repair guidance, and `plugin list` marks it as broken.

Global plugins are conveniences, not project dependencies. Team projects and CI should still declare the provider in `:dependencies` and run `spork sync`; the project-local provider then predictably shadows the global installation. When a global provider host does not satisfy the project's `:spork-version`, Spork refuses to execute it and recommends adding the provider to the project. `spork plugin` itself is a non-delegated bootstrap command, so running it inside a project always manages the user's global registry.

Providers are trusted executable packages. Spork never installs one because a project mentions a command, never copies a global provider into a project implicitly, and does not import unselected providers during discovery.

The provider receives `CommandContext` and a fresh list containing the exact strings after the top-level command. Returning `nil`/`None` means success, and an exact integer becomes the process status. Booleans and other result types are invalid. Broken selected entry points produce concise diagnostics; unexpected provider exceptions are not hidden. Project-backed contexts expose the selected manifest and source runtime.

Compatible project toolchains receive extension candidates through the same delegation used for project-aware core commands. The top-level command and every remaining argument are preserved. Missing or stale project toolchains retain the existing `spork sync` guidance. The top-level name `plugin` is reserved by the launcher and is never delegated to a provider.

Core and installed provider names are commands. Explicit paths and names ending in `.spork` remain files, so `spork ./greet` can execute a file even when `greet` is installed. An unknown bare name is reported as an unknown command and may suggest a close core or extension name.
