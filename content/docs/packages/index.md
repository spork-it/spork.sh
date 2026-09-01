---
title: Packages
description: Published Spork packages, their supported boundaries, and complete public references.
section: package
group: packages
project: spork-lang
order: 600
nav-title: Package index
package-version: "0.6.1"
version-label: independently versioned
changefreq: monthly
priority: 0.7
---

Spork is released as a small set of independently versioned packages. Applications use the language toolchain while compiled distributions depend only on the runtime and any libraries they actually import.

## Package boundaries

- [**spork-lang**](/docs/packages/spork-lang/) owns the reader, compiler, project manager, launcher, and language tooling.
- [**spork-runtime**](/docs/packages/spork-runtime/) contains the Python runtime expected by compiled Spork code.
- [**spork-pds**](/docs/packages/spork-pds/) provides standalone native persistent collections for Python and Spork.
- [**spork-state**](/docs/packages/spork-state/) provides a synchronized observable atom API to both languages.
- [**spork-site**](/docs/packages/spork-site/) provides structural markup, deterministic static publishing, and the top-level `spork site` command.

Each package page identifies its documented stable release. Package versions are independent; there is no single documentation version.
