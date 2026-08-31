---
title: Install Spork
description: Spork supports CPython 3.10 through 3.14
changefreq: weekly
priority: 0.9
---

# Install `spork`

```bash
curl -fsSL https://spork.sh/install | sh
```

The installer creates an isolated environment under `~/.spork` and links `spork` into `~/.local/bin`. It does not use `sudo` or edit shell configuration. You can [read the installer source](/install) before running it.

The [complete getting-started guide](/docs/getting-started/) covers checksum verification, `pipx` and `pip`, running a first source file, the REPL, project environments, dependencies, tests, and builds.
