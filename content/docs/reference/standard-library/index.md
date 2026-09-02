---
title: Standard library reference
description: Built-in values, collection operations, prelude macros, and std.* modules in Spork 0.6.3.
section: reference
group: standard-library
project: spork-lang
order: 390
nav-title: Standard library
package-version: "0.6.3"
changefreq: weekly
priority: 0.8
---

Every Spork namespace receives core runtime functions and the prelude automatically. Python-backed `std.*` namespaces provide focused string, map, and JSON operations. Reader syntax belongs to the [language reference](/docs/reference/language/reader-macros/).

Use this section as the standard-library contract for Spork 0.6.3. Collection literals and language forms are described in the [language reference](/docs/reference/language/); the pages here describe the values and functions available to those forms.

## What is automatically available

- persistent collection types and core collection functions;
- lazy sequence functions, reducers, numeric helpers, and bit operations;
- prelude macros; and
- common Python builtins.

`std.string`, `std.map`, and `std.json` are explicit Spork namespaces. Require them with an alias before use.
