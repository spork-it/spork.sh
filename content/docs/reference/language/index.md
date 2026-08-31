---
title: Language reference
description: Complete semantics for Spork 0.6.0 lexical and reader syntax, forms, functions, types, namespaces, and Python interoperability.
section: reference
group: language
project: spork-lang
order: 90
nav-title: Language reference
package-version: "0.6.0"
changefreq: weekly
priority: 0.8
---

Spork is a Lisp dialect hosted on CPython. It compiles forms to Python AST, uses Python objects and exceptions directly, and supplies Lisp syntax, macros, and persistent collections.

Use the pages in this section as the language contract for Spork 0.6.0. Start with [lexical syntax](/docs/reference/language/lexical-syntax/) for tokens and literals, then [reader macros](/docs/reference/language/reader-macros/) for every prefix transformation. For a shorter introduction, use the [language tour](/docs/language/). Standard functions and collection operations are documented separately in the [standard library reference](/docs/reference/standard-library/).

## Execution model

Spork keeps Python’s object model, exceptions, modules, call conventions, and runtime tooling. Lisp forms provide expression-oriented control flow, immutable collection literals, destructuring, macros, protocols, and explicit tail recursion.

## Feature summary

| Feature | Python | Spork | Implementation |
|---------|--------|-------|----------------|
| Tail Recursion | No built-in optimization | Explicit `loop`/`recur` | Compiles to a loop |
| Data Structures | Mutable and immutable built-ins | Persistent collection literals | `spork-pds` tries and trees |
| Conditionals | `if`/`elif`/`else`, `match` | `if`, `cond`, `match` | Compiles to Python control flow |
| Metaprogramming | Decorators, metaclasses | Macros and decorators | AST transformation |
| Variable Scope | Function, global, and `nonlocal` | Python scopes plus lexical `let` bindings | Scoped helper functions when needed |
| Function Arity | Defaults and variadic parameters | Defaults, variadic parameters, and multi-arity clauses | Python signatures or runtime dispatch |
| Destructuring | Sequence unpacking and patterns | Nested vector and map patterns | Recursive assignment or pattern tests |
| Imports | `import`/`from` | `ns` with `:require` and `:import` | Macro discovery for required Spork namespaces |
| Protocols | ABCs and duck typing | `defprotocol` | Runtime dispatch table |
| Batch Mutation | Mutable built-in collections | `transient`/`persistent!` | Controlled mutable views |
