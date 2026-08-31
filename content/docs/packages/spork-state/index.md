---
title: spork-state
description: Thread-safe validated and observable atoms with one Spork implementation and typed Python API.
section: package
group: packages
nav-path: [packages, spork-state]
project: spork-state
order: 640
package-version: "0.2.1"
changefreq: monthly
priority: 0.7
---

`spork-state` provides `Atom`, a mutable reference whose updates are synchronized, validated before commit, and observed through synchronous watches. Its implementation and declarations are written in Spork; package builds generate both the public Spork namespace and typed Python facade.

## Install

Python projects:

```bash
python -m pip install "spork-state==0.2.1"
```

Spork projects declare the compatible stable line in `spork.it` and synchronize:

<!-- verify-docs: compile=manifest-fragment -->
```spork
:dependencies ["spork-state>=0.2,<0.3"]
```

```bash
spork sync
```

## Contract

- updates, validator replacement, and compare-and-set are linearizable;
- swap functions run exactly once under a reentrant lock;
- validators run before commit;
- watches run synchronously after commit and outside the lock;
- identity, rather than equality, controls compare-and-set and notification; and
- atom synchronization does not make a mutable stored object safe to mutate.

Continue with the [practical guide](/docs/packages/spork-state/guide/), [API reference](/docs/packages/spork-state/api/), and [concurrency design](/docs/packages/spork-state/design/).

- [Source](https://github.com/spork-it/spork-state)
- [PyPI](https://pypi.org/project/spork-state/0.2.1/)
