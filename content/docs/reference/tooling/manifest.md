---
title: The spork.it manifest
description: Reference for project metadata, tooling settings, package APIs, and provider configuration.
section: reference
group: tooling
project: spork-lang
order: 310
package-version: "0.6.2"
changefreq: monthly
priority: 0.7
---

A manifest is a Spork map containing project metadata and tooling settings:

```spork
{:name "hello-spork"
 :version "0.1.0"
 :description "A small Spork application"
 :requires-python ">=3.10"
 :spork-version ">=0.6,<0.7"
 :dependencies ["httpx>=0.27" "rich"]
 :dev-dependencies []
 :source-paths ["src"]
 :test-paths ["tests"]
 :main "hello-spork.core:main"}
```

Paths are relative to the directory containing `spork.it`.

| Key | Required | Default | Purpose |
| --- | --- | --- | --- |
| `:name` | yes | — | Project and distribution name. |
| `:version` | yes | — | Project version string. |
| `:description` | no | none | Distribution description. |
| `:requires-python` | no | `">=3.10"` | Python compatibility written to package metadata. |
| `:spork-version` | no | active version | Compatible `spork-lang` toolchain range used by synchronization, CLI delegation, and distribution builds. |
| `:api` | no | none | Generate public Spork and Python package APIs from one canonical namespace. |
| `:commands` | no | `{}` | Top-level command providers published in distribution metadata. |
| `:dependencies` | no | `[]` | Runtime package requirements accepted by `pip`. |
| `:dev-dependencies` | no | `[]` | Local tools installed by `spork sync --dev`. |
| `:optional-dependencies` | no | `{}` | Named Python package extras, such as `{:docs ["sphinx>=8"]}`. |
| `:source-paths` | no | `["src"]` | Directories searched for Spork namespaces and build inputs. |
| `:test-paths` | no | `["tests"]` | Directories searched by `spork test`. |
| `:main` | no | none | Entry point used by `spork run`, in `namespace:function` form. |
| `:readme` | no | `README.md` if present | README included in distribution metadata. |
| `:license` / `:license-file` | no | none / detected `LICENSE*` | SPDX license expression and license file. |
| `:authors` | no | `[]` | Author maps containing `:name` and/or `:email`. |
| `:keywords` / `:classifiers` | no | `[]` | PyPI search terms and trove classifiers. |
| `:urls` | no | `{}` | Labeled project links included in package metadata. |
| package-specific keys | no | none | Configuration owned by an installed tool, such as `:site`. |

Unknown keys are preserved without being interpreted by core project commands. Tool providers can read them through the recursive read-only `ProjectConfig.manifest` mapping, `ProjectConfig.get(...)`, or `ProjectConfig.get_plugin_config(...)`; nested maps and vectors are exposed as immutable mappings and tuples.
